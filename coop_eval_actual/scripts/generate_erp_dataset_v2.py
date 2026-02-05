"""
反向生成 ERP 测试数据集

策略：先选择 expected_agents（叶子节点），再用 LLM 生成与之匹配的任务描述。
这样确保任务描述与期望的 agents 语义一致。
"""
import json
import random
import re
import sys
import os
from typing import Dict, List, Any
from pathlib import Path

# 添加 tasks 目录到 path
TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tasks"))
if TASKS_ROOT not in sys.path:
    sys.path.insert(0, TASKS_ROOT)


def load_agents(records_path: str) -> List[Dict[str, Any]]:
    """加载 Agent 记录"""
    with open(records_path, "rb") as f:
        content = f.read().decode("utf-8-sig", errors="replace")
    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
    data = json.loads(content)

    agents = []
    for item in data:
        props = item.get("n", {}).get("properties", {})
        agent_id = props.get("id") or props.get("agent_id")
        if agent_id:
            agents.append({
                "agent_id": agent_id,
                "name": props.get("name", ""),
                "capability": props.get("capability", ""),
                "parent_id": props.get("parent_id", ""),
            })
    return agents


def get_leaf_agents(agents: List[Dict]) -> List[Dict]:
    """获取叶子节点"""
    parent_ids = {a.get("parent_id") for a in agents if a.get("parent_id")}
    return [a for a in agents if a["agent_id"] not in parent_ids]


def generate_task_description(llm, selected_agents: List[Dict]) -> str:
    """用 LLM 根据选中的 agents 生成任务描述"""
    agents_info = "\n".join([
        f"- {a['agent_id']}: {a.get('name', '')} - {a.get('capability', '')[:100]}"
        for a in selected_agents
    ])

    prompt = f"""你是一个任务描述生成器。根据以下 Agent 的能力，生成一个自然的用户任务请求。

## 需要调用的 Agents
{agents_info}

## 要求
1. 生成一个自然的中文任务描述，像用户真实提出的需求
2. 任务描述应该隐含需要调用上述所有 Agent 的能力
3. 不要直接提及 Agent 的 ID 或名称
4. 任务描述应该是一个完整的句子或段落
5. 只输出任务描述，不要其他内容

## 示例
如果 Agents 是：
- erp_product_system__pricing_specialist__price_list_definition__internal_settlement_price
- erp_product_system__sku_master_data_specialist__master_data_entry__create_product

则任务描述可以是：
"请帮我创建一个新产品，并设置其内部结算价格。"

## 输出
"""

    response = llm.generate(prompt)
    return response.strip() if response else "请完成相关任务"


def generate_dataset_reverse(
    records_path: str,
    output_path: str,
    num_tasks: int = 50,
    seed: int = 42
) -> None:
    """反向生成数据集"""
    random.seed(seed)

    print(f"Loading agents from {records_path}...")
    agents = load_agents(records_path)
    leaf_agents = get_leaf_agents(agents)
    print(f"Loaded {len(agents)} agents, {len(leaf_agents)} leaves")

    # 初始化 LLM
    print("Initializing LLM...")
    from capabilities.llm.qwen_llm import QwenLLM
    llm = QwenLLM()
    llm.initialize({})

    dataset = []
    task_id = 1

    print(f"Generating {num_tasks} tasks...")
    for i in range(num_tasks):
        # 随机选择 2-4 个叶子节点
        num_agents = random.randint(2, min(4, len(leaf_agents)))
        selected = random.sample(leaf_agents, num_agents)
        expected_agents = [a["agent_id"] for a in selected]

        # 用 LLM 生成任务描述
        print(f"  [{i+1}/{num_tasks}] Generating task for {num_agents} agents...")
        prompt = generate_task_description(llm, selected)

        dataset.append({
            "task_id": task_id,
            "level": num_agents,
            "prompt": prompt,
            "expected_agents": expected_agents,
        })
        task_id += 1

        # 每 10 个任务保存一次（防止中断丢失）
        if task_id % 10 == 0:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)

    # 最终保存
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(dataset)} tasks")
    print(f"Output: {output_path}")

    # 打印样例
    print("\n--- Sample Tasks ---")
    for task in dataset[:3]:
        print(f"Task {task['task_id']} (level={task['level']}):")
        print(f"  Prompt: {task['prompt'][:80]}...")
        print(f"  Expected: {[a.split('__')[-1] for a in task['expected_agents']]}")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate ERP dataset (reverse)")
    parser.add_argument("--records", default="records (2).json", help="Agent records path")
    parser.add_argument("--output", default="coop_eval_actual/data/dataset_erp_v2.json", help="Output path")
    parser.add_argument("--num_tasks", type=int, default=30, help="Number of tasks")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    generate_dataset_reverse(args.records, args.output, args.num_tasks, args.seed)


if __name__ == "__main__":
    main()
