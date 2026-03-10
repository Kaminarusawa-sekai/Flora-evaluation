"""
能力组合器 - 智能组合底层能力单元
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Tuple
from shared.logger import get_logger
from shared.llm_client import LLMClient
from .capability_unit_registry import CapabilityUnitRegistry

logger = get_logger(__name__)


class CapabilityComposer:
    """能力组合器"""

    def __init__(self, registry: CapabilityUnitRegistry, llm_client: LLMClient):
        self.registry = registry
        self.llm_client = llm_client

    def compose_capabilities(
        self,
        agents: List[Dict[str, Any]],
        composition_strategy: str = "auto"
    ) -> Dict[str, List[str]]:
        """
        为 Agent 组合能力

        Args:
            agents: Agent 列表
            composition_strategy: 组合策略 (auto/horizontal/vertical/cross_domain)

        Returns:
            {agent_id: [composed_capability_ids]}
        """
        logger.info(f"Composing capabilities with strategy: {composition_strategy}")

        compositions = {}

        if composition_strategy == "auto":
            # 自动识别并应用所有策略
            compositions.update(self._horizontal_reuse(agents))
            compositions.update(self._vertical_promotion(agents))
            compositions.update(self._cross_domain_composition(agents))
        elif composition_strategy == "horizontal":
            compositions = self._horizontal_reuse(agents)
        elif composition_strategy == "vertical":
            compositions = self._vertical_promotion(agents)
        elif composition_strategy == "cross_domain":
            compositions = self._cross_domain_composition(agents)

        logger.info(f"Capability composition completed for {len(compositions)} agents")
        return compositions

    def _horizontal_reuse(self, agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        横向复用 - 同级 Agent 共享能力

        场景：多个同级 Agent 需要相同能力
        策略：能力单元保持单例，每个 Agent 持有引用指针
        """
        logger.info("Applying horizontal reuse strategy")

        compositions = {}

        # 找出被多个同级 Agent 使用的能力
        level_capabilities = {}  # level -> {capability_id: [agent_ids]}

        for agent in agents:
            level = agent['level']
            if level not in level_capabilities:
                level_capabilities[level] = {}

            # 收集该 Agent 的所有能力
            interface = agent.get('capability_interface', {})
            all_caps = (interface.get('direct_capabilities', []) +
                       interface.get('composed_capabilities', []))

            for cap_ref in all_caps:
                unit_id = cap_ref['unit_id']
                if unit_id not in level_capabilities[level]:
                    level_capabilities[level][unit_id] = []
                level_capabilities[level][unit_id].append(agent['agent_id'])

        # 识别共享能力（被2个以上 Agent 使用）
        for level, caps in level_capabilities.items():
            for unit_id, agent_ids in caps.items():
                if len(agent_ids) >= 2:
                    unit = self.registry.get_unit(unit_id)
                    logger.info(f"  Shared capability: {unit['name']} by {len(agent_ids)} agents at {level}")

        return compositions

    def _vertical_promotion(self, agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        纵向晋升 - 上级需要下级能力的抽象视图

        场景：主管需要管理下属的能力
        策略：创建新的 composed 能力单元，包含对底层能力的引用
        """
        logger.info("Applying vertical promotion strategy")

        compositions = {}

        # 按层级分组
        agents_by_level = {}
        for agent in agents:
            level = agent['level']
            if level not in agents_by_level:
                agents_by_level[level] = []
            agents_by_level[level].append(agent)

        # 为主管层级创建晋升能力
        if 'supervisor' in agents_by_level and 'specialist' in agents_by_level:
            for supervisor in agents_by_level['supervisor']:
                # 收集下属的能力
                subordinate_caps = []
                for specialist in agents_by_level['specialist']:
                    interface = specialist.get('capability_interface', {})
                    subordinate_caps.extend([cap['unit_id'] for cap in
                                           interface.get('direct_capabilities', [])])

                if subordinate_caps:
                    # 使用 LLM 生成晋升能力
                    promoted_cap_id = self._promote_with_llm(
                        supervisor['agent_name'],
                        subordinate_caps
                    )

                    if promoted_cap_id:
                        if supervisor['agent_id'] not in compositions:
                            compositions[supervisor['agent_id']] = []
                        compositions[supervisor['agent_id']].append(promoted_cap_id)

        return compositions

    def _cross_domain_composition(self, agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        跨域组合 - 高层 Agent 需要跨部门协调

        场景：CEO/总监需要跨域能力
        策略：创建 strategic 级别的能力单元
        """
        logger.info("Applying cross-domain composition strategy")

        compositions = {}

        # 找出高层 Agent（manager 及以上）
        high_level_agents = [agent for agent in agents
                            if agent['level'] in ['manager', 'director', 'ceo']]

        for agent in high_level_agents:
            # 收集跨域能力
            cross_domain_caps = self._identify_cross_domain_capabilities(agents)

            if cross_domain_caps:
                # 创建战略能力
                strategic_cap_id = self.registry.register_strategic_capability(
                    name=f"{agent['agent_name']}战略协调能力",
                    composed_of=cross_domain_caps,
                    semantic_description=f"跨部门协调和战略决策能力",
                    cross_domain=True,
                    owner=agent['agent_name']
                )

                if agent['agent_id'] not in compositions:
                    compositions[agent['agent_id']] = []
                compositions[agent['agent_id']].append(strategic_cap_id)

        return compositions

    def _promote_with_llm(
        self,
        supervisor_name: str,
        subordinate_cap_ids: List[str]
    ) -> str:
        """使用 LLM 生成晋升能力"""
        # 获取能力详情
        cap_details = []
        for cap_id in subordinate_cap_ids[:10]:  # 限制数量
            unit = self.registry.get_unit(cap_id)
            if unit:
                cap_details.append(f"- {unit['name']}: {unit.get('semantic_description', '')}")

        cap_text = "\n".join(cap_details)

        prompt = f"""为"{supervisor_name}"主管创建一个高阶能力，该能力组合了以下下属的能力：

{cap_text}

请生成一个语义化的能力描述和编排逻辑。

返回 JSON 格式：
{{
  "name": "能力名称",
  "description": "语义描述",
  "orchestration": "编排逻辑"
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务流程专家。"},
                {"role": "user", "content": prompt}
            ])

            # 注册组合能力
            cap_id = self.registry.register_composed_capability(
                name=response['name'],
                composed_of=subordinate_cap_ids,
                semantic_description=response['description'],
                orchestration_logic=response.get('orchestration', ''),
                owner=supervisor_name
            )

            return cap_id

        except Exception as e:
            logger.warning(f"Failed to promote capability with LLM: {e}")
            return None

    def _identify_cross_domain_capabilities(self, agents: List[Dict[str, Any]]) -> List[str]:
        """识别跨域能力"""
        # 简单实现：收集不同领域的能力
        domain_caps = {}

        for agent in agents:
            # 假设从 agent 的 metadata 中获取领域信息
            domain = agent.get('metadata', {}).get('domain', 'unknown')

            interface = agent.get('capability_interface', {})
            caps = [cap['unit_id'] for cap in interface.get('direct_capabilities', [])]

            if domain not in domain_caps:
                domain_caps[domain] = []
            domain_caps[domain].extend(caps)

        # 如果有多个领域，返回跨域能力
        if len(domain_caps) > 1:
            cross_domain = []
            for caps in domain_caps.values():
                cross_domain.extend(caps[:2])  # 每个领域取2个
            return cross_domain

        return []
