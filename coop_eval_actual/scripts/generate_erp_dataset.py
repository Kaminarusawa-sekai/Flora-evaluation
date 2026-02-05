"""
生成 ERP 场景的测试数据集

基于 records (2).json 的树形 Agent 结构，生成真实的 ERP 业务任务。
"""
import json
import random
from typing import Dict, List, Any
from pathlib import Path


def load_agents(records_path: str) -> List[Dict[str, Any]]:
    """加载 Agent 记录"""
    import re

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


def build_tree(agents: List[Dict]) -> Dict[str, List[str]]:
    """构建父子关系映射"""
    children_map = {}
    for agent in agents:
        parent = agent.get("parent_id", "")
        if parent and parent.strip():
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(agent["agent_id"])
    return children_map


def get_leaf_agents(agents: List[Dict], children_map: Dict) -> List[Dict]:
    """获取叶子节点"""
    return [a for a in agents if a["agent_id"] not in children_map]


def generate_task_path(agent_id: str, agents: List[Dict], children_map: Dict, depth: int = 3) -> List[str]:
    """
    从某个节点开始，生成一条执行路径（模拟真实业务流程）
    """
    agent_map = {a["agent_id"]: a for a in agents}
    path = [agent_id]

    current = agent_id
    for _ in range(depth - 1):
        # 找同级或相关的节点
        parent = agent_map.get(current, {}).get("parent_id", "")
        if parent and parent in children_map:
            siblings = [s for s in children_map[parent] if s != current and s not in path]
            if siblings:
                next_agent = random.choice(siblings)
                path.append(next_agent)
                current = next_agent

    return path


# ERP 业务场景模板
ERP_TASK_TEMPLATES = [
    # 产品管理场景
    {
        "template": "请帮我完成产品管理任务：{steps}",
        "domain": "erp_product_system",
        "steps_templates": [
            "制定产品年度规划",
            "进行市场调研分析",
            "管理产品生命周期",
            "设置产品定价策略",
            "维护SKU主数据",
        ]
    },
    # 销售管理场景
    {
        "template": "请处理以下销售业务：{steps}",
        "domain": "erp_sales_system",
        "steps_templates": [
            "分解销售目标",
            "管理客户关系",
            "处理销售订单",
            "进行应收账款对账",
            "审批特殊价格申请",
        ]
    },
    # 供应链场景
    {
        "template": "请执行供应链管理流程：{steps}",
        "domain": "erp_supply_chain_system",
        "steps_templates": [
            "制定需求计划",
            "管理采购订单",
            "处理入库出库",
            "进行库存盘点",
            "协调物流配送",
        ]
    },
    # 财务场景
    {
        "template": "请完成财务处理任务：{steps}",
        "domain": "erp_finance_system",
        "steps_templates": [
            "处理付款申请",
            "进行收款确认",
            "生成财务凭证",
            "进行账务核对",
        ]
    },
]


def generate_erp_dataset(agents: List[Dict], num_tasks: int = 50) -> List[Dict]:
    """生成 ERP 测试数据集"""
    children_map = build_tree(agents)
    leaf_agents = get_leaf_agents(agents, children_map)
    agent_map = {a["agent_id"]: a for a in agents}

    # 按域分组叶子节点
    domain_leaves = {}
    for leaf in leaf_agents:
        # 从 agent_id 提取域
        parts = leaf["agent_id"].split("__")
        if parts:
            domain = parts[0]
            if domain not in domain_leaves:
                domain_leaves[domain] = []
            domain_leaves[domain].append(leaf)

    dataset = []
    task_id = 1

    for _ in range(num_tasks):
        # 随机选择场景模板
        template_info = random.choice(ERP_TASK_TEMPLATES)
        domain = template_info["domain"]

        # 获取该域的叶子节点
        available_leaves = domain_leaves.get(domain, leaf_agents)
        if len(available_leaves) < 2:
            available_leaves = leaf_agents

        # 随机选择 2-5 个叶子节点作为期望执行的 agents
        num_agents = random.randint(2, min(5, len(available_leaves)))
        selected_agents = random.sample(available_leaves, num_agents)
        expected_agents = [a["agent_id"] for a in selected_agents]

        # 生成任务描述
        steps = random.sample(template_info["steps_templates"], min(num_agents, len(template_info["steps_templates"])))
        steps_text = "、".join([f"{i+1}) {s}" for i, s in enumerate(steps)])
        prompt = template_info["template"].format(steps=steps_text)

        dataset.append({
            "task_id": task_id,
            "level": num_agents,  # 用 agent 数量作为复杂度级别
            "prompt": prompt,
            "expected_agents": expected_agents,
            "domain": domain,
        })
        task_id += 1

    return dataset


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate ERP test dataset")
    parser.add_argument("--records", default="records (2).json", help="Agent records path")
    parser.add_argument("--output", default="coop_eval_actual/data/dataset_erp.json", help="Output path")
    parser.add_argument("--num_tasks", type=int, default=50, help="Number of tasks to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Loading agents from {args.records}...")
    agents = load_agents(args.records)
    print(f"Loaded {len(agents)} agents")

    print(f"Generating {args.num_tasks} tasks...")
    dataset = generate_erp_dataset(agents, args.num_tasks)

    # 保存
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(dataset)} tasks")
    print(f"Output: {args.output}")

    # 打印样例
    print("\n--- Sample Tasks ---")
    for task in dataset[:3]:
        print(f"Task {task['task_id']} (level={task['level']}):")
        print(f"  Prompt: {task['prompt'][:80]}...")
        print(f"  Expected: {task['expected_agents'][:2]}...")
        print()


if __name__ == "__main__":
    main()
