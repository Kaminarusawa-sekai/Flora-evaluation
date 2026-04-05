"""
评估模块适配器
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any

from core.module_adapter import ModuleAdapter
from schemas.schemas import Stage5Output, TestResult

logger = logging.getLogger(__name__)


class EvaluationAdapter(ModuleAdapter):
    """评估模块适配器 - 使用 CoopRunner 进行真实评估"""

    def __init__(self):
        self.runner = None
        self.config_path = None
        self.records_path = None

    def process(self, input_data: Dict, config: Dict) -> Stage5Output:
        """
        执行评估流程

        Args:
            input_data: 包含测试场景的输入数据
            config: 评估配置，包含：
                - agent_records_path: Agent 记录文件路径
                - capabilities_config: 能力配置文件路径
                - seed: 随机种子
                - error_injection_rate: 错误注入率
        """
        # 提取测试场景
        scenarios = self._extract_scenarios(input_data)

        if not scenarios:
            logger.warning("No scenarios found in input data")
            return self._create_empty_output(config)

        # 初始化 CoopRunner
        try:
            from coop_eval_actual.coop_runner import CoopRunner

            records_path = config.get('agent_records_path', 'output/stage4a/agent_records.json')
            capabilities_config = config.get('capabilities_config')
            seed = config.get('seed', 42)
            error_injection_rate = config.get('error_injection_rate', 0.0)

            logger.info(f"Initializing CoopRunner with records: {records_path}")
            self.runner = CoopRunner(
                config_path=capabilities_config,
                records_path=records_path,
                seed=seed,
                error_injection_rate=error_injection_rate
            )

        except Exception as e:
            logger.error(f"Failed to initialize CoopRunner: {e}")
            return self._create_error_output(str(e), config)

        # 运行评估
        results = self._run_evaluation(scenarios, config)

        # 关闭 runner
        if self.runner:
            try:
                self.runner.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down runner: {e}")

        # 计算统计信息
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        total_time = sum(r.execution_time for r in results)
        total_api_calls = sum(r.api_calls for r in results)

        return Stage5Output(
            test_results=results,
            summary={
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'total_api_calls': total_api_calls,
                'total_execution_time': total_time
            },
            success_rate=successful_tests / total_tests if total_tests > 0 else 0,
            average_execution_time=total_time / total_tests if total_tests > 0 else 0,
            metadata={
                'stage': 'evaluation',
                'version': '2.0.0',
                'config': config,
                'runner_type': 'CoopRunner'
            }
        )

    def _extract_scenarios(self, input_data: Dict) -> List[Dict]:
        """从输入数据中提取测试场景"""
        scenarios = []

        if isinstance(input_data, dict):
            # 处理 multiple 类型输入格式
            for key, value in input_data.items():
                if isinstance(value, dict) and 'scenarios' in value:
                    scenarios = value['scenarios']
                    break

            # 如果没有找到，尝试直接格式
            if not scenarios:
                scenarios = input_data.get('scenarios', [])
                if 'sources' in input_data:
                    sources = input_data['sources']
                    if isinstance(sources, list) and len(sources) > 0:
                        scenarios = sources[0].get('scenarios', [])

        return scenarios

    def _run_evaluation(self, scenarios: List[Dict], config: Dict) -> List[TestResult]:
        """运行评估测试"""
        results = []

        for i, scenario in enumerate(scenarios):
            try:
                # 构建任务
                task = {
                    'task_id': scenario.get('scenario_id', f"task_{i}"),
                    'prompt': self._build_prompt(scenario)
                }

                logger.info(f"Running scenario {i+1}/{len(scenarios)}: {task['task_id']}")

                # 执行任务
                start_time = time.time()
                result = self.runner.run_task(task)
                execution_time = time.time() - start_time

                # 转换为 TestResult
                test_result = TestResult(
                    test_id=f"test_{i}",
                    scenario_id=task['task_id'],
                    success=result.get('success', False),
                    execution_time=execution_time,
                    api_calls=len(result.get('executed_agents', [])),
                    errors=self._extract_errors(result),
                    metrics={
                        'tokens_prompt': result.get('tokens_prompt', 0),
                        'tokens_completion': result.get('tokens_completion', 0),
                        'tokens_total': result.get('tokens_total', 0),
                        'llm_calls': result.get('llm_calls', 0),
                        'executed_agents': result.get('executed_agents', []),
                        'duration_ms': result.get('duration_ms', 0),
                        'status': result.get('status', 'UNKNOWN')
                    }
                )
                results.append(test_result)

            except Exception as e:
                logger.error(f"Error running scenario {i}: {e}")
                # 创建失败的测试结果
                test_result = TestResult(
                    test_id=f"test_{i}",
                    scenario_id=scenario.get('scenario_id', f"scenario_{i}"),
                    success=False,
                    execution_time=0.0,
                    api_calls=0,
                    errors=[str(e)],
                    metrics={}
                )
                results.append(test_result)

        return results

    def _build_prompt(self, scenario: Dict) -> str:
        """根据场景构建提示词"""
        title = scenario.get('title', '')
        description = scenario.get('description', '')
        expected_outcome = scenario.get('expected_outcome', '')

        prompt = f"{title}\n\n{description}"
        if expected_outcome:
            prompt += f"\n\nExpected outcome: {expected_outcome}"

        return prompt

    def _extract_errors(self, result: Dict) -> List[str]:
        """从结果中提取错误信息"""
        errors = []

        if not result.get('success', False):
            error_type = result.get('error_type', 'unknown')
            errors.append(f"Error type: {error_type}")

        status = result.get('status', '')
        if status and status != 'SUCCESS':
            errors.append(f"Status: {status}")

        return errors

    def _create_empty_output(self, config: Dict) -> Stage5Output:
        """创建空的输出结果"""
        return Stage5Output(
            test_results=[],
            summary={
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'total_api_calls': 0,
                'total_execution_time': 0.0
            },
            success_rate=0.0,
            average_execution_time=0.0,
            metadata={
                'stage': 'evaluation',
                'version': '2.0.0',
                'config': config,
                'error': 'No scenarios found'
            }
        )

    def _create_error_output(self, error_msg: str, config: Dict) -> Stage5Output:
        """创建错误输出结果"""
        return Stage5Output(
            test_results=[],
            summary={
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'total_api_calls': 0,
                'total_execution_time': 0.0
            },
            success_rate=0.0,
            average_execution_time=0.0,
            metadata={
                'stage': 'evaluation',
                'version': '2.0.0',
                'config': config,
                'error': error_msg
            }
        )



    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据格式"""
        if isinstance(input_data, dict):
            # 检查是否是 multiple 类型输入格式
            for key, value in input_data.items():
                if isinstance(value, dict) and 'scenarios' in value:
                    return True

            # 检查直接格式
            if 'scenarios' in input_data or 'sources' in input_data:
                return True

        return False

    def get_metadata(self) -> Dict:
        """返回适配器元数据"""
        return {
            'name': 'Evaluation',
            'version': '2.0.0',
            'description': 'Evaluate agent system with test scenarios using CoopRunner',
            'input_format': 'test_scenarios',
            'output_format': 'evaluation_results',
            'required_config': [
                'agent_records_path',
                'capabilities_config'
            ],
            'optional_config': [
                'seed',
                'error_injection_rate'
            ]
        }
