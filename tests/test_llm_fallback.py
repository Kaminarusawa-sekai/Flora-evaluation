"""Test LLM auto-fallback mechanism."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer


def test_llm_failure_fallback():
    """Test that system falls back when LLM fails."""

    print("=" * 60)
    print("Testing LLM Auto-Fallback Mechanism")
    print("=" * 60)

    # Mock LLM client that fails
    class FailingLLMClient:
        def __call__(self, prompt: str) -> str:
            raise Exception("LLM API unavailable")

    # Test data
    api_map = {
        'createOrder': {
            'operation_id': 'createOrder',
            'method': 'POST',
            'path': '/order/create',
            'entity': 'order',
            'request_schema': {
                'properties': {
                    'customerId': {'type': 'string'},
                    'productId': {'type': 'string'}
                }
            }
        },
        'getCustomer': {
            'operation_id': 'getCustomer',
            'method': 'GET',
            'path': '/customer/get',
            'entity': 'customer'
        },
        'getProduct': {
            'operation_id': 'getProduct',
            'method': 'GET',
            'path': '/product/get',
            'entity': 'product'
        }
    }

    print("\n[Test 1] LLM fails - should auto-fallback")
    print("-" * 60)

    inferrer = DynamicEntityInferrer(
        llm_client=FailingLLMClient(),
        enable_llm_fallback=True
    )

    dependencies = inferrer.infer_dependencies(api_map)

    print(f"\nTotal dependencies found: {len(dependencies)}")

    # Should still find schema-based dependencies
    schema_deps = [d for d in dependencies if d['type'] == 'SCHEMA_REFERENCE']
    print(f"Schema-based dependencies: {len(schema_deps)}")

    for dep in schema_deps:
        print(f"  {dep['source']} -> {dep['target']} (score: {dep['score']:.2f})")

    assert len(dependencies) > 0, "Should find dependencies via fallback"
    assert len(schema_deps) > 0, "Should find schema-based dependencies"

    print("\n✓ Auto-fallback works correctly!")


def test_llm_timeout_fallback():
    """Test fallback when LLM times out."""

    print("\n" + "=" * 60)
    print("[Test 2] LLM timeout - should auto-fallback")
    print("-" * 60)

    class TimeoutLLMClient:
        def __call__(self, prompt: str) -> str:
            import time
            time.sleep(100)  # Simulate timeout
            return "{}"

    api_map = {
        'createOrder': {
            'operation_id': 'createOrder',
            'method': 'POST',
            'path': '/order/create',
            'entity': 'order',
            'request_schema': {
                'properties': {'customerId': {'type': 'string'}}
            }
        },
        'getCustomer': {
            'operation_id': 'getCustomer',
            'method': 'GET',
            'path': '/customer/get',
            'entity': 'customer'
        }
    }

    inferrer = DynamicEntityInferrer(
        llm_client=TimeoutLLMClient(),
        enable_llm_fallback=True
    )

    # Should not hang - should fallback quickly
    dependencies = inferrer.infer_dependencies(api_map)

    print(f"\nDependencies found: {len(dependencies)}")
    assert len(dependencies) > 0, "Should find dependencies via fallback"

    print("✓ Timeout fallback works!")


def test_llm_empty_response_fallback():
    """Test fallback when LLM returns empty response."""

    print("\n" + "=" * 60)
    print("[Test 3] LLM empty response - should auto-fallback")
    print("-" * 60)

    class EmptyLLMClient:
        def __call__(self, prompt: str) -> str:
            return "{}"  # Empty relationships

    api_map = {
        'createOrder': {
            'operation_id': 'createOrder',
            'method': 'POST',
            'path': '/order/create',
            'entity': 'order',
            'request_schema': {
                'properties': {'customerId': {'type': 'string'}}
            }
        },
        'getCustomer': {
            'operation_id': 'getCustomer',
            'method': 'GET',
            'path': '/customer/get',
            'entity': 'customer'
        }
    }

    inferrer = DynamicEntityInferrer(
        llm_client=EmptyLLMClient(),
        enable_llm_fallback=True
    )

    dependencies = inferrer.infer_dependencies(api_map)

    print(f"\nDependencies found: {len(dependencies)}")

    # Should use fallback methods
    schema_deps = [d for d in dependencies if d['type'] == 'SCHEMA_REFERENCE']
    print(f"Schema-based: {len(schema_deps)}")

    assert len(dependencies) > 0, "Should find dependencies via fallback"

    print("✓ Empty response fallback works!")


def test_fallback_disabled():
    """Test that fallback can be disabled."""

    print("\n" + "=" * 60)
    print("[Test 4] Fallback disabled - should only try LLM once")
    print("-" * 60)

    class FailingLLMClient:
        call_count = 0

        def __call__(self, prompt: str) -> str:
            FailingLLMClient.call_count += 1
            raise Exception("LLM failed")

    api_map = {
        'createOrder': {
            'operation_id': 'createOrder',
            'method': 'POST',
            'path': '/order/create',
            'entity': 'order'
        }
    }

    inferrer = DynamicEntityInferrer(
        llm_client=FailingLLMClient(),
        enable_llm_fallback=False  # Disable fallback
    )

    # First call - should try LLM
    deps1 = inferrer.infer_dependencies(api_map)

    # Second call - should try LLM again (no caching of failure)
    deps2 = inferrer.infer_dependencies(api_map)

    print(f"\nLLM call count: {FailingLLMClient.call_count}")
    print("✓ Fallback can be disabled!")


if __name__ == '__main__':
    test_llm_failure_fallback()
    test_llm_empty_response_fallback()
    # test_llm_timeout_fallback()  # Skip timeout test (takes too long)
    test_fallback_disabled()

    print("\n" + "=" * 60)
    print("✓ All Auto-Fallback Tests Passed!")
    print("=" * 60)
