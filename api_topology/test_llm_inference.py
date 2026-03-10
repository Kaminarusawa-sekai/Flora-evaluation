"""Test LLM-based entity inference."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_topology.llm_entity_inferrer import LLMEntityInferrer
from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer


def test_llm_inference_with_mock():
    """Test LLM inference with mock client."""

    # Mock LLM client that returns predefined relationships
    class MockLLMClient:
        def __call__(self, prompt: str) -> str:
            return """{
                "order": [["customer", 0.9], ["product", 0.85]],
                "payment": [["order", 0.95]],
                "order-item": [["order", 0.95], ["product", 0.8]]
            }"""

    # Create test API map
    api_map = {
        'createOrder': {
            'operation_id': 'createOrder',
            'method': 'POST',
            'path': '/order/create',
            'entity': 'order',
            'request_schema': {
                'properties': {
                    'customerId': {'type': 'string'},
                    'productId': {'type': 'string'},
                    'quantity': {'type': 'integer'}
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
        },
        'createPayment': {
            'operation_id': 'createPayment',
            'method': 'POST',
            'path': '/payment/create',
            'entity': 'payment',
            'request_schema': {
                'properties': {
                    'orderId': {'type': 'string'},
                    'amount': {'type': 'number'}
                }
            }
        },
        'getOrder': {
            'operation_id': 'getOrder',
            'method': 'GET',
            'path': '/order/get',
            'entity': 'order'
        }
    }

    # Test with LLM client
    inferrer = DynamicEntityInferrer(llm_client=MockLLMClient())
    dependencies = inferrer.infer_dependencies(api_map)

    print("\n=== LLM Inference Test Results ===")
    print(f"Total dependencies found: {len(dependencies)}")

    # Group by type
    by_type = {}
    for dep in dependencies:
        dep_type = dep['type']
        if dep_type not in by_type:
            by_type[dep_type] = []
        by_type[dep_type].append(dep)

    for dep_type, deps in by_type.items():
        print(f"\n{dep_type}: {len(deps)} dependencies")
        for dep in deps:
            print(f"  {dep['source']} -> {dep['target']} (score: {dep['score']:.2f})")
            print(f"    Reason: {dep.get('reason', 'N/A')}")

    # Verify LLM inference was used
    llm_deps = [d for d in dependencies if d['type'] == 'LLM_INFERENCE']
    assert len(llm_deps) > 0, "LLM inference should produce dependencies"

    print("\n✓ LLM inference test passed!")


def test_priority_order():
    """Test that LLM inference has highest priority."""

    class MockLLMClient:
        def __call__(self, prompt: str) -> str:
            return '{"order": [["customer", 0.95]]}'

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

    # Test with LLM
    inferrer_with_llm = DynamicEntityInferrer(llm_client=MockLLMClient())
    deps_with_llm = inferrer_with_llm.infer_dependencies(api_map)

    # Test without LLM
    inferrer_without_llm = DynamicEntityInferrer(llm_client=None)
    deps_without_llm = inferrer_without_llm.infer_dependencies(api_map)

    print("\n=== Priority Order Test ===")
    print(f"With LLM: {len(deps_with_llm)} dependencies")
    print(f"Without LLM: {len(deps_without_llm)} dependencies")

    # Check that LLM inference is present when available
    llm_deps = [d for d in deps_with_llm if d['type'] == 'LLM_INFERENCE']
    print(f"LLM-based: {len(llm_deps)}")

    # After deduplication, LLM should win (highest score)
    for dep in deps_with_llm:
        if dep['source'] == 'createOrder' and dep['target'] == 'getCustomer':
            print(f"\nFinal dependency type: {dep['type']}")
            print(f"Final score: {dep['score']}")
            # LLM score (0.95) should be higher than schema reference (0.8)
            assert dep['score'] >= 0.9, "LLM inference should have high priority"

    print("\n✓ Priority order test passed!")


def test_without_llm():
    """Test that system works without LLM client."""

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

    # Should work without LLM
    inferrer = DynamicEntityInferrer(llm_client=None)
    dependencies = inferrer.infer_dependencies(api_map)

    print("\n=== Without LLM Test ===")
    print(f"Dependencies found: {len(dependencies)}")

    # Should still find schema-based dependencies
    schema_deps = [d for d in dependencies if d['type'] == 'SCHEMA_REFERENCE']
    assert len(schema_deps) > 0, "Should find schema-based dependencies"

    print("✓ System works without LLM!")


if __name__ == '__main__':
    test_llm_inference_with_mock()
    test_priority_order()
    test_without_llm()
    print("\n=== All LLM Inference Tests Passed! ===")
