"""
真实 LLM 规划器模块

实现 CoT、ReAct、Workflow 三种扁平规划策略，与 COOP 的递进规划形成对比。

核心区别：
- COOP: 递进查找，每层只看当前节点的子节点（3-5个）
- CoT/ReAct/Workflow: 扁平查找，一次性面对所有 Agent（250个）
"""
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PlanResult:
    """规划结果"""
    agents: List[str]  # 规划的 agent_id 列表
    success: bool
    tokens_prompt: int = 0
    tokens_completion: int = 0
    tokens_total: int = 0
    planning_time_ms: int = 0
    reasoning: str = ""  # 规划推理过程
    error: Optional[str] = None
    iterations: int = 1  # ReAct 的迭代次数


@dataclass
class ExecutionStepResult:
    """单步执行结果"""
    agent_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None


class BaseLLMPlanner(ABC):
    """
    基础 LLM 规划器

    所有扁平规划策略的基类，提供 Agent 信息构建等公共方法。
    """

    def __init__(self, llm, all_agents: List[Dict[str, Any]]):
        """
        Args:
            llm: LLM 能力实例 (ILLMCapability)
            all_agents: 所有 Agent 列表（扁平，约 250 个）
        """
        self.llm = llm
        self.all_agents = all_agents
        self.agent_map = {a.get("agent_id"): a for a in all_agents if a.get("agent_id")}
        # 只保留叶子节点作为可执行的 Agent
        self.leaf_agents = [a for a in all_agents if a.get("is_leaf", False)]
        logger.info(f"BaseLLMPlanner initialized with {len(all_agents)} agents, {len(self.leaf_agents)} leaves")

    def _build_agent_context(self, agents: List[Dict] = None, max_desc_len: int = 150) -> str:
        """
        构建 Agent 列表上下文

        Args:
            agents: Agent 列表，默认使用叶子节点
            max_desc_len: 描述最大长度（避免 context 过长）
        """
        agents = agents or self.leaf_agents
        agent_list = []
        for a in agents:
            desc = a.get("description") or a.get("capability") or ""
            if len(desc) > max_desc_len:
                desc = desc[:max_desc_len] + "..."
            agent_list.append({
                "id": a.get("agent_id"),
                "name": a.get("name", ""),
                "description": desc
            })
        return json.dumps(agent_list, ensure_ascii=False, indent=2)

    def _call_llm(self, prompt: str) -> Tuple[str, int, int]:
        """
        调用 LLM 并返回结果和 token 统计

        Returns:
            (response_text, tokens_prompt, tokens_completion)
        """
        try:
            # 估算 prompt tokens (简单估算: 字符数/2 for 中文)
            tokens_prompt = len(prompt) // 2

            response = self.llm.generate(prompt)

            # 估算 completion tokens
            tokens_completion = len(response) // 2 if response else 0

            return response or "", tokens_prompt, tokens_completion
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return "", 0, 0

    def _parse_agent_list(self, text: str) -> List[str]:
        """从 LLM 响应中解析 agent_id 列表"""
        if not text:
            return []

        # 尝试解析 JSON 数组
        try:
            # 提取 JSON 数组
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                if isinstance(data, list):
                    # 可能是字符串列表或对象列表
                    result = []
                    for item in data:
                        if isinstance(item, str):
                            result.append(item)
                        elif isinstance(item, dict) and "id" in item:
                            result.append(item["id"])
                        elif isinstance(item, dict) and "agent_id" in item:
                            result.append(item["agent_id"])
                    return result
        except json.JSONDecodeError:
            pass

        # 回退：提取所有看起来像 agent_id 的字符串
        # agent_id 通常是 snake_case 格式
        pattern = r'[a-z][a-z0-9_]*(?:_[a-z0-9]+)+'
        matches = re.findall(pattern, text)

        # 过滤：只保留存在的 agent_id
        valid_agents = [m for m in matches if m in self.agent_map]
        return valid_agents

    @abstractmethod
    def plan(self, task: str, task_id: str = "") -> PlanResult:
        """
        执行规划

        Args:
            task: 任务描述
            task_id: 任务 ID

        Returns:
            PlanResult
        """
        pass


