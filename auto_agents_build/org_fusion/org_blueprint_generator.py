"""
组织蓝图生成器 - 生成 Layer 3 的最终输出
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from datetime import datetime
from shared.logger import get_logger
from shared.utils import save_json

logger = get_logger(__name__)


class OrgBlueprintGenerator:
    """组织蓝图生成器"""

    def generate_blueprint(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any],
        topology: Dict[str, Any],
        access_control_matrix: Dict[str, Dict[str, str]],
        contracts: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成组织运行时蓝图

        Args:
            agents: Agent 列表
            capability_registry: 能力注册表
            topology: 拓扑结构
            access_control_matrix: 访问控制矩阵
            contracts: 契约列表（来自 Layer 2）

        Returns:
            完整的 Layer 3 输出蓝图
        """
        logger.info("Generating organization runtime blueprint")

        blueprint = {
            "blueprint_version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "capability_registry": capability_registry,
            "agent_definitions": self._format_agents(agents),
            "topology": topology,
            "access_control_matrix": access_control_matrix,
            "contracts": contracts or [],
            "statistics": self._generate_statistics(agents, capability_registry, topology)
        }

        logger.info("Blueprint generated successfully")
        return blueprint

    def _format_agents(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化 Agent 定义"""
        formatted = []

        for agent in agents:
            formatted_agent = {
                "agent_id": agent['agent_id'],
                "agent_name": agent['agent_name'],
                "level": agent['level'],
                "is_virtual": agent.get('is_virtual', False),
                "responsibilities": agent.get('responsibilities', []),
                "capability_interface": agent.get('capability_interface', {}),
                "subordinates": agent.get('subordinates', []),
                "local_memory": agent.get('local_memory', {}),
                "metadata": agent.get('metadata', {})
            }

            formatted.append(formatted_agent)

        return formatted

    def _generate_statistics(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any],
        topology: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成统计信息"""
        # Agent 统计
        total_agents = len(agents)
        virtual_agents = len([a for a in agents if a.get('is_virtual', False)])

        agents_by_level = {}
        for agent in agents:
            level = agent['level']
            agents_by_level[level] = agents_by_level.get(level, 0) + 1

        # 能力统计
        atomic_caps = len(capability_registry.get('atomic_capabilities', []))
        composed_caps = len(capability_registry.get('composed_capabilities', []))
        strategic_caps = len(capability_registry.get('strategic_capabilities', []))
        shared_caps = len(capability_registry.get('shared_capabilities', []))

        # 拓扑统计
        topo_stats = topology.get('statistics', {})

        return {
            "agents": {
                "total": total_agents,
                "real": total_agents - virtual_agents,
                "virtual": virtual_agents,
                "by_level": agents_by_level
            },
            "capabilities": {
                "atomic": atomic_caps,
                "composed": composed_caps,
                "strategic": strategic_caps,
                "shared": shared_caps,
                "total": atomic_caps + composed_caps + strategic_caps
            },
            "topology": topo_stats,
            "composition_pattern": {
                "horizontal_reuse": shared_caps > 0,
                "vertical_promotion": composed_caps > 0,
                "cross_domain": strategic_caps > 0
            }
        }

    def save_blueprint(self, blueprint: Dict[str, Any], output_path: str):
        """保存蓝图到文件"""
        save_json(blueprint, output_path)
        logger.info(f"Blueprint saved to {output_path}")

    def generate_summary_report(self, blueprint: Dict[str, Any]) -> str:
        """生成摘要报告"""
        stats = blueprint['statistics']

        report_lines = [
            "=== Layer 3 组织融合层 - 输出摘要 ===",
            "",
            "Agent 统计:",
            f"  总 Agent 数: {stats['agents']['total']}",
            f"  真实 Agent: {stats['agents']['real']}",
            f"  虚拟 Agent: {stats['agents']['virtual']}",
            "",
            "Agent 层级分布:",
        ]

        for level, count in stats['agents']['by_level'].items():
            report_lines.append(f"  {level}: {count}")

        report_lines.extend([
            "",
            "能力单元统计:",
            f"  原子能力: {stats['capabilities']['atomic']}",
            f"  组合能力: {stats['capabilities']['composed']}",
            f"  战略能力: {stats['capabilities']['strategic']}",
            f"  共享能力: {stats['capabilities']['shared']}",
            f"  总能力数: {stats['capabilities']['total']}",
            "",
            "拓扑统计:",
            f"  总节点数: {stats['topology'].get('total_nodes', 0)}",
            f"  Agent 节点: {stats['topology'].get('agent_nodes', 0)}",
            f"  能力节点: {stats['topology'].get('capability_nodes', 0)}",
            f"  总边数: {stats['topology'].get('total_edges', 0)}",
            "",
            "组合模式:",
            f"  横向复用: {'是' if stats['composition_pattern']['horizontal_reuse'] else '否'}",
            f"  纵向晋升: {'是' if stats['composition_pattern']['vertical_promotion'] else '否'}",
            f"  跨域组合: {'是' if stats['composition_pattern']['cross_domain'] else '否'}",
            "",
            "=== 报告结束 ==="
        ])

        return "\n".join(report_lines)

    def export_agent_manifest(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """导出 Agent 清单（用于 Layer 4）"""
        agents = blueprint['agent_definitions']

        manifest = {
            "agents": [
                {
                    "agent_id": agent['agent_id'],
                    "agent_name": agent['agent_name'],
                    "level": agent['level'],
                    "capabilities": self._extract_capability_names(
                        agent['capability_interface'],
                        blueprint['capability_registry']
                    ),
                    "subordinates": agent['subordinates']
                }
                for agent in agents
            ]
        }

        return manifest

    def _extract_capability_names(
        self,
        interface: Dict[str, Any],
        registry: Dict[str, Any]
    ) -> List[str]:
        """提取能力名称"""
        all_caps = (
            registry.get('atomic_capabilities', []) +
            registry.get('composed_capabilities', []) +
            registry.get('strategic_capabilities', [])
        )

        cap_id_to_name = {cap['unit_id']: cap['name'] for cap in all_caps}

        names = []
        for cap_list in interface.values():
            if isinstance(cap_list, list):
                for cap_ref in cap_list:
                    if isinstance(cap_ref, dict):
                        cap_id = cap_ref.get('unit_id')
                        if cap_id in cap_id_to_name:
                            names.append(cap_id_to_name[cap_id])

        return names
