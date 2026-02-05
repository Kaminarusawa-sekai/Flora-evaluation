"""
COOP 评估实验主入口（真实 LLM 版本）

对比四种策略：
- CoT: 扁平查找，一次性规划
- ReAct: 扁平查找，迭代规划
- Workflow: 扁平查找，模板匹配
- COOP: 递进查找，层级规划

核心对比点：
- COOP 每层只看 3-5 个子节点
- CoT/ReAct/Workflow 一次性面对 250 个 Agent
"""
import argparse
import csv
import json
import os
import sys
import logging
from typing import Any, Dict, List, Tuple

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from coop_eval_actual.agent_tree_loader import load_agent_records
from coop_eval_actual.baselines import run_cot, run_react, run_workflow, BaselineResult
from coop_eval_actual.coop_runner import CoopRunner
from coop_eval_actual.mock_tools import MockToolEnvironment
from coop_eval_actual.real_planners import CoTPlanner, ReActPlanner, WorkflowPlanner
from coop_eval_actual.workflow_complexity import compute_workflow_complexity


RESULT_COLUMNS = [
    "task_id",
    "level",
    "model",
    "success",
    "tokens_prompt",
    "tokens_completion",
    "tokens_total",
    "tool_calls_total",
    "hallucination_errors",
    "injected_errors",
    "recovered_errors",
    "retries",
    "iterations",
    "error_type",
    "duration_ms",
    "planning_time_ms",
    "execution_time_ms",
    "compatible",
    "expected_agents",
    "planned_agents",
    "actual_agents",
    "coverage_rate",
]

SUMMARY_COLUMNS = [
    "model",
    "level",
    "n_tasks",
    "success_rate",
    "avg_tokens_total",
    "hallucination_rate",
    "recovery_rate",
    "avg_duration_ms",
    "avg_planning_time_ms",
    "avg_tool_calls",
    "compatibility_rate",
    "workflow_complexity_score",
    "workflow_nodes",
    "workflow_branches",
    "tool_rules",
    "config_loc",
]


def load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _serialize_agents(agent_list: List[str]) -> str:
    return json.dumps(agent_list, ensure_ascii=False)


def _compatibility(expected_agents: List[str], available_agents: set) -> int:
    return int(all(agent in available_agents for agent in expected_agents))


def _tool_metrics_from_logs(logs: List[Any]) -> Tuple[int, int, int, int]:
    tool_calls_total = len(logs)
    hallucination_errors = sum(1 for log in logs if log.error_type == "invalid_tool")
    injected_errors = sum(1 for log in logs if log.error_type == "500")

    recovered_errors = 0
    if injected_errors:
        success_agents = {log.agent_id for log in logs if log.status == "ok"}
        recovered_errors = sum(
            1 for log in logs if log.error_type == "500" and log.agent_id in success_agents
        )
    return tool_calls_total, hallucination_errors, injected_errors, recovered_errors


def _aggregate_summary(results: List[Dict[str, Any]], workflow_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
    summary_rows: List[Dict[str, Any]] = []
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}

    for row in results:
        key = (row["model"], row["level"])
        grouped.setdefault(key, []).append(row)

    for (model, level), rows in sorted(grouped.items()):
        n_tasks = len(rows)
        success_rate = sum(r["success"] for r in rows) / n_tasks if n_tasks else 0
        avg_tokens_total = sum(r["tokens_total"] for r in rows) / n_tasks if n_tasks else 0
        hallucination_rate = (
            sum(r["hallucination_errors"] for r in rows) /
            max(1, sum(r["tool_calls_total"] for r in rows))
        )
        recovery_rate = (
            sum(r["recovered_errors"] for r in rows) /
            max(1, sum(r["injected_errors"] for r in rows))
        )
        avg_duration_ms = sum(r["duration_ms"] for r in rows) / n_tasks if n_tasks else 0
        avg_planning_time_ms = sum(r.get("planning_time_ms", 0) for r in rows) / n_tasks if n_tasks else 0
        avg_tool_calls = sum(r["tool_calls_total"] for r in rows) / n_tasks if n_tasks else 0
        compatibility_rate = sum(r["compatible"] for r in rows) / n_tasks if n_tasks else 0

        workflow_data = {
            "workflow_complexity_score": "",
            "workflow_nodes": "",
            "workflow_branches": "",
            "tool_rules": "",
            "config_loc": "",
        }
        if model == "ReAct":
            workflow_data = workflow_metrics

        summary_rows.append({
            "model": model,
            "level": level,
            "n_tasks": n_tasks,
            "success_rate": round(success_rate, 4),
            "avg_tokens_total": round(avg_tokens_total, 2),
            "hallucination_rate": round(hallucination_rate, 4),
            "recovery_rate": round(recovery_rate, 4),
            "avg_duration_ms": round(avg_duration_ms, 2),
            "avg_planning_time_ms": round(avg_planning_time_ms, 2),
            "avg_tool_calls": round(avg_tool_calls, 2),
            "compatibility_rate": round(compatibility_rate, 4),
            **workflow_data,
        })

    return summary_rows