class CoTPlanner(BaseLLMPlanner):
    """
    Chain-of-Thought 规划器

    特点：一次性生成完整的执行计划，不进行迭代。
    劣势：面对 250 个 Agent，容易选错或遗漏。
    """

    def plan(self, task: str, task_id: str = "") -> PlanResult:
        start_time = time.perf_counter()
        total_prompt_tokens = 0
        total_completion_tokens = 0

        prompt = f"""你是一个任务规划专家。请根据用户任务，从可用的 Agent 列表中选择需要执行的 Agent，并确定执行顺序。

## 可用 Agents（共 {len(self.leaf_agents)} 个）
{self._build_agent_context()}

## 用户任务
{task}

## 要求
1. 仔细分析任务需要哪些能力
2. 从上述 Agent 中选择合适的执行者
3. 确定执行顺序（有依赖关系的要先执行前置任务）
4. 只选择必要的 Agent，不要多选

## 输出格式
请输出一个 JSON 数组，包含按执行顺序排列的 agent_id：
["agent_id_1", "agent_id_2", "agent_id_3"]

只输出 JSON 数组，不要其他内容。
"""

        response, prompt_tokens, completion_tokens = self._call_llm(prompt)
        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens

        agents = self._parse_agent_list(response)

        planning_time_ms = int((time.perf_counter() - start_time) * 1000)

        return PlanResult(
            agents=agents,
            success=len(agents) > 0,
            tokens_prompt=total_prompt_tokens,
            tokens_completion=total_completion_tokens,
            tokens_total=total_prompt_tokens + total_completion_tokens,
            planning_time_ms=planning_time_ms,
            reasoning=response,
            iterations=1
        )


