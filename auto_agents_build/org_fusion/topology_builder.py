"""
拓扑结构构建器 - 构建基于图的组织拓扑
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from shared.logger import get_logger

logger = get_logger(__name__)


class TopologyBuilder:
    """拓扑结构构建器"""

    def __init__(self):
        self.nodes = []
        self.edges = []

    def build_topology(
        self,
        agents: List[Dict[str, Any]],
        registry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构建组织拓扑

        Args:
            agents: Agent 列表
            registry_data: 能力注册表数据

        Returns:
            拓扑结构
        """
        logger.info("Building organization topology")

        # 1. 创建 Agent 节点
        self._create_agent_nodes(agents)

        # 2. 创建 Capability 节点
        self._create_capability_nodes(registry_data)

        # 3. 创建关系边
        self._create_relationships(agents)

        topology = {
            "nodes": self.nodes,
            "edges": self.edges,
            "statistics": self._calculate_statistics()
        }

        logger.info(f"Topology built: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return topology

    def _create_agent_nodes(self, agents: List[Dict[str, Any]]):
        """创建 Agent 节点"""
        for agent in agents:
            node = {
                "id": agent['agent_id'],
                "type": "Agent",
                "label": agent['agent_name'],
                "properties": {
                    "level": agent['level'],
                    "is_virtual": agent.get('is_virtual', False),
                    "responsibilities": agent.get('responsibilities', [])
                }
            }
            self.nodes.append(node)

    def _create_capability_nodes(self, registry_data: Dict[str, Any]):
        """创建 Capability 节点"""
        all_capabilities = (
            registry_data.get('atomic_capabilities', []) +
            registry_data.get('composed_capabilities', []) +
            registry_data.get('strategic_capabilities', [])
        )

        for cap in all_capabilities:
            node = {
                "id": cap['unit_id'],
                "type": "Capability",
                "label": cap['name'],
                "properties": {
                    "level": cap['level'],
                    "ref_count": cap.get('ref_count', 0),
                    "owner": cap.get('owner')
                }
            }
            self.nodes.append(node)

    def _create_relationships(self, agents: List[Dict[str, Any]]):
        """创建关系边"""
        for agent in agents:
            agent_id = agent['agent_id']

            # 1. Agent -> Capability (REFERENCES)
            interface = agent.get('capability_interface', {})
            all_caps = (
                interface.get('direct_capabilities', []) +
                interface.get('composed_capabilities', []) +
                interface.get('delegated_capabilities', [])
            )

            for cap_ref in all_caps:
                edge = {
                    "source": agent_id,
                    "target": cap_ref['unit_id'],
                    "type": "REFERENCES",
                    "properties": {
                        "access_mode": cap_ref.get('access_mode', 'execute'),
                        "priority": cap_ref.get('priority', 'medium')
                    }
                }
                self.edges.append(edge)

            # 2. Agent -> Agent (MANAGES)
            for subordinate_id in agent.get('subordinates', []):
                edge = {
                    "source": agent_id,
                    "target": subordinate_id,
                    "type": "MANAGES",
                    "properties": {}
                }
                self.edges.append(edge)

    def _calculate_statistics(self) -> Dict[str, Any]:
        """计算拓扑统计"""
        agent_nodes = [n for n in self.nodes if n['type'] == 'Agent']
        cap_nodes = [n for n in self.nodes if n['type'] == 'Capability']

        references_edges = [e for e in self.edges if e['type'] == 'REFERENCES']
        manages_edges = [e for e in self.edges if e['type'] == 'MANAGES']

        return {
            "total_nodes": len(self.nodes),
            "agent_nodes": len(agent_nodes),
            "capability_nodes": len(cap_nodes),
            "total_edges": len(self.edges),
            "reference_edges": len(references_edges),
            "management_edges": len(manages_edges)
        }

    def infer_hierarchy(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        推断层级关系

        Args:
            agents: Agent 列表

        Returns:
            更新后的 Agent 列表（包含 subordinates）
        """
        logger.info("Inferring agent hierarchy")

        # 按层级分组
        agents_by_level = {}
        for agent in agents:
            level = agent['level']
            if level not in agents_by_level:
                agents_by_level[level] = []
            agents_by_level[level].append(agent)

        # 定义层级顺序
        level_order = ['specialist', 'supervisor', 'manager', 'director', 'ceo']

        # 为每个层级分配下属
        for i, level in enumerate(level_order[:-1]):
            if level not in agents_by_level:
                continue

            # 下一层级
            subordinate_level = level_order[i - 1] if i > 0 else None
            if not subordinate_level or subordinate_level not in agents_by_level:
                continue

            # 简单策略：每个上级管理所有下级
            for agent in agents_by_level[level]:
                agent['subordinates'] = [sub['agent_id'] for sub in agents_by_level[subordinate_level]]

        logger.info("Hierarchy inference completed")
        return agents

    def export_to_neo4j_cypher(self) -> str:
        """导出为 Neo4j Cypher 语句"""
        cypher_statements = []

        # 创建节点
        for node in self.nodes:
            props = ", ".join([f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}"
                             for k, v in node['properties'].items()])
            cypher = f"CREATE (:{node['type']} {{id: '{node['id']}', label: '{node['label']}', {props}}})"
            cypher_statements.append(cypher)

        # 创建关系
        for edge in self.edges:
            props = ", ".join([f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}"
                             for k, v in edge['properties'].items()])
            cypher = f"MATCH (a {{id: '{edge['source']}'}}), (b {{id: '{edge['target']}'}}) CREATE (a)-[:{edge['type']} {{{props}}}]->(b)"
            cypher_statements.append(cypher)

        return "\n".join(cypher_statements)

    def query_shared_capabilities(self, min_ref_count: int = 2) -> List[Dict[str, Any]]:
        """查询被多个 Agent 引用的能力"""
        cap_references = {}

        for edge in self.edges:
            if edge['type'] == 'REFERENCES':
                cap_id = edge['target']
                if cap_id not in cap_references:
                    cap_references[cap_id] = []
                cap_references[cap_id].append(edge['source'])

        shared = []
        for cap_id, agent_ids in cap_references.items():
            if len(agent_ids) >= min_ref_count:
                cap_node = next((n for n in self.nodes if n['id'] == cap_id), None)
                if cap_node:
                    shared.append({
                        "capability": cap_node['label'],
                        "ref_count": len(agent_ids),
                        "agents": [next((n['label'] for n in self.nodes if n['id'] == aid), aid)
                                 for aid in agent_ids]
                    })

        return shared
