"""
Prompt 工厂 - 生成 Agent 的 Prompt
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.llm_client import LLMClient
from shared.utils import ensure_dir

logger = get_logger(__name__)


class PromptFactory:
    """Prompt 工厂"""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client

    def generate_prompts(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any],
        contracts: List[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        为所有 Agent 生成 Prompt

        Args:
            agents: Agent 列表
            capability_registry: 能力注册表
            contracts: 契约列表

        Returns:
            {agent_id: prompt_text}
        """
        logger.info(f"Generating prompts for {len(agents)} agents")

        prompts = {}

        for agent in agents:
            if agent['level'] in ['specialist', 'supervisor']:
                prompt = self._generate_specialist_prompt(agent, capability_registry, contracts)
            else:
                prompt = self._generate_supervisor_prompt(agent, capability_registry, contracts)

            prompts[agent['agent_id']] = prompt

        logger.info("Prompt generation completed")
        return prompts

    def _generate_specialist_prompt(
        self,
        agent: Dict[str, Any],
        capability_registry: Dict[str, Any],
        contracts: List[Dict[str, Any]]
    ) -> str:
        """生成职能 Agent Prompt"""
        agent_name = agent['agent_name']
        responsibilities = agent.get('responsibilities', [])

        # 提取能力和工具
        tools = self._extract_tools(agent, capability_registry)

        # 提取约束
        constraints = self._extract_constraints(agent, contracts)

        # 构建 Prompt
        prompt_parts = [
            f"# 角色定义",
            f"你是 {agent_name}，负责以下职责：",
        ]

        for i, resp in enumerate(responsibilities, 1):
            prompt_parts.append(f"{i}. {resp}")

        prompt_parts.extend([
            "",
            "# 可用工具",
            "你可以使用以下工具来完成任务：",
            ""
        ])

        for tool in tools:
            prompt_parts.append(f"## {tool['name']}")
            prompt_parts.append(f"描述: {tool['description']}")
            prompt_parts.append(f"用法: {tool['usage']}")
            if tool.get('constraints'):
                prompt_parts.append(f"约束: {tool['constraints']}")
            prompt_parts.append("")

        if constraints:
            prompt_parts.extend([
                "# 执行规范",
                "在执行任务时，你必须遵守以下规范：",
                ""
            ])

            for i, constraint in enumerate(constraints, 1):
                prompt_parts.append(f"{i}. {constraint}")

            prompt_parts.append("")

        prompt_parts.extend([
            "# 工作流程",
            "1. 仔细理解用户的需求",
            "2. 选择合适的工具",
            "3. 检查是否满足约束条件",
            "4. 执行操作并记录结果",
            "5. 如遇异常情况，及时上报主管",
            "",
            "# 注意事项",
            "- 始终以用户需求为中心",
            "- 严格遵守约束条件",
            "- 保持操作的可追溯性",
            "- 遇到权限不足时，请求上级协助"
        ])

        return "\n".join(prompt_parts)

    def _generate_supervisor_prompt(
        self,
        agent: Dict[str, Any],
        capability_registry: Dict[str, Any],
        contracts: List[Dict[str, Any]]
    ) -> str:
        """生成主管 Agent Prompt"""
        agent_name = agent['agent_name']
        subordinates = agent.get('subordinates', [])

        # 提取下属视图
        subordinate_capabilities = self._extract_subordinate_view(agent, capability_registry)

        prompt_parts = [
            f"# 角色定义",
            f"你是 {agent_name}，负责团队管理和协调工作。",
            "",
            "# 管理职责",
            "1. 协调团队成员完成任务",
            "2. 审批需要上级权限的操作",
            "3. 监控团队工作进度和质量",
            "4. 处理异常情况和冲突",
            "5. 优化资源分配",
            "",
            "# 下属团队",
            f"你管理 {len(subordinates)} 名下属，他们的能力包括：",
            ""
        ]

        for cap in subordinate_capabilities:
            prompt_parts.append(f"- {cap['name']}: {cap['description']}")

        prompt_parts.extend([
            "",
            "# 决策逻辑",
            "在处理任务时，请遵循以下决策流程：",
            "",
            "1. 分析任务需求和复杂度",
            "2. 评估哪些下属具备相应能力",
            "3. 考虑当前工作负载和优先级",
            "4. 分配任务给最合适的下属",
            "5. 监控执行过程，必要时介入",
            "",
            "# 审批规则",
            "以下情况需要你的审批：",
            "- 高风险操作（删除、修改关键数据）",
            "- 超出下属权限范围的操作",
            "- 涉及大额资金的操作",
            "- 跨部门协调的操作",
            "",
            "# Chain-of-Thought 推演",
            "在做出决策前，请明确说明你的思考过程：",
            "1. 当前情况是什么？",
            "2. 有哪些可选方案？",
            "3. 每个方案的优缺点？",
            "4. 最终选择哪个方案，为什么？",
            "",
            "# 注意事项",
            "- 充分授权，避免微观管理",
            "- 关注结果，而非过程细节",
            "- 及时给予反馈和指导",
            "- 遇到重大问题，向上级汇报"
        ])

        return "\n".join(prompt_parts)

    def _extract_tools(
        self,
        agent: Dict[str, Any],
        capability_registry: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """提取 Agent 的工具列表"""
        tools = []

        interface = agent.get('capability_interface', {})
        all_caps = (
            interface.get('direct_capabilities', []) +
            interface.get('composed_capabilities', [])
        )

        # 获取所有能力单元
        all_units = (
            capability_registry.get('atomic_capabilities', []) +
            capability_registry.get('composed_capabilities', [])
        )
        unit_map = {unit['unit_id']: unit for unit in all_units}

        for cap_ref in all_caps:
            unit_id = cap_ref['unit_id']
            unit = unit_map.get(unit_id)

            if unit:
                # 处理 constraints - 可能是字典列表
                constraints = unit.get('constraints', [])
                if constraints and isinstance(constraints, list):
                    if isinstance(constraints[0], dict):
                        # 如果是字典列表，提取 constraint_rule 或 description
                        constraint_strs = [
                            c.get('constraint_rule') or c.get('description') or str(c)
                            for c in constraints
                        ]
                        constraints_text = "; ".join(constraint_strs)
                    else:
                        # 如果是字符串列表
                        constraints_text = ", ".join(constraints)
                else:
                    constraints_text = ""

                tool = {
                    "name": unit['name'],
                    "description": unit.get('semantic_description', ''),
                    "usage": self._generate_tool_usage(unit),
                    "constraints": constraints_text
                }
                tools.append(tool)

        return tools

    def _generate_tool_usage(self, unit: Dict[str, Any]) -> str:
        """生成工具使用说明"""
        if unit['level'] == 'atomic':
            apis = unit.get('underlying_apis', [])
            params = unit.get('required_params', [])
            return f"调用 API: {', '.join(apis)}，参数: {', '.join(params)}"
        else:
            composed_of = unit.get('composed_of', [])
            return f"组合能力，包含 {len(composed_of)} 个子能力"

    def _extract_constraints(
        self,
        agent: Dict[str, Any],
        contracts: List[Dict[str, Any]]
    ) -> List[str]:
        """提取约束条件"""
        if not contracts:
            return []

        agent_id = agent['agent_id']
        constraints = []

        for contract in contracts:
            if contract.get('role_id') == agent_id.replace('agent_', 'role_'):
                constraint_text = f"{contract['api_name']}: {contract['constraint_rule']}"
                constraints.append(constraint_text)

        return constraints

    def _extract_subordinate_view(
        self,
        agent: Dict[str, Any],
        capability_registry: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """提取下属能力视图"""
        interface = agent.get('capability_interface', {})
        delegated_caps = interface.get('delegated_capabilities', [])

        all_units = (
            capability_registry.get('atomic_capabilities', []) +
            capability_registry.get('composed_capabilities', [])
        )
        unit_map = {unit['unit_id']: unit for unit in all_units}

        capabilities = []
        for cap_ref in delegated_caps:
            unit_id = cap_ref['unit_id']
            unit = unit_map.get(unit_id)

            if unit:
                capabilities.append({
                    "name": unit['name'],
                    "description": unit.get('semantic_description', '')
                })

        return capabilities

    def save_prompts(self, prompts: Dict[str, str], output_dir: str):
        """保存 Prompt 到文件"""
        ensure_dir(output_dir)

        for agent_id, prompt in prompts.items():
            file_path = Path(output_dir) / f"{agent_id}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(prompt)

        logger.info(f"Saved {len(prompts)} prompts to {output_dir}")
