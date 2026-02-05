import math
import re
import threading
from typing import List, Dict, Any


AGENT_TAG_PATTERN = re.compile(r"\[agent:([a-zA-Z0-9_\-]+)\]")


def extract_agent_tags(text: str) -> List[str]:
    if not text:
        return []
    return AGENT_TAG_PATTERN.findall(text)


def estimate_tokens_for_text(text: str) -> int:
    if not text:
        return 0
    return int(math.ceil(len(text) / 4))


class TokenTracker:
    """
    全局 Token 统计器，用于累计 COOP 多层 LLM 调用的 token 消耗。
    线程安全，支持按 task_id 分别统计。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = {}
                    cls._instance._data_lock = threading.Lock()
        return cls._instance

    def reset(self, task_id: str = None):
        """重置统计数据"""
        with self._data_lock:
            if task_id:
                self._data[task_id] = {
                    "tokens_prompt": 0,
                    "tokens_completion": 0,
                    "llm_calls": 0,
                    "layers": []
                }
            else:
                self._data.clear()

    def record_llm_call(self, task_id: str, prompt: str, completion: str, layer: int = 0, agent_id: str = ""):
        """记录一次 LLM 调用"""
        prompt_tokens = estimate_tokens_for_text(prompt)
        completion_tokens = estimate_tokens_for_text(completion)

        with self._data_lock:
            if task_id not in self._data:
                self._data[task_id] = {
                    "tokens_prompt": 0,
                    "tokens_completion": 0,
                    "llm_calls": 0,
                    "layers": []
                }

            self._data[task_id]["tokens_prompt"] += prompt_tokens
            self._data[task_id]["tokens_completion"] += completion_tokens
            self._data[task_id]["llm_calls"] += 1
            self._data[task_id]["layers"].append({
                "layer": layer,
                "agent_id": agent_id,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            })

    def get_stats(self, task_id: str) -> Dict[str, Any]:
        """获取指定任务的统计数据"""
        with self._data_lock:
            if task_id not in self._data:
                return {
                    "tokens_prompt": 0,
                    "tokens_completion": 0,
                    "tokens_total": 0,
                    "llm_calls": 0,
                    "layers": []
                }
            data = self._data[task_id].copy()
            data["tokens_total"] = data["tokens_prompt"] + data["tokens_completion"]
            return data


# 全局单例
token_tracker = TokenTracker()


def calculate_cross_system_level(expected_agents: List[str]) -> int:
    """
    根据跨业务系统数量计算任务复杂度等级。

    Level 定义：
    - Level 1: 单系统内操作
    - Level 2: 跨 2 个系统
    - Level 3: 跨 3 个系统
    - Level 4: 跨 4+ 个系统

    系统识别：从 agent_id 中提取第一段（如 erp_product_system, erp_sales_system）
    """
    if not expected_agents:
        return 1

    systems = set()
    for agent_id in expected_agents:
        # agent_id 格式: erp_product_system__sku_master_data_specialist__...
        parts = agent_id.split("__")
        if parts:
            systems.add(parts[0])

    num_systems = len(systems)
    if num_systems <= 1:
        return 1
    elif num_systems == 2:
        return 2
    elif num_systems == 3:
        return 3
    else:
        return 4
