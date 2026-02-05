"""
生成自然语言数据集（去除 [agent:xxx] 标签）

用于真实 LLM 规划实验，让各策略真正进行规划决策，而不是直接提取答案。
"""
import json
import re
import argparse
from pathlib import Path


AGENT_TAG_PATTERN = re.compile(r"\s*\[agent:[a-zA-Z0-9_\-]+\]")


def remove_agent_tags(text: str) -> str:
    """移除文本中的 [agent:xxx] 标签"""
    return AGENT_TAG_PATTERN.sub("", text).strip()


def clean_prompt(prompt: str) -> str:
    """
    清理 prompt，移除标签并优化格式

    示例:
    输入: "请按顺序执行以下步骤：1) 制定标签规则 [agent:define_tag_rules]；2) 用户分层 [agent:user_strat]"
    输出: "请按顺序执行以下步骤：1) 制定标签规则；2) 用户分层"
    """
    cleaned = remove_agent_tags(prompt)
    # 清理多余的空格和标点
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'；\s*；', '；', cleaned)
    cleaned = re.sub(r'。\s*。', '。', cleaned)
    return cleaned.strip()


def generate_natural_dataset(input_path: str, output_path: str) -> None:
    """
    从原始数据集生成自然语言版本

    Args:
        input_path: 原始数据集路径 (含 [agent:xxx] 标签)
        output_path: 输出数据集路径 (自然语言)
    """
    with open(input_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    natural_dataset = []
    for task in dataset:
        original_prompt = task.get("prompt", "")
        natural_prompt = clean_prompt(original_prompt)

        natural_task = {
            "task_id": task.get("task_id"),
            "level": task.get("level"),
            "prompt": natural_prompt,
            "original_prompt": original_prompt,  # 保留原始 prompt 用于调试
            "expected_agents": task.get("expected_agents", []),
        }
        natural_dataset.append(natural_task)

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(natural_dataset, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(natural_dataset)} tasks")
    print(f"Output: {output_path}")

    # 打印示例
    if natural_dataset:
        sample = natural_dataset[0]
        print(f"\n--- Sample ---")
        print(f"Original: {sample['original_prompt'][:100]}...")
        print(f"Natural:  {sample['prompt'][:100]}...")


def main():
    parser = argparse.ArgumentParser(description="Generate natural language dataset")
    parser.add_argument(
        "--input",
        default="coop_eval_actual/data/dataset.json",
        help="Input dataset path (with agent tags)"
    )
    parser.add_argument(
        "--output",
        default="coop_eval_actual/data/dataset_natural.json",
        help="Output dataset path (natural language)"
    )
    args = parser.parse_args()

    generate_natural_dataset(args.input, args.output)


if __name__ == "__main__":
    main()
