"""
基线方法实现（真实 LLM 版本）

CoT、ReAct、Workflow 三种策略，使用真实 LLM 进行规划和执行。
与 COOP 的递进查找形成对比（扁平查找 vs 递进查找）。
"""
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from coop_eval_actual.mock_tools import MockToolEnvironment
from coop_eval_actual.real_planners import (
    BaseLLMPlanner,
    CoTPlanner,
    ReActPlanner,
    WorkflowPlanner,
    PlanResult,
)


@dataclass
class BaselineResult:
    """基线方法执行结果"""
    success: bool
    executed_agents: List[str]
    planned_agents: List[str]  # 规划的 agents（可能与执行的不同）
    error_type: str
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    duration_ms: int
    planning_time_ms: int  # 规划耗时
    execution_time_ms: int  # 执行耗时
    hallucination_errors: int
    injected_errors: int
    recovered_errors: int
    retries: int
    iterations: int  # ReAct 迭代次数
    reasoning: str  # 规划推理过程
    coverage_rate: float = 0.0  # 覆盖率


def run_cot(
    task_id: str,
    prompt: str,
    expected_agents: List[str],
    env: MockToolEnvironment,
    planner: CoTPlanner,
    max_steps: int = 10
) -> BaselineResult:
    """
    Chain-of-Thought 策略

    特点：一次性规划，顺序执行，遇错停止。
    """
    start = time.perf_counter()

    # Phase 1: 真实 LLM 规划
    plan_result = planner.plan(prompt, task_id)
    planned_agents = plan_result.agents[:max_steps]  # 限制最大步数

    # Phase 2: Mock 执行（模拟叶子节点调用外部工具）
    exec_start = time.perf_counter()
    executed_agents: List[str] = []
    hallucination_errors = 0
    injected_errors = 0
    recovered_errors = 0
    retries = 0
    error_type = "none"

    for agent_id in planned_agents:
        result = env.execute_agent("CoT", task_id, agent_id, {"prompt": prompt})

        if result.get("status") == "SUCCESS":
            executed_agents.append(agent_id)
        else:
            err_type = result.get("error_type")
            if err_type == "invalid_tool":
                hallucination_errors += 1
                error_type = "hallucination"
            elif err_type == "500":
                injected_errors += 1
                error_type = "recovery_failed"
            else:
                error_type = "other"
            # CoT 不重试，遇错停止
            break

    execution_time_ms = int((time.perf_counter() - exec_start) * 1000)
    total_duration_ms = int((time.perf_counter() - start) * 1000)

    # 使用覆盖率评估：expected_agents 中有多少被 executed_agents 覆盖
    expected_set = set(expected_agents)
    actual_set = set(executed_agents)
    covered = expected_set & actual_set
    coverage_rate = len(covered) / len(expected_set) if expected_set else 0
    success = coverage_rate >= 0.5 and error_type == "none"

    return BaselineResult(
        success=success,
        executed_agents=executed_agents,
        planned_agents=planned_agents,
        error_type=error_type,
        tokens_prompt=plan_result.tokens_prompt,
        tokens_completion=plan_result.tokens_completion,
        tokens_total=plan_result.tokens_total,
        duration_ms=total_duration_ms,
        planning_time_ms=plan_result.planning_time_ms,
        execution_time_ms=execution_time_ms,
        hallucination_errors=hallucination_errors,
        injected_errors=injected_errors,
        recovered_errors=recovered_errors,
        retries=retries,
        iterations=1,
        reasoning=plan_result.reasoning,
        coverage_rate=coverage_rate,
    )


