import argparse
import csv
import os
from collections import defaultdict
from typing import Dict, List

import matplotlib.pyplot as plt


def load_summary(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def load_results(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def plot_success_curve(summary_rows: List[Dict[str, str]], output_path: str) -> None:
    levels = [1, 3, 5, 8]
    model_map: Dict[str, Dict[int, float]] = defaultdict(dict)
    for row in summary_rows:
        model = row["model"]
        level = int(row["level"])
        model_map[model][level] = float(row["success_rate"])

    plt.figure(figsize=(6, 4))
    for model, points in sorted(model_map.items()):
        ys = [points.get(level, 0.0) for level in levels]
        plt.plot(levels, ys, marker="o", label=model)
    plt.title("Complexity vs Success Rate")
    plt.xlabel("Task Level")
    plt.ylabel("Success Rate")
    plt.xticks(levels)
    plt.ylim(0, 1.0)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_tokens_level8(summary_rows: List[Dict[str, str]], output_path: str) -> None:
    rows = [row for row in summary_rows if int(row["level"]) == 8]
    rows.sort(key=lambda r: r["model"])
    models = [row["model"] for row in rows]
    tokens = [float(row["avg_tokens_total"]) for row in rows]
    palette = ["#5b8ff9", "#61d9a6", "#f6bd16", "#7262fd"]
    colors = palette[:len(models)]

    plt.figure(figsize=(6, 4))
    plt.bar(models, tokens, color=colors)
    plt.title("Average Tokens at Level 8")
    plt.xlabel("Model")
    plt.ylabel("Avg Tokens")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_error_types(results_rows: List[Dict[str, str]], output_path: str) -> None:
    error_types = sorted({row["error_type"] for row in results_rows if row["error_type"] != "none"})
    models = sorted({row["model"] for row in results_rows})

    counts = {model: {err: 0 for err in error_types} for model in models}
    for row in results_rows:
        err = row["error_type"]
        if err == "none":
            continue
        counts[row["model"]][err] += 1

    plt.figure(figsize=(7, 4))
    bottoms = [0] * len(models)
    for err in error_types:
        values = [counts[model][err] for model in models]
        plt.bar(models, values, bottom=bottoms, label=err)
        bottoms = [b + v for b, v in zip(bottoms, values)]

    plt.title("Error Type Distribution")
    plt.xlabel("Model")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot COOP evaluation results.")
    parser.add_argument("--summary", default="coop_eval_actual/output/summary.csv", help="Summary CSV path")
    parser.add_argument("--results", default="coop_eval_actual/output/experiment_results.csv", help="Results CSV path")
    parser.add_argument("--output_dir", default="coop_eval_actual/output", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    summary_rows = load_summary(args.summary)
    results_rows = load_results(args.results)

    plot_success_curve(summary_rows, os.path.join(args.output_dir, "figure_success_rate.png"))
    plot_tokens_level8(summary_rows, os.path.join(args.output_dir, "figure_tokens_level8.png"))
    plot_error_types(results_rows, os.path.join(args.output_dir, "figure_error_types.png"))

    print("Plots saved to", args.output_dir)


if __name__ == "__main__":
    main()
