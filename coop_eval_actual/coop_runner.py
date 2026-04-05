import os
import sys
import time
import logging
import yaml
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
if TASKS_ROOT not in sys.path:
    sys.path.insert(0, TASKS_ROOT)

from thespian.actors import ActorSystem

from agents.agent_actor import AgentActor
from common.messages.task_messages import AgentTaskMessage, TaskCompletedMessage
from capabilities import init_capabilities
from agents.tree.tree_manager import treeManager

from coop_eval_actual.agent_tree_loader import load_agents_into_tree, get_root_agents
from coop_eval_actual.mock_tools import MockToolEnvironment, set_global_env
from coop_eval_actual.utils import token_tracker, task_context_manager


class CoopRunner:
    def __init__(self, config_path: str, records_path: str, seed: int, error_injection_rate: float) -> None:
        # 设置评估模式环境变量
        os.environ["COOP_EVAL_EXECUTION"] = "1"

        # 从 pipeline_config.yaml 加载环境变量
        self._load_env_from_pipeline_config()

        self.nodes = load_agents_into_tree(records_path, treeManager)
        roots = get_root_agents(self.nodes)
        self.root_agent_id = roots[0] if roots else "agent_root"

        agent_ids = [node["agent_id"] for node in self.nodes if node.get("agent_id")]
        self.env = MockToolEnvironment(agent_ids, seed=seed, error_injection_rate=error_injection_rate)
        set_global_env(self.env)

        init_capabilities(config_path)

        self.system = ActorSystem("simpleSystemBase")
        self.agent_actor_ref = self.system.createActor(AgentActor)

    def _load_env_from_pipeline_config(self) -> None:
        """从 pipeline_config.yaml 加载环境变量"""
        pipeline_config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "pipeline_config.yaml"
        )

        if not os.path.exists(pipeline_config_path):
            logger.warning(f"pipeline_config.yaml 不存在: {pipeline_config_path}")
            return

        try:
            with open(pipeline_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 提取 Neo4j 配置
            stages = config.get('stages', {})
            for stage_name, stage_config in stages.items():
                stage_cfg = stage_config.get('config', {})

                # 设置 Neo4j 环境变量
                if 'neo4j_uri' in stage_cfg:
                    uri = stage_cfg['neo4j_uri']
                    if uri.startswith('${') and uri.endswith('}'):
                        env_var = uri[2:-1]
                        if env_var in os.environ:
                            os.environ['NEO4J_URI'] = os.environ[env_var]
                    else:
                        os.environ['NEO4J_URI'] = uri

                if 'neo4j_user' in stage_cfg:
                    user = stage_cfg['neo4j_user']
                    if user.startswith('${') and user.endswith('}'):
                        env_var = user[2:-1]
                        if env_var in os.environ:
                            os.environ['NEO4J_USER'] = os.environ[env_var]
                    else:
                        os.environ['NEO4J_USER'] = user

                if 'neo4j_password' in stage_cfg:
                    password = stage_cfg['neo4j_password']
                    if password.startswith('${') and password.endswith('}'):
                        env_var = password[2:-1]
                        if env_var in os.environ:
                            os.environ['NEO4J_PASSWORD'] = os.environ[env_var]
                    else:
                        os.environ['NEO4J_PASSWORD'] = password

            logger.info("已从 pipeline_config.yaml 加载环境变量")
        except Exception as e:
            logger.error(f"加载 pipeline_config.yaml 失败: {e}")

    def shutdown(self) -> None:
        if self.system:
            self.system.shutdown()

    def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task.get("prompt", "")
        task_id = str(task.get("task_id"))
        trace_id = task_id

        # 重置并设置当前任务的 token 统计
        token_tracker.reset(task_id)

        # 记录执行前的日志数量，用于后续提取本次任务的执行记录
        logs_before = len(self.env.logs)

        # 设置全局任务上下文（用于 LLM 记录 token）
        task_context_manager.set_current_task(task_id, layer=0)

        msg = AgentTaskMessage(
            content=prompt,
            description=prompt,
            user_id="eval_user",
            task_id=task_id,
            trace_id=trace_id,
            task_path="/",
            agent_id=self.root_agent_id,
            parameters={},
        )

        start = time.perf_counter()
        response = self.system.ask(self.agent_actor_ref, msg, timeout=120)
        duration_ms = int((time.perf_counter() - start) * 1000)

        result = self._parse_response(response)
        result["duration_ms"] = duration_ms

        # 从 MockToolEnvironment.logs 提取本次任务实际执行的 agents（最准确的来源）
        task_logs = self.env.logs[logs_before:]
        executed_from_logs = []
        logger.info(f"[COOP] Executed agents from logs: {task_logs}")
        for log in task_logs:
            if log.status == "ok" and log.agent_id not in executed_from_logs:
                executed_from_logs.append(log.agent_id)

        # 合并：优先使用日志中的数据，因为它更准确
        parsed_agents = result.get("executed_agents", [])
        all_executed = list(dict.fromkeys(executed_from_logs + parsed_agents))  # 去重保序
        result["executed_agents"] = all_executed
        result["executed_from_logs"] = executed_from_logs

        logger.info(f"[COOP] Executed agents from logs: {len(executed_from_logs)}, from response: {len(parsed_agents)}, merged: {len(all_executed)}")

        # 从 TokenTracker 获取真实的 token 统计
        token_stats = token_tracker.get_stats(task_id)
        result["tokens_prompt"] = token_stats["tokens_prompt"]
        result["tokens_completion"] = token_stats["tokens_completion"]
        result["tokens_total"] = token_stats["tokens_total"]
        result["llm_calls"] = token_stats["llm_calls"]
        result["token_layers"] = token_stats["layers"]

        return result

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        if isinstance(response, TaskCompletedMessage):
            status = response.status
            result_data = response.result or {}
        elif isinstance(response, dict):
            status = response.get("status")
            result_data = response.get("result") or {}
        else:
            status = "FAILED"
            result_data = {}

        # Debug: 打印响应结构
        logger.info(f"[COOP Response] status={status}, result_data keys={result_data.keys() if isinstance(result_data, dict) else type(result_data)}")

        executed_agents: List[str] = []
        if isinstance(result_data, dict):
            step_results = result_data.get("step_results", {})
            logger.info(f"[COOP Response] step_results keys={list(step_results.keys())[:5]}")
            for key in sorted(step_results.keys()):
                step_output = step_results[key]
                logger.info(f"[COOP Response] step {key}: type={type(step_output)}, content={str(step_output)[:200]}")
                # 递归提取所有 agent_id
                self._extract_agent_ids(step_output, executed_agents)

        success = status == "SUCCESS"
        return {
            "success": success,
            "status": status,
            "executed_agents": executed_agents,
            "error_type": "none" if success else "other",
        }

    def _extract_agent_ids(self, data: Any, result: List[str]) -> None:
        """递归提取所有 agent_id 和 executor"""
        if isinstance(data, dict):
            # 提取 agent_id
            if "agent_id" in data and data["agent_id"]:
                result.append(data["agent_id"])
            # 也提取 executor（任务执行者）
            if "executor" in data and data["executor"]:
                executor = data["executor"]
                if executor not in result:
                    result.append(executor)
            for value in data.values():
                self._extract_agent_ids(value, result)
        elif isinstance(data, list):
            for item in data:
                self._extract_agent_ids(item, result)
