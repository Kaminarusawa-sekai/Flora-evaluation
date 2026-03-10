"""
RAG 知识链接器 - 为 Agent 关联领域知识库
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.utils import save_json

logger = get_logger(__name__)


class RAGKnowledgeLinker:
    """RAG 知识链接器"""

    def __init__(self):
        # 预定义的领域知识库
        self.domain_knowledge = {
            "CRM": [
                "客户关系管理最佳实践",
                "销售流程标准",
                "客户分级策略"
            ],
            "ERP": [
                "库存管理规范",
                "采购流程标准",
                "供应链优化指南"
            ],
            "Finance": [
                "财务会计准则",
                "税务法规",
                "内部控制规范"
            ],
            "HR": [
                "人力资源管理制度",
                "劳动法规",
                "绩效考核标准"
            ],
            "MES": [
                "ISO9001 质量标准",
                "生产管理规范",
                "设备维护手册"
            ]
        }

    def link_knowledge(
        self,
        agents: List[Dict[str, Any]],
        domain: str
    ) -> Dict[str, Any]:
        """
        为 Agent 链接知识库

        Args:
            agents: Agent 列表
            domain: 主导领域

        Returns:
            知识链接配置
        """
        logger.info(f"Linking knowledge for domain: {domain}")

        knowledge_links = {}

        for agent in agents:
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']

            # 根据 Agent 角色匹配知识库
            knowledge_sources = self._match_knowledge_sources(agent_name, domain)

            # 生成检索策略
            retrieval_strategy = self._generate_retrieval_strategy(agent)

            knowledge_links[agent_id] = {
                "agent_name": agent_name,
                "knowledge_sources": knowledge_sources,
                "retrieval_strategy": retrieval_strategy
            }

        result = {
            "domain": domain,
            "knowledge_links": knowledge_links,
            "global_knowledge": self.domain_knowledge.get(domain, [])
        }

        logger.info(f"Knowledge linked for {len(agents)} agents")
        return result

    def _match_knowledge_sources(self, agent_name: str, domain: str) -> List[Dict[str, str]]:
        """匹配知识源"""
        sources = []

        # 领域通用知识
        domain_knowledge = self.domain_knowledge.get(domain, [])
        for knowledge in domain_knowledge:
            sources.append({
                "type": "domain_knowledge",
                "name": knowledge,
                "path": f"knowledge/{domain}/{knowledge}.md",
                "priority": "medium"
            })

        # 角色特定知识
        role_specific = self._get_role_specific_knowledge(agent_name)
        for knowledge in role_specific:
            sources.append({
                "type": "role_knowledge",
                "name": knowledge,
                "path": f"knowledge/roles/{agent_name}/{knowledge}.md",
                "priority": "high"
            })

        return sources

    def _get_role_specific_knowledge(self, agent_name: str) -> List[str]:
        """获取角色特定知识"""
        role_knowledge_map = {
            "质检员": ["ISO9001标准", "质量检验规范", "不良品处理流程"],
            "会计专员": ["会计准则", "凭证管理规范", "报表编制指南"],
            "采购专员": ["采购管理制度", "供应商评估标准", "合同管理规范"],
            "销售专员": ["销售话术", "客户沟通技巧", "CRM系统使用手册"],
            "HR专员": ["招聘流程", "员工手册", "考勤管理规定"]
        }

        # 模糊匹配
        for role, knowledge in role_knowledge_map.items():
            if role in agent_name:
                return knowledge

        return []

    def _generate_retrieval_strategy(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """生成检索策略"""
        level = agent['level']

        # 基层专员需要详细的操作指南
        if level == 'specialist':
            return {
                "mode": "detailed",
                "top_k": 5,
                "similarity_threshold": 0.7,
                "include_examples": True,
                "context_window": 2000
            }

        # 主管需要概要和决策支持
        elif level == 'supervisor':
            return {
                "mode": "summary",
                "top_k": 3,
                "similarity_threshold": 0.75,
                "include_examples": False,
                "context_window": 1500
            }

        # 高层需要战略性信息
        else:
            return {
                "mode": "strategic",
                "top_k": 2,
                "similarity_threshold": 0.8,
                "include_examples": False,
                "context_window": 1000
            }

    def generate_knowledge_index_config(
        self,
        knowledge_links: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成知识索引配置"""
        all_sources = []

        for agent_id, link_data in knowledge_links.get('knowledge_links', {}).items():
            all_sources.extend(link_data['knowledge_sources'])

        # 去重
        unique_sources = []
        seen = set()
        for source in all_sources:
            key = (source['type'], source['name'])
            if key not in seen:
                seen.add(key)
                unique_sources.append(source)

        return {
            "sources": unique_sources,
            "indexing": {
                "chunk_size": 500,
                "chunk_overlap": 50,
                "embedding_model": "text-embedding-ada-002"
            },
            "storage": {
                "type": "faiss",
                "index_path": "./data/knowledge_index"
            }
        }

    def save_knowledge_links(self, knowledge_links: Dict[str, Any], output_path: str):
        """保存知识链接配置"""
        save_json(knowledge_links, output_path)
        logger.info(f"Knowledge links saved to {output_path}")
