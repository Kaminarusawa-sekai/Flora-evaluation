"""
能力晋升器 - 将多个原子能力晋升为组合能力
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.llm_client import LLMClient
from .capability_unit_registry import CapabilityUnitRegistry

logger = get_logger(__name__)


class CapabilityPromoter:
    """能力晋升器"""

    def __init__(self, registry: CapabilityUnitRegistry, llm_client: LLMClient):
        self.registry = registry
        self.llm_client = llm_client

    def promote_capabilities(
        self,
        atomic_caps: List[str],
        target_agent_level: str,
        agent_name: str = None
    ) -> str:
        """
        将原子能力晋升为组合能力

        Args:
            atomic_caps: 原子能力 ID 列表
            target_agent_level: 目标 Agent 层级
            agent_name: Agent 名称

        Returns:
            晋升后的组合能力 ID
        """
        logger.info(f"Promoting {len(atomic_caps)} atomic capabilities for {target_agent_level}")

        # 1. 语义聚类
        clusters = self._semantic_cluster(atomic_caps)

        # 2. LLM 生成抽象描述
        composed_cap_id = self._generate_composed_capability(
            clusters[0] if clusters else atomic_caps,  # 使用第一个聚类
            target_agent_level,
            agent_name
        )

        return composed_cap_id

    def _semantic_cluster(self, cap_ids: List[str]) -> List[List[str]]:
        """
        语义聚类 - 将相关的原子能力分组

        Args:
            cap_ids: 能力 ID 列表

        Returns:
            聚类结果 [[cap_id1, cap_id2], [cap_id3, cap_id4], ...]
        """
        # 获取能力详情
        capabilities = []
        for cap_id in cap_ids:
            unit = self.registry.get_unit(cap_id)
            if unit:
                capabilities.append({
                    "id": cap_id,
                    "name": unit['name'],
                    "apis": unit.get('underlying_apis', [])
                })

        if not capabilities:
            return []

        # 使用 LLM 进行聚类
        cap_text = "\n".join([f"- {cap['name']}: {', '.join(cap['apis'])}"
                             for cap in capabilities])

        prompt = f"""将以下能力按照业务相关性进行聚类分组：

{cap_text}

返回 JSON 格式：
{{
  "clusters": [
    {{
      "cluster_name": "聚类名称",
      "capability_names": ["能力1", "能力2"]
    }}
  ]
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务分析专家。"},
                {"role": "user", "content": prompt}
            ])

            # 转换为 ID 列表
            clusters = []
            for cluster in response.get('clusters', []):
                cap_names = set(cluster['capability_names'])
                cluster_ids = [cap['id'] for cap in capabilities
                             if cap['name'] in cap_names]
                if cluster_ids:
                    clusters.append(cluster_ids)

            logger.info(f"Clustered into {len(clusters)} groups")
            return clusters

        except Exception as e:
            logger.warning(f"Clustering failed: {e}, using single cluster")
            return [cap_ids]

    def _generate_composed_capability(
        self,
        atomic_cap_ids: List[str],
        target_level: str,
        agent_name: str = None
    ) -> str:
        """
        生成组合能力

        Args:
            atomic_cap_ids: 原子能力 ID 列表
            target_level: 目标层级
            agent_name: Agent 名称

        Returns:
            组合能力 ID
        """
        # 获取能力详情
        cap_details = []
        for cap_id in atomic_cap_ids:
            unit = self.registry.get_unit(cap_id)
            if unit:
                cap_details.append({
                    "name": unit['name'],
                    "apis": unit.get('underlying_apis', [])
                })

        cap_text = "\n".join([f"- {cap['name']}: {', '.join(cap['apis'])}"
                             for cap in cap_details])

        prompt = f"""将以下原子能力组合成一个高阶能力，适合"{target_level}"层级使用：

{cap_text}

请生成：
1. 组合能力的名称
2. 语义化的描述
3. 能力的编排逻辑（如何协调这些原子能力）

返回 JSON 格式：
{{
  "name": "组合能力名称",
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
            composed_cap_id = self.registry.register_composed_capability(
                name=response['name'],
                composed_of=atomic_cap_ids,
                semantic_description=response['description'],
                orchestration_logic=response.get('orchestration', ''),
                owner=agent_name
            )

            logger.info(f"Generated composed capability: {response['name']}")
            return composed_cap_id

        except Exception as e:
            logger.error(f"Failed to generate composed capability: {e}")
            # 降级策略：创建简单的组合
            fallback_name = f"组合能力_{len(atomic_cap_ids)}项"
            return self.registry.register_composed_capability(
                name=fallback_name,
                composed_of=atomic_cap_ids,
                semantic_description="自动组合的能力",
                owner=agent_name
            )

    def batch_promote(
        self,
        agents: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        批量晋升能力

        Args:
            agents: Agent 列表

        Returns:
            {agent_id: [composed_capability_ids]}
        """
        promotions = {}

        for agent in agents:
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']
            level = agent['level']

            # 只为主管及以上层级晋升能力
            if level not in ['supervisor', 'manager', 'director']:
                continue

            # 收集原子能力
            interface = agent.get('capability_interface', {})
            atomic_caps = [cap['unit_id'] for cap in
                          interface.get('direct_capabilities', [])
                          if self.registry.get_unit(cap['unit_id'])['level'] == 'atomic']

            if atomic_caps:
                composed_cap_id = self.promote_capabilities(
                    atomic_caps,
                    level,
                    agent_name
                )

                promotions[agent_id] = [composed_cap_id]

        logger.info(f"Batch promoted capabilities for {len(promotions)} agents")
        return promotions
