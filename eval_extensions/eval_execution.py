"""
Eval Execution - 评估专用的执行实现
使用 MockToolEnvironment 模拟工具执行，支持错误注入
"""
import sys
import os
from typing import Dict, Any, Optional

# 确保 tasks 目录在路径中
_TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
if _TASKS_ROOT not in sys.path:
    sys.path.insert(0, _TASKS_ROOT)

from capabilities.excution.base_excution import BaseExecution


class EvalExecution(BaseExecution):
    """
    评估专用执行器。
    使用 MockToolEnvironment 模拟执行，支持错误注入和结果追踪。
    """

    def __init__(self) -> None:
        self._env = None
        self._model_name = "COOP"

    def initialize(self, config: Dict[str, Any]) -> None:
        self._model_name = config.get("model_name", "COOP")
        self._env = self._resolve_env(config)

    def shutdown(self) -> None:
        return

    def get_capability_type(self) -> str:
        return "eval_execution"

    def execute(
        self,
        connector_name: str,
        inputs: Dict[str, Any] = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if inputs is None:
            inputs = {}
        if params is None:
            params = {}

        agent_id = params.get("agent_id") or inputs.get("agent_id")
        task_id = params.get("trace_id") or params.get("task_id") or "unknown"

        if not agent_id:
            return {
                "status": "NEED_INPUT",
                "missing": {"agent_id": "missing"},
                "completed": inputs,
            }

        if self._env is None:
            return {
                "status": "FAILED",
                "error": "EvalExecution environment not initialized",
            }

        result = self._env.execute_agent(self._model_name, str(task_id), agent_id, inputs)

        # 标准化返回格式
        status = result.get("status", "FAILED")
        if status == "ok":
            # MockToolEnvironment 返回 "ok"，转换为 "SUCCESS"
            return {
                "status": "SUCCESS",
                "result": result.get("output", result),
                "connector_name": connector_name,
            }
        else:
            # 失败情况
            return {
                "status": "FAILED",
                "error": result.get("error", "Execution failed"),
                "error_type": result.get("error_type", "unknown"),
            }

    def health_check(self, connector_name: str, params: Dict[str, Any]) -> bool:
        return True

    def authenticate(self, connector_name: str, params: Dict[str, Any]) -> bool:
        return True

    @staticmethod
    def _resolve_env(config: Dict[str, Any]):
        """解析并获取 Mock 环境"""
        try:
            from coop_eval_actual.mock_tools import get_global_env, MockToolEnvironment
            env = get_global_env()
            if env:
                return env
            agent_ids = config.get("agent_ids", [])
            seed = config.get("seed", 42)
            error_rate = config.get("error_injection_rate", 0.0)
            if agent_ids:
                return MockToolEnvironment(agent_ids, seed=seed, error_injection_rate=error_rate)
        except Exception:
            return None
        return None
