"""
工具函数模块
"""
import json
import pickle
from typing import Dict, Any, List
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


class ResultSaver:
    """结果保存器"""

    @staticmethod
    def save_optimization_result(result: Dict[str, Any], filepath: str):
        """
        保存优化结果到文件

        Args:
            result: 优化结果字典
            filepath: 保存路径
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # 保存为JSON（可读性好）
        if filepath.suffix == ".json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        # 保存为pickle（保留所有信息）
        elif filepath.suffix == ".pkl":
            with open(filepath, "wb") as f:
                pickle.dump(result, f)

        print(f"结果已保存到: {filepath}")

    @staticmethod
    def load_optimization_result(filepath: str) -> Dict[str, Any]:
        """
        加载优化结果

        Args:
            filepath: 文件路径

        Returns:
            优化结果字典
        """
        filepath = Path(filepath)

        if filepath.suffix == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        elif filepath.suffix == ".pkl":
            with open(filepath, "rb") as f:
                return pickle.load(f)
        else:
            raise ValueError(f"不支持的文件格式: {filepath.suffix}")


class Visualizer:
    """可视化工具"""

    @staticmethod
    def plot_optimization_history(history: Dict[str, List], save_path: str = None):
        """
        绘制优化历史曲线

        Args:
            history: 优化历史字典
            save_path: 保存路径（可选）
        """
        iterations = history["iterations"]
        best_scores = history["best_scores"]

        plt.figure(figsize=(10, 6))
        plt.plot(iterations, best_scores, marker="o", linewidth=2, markersize=8)
        plt.xlabel("迭代次数", fontsize=12)
        plt.ylabel("最佳分数", fontsize=12)
        plt.title("提示词优化过程", fontsize=14, fontweight="bold")
        plt.grid(True, alpha=0.3)

        # 标注最终分数
        final_score = best_scores[-1]
        plt.annotate(
            f"最终: {final_score:.3f}",
            xy=(iterations[-1], final_score),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"图表已保存到: {save_path}")

        plt.show()

    @staticmethod
    def plot_candidates_comparison(
        candidates: List[str], scores: List[float], save_path: str = None
    ):
        """
        绘制候选提示词对比图

        Args:
            candidates: 候选列表
            scores: 分数列表
            save_path: 保存路径
        """
        # 截断长提示词
        labels = [
            f"候选{i+1}\n{c[:30]}..." if len(c) > 30 else f"候选{i+1}\n{c}"
            for i, c in enumerate(candidates)
        ]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(scores)), scores, color="skyblue", edgecolor="navy")

        # 高亮最佳
        best_idx = np.argmax(scores)
        bars[best_idx].set_color("gold")
        bars[best_idx].set_edgecolor("darkgoldenrod")

        plt.xlabel("候选提示词", fontsize=12)
        plt.ylabel("准确率", fontsize=12)
        plt.title("候选提示词性能对比", fontsize=14, fontweight="bold")
        plt.xticks(range(len(candidates)), labels, rotation=45, ha="right")
        plt.ylim(0, 1.0)
        plt.grid(True, axis="y", alpha=0.3)

        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, scores)):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{score:.3f}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"图表已保存到: {save_path}")

        plt.show()


class PromptAnalyzer:
    """提示词分析工具"""

    @staticmethod
    def analyze_prompt_length(prompts: List[str]) -> Dict[str, Any]:
        """分析提示词长度分布"""
        lengths = [len(p.split()) for p in prompts]
        return {
            "mean_length": np.mean(lengths),
            "std_length": np.std(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "lengths": lengths,
        }

    @staticmethod
    def extract_keywords(prompt: str, top_k: int = 10) -> List[str]:
        """
        提取提示词关键词

        简单实现：基于词频
        """
        # 移除常见停用词
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "is",
            "are",
            "was",
            "were",
        }

        words = prompt.lower().split()
        words = [w.strip(".,!?;:") for w in words if w not in stop_words]

        # 计数
        from collections import Counter

        word_counts = Counter(words)
        return [word for word, _ in word_counts.most_common(top_k)]

    @staticmethod
    def compare_prompts(prompt1: str, prompt2: str) -> Dict[str, Any]:
        """
        比较两个提示词的差异

        Returns:
            差异分析结果
        """
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())

        common = words1 & words2
        only_in_1 = words1 - words2
        only_in_2 = words2 - words1

        return {
            "common_words": list(common),
            "unique_to_prompt1": list(only_in_1),
            "unique_to_prompt2": list(only_in_2),
            "similarity": len(common) / len(words1 | words2) if words1 | words2 else 0,
        }


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def generate_markdown_report(result: Dict[str, Any], output_path: str):
        """
        生成Markdown格式的优化报告

        Args:
            result: 优化结果
            output_path: 输出路径
        """
        report_lines = []

        # 标题
        report_lines.append("# 自动提示词优化报告\n")
        report_lines.append(f"生成时间: {__import__('datetime').datetime.now()}\n")

        # 优化摘要
        report_lines.append("\n## 优化摘要\n")
        report_lines.append(f"- **最终分数**: {result['best_score']:.3f}")
        report_lines.append(f"- **迭代次数**: {result['iterations']}")
        report_lines.append(
            f"- **改进幅度**: {result['history']['best_scores'][-1] - result['history']['best_scores'][0]:.3f}"
        )

        # 最佳提示词
        report_lines.append("\n## 最佳提示词\n")
        report_lines.append("```")
        report_lines.append(result["best_prompt"])
        report_lines.append("```\n")

        # 优化历史
        report_lines.append("\n## 优化历史\n")
        report_lines.append("| 迭代 | 最佳分数 |")
        report_lines.append("|------|----------|")
        for i, score in zip(
            result["history"]["iterations"], result["history"]["best_scores"]
        ):
            report_lines.append(f"| {i} | {score:.3f} |")

        # 保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print(f"报告已保存到: {output_path}")


def print_summary(result: Dict[str, Any]):
    """打印优化结果摘要"""
    print("\n" + "=" * 70)
    print(" " * 20 + "优化结果摘要")
    print("=" * 70)

    print(f"\n✓ 最终最佳分数: {result['best_score']:.3f}")
    print(f"✓ 总迭代次数: {result['iterations']}")

    initial_score = result["history"]["best_scores"][0]
    final_score = result["history"]["best_scores"][-1]
    improvement = final_score - initial_score

    print(f"✓ 初始分数: {initial_score:.3f}")

    # 避免除以零
    if initial_score > 0:
        improvement_pct = improvement / initial_score * 100
        print(f"✓ 改进幅度: {improvement:.3f} ({improvement_pct:.1f}%)")
    else:
        print(f"✓ 改进幅度: {improvement:.3f} (从零开始)")


    print("\n最佳提示词:")
    print("-" * 70)
    print(result["best_prompt"])
    print("-" * 70)

    print("\n优化轨迹:")
    for i, score in zip(
        result["history"]["iterations"][:5], result["history"]["best_scores"][:5]
    ):
        print(f"  迭代 {i}: {score:.3f}")
    if len(result["history"]["iterations"]) > 5:
        print("  ...")
        last_i = result["history"]["iterations"][-1]
        last_score = result["history"]["best_scores"][-1]
        print(f"  迭代 {last_i}: {last_score:.3f}")

    print("\n" + "=" * 70)
