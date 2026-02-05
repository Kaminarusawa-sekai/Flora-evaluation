import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolCallLog:
    task_id: str
    model: str
    agent_id: str
    status: str
    error_type: Optional[str]
    timestamp_ms: int


_GLOBAL_ENV: Optional["MockToolEnvironment"] = None


def set_global_env(env: "MockToolEnvironment") -> None:
    global _GLOBAL_ENV
    _GLOBAL_ENV = env


def get_global_env() -> Optional["MockToolEnvironment"]:
    return _GLOBAL_ENV


class MockToolEnvironment:
    def __init__(self, agent_ids: List[str], seed: int = 42, error_injection_rate: float = 0.2) -> None:
        self.agent_ids = set(agent_ids)
        self.error_injection_rate = error_injection_rate
        self.rng = random.Random(seed)
        self.logs: List[ToolCallLog] = []

    def execute_agent(self, model: str, task_id: str, agent_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        now_ms = int(time.time() * 1000)
        if agent_id not in self.agent_ids:
            self.logs.append(ToolCallLog(task_id, model, agent_id, "error", "invalid_tool", now_ms))
            return {
                "status": "FAILED",
                "error_type": "invalid_tool",
                "error": f"Unknown agent_id: {agent_id}",
            }

        if self.rng.random() < self.error_injection_rate:
            self.logs.append(ToolCallLog(task_id, model, agent_id, "error", "500", now_ms))
            return {
                "status": "FAILED",
                "error_type": "500",
                "error": "500 Internal Error",
            }

        result = {
            "agent_id": agent_id,
            "inputs": inputs,
            "status": "ok",
        }
        self.logs.append(ToolCallLog(task_id, model, agent_id, "ok", None, now_ms))
        return {
            "status": "SUCCESS",
            "result": result,
        }

    def clear_logs(self) -> None:
        self.logs = []
