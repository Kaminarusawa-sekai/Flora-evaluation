"""
角色清单生成器 - 生成 Layer 2 的最终输出
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from datetime import datetime
from shared.logger import get_logger
from shared.utils import save_json

logger = get_logger(__name__)


class RoleManifestGenerator:
    """角色清单生成器"""

    def generate_manifest(
        self,
        roles: List[Dict[str, Any]],
        domain_info: Dict[str, Any],
        contracts: List[Dict[str, Any]],
        gap_report: str
    ) -> Dict[str, Any]:
        """
        生成职能装配清单

        Args:
            roles: 角色列表（带约束）
            domain_info: 领域信息
            contracts: 契约列表
            gap_report: 差异分析报告

        Returns:
            完整的 Layer 2 输出清单
        """
        logger.info("Generating role assembly manifest")

        manifest = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "domain": domain_info.get('primary_domain', 'Unknown'),
            "secondary_domains": domain_info.get('secondary_domains', []),
            "domain_weights": domain_info.get('domain_weights', {}),
            "roles": self._format_roles(roles),
            "contracts": contracts,
            "statistics": self._generate_statistics(roles, contracts),
            "gap_analysis": {
                "report": gap_report,
                "orphan_apis": domain_info.get('unmatched_apis', [])
            }
        }

        logger.info(f"Manifest generated with {len(roles)} roles and {len(contracts)} contracts")
        return manifest

    def _format_roles(self, roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化角色信息"""
        formatted = []

        for role in roles:
            formatted_role = {
                "role_id": role['role_id'],
                "role_name": role['role_name'],
                "level": role.get('level', 'specialist'),
                "is_virtual": role.get('is_virtual', False),
                "responsibilities": role.get('responsibilities', []),
                "assigned_apis": role.get('assigned_apis', []),
                "constraints": role.get('constraints', []),
                "statistics": {
                    "total_apis": len(role.get('assigned_apis', [])),
                    "required_apis": len([api for api in role.get('assigned_apis', [])
                                        if api.get('priority') == 'required']),
                    "optional_apis": len([api for api in role.get('assigned_apis', [])
                                        if api.get('priority') == 'optional']),
                    "sensitive_apis": role.get('sensitive_api_count', 0),
                    "constraints_count": len(role.get('constraints', []))
                }
            }

            formatted.append(formatted_role)

        return formatted

    def _generate_statistics(
        self,
        roles: List[Dict[str, Any]],
        contracts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成统计信息"""
        total_apis = sum(len(role.get('assigned_apis', [])) for role in roles)
        virtual_roles = len([role for role in roles if role.get('is_virtual', False)])
        total_constraints = sum(len(role.get('constraints', [])) for role in roles)

        # 按层级统计
        level_stats = {}
        for role in roles:
            level = role.get('level', 'specialist')
            if level not in level_stats:
                level_stats[level] = 0
            level_stats[level] += 1

        return {
            "total_roles": len(roles),
            "virtual_roles": virtual_roles,
            "real_roles": len(roles) - virtual_roles,
            "total_apis": total_apis,
            "total_contracts": len(contracts),
            "total_constraints": total_constraints,
            "roles_by_level": level_stats,
            "avg_apis_per_role": round(total_apis / len(roles), 2) if roles else 0
        }

    def save_manifest(self, manifest: Dict[str, Any], output_path: str):
        """保存清单到文件"""
        save_json(manifest, output_path)
        logger.info(f"Manifest saved to {output_path}")

    def generate_summary_report(self, manifest: Dict[str, Any]) -> str:
        """生成摘要报告"""
        stats = manifest['statistics']

        report_lines = [
            "=== Layer 2 职能对齐层 - 输出摘要 ===",
            "",
            f"领域: {manifest['domain']}",
            f"次要领域: {', '.join(manifest['secondary_domains'])}",
            "",
            "角色统计:",
            f"  总角色数: {stats['total_roles']}",
            f"  真实角色: {stats['real_roles']}",
            f"  虚拟角色: {stats['virtual_roles']}",
            "",
            "API 统计:",
            f"  总 API 数: {stats['total_apis']}",
            f"  平均每角色: {stats['avg_apis_per_role']} APIs",
            "",
            "约束统计:",
            f"  总契约数: {stats['total_contracts']}",
            f"  总约束数: {stats['total_constraints']}",
            "",
            "角色层级分布:",
        ]

        for level, count in stats['roles_by_level'].items():
            report_lines.append(f"  {level}: {count}")

        report_lines.append("")
        report_lines.append("=== 报告结束 ===")

        return "\n".join(report_lines)
