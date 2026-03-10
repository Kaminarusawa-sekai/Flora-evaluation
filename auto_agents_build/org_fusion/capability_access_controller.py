"""
能力访问控制器 - 管理能力的访问权限和并发控制
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional,List
from enum import Enum
from threading import Lock
from shared.logger import get_logger
from .capability_unit_registry import CapabilityUnitRegistry

logger = get_logger(__name__)


class AccessMode(Enum):
    """访问模式"""
    EXECUTE = "execute"      # 可执行（读写）
    READ_ONLY = "read_only"  # 只读
    DELEGATE = "delegate"    # 委托执行
    MONITOR = "monitor"      # 仅监控


class CapabilityAccessController:
    """能力访问控制器"""

    def __init__(self, registry: CapabilityUnitRegistry):
        self.registry = registry
        self.locks = {}  # capability_id -> Lock
        self.access_matrix = {}  # (agent_id, capability_id) -> AccessMode
        self.active_locks = {}  # capability_id -> agent_id

    def grant_access(
        self,
        agent_id: str,
        capability_id: str,
        access_mode: AccessMode
    ):
        """
        授予访问权限

        Args:
            agent_id: Agent ID
            capability_id: 能力单元 ID
            access_mode: 访问模式
        """
        key = (agent_id, capability_id)
        self.access_matrix[key] = access_mode
        logger.info(f"Granted {access_mode.value} access to {agent_id} for {capability_id}")

    def revoke_access(self, agent_id: str, capability_id: str):
        """撤销访问权限"""
        key = (agent_id, capability_id)
        if key in self.access_matrix:
            del self.access_matrix[key]
            logger.info(f"Revoked access for {agent_id} on {capability_id}")

    def check_permission(
        self,
        agent_id: str,
        capability_id: str,
        required_mode: AccessMode
    ) -> bool:
        """
        检查权限

        Args:
            agent_id: Agent ID
            capability_id: 能力单元 ID
            required_mode: 需要的访问模式

        Returns:
            是否有权限
        """
        key = (agent_id, capability_id)
        granted_mode = self.access_matrix.get(key)

        if not granted_mode:
            return False

        # 权限层级：EXECUTE > DELEGATE > READ_ONLY > MONITOR
        mode_hierarchy = {
            AccessMode.EXECUTE: 4,
            AccessMode.DELEGATE: 3,
            AccessMode.READ_ONLY: 2,
            AccessMode.MONITOR: 1
        }

        return mode_hierarchy.get(granted_mode, 0) >= mode_hierarchy.get(required_mode, 0)

    def acquire_capability(
        self,
        agent_id: str,
        capability_id: str,
        mode: AccessMode
    ) -> Optional['CapabilityHandle']:
        """
        获取能力的访问权限

        Args:
            agent_id: Agent ID
            capability_id: 能力单元 ID
            mode: 访问模式

        Returns:
            能力句柄，如果获取失败返回 None
        """
        # 检查权限
        if not self.check_permission(agent_id, capability_id, mode):
            logger.warning(f"Permission denied: {agent_id} on {capability_id}")
            return None

        # 获取能力单元
        unit = self.registry.get_unit(capability_id)
        if not unit:
            logger.error(f"Capability not found: {capability_id}")
            return None

        # 并发控制
        if mode == AccessMode.EXECUTE:
            if not self._acquire_lock(capability_id, agent_id):
                logger.warning(f"Capability locked: {capability_id}")
                return None

        return CapabilityHandle(unit, mode, agent_id, self)

    def release_capability(self, capability_id: str, agent_id: str):
        """释放能力"""
        self._release_lock(capability_id, agent_id)

    def _acquire_lock(self, capability_id: str, agent_id: str) -> bool:
        """获取锁"""
        if capability_id not in self.locks:
            self.locks[capability_id] = Lock()

        lock = self.locks[capability_id]

        if lock.acquire(blocking=False):
            self.active_locks[capability_id] = agent_id
            logger.debug(f"Lock acquired: {capability_id} by {agent_id}")
            return True

        return False

    def _release_lock(self, capability_id: str, agent_id: str):
        """释放锁"""
        if capability_id in self.locks:
            lock = self.locks[capability_id]
            if self.active_locks.get(capability_id) == agent_id:
                lock.release()
                del self.active_locks[capability_id]
                logger.debug(f"Lock released: {capability_id} by {agent_id}")

    def build_access_control_matrix(
        self,
        agents: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, str]]:
        """
        构建访问控制矩阵

        Args:
            agents: Agent 列表

        Returns:
            {agent_id: {capability_id: access_mode}}
        """
        logger.info("Building access control matrix")

        matrix = {}

        for agent in agents:
            agent_id = agent['agent_id']
            matrix[agent_id] = {}

            interface = agent.get('capability_interface', {})

            # 直接能力
            for cap_ref in interface.get('direct_capabilities', []):
                cap_id = cap_ref['unit_id']
                access_mode = cap_ref.get('access_mode', 'execute')
                matrix[agent_id][cap_id] = access_mode
                self.grant_access(agent_id, cap_id, AccessMode(access_mode))

            # 组合能力
            for cap_ref in interface.get('composed_capabilities', []):
                cap_id = cap_ref['unit_id']
                access_mode = cap_ref.get('access_mode', 'execute')
                matrix[agent_id][cap_id] = access_mode
                self.grant_access(agent_id, cap_id, AccessMode(access_mode))

            # 委托能力
            for cap_ref in interface.get('delegated_capabilities', []):
                cap_id = cap_ref['unit_id']
                access_mode = cap_ref.get('access_mode', 'delegate')
                matrix[agent_id][cap_id] = access_mode
                self.grant_access(agent_id, cap_id, AccessMode(access_mode))

        logger.info(f"Access control matrix built for {len(matrix)} agents")
        return matrix


class CapabilityHandle:
    """能力句柄"""

    def __init__(
        self,
        unit: Dict[str, Any],
        mode: AccessMode,
        agent_id: str,
        controller: CapabilityAccessController
    ):
        self.unit = unit
        self.mode = mode
        self.agent_id = agent_id
        self.controller = controller

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode == AccessMode.EXECUTE:
            self.controller.release_capability(self.unit['unit_id'], self.agent_id)

    def get_unit(self) -> Dict[str, Any]:
        """获取能力单元"""
        return self.unit

    def can_execute(self) -> bool:
        """是否可以执行"""
        return self.mode in [AccessMode.EXECUTE, AccessMode.DELEGATE]
