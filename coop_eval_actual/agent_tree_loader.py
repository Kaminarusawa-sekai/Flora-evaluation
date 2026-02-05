import json
import re
from typing import Dict, List, Optional


class MemoryAgentStructure:
    def __init__(self) -> None:
        self.agents: List[Dict[str, object]] = []
        self.relationships: Dict[str, Dict[str, object]] = {}

    def load_all_agents(self) -> List[Dict[str, object]]:
        return list(self.agents)

    def get_agent_relationship(self, agent_id: str) -> Dict[str, object]:
        return self.relationships.get(agent_id, {"parent": None, "children": []})

    def add_agent(self, node: Dict[str, object]) -> None:
        self.agents.append(node)

    def add_relationship(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self.relationships:
            self.relationships[parent_id] = {"parent": None, "children": []}
        if child_id not in self.relationships:
            self.relationships[child_id] = {"parent": None, "children": []}
        if child_id not in self.relationships[parent_id]["children"]:
            self.relationships[parent_id]["children"].append(child_id)
        self.relationships[child_id]["parent"] = parent_id


def _normalize_properties(props: Dict[str, object]) -> Dict[str, object]:
    agent_id = props.get("id") or props.get("agent_id")
    name = props.get("name") or ""
    capability = props.get("capability") or ""
    datascope = props.get("datascope") or ""
    dify = props.get("dify") or ""
    seq = props.get("seq") or 0
    parent_id = props.get("parent_id") or props.get("parentId")

    node = {
        "agent_id": agent_id,
        "name": name,
        "description": capability,
        "capability": capability,
        "datascope": datascope,
        "dify": dify,
        "seq": seq,
        "parent_id": parent_id,
    }
    return node


def load_agent_records(records_path: str) -> List[Dict[str, object]]:
    """加载 Agent 记录，支持多种编码格式"""
    # 尝试不同的编码方式
    content = None
    for encoding in ["utf-8-sig", "utf-8", "gbk"]:
        try:
            with open(records_path, "rb") as handle:
                raw = handle.read()
            content = raw.decode(encoding, errors="replace")
            break
        except Exception:
            continue

    if content is None:
        raise ValueError(f"Failed to read file: {records_path}")

    # 清理控制字符（可能导致 JSON 解析失败）
    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")

    nodes: List[Dict[str, object]] = []
    for item in data:
        props = item.get("n", {}).get("properties", {})
        node = _normalize_properties(props)
        if node.get("agent_id"):
            nodes.append(node)

    # 标记叶子节点
    _mark_leaf_nodes(nodes)

    return nodes


def _mark_leaf_nodes(nodes: List[Dict[str, object]]) -> None:
    """标记叶子节点（没有子节点的节点）"""
    # 收集所有 parent_id
    parent_ids = set()
    for node in nodes:
        parent_id = node.get("parent_id")
        if parent_id and str(parent_id).strip():
            parent_ids.add(parent_id)

    # 标记叶子节点
    for node in nodes:
        agent_id = node.get("agent_id")
        node["is_leaf"] = agent_id not in parent_ids


def load_agents_into_tree(records_path: str, tree_manager) -> List[Dict[str, object]]:
    nodes = load_agent_records(records_path)
    structure = MemoryAgentStructure()

    node_map: Dict[str, Dict[str, object]] = {}
    for node in nodes:
        node_map[node["agent_id"]] = node
        structure.add_agent(node)

    for node in nodes:
        parent_id = node.get("parent_id")
        if parent_id:
            structure.add_relationship(parent_id, node["agent_id"])

    for node in nodes:
        children = structure.get_agent_relationship(node["agent_id"]).get("children", [])
        node["is_leaf"] = len(children) == 0

    tree_manager.node_service.structure = structure
    tree_manager.relationship_service.structure = structure
    tree_manager.node_service.node_cache = {}
    tree_manager.node_service.all_nodes_cache = None
    tree_manager.relationship_service.relationship_cache = {}
    tree_manager.actor_refs = {}

    return nodes


def get_root_agents(nodes: List[Dict[str, object]]) -> List[str]:
    roots: List[str] = []
    for node in nodes:
        if not node.get("parent_id"):
            roots.append(node["agent_id"])
    return roots
