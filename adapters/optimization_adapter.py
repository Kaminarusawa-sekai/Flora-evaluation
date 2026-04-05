"""
优化模块适配器 - 集成 automatic_prompt 优化功能
"""

from core.module_adapter import ModuleAdapter
from schemas.schemas import Stage5Output, Stage6Output, OptimizationSuggestion
from typing import Dict, List
import sys
import os

# 添加 automatic_prompt 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'automatic_prompt'))

from config import APOConfig, Task
from optimizer import PromptOptimizer


class OptimizationAdapter(ModuleAdapter):
    """
    优化模块适配器 - 直接调用 automatic_prompt 优化器
    """

    def __init__(self):
        pass

    def process(self, input_data: Dict, config: Dict) -> Stage6Output:
        """
        处理优化请求

        Args:
            input_data: Stage 5 的评估结果
            config: 优化配置
                - max_iterations: 最大迭代次数
                - num_candidates: 候选数量
                - top_k: 保留的最优候选数
                - early_stop_threshold: 早停阈值
                - auto_augment_data: 是否自动增强数据
                - fast_mode: 快速模式
        """
        # 提取评估结果
        evaluation_results = Stage5Output(**input_data)

        # 分析失败的测试，识别需要优化的 Agent
        agents_to_optimize = self._identify_agents_to_optimize(evaluation_results)

        # 为每个 Agent 执行优化
        optimized_prompts = {}
        suggestions = []

        for agent_info in agents_to_optimize:
            print(f"\n优化 Agent: {agent_info['agent_id']}")
            print(f"失败次数: {agent_info['failures']}")
            print(f"问题: {agent_info['issues'][:3]}")

            # 直接调用优化器
            result = self._optimize_agent(agent_info, config)

            if result and result['best_score'] > 0:
                optimized_prompts[agent_info['agent_id']] = result['best_prompt']

                # 生成优化建议
                suggestion = OptimizationSuggestion(
                    target=agent_info['agent_id'],
                    issue=f"准确率低: {', '.join(agent_info['issues'][:2])}",
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
                'method': 'direct_call',
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

    def _optimize_agent(self, agent_info: Dict, config: Dict) -> Dict:
        """
        直接调用优化器优化 Agent Prompt

        Args:
            agent_info: Agent 信息
            config: 优化配置

        Returns:
            优化结果
        """
        try:
            # 从失败案例中提取训练样本
            examples = self._extract_examples_from_failures(agent_info['issues'])

            # 使用测试场景作为验证数据
            validation_data = self._extract_validation_data(agent_info['agent_id'])

            # 创建任务定义
            task = Task(
                name=f"优化 Agent: {agent_info['agent_id']}",
                description=f"优化 Agent Prompt 以提高准确率",
                examples=examples,
                validation_data=validation_data
            )

            # 创建优化配置
            apo_config = APOConfig(
                max_iterations=config.get('max_iterations', 10),
                num_candidates=config.get('num_candidates', 5),
                top_k=config.get('top_k', 3),
                early_stop_threshold=config.get('early_stop_threshold', 0.90),
                generation_strategy="llm_rewrite" if not config.get('fast_mode', False) else "mutation",
                use_llm_feedback=not config.get('fast_mode', False),
                verbose=True
            )

            # 创建优化器
            optimizer = PromptOptimizer(apo_config, task)

            # 执行优化
            result = optimizer.optimize(
                initial_prompts=[agent_info['current_prompt']],
                auto_augment_data=config.get('auto_augment_data', True) and not config.get('fast_mode', False),
                target_validation_size=30 if not config.get('fast_mode', False) else len(validation_data)
            )

            return result

        except Exception as e:
            print(f"优化 Agent {agent_info['agent_id']} 失败: {str(e)}")
            return None

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
            'description': 'Optimize agent prompts using automatic_prompt optimizer (direct call)',
            'input_format': 'evaluation_results',
            'output_format': 'optimization_suggestions',
            'method': 'direct_call'
        }
