"""Test entity-level relationship building."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api_normalization import NormalizationService
from api_topology import TopologyService


def test_entity_skeleton():
    """测试实体级逻辑骨架构建"""
    print("=" * 80)
    print("Testing Entity-Level Logical Skeleton")
    print("=" * 80)

    # 1. 规范化 API
    print("\n[Step 1] Normalizing APIs with entity clustering")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"✓ Normalized {result['statistics']['total_apis']} APIs")
    print(f"✓ Identified {result['statistics']['total_capabilities']} capabilities")

    # 2. 构建拓扑图（启用实体推断）
    print("\n[Step 2] Building topology graph with entity skeleton")
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
    print(f"Explicit dependencies: {build_result['explicit_dependencies']}")
    print(f"Inferred dependencies: {build_result['inferred_dependencies']}")
    print(f"  - Field-based: {build_result.get('field_based_dependencies', 0)}")
    print(f"  - Entity-based: {build_result.get('entity_based_dependencies', 0)}")
    print(f"\nEntity Skeleton:")
    print(f"  - Entity relationships: {build_result.get('entity_relationships', 0)}")
    print(f"  - Capability contracts: {build_result.get('capability_contracts', 0)}")

    # 3. 查询实体关系
    print("\n" + "=" * 80)
    print("[Step 3] Querying Entity Relationships")
    print("=" * 80)

    with service.builder.driver.session() as session:
        # Query entity relationships
        result = session.run("""
            MATCH (e:Entity)-[r:REQUIRES_DATA]->(f:Entity)
            RETURN e.name as source, f.name as target,
                   r.edge_count as count, r.avg_confidence as confidence,
                   r.data_fields as fields, r.producer_apis as producers
            ORDER BY r.edge_count DESC
            LIMIT 10
        """)

        print("\nTop Entity Relationships:")
        for record in result:
            print(f"\n  {record['source']} → {record['target']}")
            print(f"    Edge count: {record['count']}")
            print(f"    Confidence: {record['confidence']:.2f}")
            print(f"    Data fields: {record['fields']}")
            print(f"    Producer APIs: {record['producers'][:2]}...")  # Show first 2

    # 4. 查询 API 角色
    print("\n" + "=" * 80)
    print("[Step 4] Querying API Roles")
    print("=" * 80)

    with service.builder.driver.session() as session:
        # Query producers
        result = session.run("""
            MATCH (a:API)
            WHERE a.role = 'PRODUCER'
            RETURN a.operation_id as op_id, a.entity as entity,
                   a.path as path, a.output_fields_list as outputs
            LIMIT 5
        """)

        print("\nProducer APIs (provide data to other entities):")
        for record in result:
            print(f"  {record['op_id']} ({record['entity']})")
            print(f"    Path: {record['path']}")
            print(f"    Outputs: {record['outputs'][:3]}...")

        # Query consumers
        result = session.run("""
            MATCH (a:API)
            WHERE a.role = 'CONSUMER'
            RETURN a.operation_id as op_id, a.entity as entity,
                   a.path as path, a.input_fields_list as inputs
            LIMIT 5
        """)

        print("\nConsumer APIs (consume data from other entities):")
        for record in result:
            print(f"  {record['op_id']} ({record['entity']})")
            print(f"    Path: {record['path']}")
            print(f"    Inputs: {record['inputs'][:3]}...")

    # 5. 查询能力契约
    print("\n" + "=" * 80)
    print("[Step 5] Querying Capability Contracts")
    print("=" * 80)

    with service.builder.driver.session() as session:
        result = session.run("""
            MATCH (c:Capability)
            RETURN c.name as capability, c.entity as entity,
                   c.required_inputs as inputs, c.entry_points as entry_points
            LIMIT 5
        """)

        print("\nCapability Contracts:")
        for record in result:
            print(f"\n  Capability: {record['capability']}")
            print(f"    Entity: {record['entity']}")
            print(f"    Required inputs: {record['inputs']}")
            print(f"    Entry points: {record['entry_points'][:100]}...")

    # 6. 演示 Agent 查询流程
    print("\n" + "=" * 80)
    print("[Step 6] Agent Query Example")
    print("=" * 80)

    print("\nScenario: Agent wants to cancel an order")
    print("\nStep 1: Find capability")
    with service.builder.driver.session() as session:
        result = session.run("""
            MATCH (c:Capability)
            WHERE c.name CONTAINS 'order' OR c.entity CONTAINS 'order'
            RETURN c.name as capability, c.required_inputs as inputs
            LIMIT 3
        """)

        for record in result:
            print(f"  Found: {record['capability']}")
            print(f"    Needs: {record['inputs']}")

    print("\nStep 2: Find data sources")
    with service.builder.driver.session() as session:
        result = session.run("""
            MATCH (e:Entity {name: 'order'})-[r:REQUIRES_DATA]->(f:Entity)
            RETURN f.name as source_entity, r.data_fields as fields,
                   r.producer_apis as apis
            LIMIT 3
        """)

        for record in result:
            print(f"  Can get data from: {record['source_entity']}")
            print(f"    Fields: {record['fields']}")
            print(f"    Via APIs: {record['apis'][:2]}")

    service.close()

    print("\n" + "=" * 80)
    print("✓ Entity Skeleton Test Completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_entity_skeleton()
