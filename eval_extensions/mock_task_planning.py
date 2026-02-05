"""
Mock Task Planning - 评估专用的任务规划实现
通过解析任务描述中的 [agent:xxx] 标签来确定执行计划
"""
import logging
import re
import sys
import os
from typing import Any, Dict, List, Optional

# 确保 tasks 目录在路径中
_TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
if _TASKS_ROOT not in sys.path:
    sys.path.insert(0, _TASKS_ROOT)

from capabilities.task_planning.interface import ITaskPlanningCapability


AGENT_TAG_PATTERN = re.compile(r"\[agent:([a-zA-Z0-9_\-]+)\]")


class MockTaskPlanning(ITaskPlanningCapability):
    """
    Mock 任务规划器，用于评估场景。
    从任务描述中提取 [agent:xxx] 标签作为执行计划。
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._tree_manager = None

    def get_capability_type(self) -> str:
        return "mock_task_planning"

    def initialize(self, config: Dict[str, Any]) -> bool:
        # 延迟导入，避免循环依赖
        try:
            from agents.tree.tree_manager import treeManager
            self._tree_manager = treeManager
        except ImportError:
            self.logger.warning("Could not import treeManager, agent lookup will be limited")
        return True

    def shutdown(self) -> None:
        return

    def generate_execution_plan(
        self,
        agent_id: str,
        user_input: str,
        memory_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        tags = AGENT_TAG_PATTERN.findall(user_input or "")
        # 处理重复标签（有时标签会重复出现）
        if tags and len(tags) % 2 == 0:
            half = len(tags) // 2
            if tags[:half] == tags[half:]:
                tags = tags[:half]

        available_agents = self._get_all_agents()
        name_map = {item.get("agent_id"): item.get("name", "") for item in available_agents}

        planned_agents = []
        if tags:
            planned_agents = tags
        else:
            # 回退：从文本中匹配 agent_id 或 name
            for agent in available_agents:
                candidate_id = agent.get("agent_id")
                candidate_name = agent.get("name", "")
                if candidate_id and candidate_id in user_input:
                    planned_agents.append(candidate_id)
                elif candidate_name and candidate_name in user_input:
                    planned_agents.append(candidate_id)

        if not planned_agents:
            planned_agents = [agent_id]

        plans = []
        for idx, executor in enumerate(planned_agents, start=1):
            executor_name = name_map.get(executor, executor)
            plans.append({
                "step": idx,
                "type": "AGENT",
                "executor": executor,
                "content": f"执行代理 {executor_name} 的任务。",
                "description": f"调用 {executor_name}",
                "params": {"executor": executor},
            })
        return plans

    def plan_subtasks(self, parent_agent_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    def _get_all_agents(self) -> List[Dict[str, Any]]:
        if self._tree_manager is None:
            return []
        try:
            return self._tree_manager.node_service.get_all_nodes()
        except Exception:
            return []
