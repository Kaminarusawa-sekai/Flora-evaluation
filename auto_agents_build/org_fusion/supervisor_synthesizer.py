"""
主管合成器 - 动态生成主管 Agent
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.llm_client import LLMClient
from .capability_unit_registry import CapabilityUnitRegistry
from .capability_promoter import CapabilityPromoter

logger = get_logger(__name__)


class SupervisorSynthesizer:
    """主管合成器"""

    def __init__(
        self,
        registry: CapabilityUnitRegistry,
        llm_client: LLMClient,
        promoter: CapabilityPromoter
    ):
        self.registry = registry
        self.llm_client = llm_client
        self.promoter = promoter

    def synthesize_supervisors(
        self,
        specialist_agents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为专员 Agent 合成主管 Agent

        Args:
            specialist_agents: 专员 Agent 列表

        Returns:
            主管 Agent 列表
        """
        logger.info(f"Synthesizing supervisors for {len(specialist_agents)} specialists")

        supervisors = []

        # 按领域/职能分组专员
        groups = self._group_specialists(specialist_agents)

        for group_name, specialists in groups.items():
            supervisor = self._create_supervisor(group_name, specialists)
            supervisors.append(supervisor)

        logger.info(f"Synthesized {len(supervisors)} supervisors")
        return supervisors

    def _group_specialists(
        self,
        specialists: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """将专员按职能分组"""
        # 使用 LLM 进行智能分组
        specialist_info = []
        for agent in specialists:
            specialist_info.append({
                "name": agent['agent_name'],
                "responsibilities": agent.get('responsibilities', [])
            })

        prompt = f"""将以下专员按照职能相关性分组，每组应该由一个主管管理。

专员列表：
{self._format_specialists(specialist_info)}

返回 JSON 格式：
{{
  "groups": [
    {{
      "group_name": "组名（如：销售组、财务组）",
      "specialist_names": ["专员1", "专员2"]
    }}
  ]
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个组织架构专家。"},
                {"role": "user", "content": prompt}
            ])

            # 转换为分组字典
            groups = {}
            for group in response.get('groups', []):
                group_name = group['group_name']
                specialist_names = set(group['specialist_names'])

                groups[group_name] = [
                    agent for agent in specialists
                    if agent['agent_name'] in specialist_names
                ]

            return groups

        except Exception as e:
            logger.warning(f"LLM grouping failed: {e}, using default grouping")
            # 降级策略：所有专员归为一组
            return {"默认组": specialists}

    def _create_supervisor(
        self,
        group_name: str,
        subordinates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建主管 Agent"""
        supervisor_name = f"{group_name}主管"
        supervisor_id = f"agent_supervisor_{hash(supervisor_name) % 10000}"

        logger.info(f"Creating supervisor: {supervisor_name}")

        # 生成主管的能力视图
        capability_view = self._synthesize_supervisor_view(subordinates)

        supervisor = {
            "agent_id": supervisor_id,
            "agent_name": supervisor_name,
            "level": "supervisor",
            "is_virtual": False,
            "responsibilities": self._generate_supervisor_responsibilities(group_name),
            "capability_interface": capability_view,
            "subordinates": [agent['agent_id'] for agent in subordinates],
            "local_memory": {
                "type": "short_term",
                "capacity": "2000_messages"
            },
            "metadata": {
                "synthesized": True,
                "group": group_name,
                "subordinate_count": len(subordinates)
            }
        }

        return supervisor

    def _synthesize_supervisor_view(
        self,
        subordinates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        为主管生成能力视图

        主管不"拥有"下属的能力，而是"引用"或"委托"
        """
        view = {
            "direct_capabilities": [],      # 主管自己可执行的
            "delegated_capabilities": [],   # 需要委托给下属的
            "monitoring_capabilities": []   # 只监控不执行的
        }

        # 1. 收集下属的所有能力
        all_sub_caps = []
        for sub in subordinates:
            interface = sub.get('capability_interface', {})
            all_sub_caps.extend(interface.get('direct_capabilities', []))

        # 2. 晋升为组合能力
        if all_sub_caps:
            sub_cap_ids = [cap['unit_id'] for cap in all_sub_caps]
            composed_cap_id = self.promoter.promote_capabilities(
                sub_cap_ids,
                "supervisor",
                f"{subordinates[0]['agent_name']}主管" if subordinates else "主管"
            )

            # 3. 分类能力
            composed_unit = self.registry.get_unit(composed_cap_id)
            if composed_unit:
                # 主管可以直接执行组合能力
                view['direct_capabilities'].append({
                    "unit_id": composed_cap_id,
                    "name": composed_unit['name'],
                    "access_mode": "execute",
                    "priority": "high"
                })

        # 4. 下属的能力作为委托能力
        for cap_ref in all_sub_caps[:5]:  # 限制数量
            view['delegated_capabilities'].append({
                "unit_id": cap_ref['unit_id'],
                "name": cap_ref.get('name', ''),
                "access_mode": "delegate",
                "priority": "medium",
                "delegate_to": [sub['agent_id'] for sub in subordinates]
            })

        return view

    def _generate_supervisor_responsibilities(self, group_name: str) -> List[str]:
        """生成主管职责"""
        return [
            f"{group_name}团队管理",
            "工作分配和协调",
            "绩效监控和评估",
            "异常处理和升级",
            "资源调配"
        ]

    def _format_specialists(self, specialists: List[Dict[str, Any]]) -> str:
        """格式化专员信息"""
        lines = []
        for spec in specialists:
            resp = ", ".join(spec.get('responsibilities', []))
            lines.append(f"- {spec['name']}: {resp}")
        return "\n".join(lines)