class ReActPlanner(BaseLLMPlanner):
    """
    ReAct (Reasoning + Acting) 规划器

    特点：思考-行动-观察循环，每步都进行推理。
    劣势：每次迭代都面对 250 个 Agent，决策负担重。
    """

    def __init__(self, llm, all_agents: List[Dict[str, Any]], max_iterations: int = 8):
        super().__init__(llm, all_agents)
        self.max_iterations = max_iterations

    def plan(self, task: str, task_id: str = "") -> PlanResult:
        start_time = time.perf_counter()
        total_prompt_tokens = 0
        total_completion_tokens = 0

        executed_agents: List[str] = []
        reasoning_history: List[str] = []
        iterations = 0

        agent_context = self._build_agent_context()

        for i in range(self.max_iterations):
            iterations = i + 1

            # 构建当前状态的 prompt
            history_str = "\n".join(reasoning_history[-3:]) if reasoning_history else "无"

            prompt = f"""你是一个任务执行专家，使用 ReAct 方法逐步完成任务。

## 原始任务
{task}

## 可用 Agents（共 {len(self.leaf_agents)} 个）
{agent_context}

## 已执行的 Agents
{json.dumps(executed_agents, ensure_ascii=False) if executed_agents else "无"}

## 最近的推理历史
{history_str}

## 当前步骤 {i + 1}
请按以下格式输出：

Thought: <分析当前状态，思考下一步应该做什么>
Action: <选择一个 agent_id 执行，或输出 FINISH 表示任务完成>

注意：
- 如果任务已完成，Action 输出 FINISH
- 如果还需要执行，Action 输出一个具体的 agent_id
- 不要重复执行已执行过的 Agent
"""

            response, prompt_tokens, completion_tokens = self._call_llm(prompt)
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens

            reasoning_history.append(f"Step {i + 1}:\n{response}")

            # 解析 Action
            action = self._parse_action(response)

            if action == "FINISH" or action is None:
                break

            # 验证 agent_id 是否有效
            if action in self.agent_map and action not in executed_agents:
                executed_agents.append(action)
            elif action in executed_agents:
                # 已执行过，跳过
                reasoning_history.append(f"(跳过重复的 Agent: {action})")
            else:
                # 无效的 agent_id
                reasoning_history.append(f"(无效的 Agent: {action})")

        planning_time_ms = int((time.perf_counter() - start_time) * 1000)

        return PlanResult(
            agents=executed_agents,
            success=len(executed_agents) > 0,
            tokens_prompt=total_prompt_tokens,
            tokens_completion=total_completion_tokens,
            tokens_total=total_prompt_tokens + total_completion_tokens,
            planning_time_ms=planning_time_ms,
            reasoning="\n---\n".join(reasoning_history),
            iterations=iterations
        )

    def _parse_action(self, response: str) -> Optional[str]:
        """从 ReAct 响应中解析 Action"""
        if not response:
            return None

        # 查找 Action: 行
        match = re.search(r'Action:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if not match:
            return None

        action = match.group(1).strip()

        # 检查是否是 FINISH
        if action.upper() in ["FINISH", "DONE", "完成", "结束"]:
            return "FINISH"

        # 清理 action（可能包含引号或其他字符）
        action = re.sub(r'["\'\[\]]', '', action).strip()

        return action if action else None


class WorkflowPlanner(BaseLLMPlanner):
    """
    Workflow 规划器（类 LangChain 风格）

    特点：先分类任务类型，再匹配预定义工作流模板。
    公平性：COOP 也有预定义的树结构，所以 Workflow 也可以有预定义模板。
    """

    def __init__(self, llm, all_agents: List[Dict[str, Any]], workflow_templates: Dict[str, List[str]] = None):
        super().__init__(llm, all_agents)
        # 预定义工作流模板（可以从配置文件加载）
        self.workflow_templates = workflow_templates or {}

    def plan(self, task: str, task_id: str = "") -> PlanResult:
        start_time = time.perf_counter()
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # 如果有预定义模板，先尝试匹配
        if self.workflow_templates:
            template_result = self._match_template(task)
            if template_result:
                total_prompt_tokens += template_result[1]
                total_completion_tokens += template_result[2]
                if template_result[0]:
                    planning_time_ms = int((time.perf_counter() - start_time) * 1000)
                    return PlanResult(
                        agents=template_result[0],
                        success=True,
                        tokens_prompt=total_prompt_tokens,
                        tokens_completion=total_completion_tokens,
                        tokens_total=total_prompt_tokens + total_completion_tokens,
                        planning_time_ms=planning_time_ms,
                        reasoning="Matched workflow template",
                        iterations=1
                    )

        # 没有匹配的模板，使用 LLM 直接规划（类似 CoT）
        prompt = f"""你是一个工作流规划专家。请根据任务描述，设计一个执行工作流。

## 可用 Agents（共 {len(self.leaf_agents)} 个）
{self._build_agent_context()}

## 任务描述
{task}

## 要求
1. 分析任务类型和所需步骤
2. 选择合适的 Agent 组成工作流
3. 确保工作流的步骤顺序合理

## 输出格式
请输出一个 JSON 数组，包含工作流中按顺序执行的 agent_id：
["agent_id_1", "agent_id_2", "agent_id_3"]

只输出 JSON 数组，不要其他内容。
"""

        response, prompt_tokens, completion_tokens = self._call_llm(prompt)
        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens

        agents = self._parse_agent_list(response)

        planning_time_ms = int((time.perf_counter() - start_time) * 1000)

        return PlanResult(
            agents=agents,
            success=len(agents) > 0,
            tokens_prompt=total_prompt_tokens,
            tokens_completion=total_completion_tokens,
            tokens_total=total_prompt_tokens + total_completion_tokens,
            planning_time_ms=planning_time_ms,
            reasoning=response,
            iterations=1
        )

    def _match_template(self, task: str) -> Optional[Tuple[List[str], int, int]]:
        """
        尝试匹配预定义工作流模板

        Returns:
            (agent_list, prompt_tokens, completion_tokens) or None
        """
        if not self.workflow_templates:
            return None

        template_names = list(self.workflow_templates.keys())
        prompt = f"""请判断以下任务最匹配哪个工作流类型：

任务：{task}

可选工作流类型：
{json.dumps(template_names, ensure_ascii=False)}

请只输出最匹配的工作流类型名称，不要其他内容。如果都不匹配，输出 "NONE"。
"""

        response, prompt_tokens, completion_tokens = self._call_llm(prompt)

        if not response or "NONE" in response.upper():
            return None

        # 查找匹配的模板
        response_clean = response.strip().strip('"\'')
        for name in template_names:
            if name in response_clean or response_clean in name:
                return (self.workflow_templates[name], prompt_tokens, completion_tokens)

        return None


def create_planner(
    planner_type: str,
    llm,
    all_agents: List[Dict[str, Any]],
    **kwargs
) -> BaseLLMPlanner:
    """
    工厂函数：创建规划器实例

    Args:
        planner_type: "cot", "react", "workflow"
        llm: LLM 能力实例
        all_agents: Agent 列表
        **kwargs: 额外参数

    Returns:
        BaseLLMPlanner 实例
    """
    planner_type = planner_type.lower()

    if planner_type == "cot":
        return CoTPlanner(llm, all_agents)
    elif planner_type == "react":
        max_iterations = kwargs.get("max_iterations", 8)
        return ReActPlanner(llm, all_agents, max_iterations=max_iterations)
    elif planner_type == "workflow":
        templates = kwargs.get("workflow_templates", {})
        return WorkflowPlanner(llm, all_agents, workflow_templates=templates)
    else:
        raise ValueError(f"Unknown planner type: {planner_type}")
