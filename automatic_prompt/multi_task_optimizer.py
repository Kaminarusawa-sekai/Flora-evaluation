"""
多任务优化模块
支持同时优化多个任务，利用任务间相关性
"""
from typing import List, Dict, Any, Optional
import numpy as np
from config import APOConfig, Task
from optimizer import PromptOptimizer
from evaluator import Evaluator
import logging


class MultiTaskOptimizer:
    """多任务提示词优化器"""

    def __init__(self, configs: List[APOConfig], tasks: List[Task]):
        """
        初始化多任务优化器

        Args:
            configs: 每个任务的配置列表
            tasks: 任务列表
        """
        if len(configs) != len(tasks):
            # 如果只提供一个config，所有任务共享
            if len(configs) == 1:
                configs = configs * len(tasks)
            else:
                raise ValueError("configs和tasks长度必须相同")

        self.configs = configs
        self.tasks = tasks
        self.num_tasks = len(tasks)

        # 为每个任务创建优化器
        self.optimizers = [
            PromptOptimizer(config, task)
            for config, task in zip(configs, tasks)
        ]

        # 为每个任务创建评估器
        self.evaluators = [
            Evaluator(config, task)
            for config, task in zip(configs, tasks)
        ]

        self.logger = logging.getLogger("MultiTaskOptimizer")
        self.logger.setLevel(logging.INFO)

    def optimize_jointly(
        self,
        initial_prompts: List[List[str]],
        share_prompts: bool = True,
        task_weights: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        联合优化多个任务

        Args:
            initial_prompts: 每个任务的初始提示词列表
            share_prompts: 是否在任务间共享提示词
            task_weights: 任务权重（用于计算综合分数）

        Returns:
            包含每个任务最佳提示词的结果字典
        """
        self.logger.info(f"开始多任务联合优化，共{self.num_tasks}个任务")

        # 默认权重
        if task_weights is None:
            task_weights = [1.0 / self.num_tasks] * self.num_tasks

        if share_prompts:
            # 共享提示词：使用同一个提示词优化所有任务
            result = self._optimize_with_shared_prompts(
                initial_prompts[0] if initial_prompts else None,
                task_weights
            )
        else:
            # 独立优化：每个任务独立优化
            result = self._optimize_independently(initial_prompts)

        return result

    def _optimize_with_shared_prompts(
        self,
        initial_prompts: Optional[List[str]],
        task_weights: List[float]
    ) -> Dict[str, Any]:
        """
        使用共享提示词优化所有任务

        Args:
            initial_prompts: 初始提示词列表
            task_weights: 任务权重

        Returns:
            优化结果
        """
        self.logger.info("使用共享提示词策略")

        # 初始化
        if initial_prompts is None:
            initial_prompts = self.optimizers[0].generator.initialize_seed_prompts(3)

        current_prompts = initial_prompts
        best_prompt = current_prompts[0]
        best_weighted_score = 0.0

        max_iterations = self.configs[0].max_iterations
        history = {"iterations": [], "weighted_scores": [], "task_scores": []}

        for iteration in range(max_iterations):
            self.logger.info(f"\n===== 迭代 {iteration + 1}/{max_iterations} =====")

            # 在所有任务上评估每个提示词
            all_scores = []
            for prompt in current_prompts:
                task_scores = []
                for task_idx, evaluator in enumerate(self.evaluators):
                    result = evaluator.evaluate_prompt(prompt)
                    score = result.get("accuracy", 0.0)
                    task_scores.append(score)

                # 计算加权平均分数
                weighted_score = sum(
                    score * weight
                    for score, weight in zip(task_scores, task_weights)
                )
                all_scores.append(weighted_score)

                self.logger.info(
                    f"提示词: {prompt[:50]}... | "
                    f"加权分数: {weighted_score:.3f} | "
                    f"各任务: {[f'{s:.2f}' for s in task_scores]}"
                )

            # 更新最佳结果
            max_score_idx = np.argmax(all_scores)
            if all_scores[max_score_idx] > best_weighted_score:
                best_weighted_score = all_scores[max_score_idx]
                best_prompt = current_prompts[max_score_idx]
                self.logger.info(f"✓ 发现更好的提示词！加权分数: {best_weighted_score:.3f}")

            # 记录历史
            history["iterations"].append(iteration)
            history["weighted_scores"].append(best_weighted_score)
            history["task_scores"].append(task_scores)

            # 早停检查
            if best_weighted_score >= 0.95:
                self.logger.info("达到目标分数，提前停止")
                break

            # 生成新候选（使用第一个任务的生成器）
            # 收集反馈
            feedback = [{
                "accuracy": all_scores[i],
                "task_scores": None  # 可以添加更详细的反馈
            } for i in range(len(current_prompts))]

            new_prompts = self.optimizers[0].generator.generate_candidates(
                current_prompts, feedback
            )

            # 选择下一轮候选
            current_prompts = self.optimizers[0].selector.select_top_k(
                current_prompts + new_prompts,
                all_scores + [0.0] * len(new_prompts),  # 新候选分数未知
                k=min(len(current_prompts), self.configs[0].top_k)
            )

        # 最终在每个任务上评估最佳提示词
        final_task_results = []
        for task_idx, (task, evaluator) in enumerate(zip(self.tasks, self.evaluators)):
            result = evaluator.evaluate_prompt(best_prompt)
            final_task_results.append({
                "task_name": task.name,
                "score": result.get("accuracy", 0.0),
                "details": result
            })

        return {
            "best_prompt": best_prompt,
            "weighted_score": best_weighted_score,
            "task_results": final_task_results,
            "history": history,
            "iterations": iteration + 1
        }

    def _optimize_independently(
        self,
        initial_prompts: List[List[str]]
    ) -> Dict[str, Any]:
        """
        独立优化每个任务

        Args:
            initial_prompts: 每个任务的初始提示词列表

        Returns:
            每个任务的优化结果
        """
        self.logger.info("使用独立优化策略")

        results = []
        for task_idx, (optimizer, task, prompts) in enumerate(
            zip(self.optimizers, self.tasks, initial_prompts)
        ):
            self.logger.info(f"\n优化任务 {task_idx + 1}/{self.num_tasks}: {task.name}")

            # 优化单个任务
            result = optimizer.optimize(
                initial_prompts=prompts,
                auto_augment_data=False
            )

            results.append({
                "task_name": task.name,
                "best_prompt": result["best_prompt"],
                "best_score": result["best_score"],
                "iterations": result["iterations"]
            })

        return {
            "strategy": "independent",
            "task_results": results
        }

    def transfer_learning(
        self,
        source_task_idx: int,
        target_task_idx: int,
        source_prompt: str
    ) -> Dict[str, Any]:
        """
        从源任务迁移到目标任务

        Args:
            source_task_idx: 源任务索引
            target_task_idx: 目标任务索引
            source_prompt: 源任务的提示词

        Returns:
            迁移学习结果
        """
        self.logger.info(
            f"迁移学习: {self.tasks[source_task_idx].name} -> "
            f"{self.tasks[target_task_idx].name}"
        )

        # 在目标任务上评估源提示词
        target_evaluator = self.evaluators[target_task_idx]
        source_result = target_evaluator.evaluate_prompt(source_prompt)

        self.logger.info(f"源提示词在目标任务上的分数: {source_result['accuracy']:.3f}")

        # 使用源提示词作为起点，在目标任务上微调
        target_optimizer = self.optimizers[target_task_idx]
        adapted_result = target_optimizer.optimize(
            initial_prompts=[source_prompt],
            auto_augment_data=False
        )

        return {
            "source_task": self.tasks[source_task_idx].name,
            "target_task": self.tasks[target_task_idx].name,
            "source_prompt": source_prompt,
            "source_score_on_target": source_result["accuracy"],
            "adapted_prompt": adapted_result["best_prompt"],
            "adapted_score": adapted_result["best_score"],
            "improvement": adapted_result["best_score"] - source_result["accuracy"]
        }

    def meta_learning(
        self,
        support_tasks_indices: List[int],
        query_task_idx: int,
        num_adaptation_steps: int = 5
    ) -> Dict[str, Any]:
        """
        元学习：从多个支持任务学习，快速适应查询任务

        Args:
            support_tasks_indices: 支持任务的索引列表
            query_task_idx: 查询任务索引
            num_adaptation_steps: 适应步数

        Returns:
            元学习结果
        """
        self.logger.info(
            f"元学习: 从{len(support_tasks_indices)}个任务学习，"
            f"适应到{self.tasks[query_task_idx].name}"
        )

        # 在支持任务上学习通用提示词模式
        support_prompts = []
        for task_idx in support_tasks_indices:
            optimizer = self.optimizers[task_idx]
            result = optimizer.optimize(
                initial_prompts=None,
                auto_augment_data=False,
                num_seeds=2
            )
            support_prompts.append(result["best_prompt"])
            self.logger.info(
                f"支持任务 {self.tasks[task_idx].name}: "
                f"分数 {result['best_score']:.3f}"
            )

        # 分析支持任务提示词的共同模式
        # （简化版本：使用支持任务的最佳提示词作为元初始化）
        meta_prompt = self._extract_meta_template(support_prompts)

        self.logger.info(f"提取的元模板: {meta_prompt[:100]}...")

        # 在查询任务上快速适应
        query_optimizer = self.optimizers[query_task_idx]
        adapted_result = query_optimizer.optimize(
            initial_prompts=[meta_prompt],
            auto_augment_data=False
        )

        return {
            "support_tasks": [self.tasks[i].name for i in support_tasks_indices],
            "query_task": self.tasks[query_task_idx].name,
            "meta_template": meta_prompt,
            "adapted_prompt": adapted_result["best_prompt"],
            "adapted_score": adapted_result["best_score"],
            "adaptation_steps": adapted_result["iterations"]
        }

    def _extract_meta_template(self, prompts: List[str]) -> str:
        """
        从多个提示词中提取元模板

        简化版本：选择最长的提示词作为模板
        未来可以使用更复杂的方法（如提取共同结构）
        """
        # 简单策略：返回最长的提示词
        return max(prompts, key=len)

    def compute_task_similarity(self) -> np.ndarray:
        """
        计算任务间的相似度矩阵

        Returns:
            相似度矩阵 (num_tasks x num_tasks)
        """
        similarity_matrix = np.zeros((self.num_tasks, self.num_tasks))

        # 使用一个通用提示词在所有任务上评估
        generic_prompt = "Please complete the following task carefully."

        scores = []
        for evaluator in self.evaluators:
            result = evaluator.evaluate_prompt(generic_prompt)
            scores.append(result.get("accuracy", 0.0))

        # 计算相关系数（简化版本）
        for i in range(self.num_tasks):
            for j in range(self.num_tasks):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    # 基于分数差异计算相似度
                    diff = abs(scores[i] - scores[j])
                    similarity_matrix[i, j] = 1.0 - diff

        return similarity_matrix


# 便捷函数

def optimize_multiple_tasks(
    tasks: List[Task],
    initial_prompts: Optional[List[List[str]]] = None,
    shared_config: Optional[APOConfig] = None
) -> Dict[str, Any]:
    """
    便捷的多任务优化函数

    Args:
        tasks: 任务列表
        initial_prompts: 每个任务的初始提示词
        shared_config: 共享配置（如果为None则使用默认配置）

    Returns:
        优化结果
    """
    if shared_config is None:
        shared_config = APOConfig()

    configs = [shared_config] * len(tasks)

    if initial_prompts is None:
        initial_prompts = [None] * len(tasks)

    multi_optimizer = MultiTaskOptimizer(configs, tasks)

    return multi_optimizer.optimize_jointly(
        initial_prompts=initial_prompts,
        share_prompts=True
    )
