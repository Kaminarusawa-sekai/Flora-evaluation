"""测试 EvalExecution 是否正确加载和工作"""
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
print(f"Initial logs count: {len(env.logs)}")

# 初始化能力
from capabilities import init_capabilities

config_path = "coop_eval_actual/configs/eval_config.json"
manager = init_capabilities(config_path, load_extensions=False)

print(f"\nCapabilities initialized from {config_path}")

# 获取 excution 能力
from capabilities.excution import BaseExecution

try:
    excution = manager.get_capability("excution", BaseExecution)
    print(f"\nGot excution capability: {type(excution).__name__}")
    print(f"Capability type: {excution.get_capability_type()}")
except Exception as e:
    print(f"\nFailed to get excution capability: {e}")
    sys.exit(1)

# 测试执行
print("\n" + "="*60)
print("Testing execution...")
print("="*60)

result = excution.execute(
    connector_name="dify",
    inputs={"test": "input"},
    params={
        "agent_id": "agent_1",
        "task_id": "test_task_1",
    }
)

print(f"\nExecution result:")
print(f"  Status: {result.get('status')}")
print(f"  Error type: {result.get('error_type')}")
print(f"  Error: {result.get('error')}")

print(f"\nMockToolEnvironment logs count: {len(env.logs)}")
if env.logs:
    print(f"Latest log:")
    log = env.logs[-1]
    print(f"  task_id: {log.task_id}")
    print(f"  agent_id: {log.agent_id}")
    print(f"  status: {log.status}")
    print(f"  error_type: {log.error_type}")
else:
    print("  No logs recorded!")

print("\n" + "="*60)
print("Test completed")
print("="*60)
