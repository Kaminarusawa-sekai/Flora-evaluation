"""测试改进后的推断策略"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_topology.graph_builder import GraphBuilder
from openai import OpenAI


def create_test_capabilities():
    """创建测试数据：模拟 ERP 系统的采购订单和供应商"""
    return [
        {
            'name': 'Purchase Order Management',
            'resource': 'purchase-order',
            'apis': [
                {
                    'operation_id': 'createPurchaseOrder',
                    'method': 'POST',
                    'path': '/purchase-order/create',
                    'summary': 'Create a new purchase order',
                    'entity_anchor': 'purchase-order',
                    'request_fields': [
                        {'name': 'supplierCode', 'type': 'string'},  # 不规范命名
                        {'name': 'productList', 'type': 'array'},
                        {'name': 'totalAmount', 'type': 'number'}
                    ],
                    'response_fields': [
                        {'name': 'orderId', 'type': 'string'},
                        {'name': 'status', 'type': 'string'}
                    ]
                },
                {
                    'operation_id': 'updatePurchaseOrder',
                    'method': 'PUT',
                    'path': '/purchase-order/update',
                    'summary': 'Update purchase order',
                    'entity_anchor': 'purchase-order',
                    'request_fields': [
                        {'name': 'orderId', 'type': 'string'},
                        {'name': 'status', 'type': 'string'}
                    ],
                    'response_fields': [
                        {'name': 'success', 'type': 'boolean'}
                    ]
                },
                {
                    'operation_id': 'getPurchaseOrder',
                    'method': 'GET',
                    'path': '/purchase-order/get',
                    'summary': 'Get purchase order details',
                    'entity_anchor': 'purchase-order',
                    'request_fields': [
                        {'name': 'orderId', 'type': 'string'}
                    ],
                    'response_fields': [
                        {'name': 'orderId', 'type': 'string'},
                        {'name': 'supplierCode', 'type': 'string'},
                        {'name': 'productList', 'type': 'array'},
                        {'name': 'status', 'type': 'string'}
                    ]
                }
            ]
        },
        {
            'name': 'Supplier Management',
            'resource': 'supplier',
            'apis': [
                {
                    'operation_id': 'getSupplier',
                    'method': 'GET',
                    'path': '/supplier/get',
                    'summary': 'Get supplier information',
                    'entity_anchor': 'supplier',
                    'request_fields': [
                        {'name': 'supplierCode', 'type': 'string'}
                    ],
                    'response_fields': [
                        {'name': 'supplierCode', 'type': 'string'},
                        {'name': 'supplierName', 'type': 'string'},
                        {'name': 'contactInfo', 'type': 'object'}
                    ]
                },
                {
                    'operation_id': 'listSuppliers',
                    'method': 'GET',
                    'path': '/supplier/list',
                    'summary': 'List all suppliers',
                    'entity_anchor': 'supplier',
                    'request_fields': [],
                    'response_fields': [
                        {'name': 'suppliers', 'type': 'array'}
                    ]
                }
            ]
        },
        {
            'name': 'Product Management',
            'resource': 'product',
            'apis': [
                {
                    'operation_id': 'getProduct',
                    'method': 'GET',
                    'path': '/product/get',
                    'summary': 'Get product information',
                    'entity_anchor': 'product',
                    'request_fields': [
                        {'name': 'productId', 'type': 'string'}
                    ],
                    'response_fields': [
                        {'name': 'productId', 'type': 'string'},
                        {'name': 'productName', 'type': 'string'},
                        {'name': 'price', 'type': 'number'}
                    ]
                }
            ]
        }
    ]


def test_with_llm():
    """测试带 LLM 的推断"""
    print("=" * 80)
    print("测试 1: 带 LLM 的多层推断")
    print("=" * 80)

    # 初始化 LLM 客户端（使用通义千问）
    try:
        llm_client = OpenAI(
            api_key="sk-",  # 替换为你的 API key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        print("✓ LLM 客户端初始化成功")
    except Exception as e:
        print(f"✗ LLM 客户端初始化失败: {e}")
        llm_client = None

    # 创建 GraphBuilder
    builder = GraphBuilder(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="12345678",
        llm_client=llm_client
    )

    # 构建图
    capabilities = create_test_capabilities()
    result = builder.build(capabilities)

    print("\n" + "=" * 80)
    print("构建结果:")
    print("=" * 80)
    print(f"API 节点数: {result['apis_created']}")
    print(f"实体节点数: {result['entities_created']}")
    print(f"实体关系数: {result['entity_relationships']}")
    print(f"API 依赖数: {result['api_dependencies']}")

    # 查询结果
    with builder.driver.session() as session:
        print("\n" + "=" * 80)
        print("实体关系 (L1 层 - 骨架):")
        print("=" * 80)
        result = session.run("""
            MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
            RETURN e1.name as source, e2.name as target,
                   r.inferred_from as method, r.confidence as confidence
            ORDER BY r.confidence DESC
        """)
        for record in result:
            print(f"  {record['source']} -> {record['target']}")
            print(f"    方法: {record['method']}, 置信度: {record['confidence']:.2f}")

        print("\n" + "=" * 80)
        print("API 依赖 (L3 层 - 肌肉):")
        print("=" * 80)
        result = session.run("""
            MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
            RETURN a1.operation_id as source, a2.operation_id as target,
                   r.type as method, r.score as score, r.filtered_by_entity_relation as filter
            ORDER BY r.score DESC
        """)
        for record in result:
            print(f"  {record['source']} -> {record['target']}")
            print(f"    方法: {record['method']}, 分数: {record['score']:.2f}, 过滤器: {record['filter']}")

    builder.close()
    print("\n✓ 测试完成")


def test_without_llm():
    """测试不带 LLM 的降级推断"""
    print("\n" + "=" * 80)
    print("测试 2: 不带 LLM 的降级推断")
    print("=" * 80)

    # 创建 GraphBuilder（不使用 LLM）
    builder = GraphBuilder(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="12345678",
        llm_client=None
    )

    # 构建图
    capabilities = create_test_capabilities()
    result = builder.build(capabilities)

    print("\n" + "=" * 80)
    print("构建结果:")
    print("=" * 80)
    print(f"API 节点数: {result['apis_created']}")
    print(f"实体节点数: {result['entities_created']}")
    print(f"实体关系数: {result['entity_relationships']}")
    print(f"API 依赖数: {result['api_dependencies']}")

    # 查询结果
    with builder.driver.session() as session:
        print("\n" + "=" * 80)
        print("实体关系 (降级方案):")
        print("=" * 80)
        result = session.run("""
            MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
            RETURN e1.name as source, e2.name as target,
                   r.inferred_from as method, r.confidence as confidence
            ORDER BY r.confidence DESC
        """)
        count = 0
        for record in result:
            print(f"  {record['source']} -> {record['target']}")
            print(f"    方法: {record['method']}, 置信度: {record['confidence']:.2f}")
            count += 1

        if count == 0:
            print("  (无实体关系被推断出)")

        print("\n" + "=" * 80)
        print("API 依赖 (降级方案):")
        print("=" * 80)
        result = session.run("""
            MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
            RETURN a1.operation_id as source, a2.operation_id as target,
                   r.type as method, r.score as score
            ORDER BY r.score DESC
        """)
        count = 0
        for record in result:
            print(f"  {record['source']} -> {record['target']}")
            print(f"    方法: {record['method']}, 分数: {record['score']:.2f}")
            count += 1

        if count == 0:
            print("  (无 API 依赖被推断出)")

    builder.close()
    print("\n✓ 测试完成")


if __name__ == '__main__':
    # 测试 1: 带 LLM
    test_with_llm()

    # 测试 2: 不带 LLM（降级）
    test_without_llm()

    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)
    print("\n预期结果:")
    print("1. 实体关系推断:")
    print("   - LLM 模式: purchase-order -> supplier (通过 LLM 理解语义)")
    print("   - 降级模式: purchase-order -> supplier (通过字段 supplierCode)")
    print("\n2. API 依赖推断:")
    print("   - 字段匹配: createPurchaseOrder -> getSupplier (supplierCode 匹配)")
    print("   - CRUD Flow: updatePurchaseOrder -> getPurchaseOrder (update 依赖 get)")
    print("   - LLM 语义: 补充字段匹配未发现的依赖")
