"""测试 EvalTaskPlanning 是否正确加载和工作"""
import os
import sys

# 添加 tasks 到路径
TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "tasks"))
if TASKS_ROOT not in sys.path:
    sys.path.insert(0, TASKS_ROOT)

# 设置评估模式
os.environ["COOP_EVAL_EXECUTION"] = "1"

# 初始化 MockToolEnvironment
from coop_eval_actual.mock_tools import MockToolEnvironment, set_global_env

agent_ids = ["agent_1", "agent_2", "agent_3"]
env = MockToolEnvironment(agent_ids, seed=42, error_injection_rate=0.1)
set_global_env(env)

print(f"MockToolEnvironment initialized with {len(agent_ids)} agents")

# 加载 agent tree
from coop_eval_actual.agent_tree_loader import load_agents_into_tree

# 直接导入 tree_manager 模块，避免导入 agent_actor
import sys
tree_manager_path = os.path.join(TASKS_ROOT, "agents", "tree")
if tree_manager_path not in sys.path:
    sys.path.insert(0, tree_manager_path)

from tree_manager import treeManager

records_path = "records (2).json"
nodes = load_agents_into_tree(records_path, treeManager)
print(f"Loaded {len(nodes)} agents into tree")

# 初始化能力
from capabilities import init_capabilities

config_path = "coop_eval_actual/configs/eval_config.json"
manager = init_capabilities(config_path, load_extensions=False)

print(f"\nCapabilities initialized from {config_path}")

# 获取 task_planning 能力
from capabilities.task_planning.interface import ITaskPlanningCapability

try:
    task_planner = manager.get_capability("task_planning", ITaskPlanningCapability)
    print(f"\nGot task_planning capability: {type(task_planner).__name__}")
    print(f"Capability type: {task_planner.get_capability_type()}")
except Exception as e:
    print(f"\nFailed to get task_planning capability: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试生成执行计划
print("\n" + "="*60)
print("Testing task planning...")
print("="*60)

# 找一个有子节点的 agent
root_agents = [node for node in nodes if not node.get("parent_id")]
if root_agents:
    test_agent_id = root_agents[0]["agent_id"]
    print(f"\nTesting with agent: {test_agent_id}")

    plans = task_planner.generate_execution_plan(
        agent_id=test_agent_id,
        task_description="Test task description",
        memory_context=None
    )

    print(f"\nGenerated {len(plans)} execution steps:")
    for i, plan in enumerate(plans):
        print(f"  Step {i+1}:")
        print(f"    Executor: {plan.get('executor')}")
        print(f"    Type: {plan.get('type')}")
        print(f"    Is parallel: {plan.get('is_parallel')}")
        print(f"    Is leaf: {plan.get('is_leaf')}")
else:
    print("\nNo root agents found in tree")

print("\n" + "="*60)
print("Test completed")
print("="*60)
