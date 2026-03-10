"""
差异分析器 - 分析角色和 API 的差异，进行调整
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.llm_client import LLMClient

logger = get_logger(__name__)


class GapAnalyzer:
    """差异分析器"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def analyze_gaps(
        self,
        filled_roles: List[Dict[str, Any]],
        orphan_apis: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析差异并提出调整方案

        Args:
            filled_roles: 已填充的角色列表
            orphan_apis: 孤儿 API 列表

        Returns:
            {
                "adjusted_roles": [...],
                "frozen_roles": [...],
                "new_roles": [...],
                "report": "..."
            }
        """
        logger.info("Analyzing gaps between roles and APIs")

        # 1. 识别空角色（无 API 支撑）
        empty_roles = self._find_empty_roles(filled_roles)

        # 2. 为孤儿 API 创建新角色
        new_roles = self._create_roles_for_orphans(orphan_apis)

        # 3. 生成调整报告
        report = self._generate_report(filled_roles, empty_roles, new_roles, orphan_apis)

        # 4. 调整后的角色列表
        adjusted_roles = [role for role in filled_roles if role not in empty_roles]
        adjusted_roles.extend(new_roles)

        result = {
            "adjusted_roles": adjusted_roles,
            "frozen_roles": empty_roles,
            "new_roles": new_roles,
            "report": report
        }

        logger.info(f"Gap analysis completed: {len(empty_roles)} frozen, {len(new_roles)} new roles")
        return result

    def _find_empty_roles(self, filled_roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别无 API 支撑的空角色"""
        empty = []

        for role in filled_roles:
            if not role.get('assigned_apis'):
                empty.append(role)
                logger.info(f"  Empty role found: {role['role_name']}")

        return empty

    def _create_roles_for_orphans(self, orphan_apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为孤儿 API 创建新角色"""
        if not orphan_apis:
            return []

        logger.info(f"Creating roles for {len(orphan_apis)} orphan APIs")

        # 使用 LLM 聚类孤儿 API 并生成角色
        new_roles = self._llm_cluster_and_create_roles(orphan_apis)

        return new_roles

    def _llm_cluster_and_create_roles(self, orphan_apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用 LLM 聚类孤儿 API 并创建角色"""
        # 构建 API 列表
        api_list = []
        for api in orphan_apis[:20]:  # 限制数量
            api_list.append(f"- {api.get('name', 'Unknown')}: {api.get('description', '')}")

        api_text = "\n".join(api_list)

        prompt = f"""以下是一些未分配到任何角色的 API，请分析它们的业务特征，将相似的 API 聚类，并为每个聚类创建一个合适的角色。

孤儿 API：
{api_text}

请返回 JSON 格式：
{{
  "new_roles": [
    {{
      "role_name": "角色名称",
      "level": "specialist",
      "responsibilities": ["职责1", "职责2"],
      "assigned_api_names": ["API名称1", "API名称2"],
      "reasoning": "创建理由"
    }}
  ]
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务流程分析专家。"},
                {"role": "user", "content": prompt}
            ])

            new_roles_data = response.get('new_roles', [])

            # 构建完整的角色对象
            new_roles = []
            for role_data in new_roles_data:
                role_name = role_data['role_name']
                assigned_names = set(role_data.get('assigned_api_names', []))

                # 找到对应的 API 对象
                assigned_apis = []
                for api in orphan_apis:
                    if api.get('name') in assigned_names:
                        assigned_apis.append({
                            "api_id": api.get('id', api.get('name')),
                            "api_name": api.get('name'),
                            "business_name": api.get('description', api.get('name')),
                            "priority": "required",
                            "method": api.get('method', 'GET'),
                            "path": api.get('path', ''),
                            "description": api.get('description', '')
                        })

                new_role = {
                    "role_id": self._generate_role_id(role_name),
                    "role_name": role_name,
                    "level": role_data.get('level', 'specialist'),
                    "responsibilities": role_data.get('responsibilities', []),
                    "assigned_apis": assigned_apis,
                    "is_virtual": True,  # 标记为虚拟角色
                    "creation_reason": role_data.get('reasoning', '')
                }

                new_roles.append(new_role)
                logger.info(f"  Created virtual role: {role_name} with {len(assigned_apis)} APIs")

            return new_roles

        except Exception as e:
            logger.error(f"Failed to create roles for orphans: {e}")
            return []

    def _generate_report(
        self,
        filled_roles: List[Dict[str, Any]],
        empty_roles: List[Dict[str, Any]],
        new_roles: List[Dict[str, Any]],
        orphan_apis: List[Dict[str, Any]]
    ) -> str:
        """生成差异分析报告"""
        report_lines = [
            "=== 角色调整报告 ===",
            "",
            f"总角色数: {len(filled_roles)}",
            f"有效角色数: {len(filled_roles) - len(empty_roles)}",
            f"空角色数: {len(empty_roles)}",
            f"新增虚拟角色数: {len(new_roles)}",
            f"孤儿 API 数: {len(orphan_apis)}",
            ""
        ]

        if empty_roles:
            report_lines.append("冻结的空角色：")
            for role in empty_roles:
                report_lines.append(f"  - {role['role_name']}: 无 API 支撑")
            report_lines.append("")

        if new_roles:
            report_lines.append("新增的虚拟角色：")
            for role in new_roles:
                api_count = len(role.get('assigned_apis', []))
                report_lines.append(f"  - {role['role_name']}: {api_count} APIs")
                report_lines.append(f"    理由: {role.get('creation_reason', 'N/A')}")
            report_lines.append("")

        report_lines.append("=== 报告结束 ===")

        return "\n".join(report_lines)

    def _generate_role_id(self, role_name: str) -> str:
        """生成角色 ID"""
        import hashlib
        return f"role_{hashlib.md5(role_name.encode()).hexdigest()[:8]}"
