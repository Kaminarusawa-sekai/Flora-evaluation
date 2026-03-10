"""
将 erp-server-refined.json 转换为 EntiMap 所需的 entities.json 格式
"""

import json
from pathlib import Path


def convert_refined_to_entities(refined_path: str, output_path: str):
    """
    转换聚类后的API定义为EntiMap实体格式

    Args:
        refined_path: erp-server-refined.json 路径
        output_path: 输出的 entities.json 路径
    """
    with open(refined_path, 'r', encoding='utf-8') as f:
        refined_data = json.load(f)

    entities = []

    # 遍历所有 capabilities
    for cap in refined_data.get('capabilities', []):
        entity = {
            'name': cap.get('name', 'Unknown'),
            'description': cap.get('description', ''),
            'api_fields': [],
            'api_paths': []
        }

        # 收集所有API的参数作为字段
        field_map = {}  # 用于去重

        for api in cap.get('apis', []):
            # 添加API路径
            if api.get('path'):
                entity['api_paths'].append(api['path'])

            # 提取参数
            params = api.get('parameters', {})

            # 处理各种参数类型
            for param_type in ['query', 'body', 'path']:
                for param in params.get(param_type, []):
                    field_name = param.get('name', '')
                    if field_name and field_name not in field_map:
                        field_map[field_name] = {
                            'name': field_name,
                            'description': param.get('description', ''),
                            'type': param.get('type', 'string')
                        }

        # 转换为列表
        entity['api_fields'] = list(field_map.values())

        # 只保留有字段的实体
        if entity['api_fields'] or entity['api_paths']:
            entities.append(entity)

    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)

    print(f"转换完成！")
    print(f"- 输入: {refined_path}")
    print(f"- 输出: {output_path}")
    print(f"- 实体数量: {len(entities)}")
    print(f"- 总API数量: {sum(len(e['api_paths']) for e in entities)}")
    print(f"- 总字段数量: {sum(len(e['api_fields']) for e in entities)}")

    return entities


if __name__ == "__main__":
    # 转换文件
    entities = convert_refined_to_entities(
        refined_path="../erp-server-refined.json",
        output_path="./entities.json"
    )

    # 显示前3个实体作为示例
    print("\n前3个实体示例：")
    for i, entity in enumerate(entities[:3], 1):
        print(f"\n{i}. {entity['name']}")
        print(f"   描述: {entity['description']}")
        print(f"   API数量: {len(entity['api_paths'])}")
        print(f"   字段数量: {len(entity['api_fields'])}")
        if entity['api_fields']:
            print(f"   示例字段: {', '.join([f['name'] for f in entity['api_fields'][:5]])}")
