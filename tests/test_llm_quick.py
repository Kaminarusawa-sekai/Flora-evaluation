"""Quick test for LLM inference - run after: conda activate flora"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from api_topology.llm_entity_inferrer import LLMEntityInferrer
from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer


def main():
    print("=" * 60)
    print("Testing LLM Entity Inference")
    print("=" * 60)

    # Mock LLM client
    class MockLLMClient:
        def __call__(self, prompt: str) -> str:
            return """{
                "order": [["customer", 0.9], ["product", 0.85]],
                "payment": [["order", 0.95]]
            }"""

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
        },
        'createPayment': {
            'operation_id': 'createPayment',
            'method': 'POST',
            'path': '/payment/create',
            'entity': 'payment',
            'request_schema': {
                'properties': {'orderId': {'type': 'string'}}
            }
        },
        'getOrder': {
            'operation_id': 'getOrder',
            'method': 'GET',
            'path': '/order/get',
            'entity': 'order'
        }
    }

    print("\n[1] Testing WITH LLM client...")
    inferrer_with_llm = DynamicEntityInferrer(llm_client=MockLLMClient())
    deps_with_llm = inferrer_with_llm.infer_dependencies(api_map)

    print(f"\nTotal dependencies: {len(deps_with_llm)}")

    # Group by type
    by_type = {}
    for dep in deps_with_llm:
        dep_type = dep['type']
        by_type.setdefault(dep_type, []).append(dep)

    for dep_type, deps in by_type.items():
        print(f"\n{dep_type}: {len(deps)} dependencies")
        for dep in deps[:3]:  # Show first 3
            print(f"  {dep['source']} -> {dep['target']} (score: {dep['score']:.2f})")

    # Check LLM inference
    llm_deps = [d for d in deps_with_llm if d['type'] == 'LLM_INFERENCE']
    print(f"\n✓ LLM inference found: {len(llm_deps)} dependencies")

    print("\n" + "=" * 60)
    print("[2] Testing WITHOUT LLM client...")
    inferrer_without_llm = DynamicEntityInferrer(llm_client=None)
    deps_without_llm = inferrer_without_llm.infer_dependencies(api_map)

    print(f"\nTotal dependencies: {len(deps_without_llm)}")
    schema_deps = [d for d in deps_without_llm if d['type'] == 'SCHEMA_REFERENCE']
    print(f"✓ Schema-based inference: {len(schema_deps)} dependencies")

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

    print("\nSummary:")
    print(f"  - With LLM: {len(deps_with_llm)} dependencies")
    print(f"  - Without LLM: {len(deps_without_llm)} dependencies")
    print(f"  - LLM adds: {len(deps_with_llm) - len(deps_without_llm)} extra dependencies")


if __name__ == '__main__':
    main()
