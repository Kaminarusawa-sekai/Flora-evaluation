"""
内存版 Agent 结构管理器 - 用于评估和测试环境
这个实现独立于 tasks 目录，当 tasks 被替换时不会受影响
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryAgentStructure:
    """
    内存版本的 Agent 结构管理器
    用于开发和测试环境，不依赖 Neo4j
    """

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, List[str]]] = {}
        logger.info("MemoryAgentStructure 初始化完成")

    def get_agent_relationship(self, agent_id: str) -> Dict[str, Any]:
        """获取 Agent 的关系信息"""
        return self.relationships.get(agent_id, {})

    def load_all_agents(self) -> List[Dict[str, Any]]:
        """加载所有 Agent"""
        return list(self.agents.values())

    def close(self):
        """关闭连接（内存版无需操作）"""
        pass

    def add_agent_relationship(self, parent_id: str, child_id: str, relationship_type: str) -> bool:
        """添加 Agent 关系"""
        if parent_id not in self.relationships:
            self.relationships[parent_id] = {'children': []}
        self.relationships[parent_id]['children'].append(child_id)
        return True

    def remove_agent(self, agent_id: str) -> bool:
        """删除 Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
        # 从关系中移除
        for parent_id, rels in list(self.relationships.items()):
            if agent_id in rels.get('children', []):
                rels['children'].remove(agent_id)
            if parent_id == agent_id:
                del self.relationships[parent_id]
        return True
