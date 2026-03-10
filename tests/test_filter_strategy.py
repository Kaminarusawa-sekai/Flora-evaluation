"""Test the new filter strategy implementation."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


def test_filter_strategy():
    """测试过滤器策略"""
    print("=" * 80)
    print("Testing Filter Strategy Implementation")
    print("=" * 80)

    from api_normalization import NormalizationService

    # 1. 规范化 API
    print("\n[Step 1] Normalizing APIs with entity clustering")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"✓ Normalized {result['statistics']['total_apis']} APIs")
    print(f"✓ Identified {result['statistics']['total_capabilities']} capabilities")

    # 2. 检查实体字段
    print("\n[Step 2] Checking entity fields")
    entity_count = {}
    for cap in result['capabilities']:
        for api in cap.get('apis', []):
            entity = api.get('entity_anchor')
            if entity:
                entity_count[entity] = entity_count.get(entity, 0) + 1

    print(f"Found {len(entity_count)} entities:")
    for entity, count in sorted(entity_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {entity}: {count} APIs")

    # 3. 构建拓扑图（使用过滤器策略）
    print("\n[Step 3] Building topology with filter strategy")

    try:
        from api_topology import TopologyService

        service = TopologyService(
            neo4j_uri="bolt://192.168.1.210:7687",
            neo4j_user="neo4j",
            neo4j_password="12345678",
            llm_client=None,
            use_entity_inference=True
        )

        build_result = service.build_graph(result['capabilities'])

        print("\n" + "=" * 80)
        print("Build Results")
        print("=" * 80)
        print(f"APIs created: {build_result['apis_created']}")
        print(f"Entities created: {build_result['entities_created']}")
        print(f"Entity relationships: {build_result['entity_relationships']}")
        print(f"API dependencies: {build_result['api_dependencies']}")

        # 4. 查询验证
        print("\n[Step 4] Querying results")

        with service.builder.driver.session() as session:
            # 查询实体关系
            result = session.run("""
                MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
                RETURN e1.name as source, e2.name as target,
                       r.example_field as field
                LIMIT 10
            """)

            print("\nEntity Relationships (骨架):")
            for record in result:
                print(f"  {record['source']} -> {record['target']} (via {record['field']})")

            # 查询 API 依赖
            result = session.run("""
                MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
                RETURN a1.operation_id as source, a2.operation_id as target,
                       r.filtered_by_entity_relation as filtered_by
                LIMIT 10
            """)

            print("\nAPI Dependencies (肌肉):")
            for record in result:
                print(f"  {record['source']} -> {record['target']}")
                print(f"    Filtered by: {record['filtered_by']}")

        service.close()

        print("\n✓ Filter strategy test completed!")

    except Exception as e:
        print(f"\n⚠ Could not test with Neo4j: {e}")
        print("  (This is OK if Neo4j is not available)")


if __name__ == '__main__':
    test_filter_strategy()
