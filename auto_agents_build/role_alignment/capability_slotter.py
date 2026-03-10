"""
能力填装器 - 将 API 能力填入角色槽位
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger

logger = get_logger(__name__)


class CapabilitySlotter:
    """能力填装器"""

    def slot_capabilities(
        self,
        roles: List[Dict[str, Any]],
        alignment_result: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        将对齐的 API 填入角色槽位

        Args:
            roles: 角色模板列表
            alignment_result: 对齐结果 {role_name: [api1, api2, ...]}

        Returns:
            {
                "filled_roles": [...],
                "orphan_apis": [...]
            }
        """
        logger.info("Slotting capabilities into roles")

        filled_roles = []
        assigned_api_ids = set()

        for role in roles:
            role_name = role['role_name']
            assigned_apis = alignment_result.get(role_name, [])

            # 分类 API：必需 vs 可选
            required_apis, optional_apis = self._classify_apis(role, assigned_apis)

            # 填充角色
            filled_role = {
                "role_id": self._generate_role_id(role_name),
                "role_name": role_name,
                "level": role.get('level', 'specialist'),
                "responsibilities": role.get('responsibilities', []),
                "assigned_apis": [
                    {
                        "api_id": api.get('id', api.get('name')),
                        "api_name": api.get('name'),
                        "business_name": api.get('description', api.get('name')),
                        "priority": "required" if api in required_apis else "optional",
                        "method": api.get('method', 'GET'),
                        "path": api.get('path', ''),
                        "description": api.get('description', '')
                    }
                    for api in assigned_apis
                ],
                "required_capabilities": role.get('required_capabilities', []),
                "optional_capabilities": role.get('optional_capabilities', [])
            }

            filled_roles.append(filled_role)

            # 记录已分配的 API
            for api in assigned_apis:
                assigned_api_ids.add(api.get('id', api.get('name')))

            logger.info(f"  {role_name}: {len(assigned_apis)} APIs assigned")

        # 识别孤儿 API（未分配的）
        all_apis = set()
        for apis in alignment_result.values():
            for api in apis:
                all_apis.add(api.get('id', api.get('name')))

        # 注意：这里需要从原始 API 列表中找孤儿，暂时返回空
        orphan_apis = []

        result = {
            "filled_roles": filled_roles,
            "orphan_apis": orphan_apis
        }

        logger.info(f"Slotting completed: {len(filled_roles)} roles filled")
        return result

    def _classify_apis(
        self,
        role: Dict[str, Any],
        assigned_apis: List[Dict[str, Any]]
    ) -> tuple:
        """
        分类 API 为必需和可选

        Args:
            role: 角色定义
            assigned_apis: 分配的 API 列表

        Returns:
            (required_apis, optional_apis)
        """
        required_capabilities = set(role.get('required_capabilities', []))
        optional_capabilities = set(role.get('optional_capabilities', []))

        required_apis = []
        optional_apis = []

        for api in assigned_apis:
            api_name = api.get('name', '').lower()
            api_desc = api.get('description', '').lower()

            # 简单匹配：检查 API 名称或描述是否包含必需能力关键词
            is_required = False
            for cap in required_capabilities:
                if cap.lower() in api_name or cap.lower() in api_desc:
                    is_required = True
                    break

            if is_required:
                required_apis.append(api)
            else:
                optional_apis.append(api)

        return required_apis, optional_apis

    def _generate_role_id(self, role_name: str) -> str:
        """生成角色 ID"""
        # 简单的 ID 生成：使用拼音或英文
        import hashlib
        return f"role_{hashlib.md5(role_name.encode()).hexdigest()[:8]}"

    def find_orphan_apis(
        self,
        all_apis: List[Dict[str, Any]],
        alignment_result: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        找出未分配的孤儿 API

        Args:
            all_apis: 所有 API 列表
            alignment_result: 对齐结果

        Returns:
            孤儿 API 列表
        """
        # 收集所有已分配的 API ID
        assigned_ids = set()
        for apis in alignment_result.values():
            for api in apis:
                assigned_ids.add(api.get('id', api.get('name')))

        # 找出未分配的
        orphans = []
        for api in all_apis:
            api_id = api.get('id', api.get('name'))
            if api_id not in assigned_ids:
                orphans.append(api)

        logger.info(f"Found {len(orphans)} orphan APIs")
        return orphans
