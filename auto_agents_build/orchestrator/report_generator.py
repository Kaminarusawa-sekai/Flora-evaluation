"""
报告生成器 - 生成构建过程的详细报告
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any
from datetime import datetime
from shared.logger import get_logger
from shared.utils import save_file

logger = get_logger(__name__)


class ReportGenerator:
    """报告生成器"""

    def generate_report(self, pipeline_result: Dict[str, Any]) -> str:
        """
        生成完整的构建报告

        Args:
            pipeline_result: 流水线执行结果

        Returns:
            报告文本
        """
        logger.info("Generating build report")

        report_lines = [
            "=" * 80,
            "Agent 自动化构建系统 - 执行报告",
            "=" * 80,
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"执行状态: {'成功' if pipeline_result.get('success') else '失败'}",
            f"总耗时: {pipeline_result.get('duration_seconds', 0):.2f} 秒",
            "",
        ]

        if not pipeline_result.get('success'):
            report_lines.extend([
                "错误信息:",
                f"  {pipeline_result.get('error', 'Unknown error')}",
                ""
            ])
            return "\n".join(report_lines)

        # Layer 2 报告
        if 'layer2' in pipeline_result:
            report_lines.extend(self._generate_layer2_section(pipeline_result['layer2']))

        # Layer 3 报告
        if 'layer3' in pipeline_result:
            report_lines.extend(self._generate_layer3_section(pipeline_result['layer3']))

        # Layer 4 报告
        if 'layer4' in pipeline_result:
            report_lines.extend(self._generate_layer4_section(pipeline_result['layer4']))

        # 总结
        report_lines.extend(self._generate_summary(pipeline_result))

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def _generate_layer2_section(self, layer2_result: Dict[str, Any]) -> list:
        """生成 Layer 2 报告部分"""
        stats = layer2_result.get('statistics', {})

        lines = [
            "─" * 80,
            "Layer 2: 职能对齐层",
            "─" * 80,
            "",
            f"领域: {layer2_result.get('domain', 'Unknown')}",
            f"次要领域: {', '.join(layer2_result.get('secondary_domains', []))}",
            "",
            "角色统计:",
            f"  总角色数: {stats.get('total_roles', 0)}",
            f"  真实角色: {stats.get('real_roles', 0)}",
            f"  虚拟角色: {stats.get('virtual_roles', 0)}",
            "",
            "API 统计:",
            f"  总 API 数: {stats.get('total_apis', 0)}",
            f"  平均每角色: {stats.get('avg_apis_per_role', 0)} APIs",
            "",
            "约束统计:",
            f"  总契约数: {stats.get('total_contracts', 0)}",
            f"  总约束数: {stats.get('total_constraints', 0)}",
            "",
        ]

        return lines

    def _generate_layer3_section(self, layer3_result: Dict[str, Any]) -> list:
        """生成 Layer 3 报告部分"""
        stats = layer3_result.get('statistics', {})
        agent_stats = stats.get('agents', {})
        cap_stats = stats.get('capabilities', {})
        topo_stats = stats.get('topology', {})

        lines = [
            "─" * 80,
            "Layer 3: 组织融合层",
            "─" * 80,
            "",
            "Agent 统计:",
            f"  总 Agent 数: {agent_stats.get('total', 0)}",
            f"  真实 Agent: {agent_stats.get('real', 0)}",
            f"  虚拟 Agent: {agent_stats.get('virtual', 0)}",
            "",
            "能力单元统计:",
            f"  原子能力: {cap_stats.get('atomic', 0)}",
            f"  组合能力: {cap_stats.get('composed', 0)}",
            f"  战略能力: {cap_stats.get('strategic', 0)}",
            f"  共享能力: {cap_stats.get('shared', 0)}",
            "",
            "拓扑统计:",
            f"  总节点数: {topo_stats.get('total_nodes', 0)}",
            f"  总边数: {topo_stats.get('total_edges', 0)}",
            "",
        ]

        return lines

    def _generate_layer4_section(self, layer4_result: Dict[str, Any]) -> list:
        """生成 Layer 4 报告部分"""
        lines = [
            "─" * 80,
            "Layer 4: 代码生成层",
            "─" * 80,
            "",
            f"生成的 Prompt 数: {layer4_result.get('prompts_count', 0)}",
            f"配置清单: 已生成",
            f"知识库链接: 已配置",
            f"监控配置: 已生成",
            "",
        ]

        return lines

    def _generate_summary(self, pipeline_result: Dict[str, Any]) -> list:
        """生成总结"""
        layer2 = pipeline_result.get('layer2', {})
        layer3 = pipeline_result.get('layer3', {})
        layer4 = pipeline_result.get('layer4', {})

        total_roles = layer2.get('statistics', {}).get('total_roles', 0)
        total_agents = layer3.get('statistics', {}).get('agents', {}).get('total', 0)
        total_capabilities = layer3.get('statistics', {}).get('capabilities', {}).get('total', 0)
        total_prompts = layer4.get('prompts_count', 0)

        lines = [
            "─" * 80,
            "执行总结",
            "─" * 80,
            "",
            f"✓ 识别了 {total_roles} 个职能角色",
            f"✓ 生成了 {total_agents} 个 Agent",
            f"✓ 注册了 {total_capabilities} 个能力单元",
            f"✓ 生成了 {total_prompts} 个 Agent Prompt",
            f"✓ 配置了监控和知识库",
            "",
            "输出文件:",
            "  - output/layer2/role_manifest.json",
            "  - output/layer3/org_blueprint.json",
            "  - output/layer4/prompts/",
            "  - output/layer4/manifest.json",
            "  - output/layer4/knowledge_links.json",
            "  - output/layer4/monitoring/",
            "",
        ]

        return lines

    def save_report(self, report: str, output_path: str):
        """保存报告到文件"""
        save_file(report, output_path)
        logger.info(f"Report saved to {output_path}")

    def generate_html_report(self, pipeline_result: Dict[str, Any]) -> str:
        """生成 HTML 格式的报告"""
        text_report = self.generate_report(pipeline_result)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Agent 构建报告</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            line-height: 1.6;
        }}
        pre {{
            background-color: #252526;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .success {{
            color: #4ec9b0;
        }}
        .error {{
            color: #f48771;
        }}
    </style>
</head>
<body>
    <pre class="{'success' if pipeline_result.get('success') else 'error'}">
{text_report}
    </pre>
</body>
</html>
"""
        return html

    def save_html_report(self, pipeline_result: Dict[str, Any], output_path: str):
        """保存 HTML 报告"""
        html = self.generate_html_report(pipeline_result)
        save_file(html, output_path)
        logger.info(f"HTML report saved to {output_path}")
