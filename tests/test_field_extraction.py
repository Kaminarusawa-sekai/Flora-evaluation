"""测试字段提取功能"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_topology.graph_builder import GraphBuilder


def test_field_extraction():
    """测试不同数据格式的字段提取"""

    # 创建 GraphBuilder 实例
    builder = GraphBuilder(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="12345678"
    )

    print("=" * 80)
    print("测试字段提取功能")
    print("=" * 80)

    # 测试用例1: parameters 格式（实际数据格式）
    api1 = {
        'operation_id': 'test_api_1',
        'method': 'GET',
        'path': '/test/api',
        'parameters': {
            'path': [],
            'query': [
                {'name': 'supplierId', 'type': 'string', 'required': False},
                {'name': 'status', 'type': 'string', 'required': False}
            ],
            'body': [],
            'header': []
        }
    }

    print("\n测试用例1: parameters 格式")
    print(f"输入: {api1['parameters']}")
    request_fields = builder._extract_request_fields(api1)
    print(f"提取的请求字段: {request_fields}")

    # 测试用例2: request_schema 格式
    api2 = {
        'operation_id': 'test_api_2',
        'method': 'POST',
        'path': '/test/create',
        'request_schema': {
            'type': 'object',
            'properties': {
                'supplierCode': {'type': 'string'},
                'productList': {'type': 'array'}
            }
        },
        'response_schemas': {
            '200': {
                'type': 'object',
                'properties': {
                    'orderId': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        }
    }

    print("\n测试用例2: request_schema 格式")
    print(f"输入 request_schema: {api2['request_schema']}")
    request_fields = builder._extract_request_fields(api2)
    print(f"提取的请求字段: {request_fields}")

    print(f"输入 response_schemas: {api2['response_schemas']}")
    response_fields = builder._extract_response_fields(api2)
    print(f"提取的响应字段: {response_fields}")

    # 测试用例3: 直接的 request_fields/response_fields
    api3 = {
        'operation_id': 'test_api_3',
        'method': 'PUT',
        'path': '/test/update',
        'request_fields': [
            {'name': 'orderId', 'type': 'string'},
            {'name': 'status', 'type': 'string'}
        ],
        'response_fields': [
            {'name': 'success', 'type': 'boolean'}
        ]
    }

    print("\n测试用例3: 直接的 request_fields/response_fields")
    print(f"输入 request_fields: {api3['request_fields']}")
    request_fields = builder._extract_request_fields(api3)
    print(f"提取的请求字段: {request_fields}")

    print(f"输入 response_fields: {api3['response_fields']}")
    response_fields = builder._extract_response_fields(api3)
    print(f"提取的响应字段: {response_fields}")

    # 测试字段名提取
    print("\n" + "=" * 80)
    print("测试字段名提取")
    print("=" * 80)

    # 为测试用例添加提取的字段
    api1['request_fields'] = builder._extract_request_fields(api1)
    api1['response_fields'] = builder._extract_response_fields(api1)

    field_names = builder._extract_field_names_from_api(api1, 'request')
    print(f"\nAPI 1 请求字段名: {field_names}")

    api2['request_fields'] = builder._extract_request_fields(api2)
    api2['response_fields'] = builder._extract_response_fields(api2)

    field_names = builder._extract_field_names_from_api(api2, 'request')
    print(f"API 2 请求字段名: {field_names}")

    field_names = builder._extract_field_names_from_api(api2, 'response')
    print(f"API 2 响应字段名: {field_names}")

    builder.close()

    print("\n" + "=" * 80)
    print("✓ 测试完成")
    print("=" * 80)


if __name__ == '__main__':
    test_field_extraction()
