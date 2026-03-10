"""
评估模块适配器
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage5Output, TestResult
from typing import Dict


class EvaluationAdapter(ModuleAdapter):
    """评估模块适配器"""

    def __init__(self):
        self.runner = None

    def process(self, input_data: Dict, config: Dict) -> Stage5Output:
        # 这里简化实现，实际应该从 coop_eval_actual 导入
        # from coop_eval_actual.evaluation_runner import EvaluationRunner

        # 提取测试场景
        scenarios = input_data.get('scenarios', [])
        if 'sources' in input_data:
            scenarios = input_data['sources'][0].get('scenarios', [])

        # 模拟运行评估
        results = self._run_evaluation(scenarios, config)

        # 计算统计信息
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        total_time = sum(r.execution_time for r in results)

        return Stage5Output(
            test_results=results,
            summary={
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests
            },
            success_rate=successful_tests / total_tests if total_tests > 0 else 0,
            average_execution_time=total_time / total_tests if total_tests > 0 else 0,
            metadata={
                'stage': 'evaluation',
                'version': '1.0.0',
                'config': config
            }
        )

    def _run_evaluation(self, scenarios: list, config: Dict) -> list:
        """运行评估（简化实现）"""
        results = []

        for i, scenario in enumerate(scenarios):
            # 模拟测试执行
            result = TestResult(
                test_id=f"test_{i}",
                scenario_id=scenario.get('scenario_id', f"scenario_{i}"),
                success=True,  # 简化：假设都成功
                execution_time=1.0,
                api_calls=len(scenario.get('api_path', [])),
                errors=[],
                metrics={}
            )
            results.append(result)

        return results

    def validate_input(self, input_data: Dict) -> bool:
        return 'scenarios' in input_data or 'sources' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'Evaluation',
            'version': '1.0.0',
            'description': 'Evaluate agent system with test scenarios',
            'input_format': 'test_scenarios',
            'output_format': 'evaluation_results'
        }
