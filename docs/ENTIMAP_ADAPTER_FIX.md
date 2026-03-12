# EntiMap Adapter 修复说明

## 问题描述

在运行 pipeline 时遇到错误：
```
TypeError: string indices must be integers, not 'str'
```

错误发生在 `adapters/entimap_adapter.py` 第 45 行：
```python
table_name=result['table_name']
```

## 根本原因

`EntiMapEngine.align_entity()` 方法返回的数据结构是：
```python
{
    'table_name_1': {
        'relation_score': 72,
        'relation_type': 'association',
        'columns_role': {...},
        'field_mapping': {...},  # 注意：单数形式
        ...
    },
    'table_name_2': {...}
}
```

但代码错误地将其当作列表来遍历：
```python
for result in results:  # ❌ 错误：results 是字典，不是列表
    table_name = result['table_name']  # ❌ result 是字符串（键名）
```

## 修复方案

### 1. 修正遍历方式
```python
# 修改前
for result in results:
    table_name = result['table_name']

# 修改后
for table_name, result in results.items():
    # table_name 直接从字典键获取
```

### 2. 修正字段映射提取
```python
# field_mapping 是字典格式：
{
    'date': {
        'db_field': 'payment_time',
        'confidence': 0.8,
        ...
    }
}

# 需要转换为 FieldMapping 对象列表
field_mapping_dict = result.get('field_mapping', {})
field_mappings = []

for api_field, db_field_info in field_mapping_dict.items():
    if isinstance(db_field_info, dict):
        # 从 columns_role 获取角色信息
        columns_role = result.get('columns_role', {})
        db_column = db_field_info.get('db_field', '')
        role = 'business'  # 默认值
        
        # 查找该列的角色
        for role_type, columns in columns_role.items():
            if db_column in columns:
                role = role_type
                break
        
        field_mappings.append(FieldMapping(
            db_column=db_column,
            api_field=api_field,
            role=role,
            confidence=db_field_info.get('confidence', 0.8)
        ))
```

### 3. 修正 Golden SQL 生成
```python
# 修改前
def _generate_golden_sqls(self, entity: Dict, mappings: list) -> list:
    first_table = mappings[0]['table_name']  # ❌ mappings 是字典

# 修改后
def _generate_golden_sqls(self, entity: Dict, mappings: Dict) -> list:
    first_table = next(iter(mappings.keys()))  # ✅ 从字典获取第一个键
```

## 数据结构对照

### EntiMapEngine 返回格式
```python
{
    'erp_bookkeeping_voucher': {
        'relation_score': 72,
        'relation_type': 'association',
        'columns_role': {
            'business': ['pay_type', 'payment_time', 'pay_amount'],
            'technical': ['id', 'create_time', 'update_time', 'tenant_id'],
            'hidden_logic': ['deleted', 'tenant_id']
        },
        'field_mapping': {
            'date': {
                'db_field': 'payment_time',
                'confidence': 0.8,
                'transform': 'DATE(payment_time)'
            },
            'totalPaymentPrice': {
                'db_field': 'pay_amount',
                'confidence': 0.9,
                'aggregation': 'SUM'
            }
        },
        'join_strategy': '...',
        'enum_inference': {...},
        'reasoning': '...'
    }
}
```

### Stage3AOutput 期望格式
```python
{
    'entity_mappings': [
        {
            'table_name': 'erp_bookkeeping_voucher',
            'entity_name': 'finance-statistics',
            'relation_type': 'association',
            'relation_score': 72,
            'field_mappings': [
                {
                    'db_column': 'payment_time',
                    'api_field': 'date',
                    'role': 'business',
                    'confidence': 0.8
                },
                {
                    'db_column': 'pay_amount',
                    'api_field': 'totalPaymentPrice',
                    'role': 'business',
                    'confidence': 0.9
                }
            ]
        }
    ],
    'golden_sqls': [...],
    'vanna_training_data': {...}
}
```

## 测试验证

修复后应该能够：
1. ✅ 正确遍历字典结构
2. ✅ 提取表名和映射结果
3. ✅ 转换字段映射格式
4. ✅ 生成 Golden SQL
5. ✅ 返回符合 Stage3AOutput 格式的数据

## 相关文件

- `adapters/entimap_adapter.py` - 主要修复文件
- `ddl_entimap/entimap_engine.py` - 数据源
- `common/schemas.py` - 数据模型定义
- `docs/MODULAR_ARCHITECTURE_PLAN.md` - 整体架构设计

## 下一步

1. 运行 pipeline 验证修复
2. 检查输出数据格式是否正确
3. 完善错误处理和日志
4. 添加单元测试