def write_csv(path: str, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def init_llm():
    """初始化 LLM 能力"""
    # 添加 tasks 目录到 path
    tasks_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
    if tasks_root not in sys.path:
        sys.path.insert(0, tasks_root)

    from tasks.capabilities.llm.qwen_llm import QwenLLM

    llm = QwenLLM()
    llm.initialize({})
    logger.info("LLM initialized successfully")
    return llm


def main() -> None:
    parser = argparse.ArgumentParser(description="Run COOP evaluation with real LLM planning.")
    parser.add_argument("--dataset", default="coop_eval_actual/data/dataset_natural.json", help="Dataset JSON path")
    parser.add_argument("--records", default="records (2).json", help="Agent records JSON path")
    parser.add_argument("--config", default="coop_eval_actual/configs/eval_config.json", help="Eval config path")
    parser.add_argument("--output_dir", default="coop_eval_actual/output", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--error_injection_rate", type=float, default=0.1, help="Injected 500 error rate")
    parser.add_argument("--max_tasks", type=int, default=0, help="Limit tasks for quick runs")
    parser.add_argument("--skip_coop", action="store_true", help="Skip COOP evaluation")
    parser.add_argument("--skip_baselines", action="store_true", help="Skip baseline evaluations")
    args = parser.parse_args()

    # 检查数据集是否存在
    if not os.path.exists(args.dataset):
        logger.warning(f"Dataset not found: {args.dataset}")
        logger.info("Generating natural language dataset...")
        from coop_eval_actual.scripts.generate_natural_dataset import generate_natural_dataset
        original_dataset = "coop_eval_actual/data/dataset.json"
        if os.path.exists(original_dataset):
            generate_natural_dataset(original_dataset, args.dataset)
        else:
            logger.error(f"Original dataset not found: {original_dataset}")
            return

    dataset = load_dataset(args.dataset)
    if args.max_tasks:
        dataset = dataset[:args.max_tasks]

    logger.info(f"Loaded {len(dataset)} tasks from {args.dataset}")

    # 加载 Agent 记录
    nodes = load_agent_records(args.records)
    available_agents = {node["agent_id"] for node in nodes if node.get("agent_id")}
    leaf_agents = [node for node in nodes if node.get("is_leaf", False)]

    logger.info(f"Loaded {len(nodes)} agents, {len(leaf_agents)} leaves")

    # 初始化 LLM
    llm = init_llm()

    # 初始化扁平规划器（CoT/ReAct/Workflow 共用）
    cot_planner = CoTPlanner(llm, nodes)
    react_planner = ReActPlanner(llm, nodes, max_iterations=8)
    workflow_planner = WorkflowPlanner(llm, nodes)

    # 初始化 Mock 执行环境
    env_cot = MockToolEnvironment(list(available_agents), seed=args.seed, error_injection_rate=args.error_injection_rate)
    env_react = MockToolEnvironment(list(available_agents), seed=args.seed + 7, error_injection_rate=args.error_injection_rate)
    env_workflow = MockToolEnvironment(list(available_agents), seed=args.seed + 3, error_injection_rate=args.error_injection_rate)

    # 初始化 COOP Runner
    coop_runner = None
    if not args.skip_coop:
        try:
            coop_runner = CoopRunner(args.config, args.records, seed=args.seed + 11, error_injection_rate=args.error_injection_rate)
            logger.info("COOP Runner initialized")
        except Exception as e:
            logger.error(f"Failed to initialize COOP Runner: {e}")
            args.skip_coop = True

    results: List[Dict[str, Any]] = []

    for i, task in enumerate(dataset):
        task_id = str(task.get("task_id"))
        prompt = task.get("prompt", "")
        expected_agents = task.get("expected_agents", [])
        compatible = _compatibility(expected_agents, available_agents)

        logger.info(f"[{i+1}/{len(dataset)}] Processing task {task_id}")

        # ========== CoT ==========
        if not args.skip_baselines:
            try:
                logger.info(f"  Running CoT...")
                cot_result = run_cot(task_id, prompt, expected_agents, env_cot, cot_planner)
                results.append({
                    "task_id": task_id,
                    "level": task.get("level"),
                    "model": "CoT",
                    "success": int(cot_result.success),
                    "tokens_prompt": cot_result.tokens_prompt,
                    "tokens_completion": cot_result.tokens_completion,
                    "tokens_total": cot_result.tokens_total,
                    "tool_calls_total": len(cot_result.executed_agents),
                    "hallucination_errors": cot_result.hallucination_errors,
                    "injected_errors": cot_result.injected_errors,
                    "recovered_errors": cot_result.recovered_errors,
                    "retries": cot_result.retries,
                    "iterations": cot_result.iterations,
                    "error_type": cot_result.error_type,
                    "duration_ms": cot_result.duration_ms,
                    "planning_time_ms": cot_result.planning_time_ms,
                    "execution_time_ms": cot_result.execution_time_ms,
                    "compatible": compatible,
                    "expected_agents": _serialize_agents(expected_agents),
                    "planned_agents": _serialize_agents(cot_result.planned_agents),
                    "actual_agents": _serialize_agents(cot_result.executed_agents),
                })
                logger.info(f"    CoT: planned={len(cot_result.planned_agents)}, executed={len(cot_result.executed_agents)}, success={cot_result.success}")
            except Exception as e:
                logger.error(f"    CoT failed: {e}")

        # ========== ReAct ==========
        if not args.skip_baselines:
            try:
                logger.info(f"  Running ReAct...")
                react_result = run_react(task_id, prompt, expected_agents, env_react, react_planner)
                results.append({
                    "task_id": task_id,
                    "level": task.get("level"),
                    "model": "ReAct",
                    "success": int(react_result.success),
                    "tokens_prompt": react_result.tokens_prompt,
                    "tokens_completion": react_result.tokens_completion,
                    "tokens_total": react_result.tokens_total,
                    "tool_calls_total": len(react_result.executed_agents),
                    "hallucination_errors": react_result.hallucination_errors,
                    "injected_errors": react_result.injected_errors,
                    "recovered_errors": react_result.recovered_errors,
                    "retries": react_result.retries,
                    "iterations": react_result.iterations,
                    "error_type": react_result.error_type,
                    "duration_ms": react_result.duration_ms,
                    "planning_time_ms": react_result.planning_time_ms,
                    "execution_time_ms": react_result.execution_time_ms,
                    "compatible": compatible,
                    "expected_agents": _serialize_agents(expected_agents),
                    "planned_agents": _serialize_agents(react_result.planned_agents),
                    "actual_agents": _serialize_agents(react_result.executed_agents),
                })
                logger.info(f"    ReAct: iterations={react_result.iterations}, planned={len(react_result.planned_agents)}, success={react_result.success}")
            except Exception as e:
                logger.error(f"    ReAct failed: {e}")

        # ========== Workflow ==========
        if not args.skip_baselines:
            try:
                logger.info(f"  Running Workflow...")
                workflow_result = run_workflow(task_id, prompt, expected_agents, env_workflow, workflow_planner)
                results.append({
                    "task_id": task_id,
                    "level": task.get("level"),
                    "model": "LangChain",
                    "success": int(workflow_result.success),
                    "tokens_prompt": workflow_result.tokens_prompt,
                    "tokens_completion": workflow_result.tokens_completion,
                    "tokens_total": workflow_result.tokens_total,
                    "tool_calls_total": len(workflow_result.executed_agents),
                    "hallucination_errors": workflow_result.hallucination_errors,
                    "injected_errors": workflow_result.injected_errors,
                    "recovered_errors": workflow_result.recovered_errors,
                    "retries": workflow_result.retries,
                    "iterations": workflow_result.iterations,
                    "error_type": workflow_result.error_type,
                    "duration_ms": workflow_result.duration_ms,
                    "planning_time_ms": workflow_result.planning_time_ms,
                    "execution_time_ms": workflow_result.execution_time_ms,
                    "compatible": compatible,
                    "expected_agents": _serialize_agents(expected_agents),
                    "planned_agents": _serialize_agents(workflow_result.planned_agents),
                    "actual_agents": _serialize_agents(workflow_result.executed_agents),
                })
                logger.info(f"    Workflow: planned={len(workflow_result.planned_agents)}, success={workflow_result.success}")
            except Exception as e:
                logger.error(f"    Workflow failed: {e}")

        # ========== COOP ==========
        if not args.skip_coop and coop_runner:
            try:
                logger.info(f"  Running COOP...")
                coop_result = coop_runner.run_task(task)
                coop_logs = [log for log in coop_runner.env.logs if log.task_id == task_id and log.model == "COOP"]
                tool_calls_total, hallucination_errors, injected_errors, recovered_errors = _tool_metrics_from_logs(coop_logs)

                executed_agents = coop_result.get("executed_agents", [])

                # 使用覆盖率评估：expected_agents 中有多少被 actual_agents 覆盖
                # 覆盖率 >= 50% 视为成功
                expected_set = set(expected_agents)
                actual_set = set(executed_agents)
                covered = expected_set & actual_set
                coverage_rate = len(covered) / len(expected_set) if expected_set else 0
                success = coop_result.get("success", False) and coverage_rate >= 0.5

                results.append({
                    "task_id": task_id,
                    "level": task.get("level"),
                    "model": "COOP",
                    "success": int(success),
                    "tokens_prompt": coop_result.get("tokens_prompt", 0),
                    "tokens_completion": coop_result.get("tokens_completion", 0),
                    "tokens_total": coop_result.get("tokens_total", 0),
                    "tool_calls_total": tool_calls_total,
                    "hallucination_errors": hallucination_errors,
                    "injected_errors": injected_errors,
                    "recovered_errors": recovered_errors,
                    "retries": max(0, tool_calls_total - len(executed_agents)),
                    "iterations": coop_result.get("iterations", 1),
                    "error_type": coop_result.get("error_type", "none"),
                    "duration_ms": coop_result.get("duration_ms", 0),
                    "planning_time_ms": coop_result.get("planning_time_ms", 0),
                    "execution_time_ms": coop_result.get("execution_time_ms", 0),
                    "compatible": compatible,
                    "expected_agents": _serialize_agents(expected_agents),
                    "planned_agents": _serialize_agents(coop_result.get("planned_agents", [])),
                    "actual_agents": _serialize_agents(executed_agents),
                    "coverage_rate": round(coverage_rate, 2),
                })
                logger.info(f"    COOP: executed={len(executed_agents)}, coverage={coverage_rate:.0%}, success={success}")
            except Exception as e:
                logger.error(f"    COOP failed: {e}")

    # 输出结果
    os.makedirs(args.output_dir, exist_ok=True)

    workflow_metrics = {}
    try:
        workflow_metrics = compute_workflow_complexity("coop_eval_actual/configs/react_workflow.json")
    except Exception:
        pass

    summary_rows = _aggregate_summary(results, workflow_metrics)

    write_csv(os.path.join(args.output_dir, "experiment_results.csv"), results, RESULT_COLUMNS)
    write_csv(os.path.join(args.output_dir, "summary.csv"), summary_rows, SUMMARY_COLUMNS)

    # 保存原始日志
    raw_log_path = os.path.join(args.output_dir, "raw_logs.jsonl")
    all_logs = env_cot.logs + env_react.logs + env_workflow.logs
    if coop_runner:
        all_logs += coop_runner.env.logs
    with open(raw_log_path, "w", encoding="utf-8") as handle:
        for log in all_logs:
            handle.write(json.dumps(log.__dict__, ensure_ascii=False) + "\n")

    # 保存推理过程（用于分析）
    reasoning_path = os.path.join(args.output_dir, "reasoning_logs.jsonl")
    with open(reasoning_path, "w", encoding="utf-8") as handle:
        for row in results:
            if "reasoning" in row:
                handle.write(json.dumps({
                    "task_id": row["task_id"],
                    "model": row["model"],
                    "reasoning": row.get("reasoning", "")
                }, ensure_ascii=False) + "\n")

    if coop_runner:
        coop_runner.shutdown()

    logger.info(f"Wrote {len(results)} rows to {args.output_dir}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    for row in summary_rows:
        print(f"{row['model']:12} Level {row['level']}: success_rate={row['success_rate']:.2%}, "
              f"avg_tokens={row['avg_tokens_total']:.0f}, hallucination={row['hallucination_rate']:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
