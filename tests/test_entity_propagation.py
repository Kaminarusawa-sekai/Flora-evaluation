"""Test entity field propagation in the pipeline."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api_normalization import NormalizationService


def test_entity_propagation():
    """测试实体字段是否正确传递"""
    print("=" * 80)
    print("Testing Entity Field Propagation")
    print("=" * 80)

    # 1. 规范化 API
    print("\n[Step 1] Normalizing APIs with entity clustering")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"✓ Normalized {result['statistics']['total_apis']} APIs")
    print(f"✓ Identified {result['statistics']['total_capabilities']} capabilities")

    # 2. 检查实体字段
    print("\n[Step 2] Checking entity fields in capabilities")

    entity_count = {}
    apis_with_entity = 0
    apis_without_entity = 0

    for cap in result['capabilities']:
        resource = cap.get('resource', 'unknown')
        print(f"\nCapability: {cap.get('name', 'unnamed')}")
        print(f"  Resource: {resource}")

        for api in cap.get('apis', []):
            entity_anchor = api.get('entity_anchor')
            operation_id = api.get('operation_id', 'unknown')

            if entity_anchor:
                apis_with_entity += 1
                entity_count[entity_anchor] = entity_count.get(entity_anchor, 0) + 1
                print(f"    ✓ {operation_id}: entity_anchor = {entity_anchor}")
            else:
                apis_without_entity += 1
                print(f"    ✗ {operation_id}: NO entity_anchor (will use resource: {resource})")

    # 3. 统计
    print("\n" + "=" * 80)
    print("Entity Statistics")
    print("=" * 80)
    print(f"APIs with entity_anchor: {apis_with_entity}")
    print(f"APIs without entity_anchor: {apis_without_entity}")
    print(f"Total unique entities: {len(entity_count)}")

    print("\nEntity distribution:")
    for entity, count in sorted(entity_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {entity}: {count} APIs")

    # 4. 模拟 graph_builder 的 api_map 构建
    print("\n" + "=" * 80)
    print("Simulating graph_builder api_map construction")
    print("=" * 80)

    api_map = {}
    for cap in result['capabilities']:
        for api in cap.get('apis', []):
            # 模拟 graph_builder.py 的逻辑
            api_map[api['operation_id']] = {
                **api,
                'capability': cap.get('name', ''),
                'entity': api.get('entity_anchor', cap.get('resource', '')),
                'resource': cap.get('resource', '')
            }

    # 5. 模拟 entity grouping
    print("\n[Step 3] Simulating entity grouping")
    from collections import defaultdict

    groups = defaultdict(list)
    for op_id, api in api_map.items():
        entity = api.get('entity_anchor') or api.get('entity') or api.get('resource', 'unknown')
        if entity and entity != 'unknown':
            groups[entity].append(op_id)

    print(f"\nFound {len(groups)} entity groups:")
    for entity, ops in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {entity}: {len(ops)} APIs")
        if len(ops) <= 5:
            for op in ops:
                print(f"    - {op}")

    # 6. 检查问题
    print("\n" + "=" * 80)
    print("Diagnosis")
    print("=" * 80)

    if len(groups) == 0:
        print("❌ PROBLEM: No entity groups found!")
        print("   This means entity fields are not being propagated correctly.")
    elif len(groups) < 5:
        print("⚠ WARNING: Very few entity groups found.")
        print("   Expected more entities from clustering.")
    else:
        print(f"✓ Found {len(groups)} entity groups - looks good!")

    if apis_without_entity > apis_with_entity:
        print(f"⚠ WARNING: More APIs without entity_anchor ({apis_without_entity}) than with ({apis_with_entity})")
        print("   Entity clustering may not be working properly.")

    return {
        'total_apis': apis_with_entity + apis_without_entity,
        'apis_with_entity': apis_with_entity,
        'apis_without_entity': apis_without_entity,
        'entity_groups': len(groups),
        'groups': dict(groups)
    }


if __name__ == '__main__':
    result = test_entity_propagation()

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total APIs: {result['total_apis']}")
    print(f"With entity_anchor: {result['apis_with_entity']} ({result['apis_with_entity']/result['total_apis']*100:.1f}%)")
    print(f"Without entity_anchor: {result['apis_without_entity']} ({result['apis_without_entity']/result['total_apis']*100:.1f}%)")
    print(f"Entity groups: {result['entity_groups']}")

    if result['entity_groups'] > 0:
        print("\n✓ Entity propagation is working!")
    else:
        print("\n❌ Entity propagation has issues!")
