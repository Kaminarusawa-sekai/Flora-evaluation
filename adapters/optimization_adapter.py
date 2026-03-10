"""
优化模块适配器 - 集成 automatic_prompt 服务
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage5Output, Stage6Output, OptimizationSuggestion
from typing import Dict, List
import requests
import time


class OptimizationAdapter(ModuleAdapter):
    """
    优化模块适配器 - 调用 automatic_prompt API 服务
    """

    def __init__(self):
        self.api_base_url = None
        self.task_ids = {}

    def process(self, input_data: Dict, config: Dict) -> Stage6Output:
        """
        处理优化请求

        Args:
            input_data: Stage 5 的评估结果
            config: 优化配置
                - api_endpoint: automatic_prompt API 地址
                - max_iterations: 最大迭代次数
                - auto_augment_data: 是否自动增强数据
        """
        # 提取评估结果
        evaluation_results = Stage5Output(**input_data)

        # 设置 API 地址
        self.api_base_url = config.get('api_endpoint', 'http://localhost:8100')

        # 分析失败的测试，识别需要优化的 Agent
        agents_to_optimize = self._identify_agents_to_optimize(evaluation_results)

        # 为每个 Agent 创建优化任务
        optimization_tasks = []
        for agent_info in agents_to_optimize:
            task_id = self._create_optimization_task(agent_info, config)
            optimization_tasks.append({
                'agent_id': agent_info['agent_id'],
                'task_id': task_id,
                'current_prompt': agent_info['current_prompt'],
                'issues': agent_info['issues']
            })

        # 等待所有优化任务完成
        optimized_prompts = {}
        suggestions = []

        for task in optimization_tasks:
            result = self._wait_for_optimization(task['task_id'])

            if result['status'] == 'completed':
                optimized_prompts[task['agent_id']] = result['best_prompt']

                # 生成优化建议
                suggestion = OptimizationSuggestion(
                    target=task['agent_id'],
                    issue=f"准确率低: {', '.join(task['issues'][:2])}",
                    suggestion=f"使用优化后的 Prompt (改进: {result.get('improvement', 0):.2%})",
                    priority='high' if result.get('improvement', 0) > 0.1 else 'medium',
                    estimated_impact=result.get('improvement', 0)
                )
                suggestions.append(suggestion)

        # 计算性能改进
        performance_improvement = self._estimate_improvement(suggestions)

        # 判断是否需要重新构建
        should_rebuild = any(s.priority == 'high' for s in suggestions)

        return Stage6Output(
            suggestions=suggestions,
            optimized_prompts=optimized_prompts,
            performance_improvement=performance_improvement,
            should_rebuild=should_rebuild,
            metadata={
                'stage': 'optimization',
                'version': '1.0.0',
                'api_endpoint': self.api_base_url,
                'total_agents_optimized': len(optimized_prompts)
            }
        )

    def _identify_agents_to_optimize(self, evaluation_results: Stage5Output) -> List[Dict]:
        """
        识别需要优化的 Agent

        分析评估结果，找出表现不佳的 Agent
        """
        agents_to_optimize = []

        # 按 Agent 分组统计失败情况
        agent_failures = {}

        for test_result in evaluation_results.test_results:
            if not test_result.success:
                # 从错误信息中提取 Agent ID
                agent_id = self._extract_agent_from_error(test_result.errors)

                if agent_id not in agent_failures:
                    agent_failures[agent_id] = {
                        'agent_id': agent_id,
                        'failures': 0,
                        'issues': []
                    }

                agent_failures[agent_id]['failures'] += 1
                agent_failures[agent_id]['issues'].extend(test_result.errors)

        # 筛选需要优化的 Agent（失败次数 > 2）
        for agent_id, info in agent_failures.items():
            if info['failures'] > 2:
                # 获取当前 Prompt
                current_prompt = self._get_current_prompt(agent_id)

                agents_to_optimize.append({
                    'agent_id': agent_id,
                    'current_prompt': current_prompt,
                    'failures': info['failures'],
                    'issues': list(set(info['issues']))  # 去重
                })

        return agents_to_optimize

    def _create_optimization_task(self, agent_info: Dict, config: Dict) -> str:
        """
        调用 automatic_prompt API 创建优化任务
        """
        # 构建优化请求
        request_data = {
            "task_name": f"优化 Agent: {agent_info['agent_id']}",
            "task_description": f"优化 Agent Prompt 以提高准确率",

            # 从失败案例中提取训练样本
            "examples": self._extract_examples_from_failures(agent_info['issues']),

            # 使用测试场景作为验证数据
            "validation_data": self._extract_validation_data(agent_info['agent_id']),

            # 当前 Prompt 作为初始提示词
            "initial_prompts": [agent_info['current_prompt']],

            # 优化配置
            "max_iterations": config.get('max_iterations', 10),
            "num_candidates": config.get('num_candidates', 5),
            "top_k": config.get('top_k', 3),
            "early_stop_threshold": config.get('early_stop_threshold', 0.90),
            "auto_augment_data": config.get('auto_augment_data', True),
            "fast_mode": config.get('fast_mode', False)
        }

        # 调用 API
        response = requests.post(
            f"{self.api_base_url}/optimize",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['task_id']
        else:
            raise Exception(f"优化任务创建失败: {response.text}")

    def _wait_for_optimization(self, task_id: str, timeout: int = 600) -> Dict:
        """
        等待优化任务完成

        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 查询任务状态
            response = requests.get(
                f"{self.api_base_url}/status/{task_id}",
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                if result['status'] == 'completed':
                    return result
                elif result['status'] == 'failed':
                    raise Exception(f"优化任务失败: {result.get('error')}")

                # 等待 5 秒后重试
                time.sleep(5)
            else:
                raise Exception(f"查询任务状态失败: {response.text}")

        raise TimeoutError(f"优化任务超时: {task_id}")

    def _extract_agent_from_error(self, errors: List[str]) -> str:
        """从错误信息中提取 Agent ID"""
        for error in errors:
            if 'Agent[' in error:
                start = error.index('Agent[') + 6
                end = error.index(']', start)
                return error[start:end]

        return 'unknown_agent'

    def _get_current_prompt(self, agent_id: str) -> str:
        """
        从 Neo4j 获取 Agent 的当前 Prompt
        """
        # 简化实现：返回示例 Prompt
        return f"You are {agent_id}. Please help users with their tasks."

    def _extract_examples_from_failures(self, issues: List[str]) -> List[Dict]:
        """
        从失败案例中提取训练样本
        """
        examples = []

        # 至少需要 3 个样本
        for i, issue in enumerate(issues[:5]):
            examples.append({
                "input": f"处理任务: {issue}",
                "output": "成功完成任务"
            })

        # 如果不足 3 个，添加通用样本
        while len(examples) < 3:
            examples.append({
                "input": "执行标准任务",
                "output": "任务完成"
            })

        return examples

    def _extract_validation_data(self, agent_id: str) -> List[Dict]:
        """
        提取验证数据
        """
        return [
            {"input": "测试场景 1", "output": "预期结果 1"},
            {"input": "测试场景 2", "output": "预期结果 2"},
            {"input": "测试场景 3", "output": "预期结果 3"}
        ]

    def _estimate_improvement(self, suggestions: List[OptimizationSuggestion]) -> Dict:
        """估算性能改进"""
        total_impact = sum(s.estimated_impact for s in suggestions)

        return {
            'estimated_success_rate_improvement': total_impact,
            'high_priority_count': sum(1 for s in suggestions if s.priority == 'high'),
            'medium_priority_count': sum(1 for s in suggestions if s.priority == 'medium'),
            'low_priority_count': sum(1 for s in suggestions if s.priority == 'low'),
            'total_agents_optimized': len(suggestions)
        }

    def validate_input(self, input_data: Dict) -> bool:
        """验证输入"""
        return 'test_results' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'Automatic Prompt Optimization',
            'version': '1.0.0',
            'description': 'Optimize agent prompts using automatic_prompt service',
            'input_format': 'evaluation_results',
            'output_format': 'optimization_suggestions',
            'api_service': 'automatic_prompt'
        }
