# 修复总结 - TypeError: sequence item 0: expected str instance, dict found

## 问题描述

在 `auto_agents_build/artifact_generation/prompt_factory.py` 中运行时报错：

```python
TypeError: sequence item 0: expected str instance, dict found
```

错误发生在：
```python
"constraints": ", ".join(unit.get('constraints', []))
```

## 根本原因

`constraints` 字段是一个**字典列表**，而不是字符串列表：

```python
constraints = [
    {
        'api_id': 'api_008',
        'api_name': '更新库存',
        'constraint_type': 'data_isolation',
        'constraint_rule': '只能操作本人/本部门数据',
        'description': '自动添加 owner_id 或 department_id 过滤条件'
    },
    {
        'api_id': 'api_008',
        'api_name': '更新库存',
        'constraint_type': '审批流程',
        'constraint_rule': '单次库存变更量 ≥ 100 件...',
        'description': '防止大额/异常库存操作...'
    },
    # ... 更多约束
]
```

`", ".join()` 只能连接字符串列表，不能连接字典列表。

## 修复方案

在 `prompt_factory.py` 第 214-221 行，修改约束处理逻辑：

### 修复前

```python
if unit:
    tool = {
        "name": unit['name'],
        "description": unit.get('semantic_description', ''),
        "usage": self._generate_tool_usage(unit),
        "constraints": ", ".join(unit.get('constraints', []))  # 错误：无法连接字典
    }
    tools.append(tool)
```

### 修复后

```python
if unit:
    # 处理 constraints - 可能是字典列表
    constraints = unit.get('constraints', [])
    if constraints and isinstance(constraints, list):
        if isinstance(constraints[0], dict):
            # 如果是字典列表，提取 constraint_rule 或 description
            constraint_strs = [
                c.get('constraint_rule') or c.get('description') or str(c)
                for c in constraints
            ]
            constraints_text = "; ".join(constraint_strs)
        else:
            # 如果是字符串列表
            constraints_text = ", ".join(constraints)
    else:
        constraints_text = ""

    tool = {
        "name": unit['name'],
        "description": unit.get('semantic_description', ''),
        "usage": self._generate_tool_usage(unit),
        "constraints": constraints_text
    }
    tools.append(tool)
```

## 修复逻辑

1. **检查类型**：判断 `constraints` 是否为列表
2. **判断元素类型**：
   - 如果第一个元素是字典 → 提取 `constraint_rule` 或 `description` 字段
   - 如果第一个元素是字符串 → 直接连接
3. **使用分号分隔**：字典约束使用 `"; "` 分隔（更清晰）
4. **容错处理**：如果字段不存在，使用 `str(c)` 作为后备

## 测试验证

创建了 `test_constraint_handling.py` 进行测试：

```python
# 测试 1: 原代码（应该失败）
try:
    result = ", ".join(constraints)  # 字典列表
except TypeError as e:
    print(f"[OK] Expected error: {e}")

# 测试 2: 修复后的代码
if constraints and isinstance(constraints, list):
    if isinstance(constraints[0], dict):
        constraint_strs = [
            c.get('constraint_rule') or c.get('description') or str(c)
            for c in constraints
        ]
        constraints_text = "; ".join(constraint_strs)
    else:
        constraints_text = ", ".join(constraints)
else:
    constraints_text = ""

print(f"[OK] Successfully processed {len(constraints)} constraints")

# 测试 3: 边界情况
# - 空列表 → ""
# - None 值 → ""
# - 字符串列表 → "str1, str2, str3"
```

**测试结果**：所有测试通过 ✓

## 输出示例

修复后，约束文本格式：

```
只能操作本人/本部门数据; 单次库存变更量 ≥ 100 件或变更后库存为负值时，须经仓库主管二级审批；变更量 ≥ 500 件或涉及高价值商品（单价 ≥ 5000 元）时，须经仓储经理三级审批; 单次更新库存数量绝对值不得超过当前库存的 200%，且不得使库存数量低于 -10（预留最小负向容错阈值，仅限系统校验用，实际业务中禁止负库存）; 仓库专员仅可更新其所属仓库编码（warehouse_id）及所辖子仓范围内的商品库存，不可跨仓库、跨租户操作；API 请求必须携带有效的 warehouse_id 且与用户角色绑定的仓库权限匹配; 完整记录操作人ID、角色、仓库ID、商品SKU、原库存、新库存、变更量、审批链路（含各审批人及时间）、操作时间、客户端IP及请求TraceID，日志保留不少于180天并同步至安全审计平台
```

## 优势

1. **类型安全**：正确处理字典列表和字符串列表
2. **容错性强**：处理空列表、None 值等边界情况
3. **可读性好**：使用分号分隔多个约束规则
4. **向后兼容**：仍然支持原有的字符串列表格式

## 相关文件

- `auto_agents_build/artifact_generation/prompt_factory.py` - 修复的主文件
- `test_constraint_handling.py` - 测试脚本

## 后续建议

1. **统一数据格式**：在数据源层面统一约束的数据结构
2. **添加类型注解**：使用 TypedDict 定义约束的结构
3. **文档化**：在代码中添加注释说明约束的预期格式
4. **单元测试**：为 `_generate_tool_usage` 方法添加单元测试

## 总结

成功修复了约束处理的类型错误，使系统能够正确处理字典列表格式的约束数据。修复后的代码更加健壮，支持多种数据格式，并提供了清晰的约束文本输出。
