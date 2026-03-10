"""
语义对齐引擎 - 将 API 能力对齐到职能角色
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Tuple
import numpy as np
from shared.logger import get_logger
from shared.llm_client import LLMClient
from shared.vector_store import VectorStore

logger = get_logger(__name__)


class SemanticAlignmentEngine:
    """语义对齐引擎"""

    def __init__(self, llm_client: LLMClient, vector_store: VectorStore):
        self.llm_client = llm_client
        self.vector_store = vector_store

    def align_capabilities_to_roles(
        self,
        api_capabilities: List[Dict[str, Any]],
        roles: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        将 API 能力对齐到角色

        Args:
            api_capabilities: API 能力列表
            roles: 角色列表

        Returns:
            {
                "role_id": [api1, api2, ...],
                ...
            }
        """
        logger.info(f"Aligning {len(api_capabilities)} APIs to {len(roles)} roles")

        # 阶段1: 向量粗筛
        coarse_matches = self._vector_coarse_matching(api_capabilities, roles)

        # 阶段2: LLM 终审
        final_matches = self._llm_fine_matching(coarse_matches, roles)

        logger.info(f"Alignment completed")
        return final_matches

    def _vector_coarse_matching(
        self,
        api_capabilities: List[Dict[str, Any]],
        roles: List[Dict[str, Any]],
        top_k: int = 3,
        threshold: float = 0.6
    ) -> Dict[str, List[Tuple[Dict[str, Any], float]]]:
        """向量粗筛 - 使用 embedding 相似度"""
        logger.info("Phase 1: Vector-based coarse matching")

        # 生成角色的 embeddings
        role_embeddings = []
        for role in roles:
            role_text = self._role_to_text(role)
            embedding = self.llm_client.generate_embedding(role_text)
            role_embeddings.append(embedding)

        # 为每个 API 找到最相似的角色
        coarse_matches = {role['role_name']: [] for role in roles}

        for api in api_capabilities:
            api_text = self._api_to_text(api)
            api_embedding = self.llm_client.generate_embedding(api_text)

            # 计算与所有角色的相似度
            similarities = []
            for i, role_emb in enumerate(role_embeddings):
                similarity = self._cosine_similarity(api_embedding, role_emb)
                similarities.append((i, similarity))

            # 取 top_k 个最相似的角色
            similarities.sort(key=lambda x: x[1], reverse=True)
            for role_idx, sim in similarities[:top_k]:
                if sim >= threshold:
                    role_name = roles[role_idx]['role_name']
                    coarse_matches[role_name].append((api, sim))

        # 记录统计
        for role_name, matches in coarse_matches.items():
            logger.info(f"  {role_name}: {len(matches)} candidate APIs")

        return coarse_matches

    def _llm_fine_matching(
        self,
        coarse_matches: Dict[str, List[Tuple[Dict[str, Any], float]]],
        roles: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """LLM 终审 - 基于业务逻辑推理"""
        logger.info("Phase 2: LLM-based fine matching")

        final_matches = {}

        for role in roles:
            role_name = role['role_name']
            candidates = coarse_matches.get(role_name, [])

            if not candidates:
                final_matches[role_name] = []
                continue

            # 使用 LLM 判断哪些 API 真正属于这个角色
            confirmed_apis = self._llm_confirm_apis(role, candidates)
            final_matches[role_name] = confirmed_apis

            logger.info(f"  {role_name}: {len(confirmed_apis)} confirmed APIs")

        return final_matches

    def _llm_confirm_apis(
        self,
        role: Dict[str, Any],
        candidates: List[Tuple[Dict[str, Any], float]]
    ) -> List[Dict[str, Any]]:
        """使用 LLM 确认 API 是否属于角色"""
        role_name = role['role_name']
        responsibilities = role.get('responsibilities', [])
        required_caps = role.get('required_capabilities', [])

        # 构建候选 API 列表
        api_list = []
        for api, sim in candidates[:10]:  # 限制数量
            api_list.append(f"- {api.get('name', 'Unknown')}: {api.get('description', '')}")

        api_text = "\n".join(api_list)

        prompt = f"""判断以下 API 是否应该分配给"{role_name}"角色。

角色职责：
{', '.join(responsibilities)}

必需能力：
{', '.join(required_caps)}

候选 API：
{api_text}

请返回 JSON 格式，列出应该分配的 API 名称和理由：
{{
  "assigned_apis": [
    {{
      "api_name": "API名称",
      "reason": "分配理由"
    }}
  ]
}}
"""

        try:
            import json
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务流程分析专家。"},
                {"role": "user", "content": prompt}
            ])

            assigned_names = {item['api_name'] for item in response.get('assigned_apis', [])}

            # 过滤出确认的 API
            confirmed = []
            for api, sim in candidates:
                if api.get('name') in assigned_names:
                    confirmed.append(api)

            return confirmed

        except Exception as e:
            logger.warning(f"LLM confirmation failed for {role_name}: {e}")
            # 降级策略：使用相似度阈值
            return [api for api, sim in candidates if sim >= 0.75]

    def _role_to_text(self, role: Dict[str, Any]) -> str:
        """将角色转换为文本描述"""
        parts = [
            f"角色: {role['role_name']}",
            f"职责: {', '.join(role.get('responsibilities', []))}",
            f"必需能力: {', '.join(role.get('required_capabilities', []))}"
        ]
        return " | ".join(parts)

    def _api_to_text(self, api: Dict[str, Any]) -> str:
        """将 API 转换为文本描述"""
        parts = [
            f"API: {api.get('name', 'Unknown')}",
            f"描述: {api.get('description', '')}",
            f"标签: {', '.join(api.get('tags', []))}"
        ]
        return " | ".join(parts)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
