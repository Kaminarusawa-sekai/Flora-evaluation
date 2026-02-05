import argparse
import json
import random
from typing import Dict, List

from coop_eval_actual.agent_tree_loader import load_agent_records


LEVEL_COUNTS = {1: 20, 3: 30, 5: 30, 8: 20}


def _pick_agents(rng: random.Random, agent_ids: List[str], count: int) -> List[str]:
    if len(agent_ids) >= count:
        return rng.sample(agent_ids, count)
    selected = []
    for _ in range(count):
        selected.append(rng.choice(agent_ids))
    return selected


def _build_prompt(agent_ids: List[str], agent_name_map: Dict[str, str]) -> str:
    if len(agent_ids) == 1:
        agent_id = agent_ids[0]
        agent_name = agent_name_map.get(agent_id, agent_id)
        return (
            f"请调用代理 {agent_name} 完成任务。[agent:{agent_id}]"
        )

    steps = []
    for idx, agent_id in enumerate(agent_ids, start=1):
        agent_name = agent_name_map.get(agent_id, agent_id)
        steps.append(f"{idx}) {agent_name} [agent:{agent_id}]")
    steps_text = "；".join(steps)
    return f"请按顺序执行以下步骤：{steps_text}。"


def _compute_leaf_nodes(nodes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    children_map: Dict[str, List[str]] = {}
    for node in nodes:
        parent_id = node.get("parent_id")
        if parent_id:
            children_map.setdefault(parent_id, []).append(node["agent_id"])

    leaf_nodes = []
    for node in nodes:
        if node.get("agent_id") not in children_map:
            leaf_nodes.append(node)
    return leaf_nodes


def generate_dataset(records_path: str, seed: int) -> List[Dict[str, object]]:
    nodes = load_agent_records(records_path)
    leaf_nodes = _compute_leaf_nodes(nodes)
    if not leaf_nodes:
        leaf_nodes = nodes

    agent_name_map = {n["agent_id"]: n.get("name") or n["agent_id"] for n in nodes}
    agent_ids = [n["agent_id"] for n in leaf_nodes if n.get("agent_id")]

    rng = random.Random(seed)
    tasks: List[Dict[str, object]] = []
    task_id = 1

    for level, count in LEVEL_COUNTS.items():
        for _ in range(count):
            expected_agents = _pick_agents(rng, agent_ids, level)
            prompt = _build_prompt(expected_agents, agent_name_map)
            tasks.append({
                "task_id": task_id,
                "level": level,
                "prompt": prompt,
                "expected_agents": expected_agents,
            })
            task_id += 1

    rng.shuffle(tasks)
    for idx, task in enumerate(tasks, start=1):
        task["task_id"] = idx

    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dataset for COOP evaluation (actual run).")
    parser.add_argument("--records", default="records (1)(4)(1).json", help="Agent records JSON path")
    parser.add_argument("--output", default="coop_eval_actual/data/dataset.json", help="Output dataset JSON")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    dataset = generate_dataset(args.records, args.seed)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(dataset, handle, indent=2, ensure_ascii=True)

    print(f"Wrote {len(dataset)} tasks to {args.output}")


if __name__ == "__main__":
    main()
