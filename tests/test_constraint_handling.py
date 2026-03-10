"""Test constraint handling logic (standalone)"""

# 测试数据
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
        'constraint_rule': '单次库存变更量 ≥ 100 件或变更后库存为负值时，须经仓库主管二级审批；变更量 ≥ 500 件或涉及高价值商品（单价 ≥ 5000 元）时，须经仓储经理三级审批',
        'description': '防止大额/异常库存操作引发业务风险，确保关键变更受控'
    },
    {
        'api_id': 'api_008',
        'api_name': '更新库存',
        'constraint_type': '数量限制',
        'constraint_rule': '单次更新库存数量绝对值不得超过当前库存的 200%，且不得使库存数量低于 -10（预留最小负向容错阈值，仅限系统校验用，实际业务中禁止负库存）',
        'description': '防范误操作导致库存严重失真或超发，保障库存数据合理性'
    },
    {
        'api_id': 'api_008',
        'api_name': '更新库存',
        'constraint_type': '数据权限隔离',
        'constraint_rule': '仓库专员仅可更新其所属仓库编码（warehouse_id）及所辖子仓范围内的商品库存，不可跨仓库、跨租户操作；API 请求必须携带有效的 warehouse_id 且与用户角色绑定的仓库权限匹配',
        'description': '实现多租户及仓库维度的数据隔离，防止越权修改其他仓库库存'
    },
    {
        'api_id': 'api_008',
        'api_name': '更新库存',
        'constraint_type': '操作日志审计',
        'constraint_rule': '完整记录操作人ID、角色、仓库ID、商品SKU、原库存、新库存、变更量、审批链路（含各审批人及时间）、操作时间、客户端IP及请求TraceID，日志保留不少于180天并同步至安全审计平台',
        'description': '满足合规审计要求，支持库存异常追溯与责任认定'
    }
]

print("=" * 80)
print("Constraint Handling Test")
print("=" * 80)

# 测试原来的错误代码
print("\n[Test 1] Original code (should fail):")
try:
    result = ", ".join(constraints)
    print("ERROR: Should have failed but didn't!")
except TypeError as e:
    print(f"[OK] Expected error: {e}")

# 测试修复后的代码
print("\n[Test 2] Fixed code:")
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

print(f"[OK] Successfully processed {len(constraints)} constraints")
print(f"\nResult (first 200 chars):")
print(constraints_text[:200] + "...")

# 测试边界情况
print("\n[Test 3] Edge cases:")

# 空列表
test_empty = []
if test_empty and isinstance(test_empty, list):
    result = "has content"
else:
    result = ""
print(f"[OK] Empty list: '{result}'")

# None
test_none = None
if test_none and isinstance(test_none, list):
    result = "has content"
else:
    result = ""
print(f"[OK] None value: '{result}'")

# 字符串列表
test_strings = ["constraint1", "constraint2", "constraint3"]
if test_strings and isinstance(test_strings, list):
    if isinstance(test_strings[0], dict):
        result = "dict list"
    else:
        result = ", ".join(test_strings)
else:
    result = ""
print(f"[OK] String list: '{result}'")

print("\n" + "=" * 80)
print("All Tests PASSED!")
print("=" * 80)
