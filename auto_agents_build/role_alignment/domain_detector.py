"""
领域探测器 - 分析 API 聚类结果，识别主导领域
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Tuple
import json
from collections import Counter
from shared.logger import get_logger
from shared.llm_client import LLMClient
from .functional_meta_library import FunctionalMetaLibrary


logger = get_logger(__name__)


class DomainDetector:
    """领域探测器"""

    def __init__(self, meta_library: FunctionalMetaLibrary, llm_client: LLMClient):
        self.meta_library = meta_library
        self.llm_client = llm_client

    def detect_domains(self, api_capabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        探测 API 所属的领域

        Args:
            api_capabilities: API 能力列表，来自 Layer 1

        Returns:
            {
                "primary_domain": "CRM",
                "secondary_domains": ["Finance"],
                "domain_weights": {"CRM": 0.7, "Finance": 0.3},
                "unmatched_apis": [...]
            }
        """
        logger.info(f"Detecting domains for {len(api_capabilities)} APIs")

        # 阶段1: 关键词统计
        keyword_scores = self._keyword_matching(api_capabilities)

        # 阶段2: LLM 语义分析
        llm_scores = self._llm_semantic_analysis(api_capabilities)

        # 合并分数
        combined_scores = self._combine_scores(keyword_scores, llm_scores)

        # 确定主导领域和次要领域
        primary_domain, secondary_domains = self._determine_domains(combined_scores)

        # 识别未匹配的 API
        unmatched_apis = self._find_unmatched_apis(api_capabilities, combined_scores)

        result = {
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "domain_weights": combined_scores,
            "unmatched_apis": unmatched_apis
        }

        logger.info(f"Detected primary domain: {primary_domain}")
        logger.info(f"Secondary domains: {secondary_domains}")

        return result

    def _keyword_matching(self, api_capabilities: List[Dict[str, Any]]) -> Dict[str, float]:
        """关键词匹配统计"""
        domain_scores = Counter()

        for api in api_capabilities:
            api_text = f"{api.get('name', '')} {api.get('description', '')} {' '.join(api.get('tags', []))}"
            api_text = api_text.lower()

            # 匹配每个领域的关键词
            for domain_name in self.meta_library.get_all_domains():
                domain = self.meta_library.get_domain(domain_name)
                keywords = domain.get('keywords', [])

                # 计算匹配的关键词数量
                matches = sum(1 for keyword in keywords if keyword in api_text)
                if matches > 0:
                    domain_scores[domain_name] += matches

        # 归一化分数
        total = sum(domain_scores.values())
        if total > 0:
            return {domain: score / total for domain, score in domain_scores.items()}
        else:
            return {}

    def _llm_semantic_analysis(self, api_capabilities: List[Dict[str, Any]]) -> Dict[str, float]:
        """LLM 语义分析"""
        # 构建 API 摘要
        api_summary = []
        for api in api_capabilities[:20]:  # 限制数量以控制 token
            api_summary.append(f"- {api.get('name', 'Unknown')}: {api.get('description', '')}")

        api_text = "\n".join(api_summary)

        # 获取所有领域
        domains = self.meta_library.get_all_domains()
        domain_descriptions = {}
        for domain_name in domains:
            domain = self.meta_library.get_domain(domain_name)
            domain_descriptions[domain_name] = domain.get('domain_name', domain_name)

        # LLM 分析
        prompt = f"""分析以下 API 列表，判断它们主要属于哪些业务领域。

            可选领域：
            {json.dumps(domain_descriptions, ensure_ascii=False, indent=2)}

            API 列表：
            {api_text}

            请返回 JSON 格式，包含每个领域的权重（0-1之间，总和为1）：
            {{
            "domain_weights": {{
                "CRM": 0.6,
                "Finance": 0.3,
                "HR": 0.1
            }},
            "reasoning": "分析理由"
            }}
            """

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务领域分析专家。"},
                {"role": "user", "content": prompt}
            ])

            domain_weights = response.get('domain_weights', {})
            logger.info(f"LLM analysis reasoning: {response.get('reasoning', 'N/A')}")

            return domain_weights

        except Exception as e:
            logger.warning(f"LLM semantic analysis failed: {e}")
            return {}

    def _combine_scores(
        self,
        keyword_scores: Dict[str, float],
        llm_scores: Dict[str, float],
        keyword_weight: float = 0.3,
        llm_weight: float = 0.7
    ) -> Dict[str, float]:
        """合并关键词和 LLM 分数"""
        all_domains = set(keyword_scores.keys()) | set(llm_scores.keys())

        combined = {}
        for domain in all_domains:
            kw_score = keyword_scores.get(domain, 0)
            llm_score = llm_scores.get(domain, 0)
            combined[domain] = kw_score * keyword_weight + llm_score * llm_weight

        # 归一化
        total = sum(combined.values())
        if total > 0:
            combined = {domain: score / total for domain, score in combined.items()}

        return combined

    def _determine_domains(
        self,
        domain_scores: Dict[str, float],
        primary_threshold: float = 0.4,
        secondary_threshold: float = 0.15
    ) -> Tuple[str, List[str]]:
        """确定主导领域和次要领域"""
        if not domain_scores:
            return "Unknown", []

        # 按分数排序
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        # 主导领域
        primary_domain = sorted_domains[0][0]

        # 次要领域
        secondary_domains = [
            domain for domain, score in sorted_domains[1:]
            if score >= secondary_threshold
        ]

        return primary_domain, secondary_domains

    def _find_unmatched_apis(
        self,
        api_capabilities: List[Dict[str, Any]],
        domain_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """识别未匹配到任何领域的 API"""
        # 如果有明确的领域匹配，则认为所有 API 都已匹配
        if domain_scores:
            return []

        # 否则返回所有 API
        return api_capabilities
