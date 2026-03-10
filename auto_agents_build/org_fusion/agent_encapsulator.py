"""
Agent 标准封装器 - 为每个 Agent 生成能力引用清单
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from .capability_unit_registry import CapabilityUnitRegistry

logger = get_logger(__name__)


class AgentEncapsulator:
    """Agent 标准封装器"""

    def __init__(self, registry: CapabilityUnitRegistry):
        self.registry = registry

    def encapsulate_agent(
        self,
        role: Dict[str, Any],
        capability_units: List[str]
    ) -> Dict[str, Any]:
        """
        封装 Agent

        Args:
            role: 角色信息（来自 Layer 2）
            capability_units: 能力单元 ID 列表

        Returns:
            Agent 定义
        """
        agent_id = role['role_id'].replace('role_', 'agent_')
        agent_name = role['role_name']
        level = role.get('level', 'specialist')

        logger.info(f"Encapsulating agent: {agent_name}")

        # 构建能力接口
        capability_interface = self._build_capability_interface(
            agent_name,
            capability_units,
            level
        )

        agent = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "level": level,
            "is_virtual": role.get('is_virtual', False),
            "responsibilities": role.get('responsibilities', []),
            "capability_interface": capability_interface,
            "subordinates": [],  # 将在拓扑构建时填充
            "local_memory": {
                "type": "short_term",
                "capacity": "1000_messages"
            },
            "metadata": {
                "source_role_id": role['role_id'],
                "api_count": len(role.get('assigned_apis', [])),
                "constraint_count": len(role.get('constraints', []))
            }
        }

        # 更新注册表的引用计数
        for unit_id in capability_units:
            self.registry.add_reference(unit_id, agent_name)

        logger.info(f"  Agent {agent_name} encapsulated with {len(capability_units)} capabilities")

        return agent

    def _build_capability_interface(
        self,
        agent_name: str,
        capability_units: List[str],
        level: str
    ) -> Dict[str, Any]:
        """
        构建能力接口

        Args:
            agent_name: Agent 名称
            capability_units: 能力单元 ID 列表
            level: Agent 层级

        Returns:
            能力接口定义
        """
        interface = {
            "direct_capabilities": [],
            "delegated_capabilities": [],
            "composed_capabilities": []
        }

        for unit_id in capability_units:
            unit = self.registry.get_unit(unit_id)
            if not unit:
                continue

            # 根据能力层级和 Agent 层级决定访问模式
            access_mode = self._determine_access_mode(unit, level)

            capability_ref = {
                "unit_id": unit_id,
                "name": unit['name'],
                "access_mode": access_mode,
                "priority": "high" if unit['level'] == 'atomic' else "medium"
            }

            # 分类能力
            if unit['level'] == 'atomic':
                interface['direct_capabilities'].append(capability_ref)
            elif unit['level'] == 'composed':
                interface['composed_capabilities'].append(capability_ref)
            elif unit['level'] == 'strategic':
                interface['delegated_capabilities'].append(capability_ref)

        return interface

    def _determine_access_mode(self, unit: Dict[str, Any], agent_level: str) -> str:
        """
        确定访问模式

        Args:
            unit: 能力单元
            agent_level: Agent 层级

        Returns:
            访问模式: execute/delegate/monitor
        """
        unit_level = unit['level']

        # 基层专员直接执行原子能力
        if agent_level == 'specialist' and unit_level == 'atomic':
            return "execute"

        # 主管可以执行组合能力
        if agent_level == 'supervisor' and unit_level in ['atomic', 'composed']:
            return "execute"

        # 经理可以委托执行
        if agent_level == 'manager':
            return "delegate"

        # 默认为监控模式
        return "monitor"

    def batch_encapsulate(
        self,
        roles: List[Dict[str, Any]],
        role_to_capabilities: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        批量封装 Agent

        Args:
            roles: 角色列表
            role_to_capabilities: 角色到能力单元的映射

        Returns:
            Agent 列表
        """
        agents = []

        for role in roles:
            role_id = role['role_id']
            capability_units = role_to_capabilities.get(role_id, [])

            agent = self.encapsulate_agent(role, capability_units)
            agents.append(agent)

        logger.info(f"Batch encapsulated {len(agents)} agents")
        return agents
