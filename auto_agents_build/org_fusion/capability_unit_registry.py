"""
能力单元注册中心 - 管理所有能力单元
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from shared.logger import get_logger

logger = get_logger(__name__)


class CapabilityUnitRegistry:
    """能力单元注册中心"""

    def __init__(self):
        self.units = {}  # unit_id -> unit_data
        self.next_id = 1

    def register_atomic_capability(
        self,
        name: str,
        underlying_apis: List[str],
        required_params: List[str] = None,
        constraints: List[str] = None,
        owner: str = None
    ) -> str:
        """
        注册原子能力单元

        Args:
            name: 能力名称
            underlying_apis: 底层 API 列表
            required_params: 必需参数
            constraints: 约束条件
            owner: 所有者（角色名）

        Returns:
            能力单元 ID
        """
        unit_id = f"cap_atomic_{self.next_id}"
        self.next_id += 1

        unit = {
            "unit_id": unit_id,
            "level": "atomic",
            "name": name,
            "underlying_apis": underlying_apis,
            "required_params": required_params or [],
            "constraints": constraints or [],
            "owner": owner,
            "ref_count": 0,
            "referenced_by": []
        }

        self.units[unit_id] = unit
        logger.info(f"Registered atomic capability: {name} ({unit_id})")

        return unit_id

    def register_composed_capability(
        self,
        name: str,
        composed_of: List[str],
        semantic_description: str,
        orchestration_logic: str = None,
        owner: str = None
    ) -> str:
        """
        注册组合能力单元

        Args:
            name: 能力名称
            composed_of: 组成的能力单元 ID 列表
            semantic_description: 语义描述
            orchestration_logic: 编排逻辑
            owner: 所有者

        Returns:
            能力单元 ID
        """
        unit_id = f"cap_composed_{self.next_id}"
        self.next_id += 1

        unit = {
            "unit_id": unit_id,
            "level": "composed",
            "name": name,
            "composed_of": composed_of,
            "semantic_description": semantic_description,
            "orchestration_logic": orchestration_logic,
            "owner": owner,
            "ref_count": 0,
            "referenced_by": []
        }

        self.units[unit_id] = unit
        logger.info(f"Registered composed capability: {name} ({unit_id})")

        return unit_id

    def register_strategic_capability(
        self,
        name: str,
        composed_of: List[str],
        semantic_description: str,
        cross_domain: bool = True,
        owner: str = None
    ) -> str:
        """
        注册战略能力单元

        Args:
            name: 能力名称
            composed_of: 组成的能力单元 ID 列表
            semantic_description: 语义描述
            cross_domain: 是否跨域
            owner: 所有者

        Returns:
            能力单元 ID
        """
        unit_id = f"cap_strategic_{self.next_id}"
        self.next_id += 1

        unit = {
            "unit_id": unit_id,
            "level": "strategic",
            "name": name,
            "composed_of": composed_of,
            "semantic_description": semantic_description,
            "cross_domain": cross_domain,
            "owner": owner,
            "ref_count": 0,
            "referenced_by": []
        }

        self.units[unit_id] = unit
        logger.info(f"Registered strategic capability: {name} ({unit_id})")

        return unit_id

    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """获取能力单元"""
        return self.units.get(unit_id)

    def add_reference(self, unit_id: str, agent_name: str):
        """添加引用"""
        unit = self.units.get(unit_id)
        if unit:
            unit['ref_count'] += 1
            if agent_name not in unit['referenced_by']:
                unit['referenced_by'].append(agent_name)

    def remove_reference(self, unit_id: str, agent_name: str):
        """移除引用"""
        unit = self.units.get(unit_id)
        if unit:
            unit['ref_count'] = max(0, unit['ref_count'] - 1)
            if agent_name in unit['referenced_by']:
                unit['referenced_by'].remove(agent_name)

    def get_units_by_level(self, level: str) -> List[Dict[str, Any]]:
        """按层级获取能力单元"""
        return [unit for unit in self.units.values() if unit['level'] == level]

    def get_shared_capabilities(self, min_ref_count: int = 2) -> List[Dict[str, Any]]:
        """获取被多个 Agent 共享的能力"""
        return [unit for unit in self.units.values() if unit['ref_count'] >= min_ref_count]

    def get_all_units(self) -> Dict[str, Dict[str, Any]]:
        """获取所有能力单元"""
        return self.units.copy()

    def export_registry(self) -> Dict[str, Any]:
        """导出注册表"""
        return {
            "atomic_capabilities": self.get_units_by_level("atomic"),
            "composed_capabilities": self.get_units_by_level("composed"),
            "strategic_capabilities": self.get_units_by_level("strategic"),
            "total_count": len(self.units),
            "shared_capabilities": self.get_shared_capabilities()
        }