def run_react(
    task_id: str,
    prompt: str,
    expected_agents: List[str],
    env: MockToolEnvironment,
    planner: ReActPlanner,
    max_retries: int = 1
) -> BaselineResult:
    """
    ReAct (Reasoning + Acting) 策略

    特点：思考-行动-观察循环，支持错误恢复。
    """
    start = time.perf_counter()

    # Phase 1: 真实 LLM 规划（ReAct 的规划本身就是迭代的）
    plan_result = planner.plan(prompt, task_id)
    planned_agents = plan_result.agents

    # Phase 2: Mock 执行（带重试）
    exec_start = time.perf_counter()
    executed_agents: List[str] = []
    hallucination_errors = 0
    injected_errors = 0
    recovered_errors = 0
    retries = 0
    error_type = "none"

    for agent_id in planned_agents:
        result = env.execute_agent("ReAct", task_id, agent_id, {"prompt": prompt})

        if result.get("status") == "SUCCESS":
            executed_agents.append(agent_id)
            continue

        err_type = result.get("error_type")
        if err_type == "invalid_tool":
            hallucination_errors += 1
            error_type = "hallucination"
            break  # hallucination 不重试

        if err_type == "500":
            injected_errors += 1
            # ReAct 支持重试
            if retries < max_retries:
                retries += 1
                recovered = env.execute_agent("ReAct", task_id, agent_id, {"prompt": prompt, "retry": True})
                if recovered.get("status") == "SUCCESS":
                    recovered_errors += 1
                    executed_agents.append(agent_id)
                    continue
            error_type = "recovery_failed"
            break

        error_type = "other"
        break

    execution_time_ms = int((time.perf_counter() - exec_start) * 1000)
    total_duration_ms = int((time.perf_counter() - start) * 1000)

    # 使用覆盖率评估
    expected_set = set(expected_agents)
    actual_set = set(executed_agents)
    covered = expected_set & actual_set
    coverage_rate = len(covered) / len(expected_set) if expected_set else 0
    success = coverage_rate >= 0.5 and error_type == "none"

    return BaselineResult(
        success=success,
        executed_agents=executed_agents,
        planned_agents=planned_agents,
        error_type=error_type,
        tokens_prompt=plan_result.tokens_prompt,
        tokens_completion=plan_result.tokens_completion,
        tokens_total=plan_result.tokens_total,
        duration_ms=total_duration_ms,
        planning_time_ms=plan_result.planning_time_ms,
        execution_time_ms=execution_time_ms,
        hallucination_errors=hallucination_errors,
        injected_errors=injected_errors,
        recovered_errors=recovered_errors,
        retries=retries,
        iterations=plan_result.iterations,
        reasoning=plan_result.reasoning,
        coverage_rate=coverage_rate,
    )


def run_workflow(
    task_id: str,
    prompt: str,
    expected_agents: List[str],
    env: MockToolEnvironment,
    planner: WorkflowPlanner,
    max_steps: int = 10
) -> BaselineResult:
    """
    Workflow 策略（类 LangChain）

    特点：模板匹配 + LLM 规划，顺序执行。
    """
    start = time.perf_counter()

    # Phase 1: 真实 LLM 规划
    plan_result = planner.plan(prompt, task_id)
    planned_agents = plan_result.agents[:max_steps]

    # Phase 2: Mock 执行
    exec_start = time.perf_counter()
    executed_agents: List[str] = []
    hallucination_errors = 0
    injected_errors = 0
    recovered_errors = 0
    retries = 0
    error_type = "none"

    for agent_id in planned_agents:
        result = env.execute_agent("LangChain", task_id, agent_id, {"prompt": prompt})

        if result.get("status") == "SUCCESS":
            executed_agents.append(agent_id)
            continue

        err_type = result.get("error_type")
        if err_type == "invalid_tool":
            hallucination_errors += 1
            error_type = "hallucination"
        elif err_type == "500":
            injected_errors += 1
            error_type = "recovery_failed"
        else:
            error_type = "other"
        break

    execution_time_ms = int((time.perf_counter() - exec_start) * 1000)
    total_duration_ms = int((time.perf_counter() - start) * 1000)

    # 使用覆盖率评估
    expected_set = set(expected_agents)
    actual_set = set(executed_agents)
    covered = expected_set & actual_set
    coverage_rate = len(covered) / len(expected_set) if expected_set else 0
    success = coverage_rate >= 0.5 and error_type == "none"

    return BaselineResult(
        success=success,
        executed_agents=executed_agents,
        planned_agents=planned_agents,
        error_type=error_type,
        tokens_prompt=plan_result.tokens_prompt,
        tokens_completion=plan_result.tokens_completion,
        tokens_total=plan_result.tokens_total,
        duration_ms=total_duration_ms,
        planning_time_ms=plan_result.planning_time_ms,
        execution_time_ms=execution_time_ms,
        hallucination_errors=hallucination_errors,
        injected_errors=injected_errors,
        recovered_errors=recovered_errors,
        retries=retries,
        iterations=1,
        reasoning=plan_result.reasoning,
        coverage_rate=coverage_rate,
    )


# ============================================================================
# 兼容旧接口（用于不需要真实 LLM 的场景）
# ============================================================================

def extract_agent_tags(text: str) -> List[str]:
    """从文本中提取 [agent:xxx] 标签（兼容旧数据集）"""
    import re
    pattern = re.compile(r"\[agent:([a-zA-Z0-9_\-]+)\]")
    return pattern.findall(text) if text else []


def estimate_tokens_for_text(text: str) -> int:
    """估算文本的 token 数"""
    if not text:
        return 0
    # 简单估算：中文约 2 字符/token，英文约 4 字符/token
    return len(text) // 2
