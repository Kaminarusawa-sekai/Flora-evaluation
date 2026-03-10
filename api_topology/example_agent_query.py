"""Example: Agent query using entity skeleton."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from neo4j import GraphDatabase


def agent_query_example():
    """演示 Agent 如何使用实体骨架进行精确查询"""

    print("=" * 80)
    print("Agent Query Example: Cancel Order Task")
    print("=" * 80)

    driver = GraphDatabase.driver(
        "bolt://192.168.1.210:7687",
        auth=("neo4j", "12345678")
    )

    # Scenario: Agent 需要取消订单
    print("\n📋 Task: Cancel an order")
    print("Agent needs to figure out:")
    print("  1. What data is required?")
    print("  2. Where to get the data?")
    print("  3. Which API to call?")

    with driver.session() as session:
        # Step 1: 查找相关能力
        print("\n" + "=" * 80)
        print("Step 1: Find relevant capability")
        print("=" * 80)

        result = session.run("""
            MATCH (c:Capability)
            WHERE c.name CONTAINS 'order' OR c.entity = 'order'
            RETURN c.name as capability, c.entity as entity,
                   c.required_inputs as inputs
            LIMIT 5
        """)

        capabilities = []
        for record in result:
            cap = record['capability']
            capabilities.append(cap)
            print(f"\n  Found: {cap}")
            print(f"    Entity: {record['entity']}")
            print(f"    Required inputs: {record['inputs']}")

        if not capabilities:
            print("  ⚠ No capabilities found")
            driver.close()
            return

        # 选择第一个能力
        selected_capability = capabilities[0]
        print(f"\n  ✓ Selected: {selected_capability}")

        # Step 2: 查找数据来源（实体级）
        print("\n" + "=" * 80)
        print("Step 2: Find data sources (Entity level)")
        print("=" * 80)

        result = session.run("""
            MATCH (c:Capability {name: $capability})
            MATCH (e:Entity {name: c.entity})-[r:REQUIRES_DATA]->(f:Entity)
            RETURN f.name as source_entity,
                   r.data_fields as fields,
                   r.producer_apis as apis,
                   r.avg_confidence as confidence
            ORDER BY r.avg_confidence DESC
        """, capability=selected_capability)

        data_sources = []
        for record in result:
            source = {
                'entity': record['source_entity'],
                'fields': record['fields'],
                'apis': record['apis'],
                'confidence': record['confidence']
            }
            data_sources.append(source)

            print(f"\n  Data source: {record['source_entity']}")
            print(f"    Fields: {record['fields']}")
            print(f"    Confidence: {record['confidence']:.2f}")
            print(f"    Producer APIs: {record['apis'][:2]}...")

        # Step 3: 查找具体的 Producer API
        print("\n" + "=" * 80)
        print("Step 3: Find specific Producer APIs")
        print("=" * 80)

        if data_sources:
            first_source = data_sources[0]
            producer_apis = first_source['apis'][:3]  # 取前 3 个

            for api_id in producer_apis:
                result = session.run("""
                    MATCH (a:API {operation_id: $api_id})
                    RETURN a.operation_id as op_id,
                           a.path as path,
                           a.method as method,
                           a.role as role,
                           a.output_fields_list as outputs
                """, api_id=api_id)

                for record in result:
                    print(f"\n  Producer API: {record['op_id']}")
                    print(f"    Path: {record['path']}")
                    print(f"    Method: {record['method']}")
                    print(f"    Role: {record['role']}")
                    print(f"    Outputs: {record['outputs'][:3]}...")

        # Step 4: 查找 Consumer API（入口点）
        print("\n" + "=" * 80)
        print("Step 4: Find Consumer API (entry point)")
        print("=" * 80)

        result = session.run("""
            MATCH (c:Capability {name: $capability})
            MATCH (a:API {entity: c.entity})
            WHERE a.role = 'CONSUMER'
            RETURN a.operation_id as op_id,
                   a.path as path,
                   a.method as method,
                   a.input_fields_list as inputs
            LIMIT 3
        """, capability=selected_capability)

        consumer_apis = []
        for record in result:
            consumer_apis.append(record['op_id'])
            print(f"\n  Consumer API: {record['op_id']}")
            print(f"    Path: {record['path']}")
            print(f"    Method: {record['method']}")
            print(f"    Inputs: {record['inputs'][:3]}...")

        # Step 5: 生成执行计划
        print("\n" + "=" * 80)
        print("Step 5: Generate Execution Plan")
        print("=" * 80)

        if data_sources and consumer_apis:
            print("\n  Execution Plan:")
            print(f"  1. Call Producer API: {producer_apis[0] if producer_apis else 'N/A'}")
            print(f"     → Get data: {first_source['fields']}")
            print(f"  2. Call Consumer API: {consumer_apis[0]}")
            print(f"     → Complete task: {selected_capability}")
            print("\n  ✓ Plan generated successfully!")
        else:
            print("\n  ⚠ Cannot generate plan - missing data sources or entry points")

        # Step 6: 对比传统方式
        print("\n" + "=" * 80)
        print("Comparison: Traditional vs Entity Skeleton")
        print("=" * 80)

        print("\n  Traditional approach:")
        print("    1. Search all APIs for 'cancel'")
        print("    2. Find cancelOrder API")
        print("    3. Discover it needs order_id")
        print("    4. ❌ Don't know where to get order_id")
        print("    5. ❌ Manual intervention needed")

        print("\n  Entity Skeleton approach:")
        print("    1. Query Capability layer")
        print("    2. Get required inputs from contract")
        print("    3. Query Entity layer for data sources")
        print("    4. Get specific Producer APIs")
        print("    5. ✓ Execute with complete plan")

    driver.close()

    print("\n" + "=" * 80)
    print("✓ Agent Query Example Completed!")
    print("=" * 80)


if __name__ == '__main__':
    agent_query_example()
