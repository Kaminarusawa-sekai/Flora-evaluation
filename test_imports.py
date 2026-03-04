"""简单测试：验证 EvalTaskPlanning 能否被正确加载"""
import os
import sys
import json

# 添加 tasks 到路径
TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "tasks"))
if TASKS_ROOT not in sys.path:
    sys.path.insert(0, TASKS_ROOT)

# 读取配置文件
config_path = "coop_eval_actual/configs/eval_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

print("Configuration loaded:")
print(f"  task_planning.active_impl: {config['capabilities']['task_planning']['active_impl']}")
print(f"  excution.active_impl: {config['capabilities']['excution']['active_impl']}")

# 测试能否导入 EvalTaskPlanning
try:
    from capabilities.task_planning.eval_task_planner import EvalTaskPlanning
    print("\n[OK] EvalTaskPlanning imported successfully")
    print(f"  Class: {EvalTaskPlanning}")
except Exception as e:
    print(f"\n[FAIL] Failed to import EvalTaskPlanning: {e}")
    import traceback
    traceback.print_exc()

# 测试能否导入 EvalExecution
try:
    from capabilities.excution.eval_execution import EvalExecution
    print("\n[OK] EvalExecution imported successfully")
    print(f"  Class: {EvalExecution}")
except Exception as e:
    print(f"\n[FAIL] Failed to import EvalExecution: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Import test completed")
print("="*60)
