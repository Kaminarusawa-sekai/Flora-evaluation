import json
from typing import Dict


def compute_workflow_complexity(config_path: str) -> Dict[str, float]:
    with open(config_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    data = json.loads(content)

    nodes = len(data.get("nodes", []))
    edges = data.get("edges", [])
    branches = sum(1 for edge in edges if edge.get("condition"))
    tool_rules = len(data.get("tool_rules", []))
    config_loc = len(content.splitlines())

    score = nodes * 1.0 + branches * 2.0 + tool_rules * 1.0 + config_loc * 0.1
    return {
        "workflow_complexity_score": round(score, 2),
        "workflow_nodes": nodes,
        "workflow_branches": branches,
        "tool_rules": tool_rules,
        "config_loc": config_loc,
    }
