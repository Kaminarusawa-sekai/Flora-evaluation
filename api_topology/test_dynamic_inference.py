"""Test dynamic entity inference without hardcoded mappings."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService

# 直接导入，避免触发 Neo4j 依赖
sys.path.insert(0, str(Path(__file__).parent))
from dynamic_entity_inferrer import DynamicEntityInferrer


def main():
    print("=" * 80)
    print("Dynamic Entity Inference Test (No Hardcoded Mappings)")
    print("=" * 80)

    # 1. 使用实体聚类规范化 API
    print("\n[1] Normalizing APIs with entity-centric clustering...")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"OK Normalized {result['statistics']['total_apis']} APIs")
    print(f"OK Identified {result['statistics']['total_capabilities']} capabilities")

    # 2. 构建 API map
    print("\n[2] Building API map...")
    api_map = {}
    for cap in result['capabilities']:
        resource = cap.get('resource', 'unknown')
        for api in cap.get('apis', []):
            api_map[api['operation_id']] = {
                **api,
                'entity': api.get('entity_anchor', resource),
                'resource': resource,
                'capability': cap['name']
            }

    print(f"OK Built map with {len(api_map)} APIs")

    # 显示发现的实体
    entities = set(api.get('entity', 'unknown') for api in api_map.values())
    entities.discard('unknown')
    print(f"OK Discovered {len(entities)} entities:")
    for entity in sorted(entities)[:10]:
        print(f"   - {entity}")
    if len(entities) > 10:
        print(f"   ... and {len(entities) - 10} more")

    # 3. 动态推断实体依赖
    print("\n[3] Dynamically inferring dependencies...")
    inferrer = DynamicEntityInferrer(min_confidence=0.6)
    dependencies = inferrer.infer_dependencies(api_map)

    print(f"OK Inferred {len(dependencies)} dependencies")

    # 4. 按类型分组显示
    print("\n[4] Dependencies by inference method:")
    print("=" * 80)

    from collections import defaultdict
    deps_by_type = defaultdict(list)
    for dep in dependencies:
        deps_by_type[dep['type']].append(dep)

    for dep_type, deps in sorted(deps_by_type.items()):
        print(f"\n{dep_type} ({len(deps)} dependencies):")
        print("-" * 80)

        # 显示前 5 个
        for i, dep in enumerate(deps[:5], 1):
            source_api = api_map.get(dep['source'], {})
            target_api = api_map.get(dep['target'], {})

            source_entity = source_api.get('entity', 'unknown')
            target_entity = target_api.get('entity', 'unknown')

            print(f"\n  [{i}] {source_entity} -> {target_entity}")
            print(f"      {dep['source']}")
            print(f"      -> {dep['target']}")
            print(f"      Score: {dep['score']:.2f}")
            print(f"      Reason: {dep.get('reason', 'N/A')}")

        if len(deps) > 5:
            print(f"\n  ... and {len(deps) - 5} more")

    # 5. 分析推断方法的效果
    print("\n[5] Inference Method Analysis:")
    print("=" * 80)

    schema_ref = deps_by_type.get('SCHEMA_REFERENCE', [])
    crud_flow = deps_by_type.get('CRUD_FLOW', [])
    path_hier = deps_by_type.get('PATH_HIERARCHY', [])

    print(f"\nSchema Reference (field-based):")
    print(f"  Count: {len(schema_ref)}")
    print(f"  Avg Score: {sum(d['score'] for d in schema_ref) / len(schema_ref):.2f}" if schema_ref else "  Avg Score: N/A")
    print(f"  Example: Detects 'supplier_id' field -> depends on Supplier entity")

    print(f"\nCRUD Flow (operation-based):")
    print(f"  Count: {len(crud_flow)}")
    print(f"  Avg Score: {sum(d['score'] for d in crud_flow) / len(crud_flow):.2f}" if crud_flow else "  Avg Score: N/A")
    print(f"  Example: Update operation -> depends on Get operation")

    print(f"\nPath Hierarchy (structure-based):")
    print(f"  Count: {len(path_hier)}")
    print(f"  Avg Score: {sum(d['score'] for d in path_hier) / len(path_hier):.2f}" if path_hier else "  Avg Score: N/A")
    print(f"  Example: /order/{{id}}/items -> order depends on items")

    # 6. 显示跨实体依赖示例
    print("\n[6] Cross-Entity Dependencies (Schema-based):")
    print("=" * 80)

    if schema_ref:
        # 按源实体分组
        by_source = defaultdict(set)
        for dep in schema_ref[:20]:  # 前20个
            source_api = api_map.get(dep['source'], {})
            target_api = api_map.get(dep['target'], {})
            source_entity = source_api.get('entity', 'unknown')
            target_entity = target_api.get('entity', 'unknown')
            by_source[source_entity].add(target_entity)

        for source_entity, target_entities in sorted(by_source.items())[:5]:
            print(f"\n{source_entity}:")
            print(f"  Depends on: {', '.join(sorted(target_entities))}")

    # 7. 统计
    print("\n[7] Statistics:")
    print("=" * 80)

    high_conf = [d for d in dependencies if d['score'] >= 0.7]
    print(f"Total dependencies: {len(dependencies)}")
    print(f"High confidence (>=0.7): {len(high_conf)} ({len(high_conf)*100//len(dependencies) if dependencies else 0}%)")
    print(f"Schema-based: {len(schema_ref)}")
    print(f"CRUD-based: {len(crud_flow)}")
    print(f"Path-based: {len(path_hier)}")

    print("\n" + "=" * 80)
    print("OK Dynamic entity inference completed!")
    print("OK No hardcoded mappings - works with any API domain")
    print("=" * 80)


if __name__ == '__main__':
    main()
