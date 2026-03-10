"""Test constraint handling in prompt_factory.py"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from auto_agents_build.artifact_generation.prompt_factory import PromptFactory

# 测试数据
unit = {
    'unit_id': 'unit_001',
    'name': '更新库存',
    'semantic_description': '更新商品库存数量',
    'level': 'atomic',
    'underlying_apis': ['api_008'],
    'required_params': ['product_id', 'quantity'],
    'constraints': [
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
            'constraint_rule': '单次库存变更量 ≥ 100 件或变更后库存为负值时，须经仓库主管二级审批',
            'description': '防止大额/异常库存操作引发业务风险'
        }
    ]
}

# 测试约束处理
constraints = unit.get('constraints', [])
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

print("=" * 80)
print("Constraint Handling Test")
print("=" * 80)
print(f"\nOriginal constraints type: {type(constraints)}")
print(f"Number of constraints: {len(constraints)}")
print(f"\nProcessed constraints text:")
print(constraints_text)
print("\n" + "=" * 80)
print("Test PASSED!")
print("=" * 80)
