"""Test entity-based dependency inference without Neo4j."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService

# 直接导入，避免触发 Neo4j 依赖
sys.path.insert(0, str(Path(__file__).parent))
from entity_dependency_inferrer import EntityDependencyInferrer


def main():
    print("=" * 80)
    print("Entity-Based Dependency Inference Test")
    print("=" * 80)

    # 1. 使用实体聚类规范化 API
    print("\n[1] Normalizing APIs with entity-centric clustering...")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"✓ Normalized {result['statistics']['total_apis']} APIs")
    print(f"✓ Identified {result['statistics']['total_capabilities']} capabilities")

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

    print(f"✓ Built map with {len(api_map)} APIs")

    # 3. 推断实体依赖
    print("\n[3] Inferring entity-based dependencies...")
    inferrer = EntityDependencyInferrer()
    dependencies = inferrer.infer_dependencies(api_map)

    print(f"✓ Inferred {len(dependencies)} dependencies")

    # 4. 按类型分组显示
    print("\n[4] Dependencies by type:")
    print("=" * 80)

    from collections import defaultdict
    deps_by_type = defaultdict(list)
    for dep in dependencies:
        deps_by_type[dep['type']].append(dep)

    for dep_type, deps in sorted(deps_by_type.items()):
        print(f"\n{dep_type} ({len(deps)} dependencies):")
        print("-" * 80)

        # 显示前 10 个
        for i, dep in enumerate(deps[:10], 1):
            source_api = api_map.get(dep['source'], {})
            target_api = api_map.get(dep['target'], {})

            source_entity = source_api.get('entity', 'unknown')
            target_entity = target_api.get('entity', 'unknown')

            print(f"\n  [{i}] {dep['source']} -> {dep['target']}")
            print(f"      {source_entity} -> {target_entity}")
            print(f"      Score: {dep['score']:.2f}")
            print(f"      Reason: {dep.get('reason', 'N/A')}")

        if len(deps) > 10:
            print(f"\n  ... and {len(deps) - 10} more")

    # 5. 显示关键业务流程
    print("\n[5] Key Business Flows:")
    print("=" * 80)

    # 采购流程
    purchase_deps = [d for d in dependencies
                    if 'purchase' in d['source'].lower()
                    and d['type'] == 'ENTITY_RELATION']

    if purchase_deps:
        print("\nPurchase Flow:")
        entities_involved = set()
        for dep in purchase_deps[:5]:
            source_api = api_map.get(dep['source'], {})
            target_api = api_map.get(dep['target'], {})
            entities_involved.add(source_api.get('entity', 'unknown'))
            entities_involved.add(target_api.get('entity', 'unknown'))
            print(f"  {dep['source']} depends on {dep['target']}")

        print(f"  Entities involved: {', '.join(sorted(entities_involved))}")

    # 销售流程
    sale_deps = [d for d in dependencies
                if 'sale' in d['source'].lower()
                and d['type'] == 'ENTITY_RELATION']

    if sale_deps:
        print("\nSale Flow:")
        entities_involved = set()
        for dep in sale_deps[:5]:
            source_api = api_map.get(dep['source'], {})
            target_api = api_map.get(dep['target'], {})
            entities_involved.add(source_api.get('entity', 'unknown'))
            entities_involved.add(target_api.get('entity', 'unknown'))
            print(f"  {dep['source']} depends on {dep['target']}")

        print(f"  Entities involved: {', '.join(sorted(entities_involved))}")

    # 6. 统计
    print("\n[6] Statistics:")
    print("=" * 80)

    high_conf = [d for d in dependencies if d['score'] >= 0.7]
    print(f"Total dependencies: {len(dependencies)}")
    print(f"High confidence (≥0.7): {len(high_conf)}")
    print(f"Entity relations: {len(deps_by_type.get('ENTITY_RELATION', []))}")
    print(f"CRUD flows: {len(deps_by_type.get('CRUD_FLOW', []))}")

    print("\n" + "=" * 80)
    print("✓ Entity-based dependency inference completed!")
    print("✓ This solves the problem of missing API descriptions")
    print("=" * 80)


if __name__ == '__main__':
    main()
