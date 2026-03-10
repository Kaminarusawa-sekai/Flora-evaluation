"""
主优化器 - 整合所有模块实现APO
"""
from typing import List, Dict, Any, Optional
import logging
from config import APOConfig, Task
from evaluator import Evaluator
from generator import CandidateGenerator, FeedbackCollector
from selector import Selector, EarlyStopper
from data_synthesis import DataSynthesizer, DataQualityChecker


class PromptOptimizer:
    """自动提示词优化器 - 核心类"""

    def __init__(self, config: APOConfig, task: Task):
        """
        初始化优化器

        Args:
            config: 优化配置
            task: 任务定义
        """
        self.config = config
        self.task = task

        # 初始化各个模块
        self.evaluator = Evaluator(config, task)
        self.generator = CandidateGenerator(config, task)
        self.selector = Selector(config)
        self.early_stopper = EarlyStopper(patience=3, min_delta=0.01)
        self.data_synthesizer = DataSynthesizer(config)  # 新增：数据合成器

        # 优化历史记录
        self.history = {
            "iterations": [],
            "best_prompts": [],
            "best_scores": [],
            "all_candidates": [],
        }

        # 设置日志
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("PromptOptimizer")
        logger.setLevel(logging.INFO if self.config.verbose else logging.WARNING)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def optimize(
        self,
        initial_prompts: Optional[List[str]] = None,
        num_seeds: int = 3,
        auto_augment_data: bool = True,
        target_validation_size: int = 30
    ) -> Dict[str, Any]:
        """
        执行提示词优化主循环

        Args:
            initial_prompts: 初始提示词列表，如果为None则自动生成
            num_seeds: 初始种子数量
            auto_augment_data: 是否自动增强验证数据（默认True）
            target_validation_size: 目标验证集大小

        Returns:
            优化结果字典
        """
        self._log_optimization_start()

        # 数据增强
        if auto_augment_data:
            self._augment_validation_data_if_needed(target_validation_size)

        # 初始化种子提示词
        current_prompts = self._initialize_seed_prompts(initial_prompts, num_seeds)
        best_prompt, best_score = current_prompts[0], 0.0
        initial_score = None  # 用于记录初始分数

        # 主优化循环
        for iteration in range(self.config.max_iterations):
            self._log_iteration_start(iteration)

            # 评估当前候选
            evaluation_results, scores = self._evaluate_and_score_candidates(current_prompts)

            # 记录初始分数（第一次迭代）
            if iteration == 0 and scores:
                initial_score = max(scores) if scores else 0.0

            # 更新最佳结果
            best_prompt, best_score = self._update_best_result(
                current_prompts, scores, best_prompt, best_score
            )

            # 记录历史
            self._record_iteration_history(
                iteration, best_prompt, best_score,
                current_prompts, scores, evaluation_results
            )

            # 检查停止条件
            should_stop, stop_reason = self._check_stopping_conditions(best_score)
            if should_stop:
                self.logger.info(f"\n{stop_reason}")
                break

            # 生成新候选并选择下一轮
            current_prompts = self._generate_and_select_next_candidates(
                current_prompts, evaluation_results, scores, iteration
            )

        # 返回最终结果
        return self._create_final_result(best_prompt, best_score, current_prompts, initial_score)

    def _log_optimization_start(self) -> None:
        """记录优化开始信息"""
        self.logger.info("=" * 60)
        self.logger.info("开始自动提示词优化")
        self.logger.info(f"任务: {self.task.name}")
        self.logger.info(f"最大迭代次数: {self.config.max_iterations}")
        self.logger.info("=" * 60)

    def _augment_validation_data_if_needed(self, target_size: int) -> None:
        """数据增强（如果需要）"""
        self.logger.info("\n检查验证数据...")
        original_size = len(self.task.validation_data)
        self.logger.info(f"当前验证数据: {original_size} 个")

        if original_size < target_size:
            self.logger.info(f"验证数据不足，开始自动生成...")

            augmented_data = self.data_synthesizer.augment_validation_data(
                self.task, target_size=target_size
            )
            self.task.validation_data = augmented_data

            quality_report = DataQualityChecker.check_data_quality(augmented_data)
            DataQualityChecker.print_quality_report(quality_report)

            self.logger.info(f"✓ 数据增强完成: {original_size} -> {len(augmented_data)}")
        else:
            self.logger.info(f"✓ 验证数据充足，无需增强")

    def _initialize_seed_prompts(
        self, initial_prompts: Optional[List[str]], num_seeds: int
    ) -> List[str]:
        """初始化种子提示词"""
        if initial_prompts is None:
            self.logger.info(f"\n生成 {num_seeds} 个初始种子提示词...")
            prompts = self.generator.initialize_seed_prompts(num_seeds)
        else:
            prompts = initial_prompts

        self.logger.info(f"初始提示词数量: {len(prompts)}")
        for i, prompt in enumerate(prompts):
            self.logger.info(f"种子 {i+1}: {prompt[:100]}...")

        return prompts

    def _log_iteration_start(self, iteration: int) -> None:
        """记录迭代开始信息"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"迭代 {iteration + 1}/{self.config.max_iterations}")
        self.logger.info(f"{'='*60}")

    def _evaluate_and_score_candidates(
        self, candidates: List[str]
    ) -> tuple[List[Dict[str, float]], List[float]]:
        """评估候选并提取分数"""
        self.logger.info("评估当前候选提示词...")
        evaluation_results = self._evaluate_candidates(candidates)
        scores = [result["accuracy"] for result in evaluation_results]
        self.logger.info(f"候选分数: {[f'{s:.3f}' for s in scores]}")
        return evaluation_results, scores

    def _update_best_result(
        self,
        current_prompts: List[str],
        scores: List[float],
        best_prompt: str,
        best_score: float
    ) -> tuple[str, float]:
        """更新最佳提示词和分数"""
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        if scores[best_idx] > best_score:
            best_score = scores[best_idx]
            best_prompt = current_prompts[best_idx]
            self.logger.info(f"✓ 发现更好的提示词! 分数: {best_score:.3f}")
            self.logger.info(f"最佳提示词: {best_prompt[:150]}...")
        return best_prompt, best_score

    def _record_iteration_history(
        self,
        iteration: int,
        best_prompt: str,
        best_score: float,
        current_prompts: List[str],
        scores: List[float],
        evaluation_results: List[Dict[str, float]]
    ) -> None:
        """记录迭代历史"""
        self.history["iterations"].append(iteration + 1)
        self.history["best_scores"].append(best_score)
        self.history["best_prompts"].append(best_prompt)
        self.history["all_candidates"].append({
            "prompts": current_prompts.copy(),
            "scores": scores,
            "evaluations": evaluation_results,
        })

    def _check_stopping_conditions(self, best_score: float) -> tuple[bool, str]:
        """检查是否应该停止优化"""
        # 检查早停
        if self.early_stopper.check(best_score):
            reason = f"早停触发！连续 {self.early_stopper.patience} 轮无改进"
            return True, reason

        # 检查是否达到目标
        if best_score >= self.config.early_stop_threshold:
            reason = f"达到目标分数 {self.config.early_stop_threshold}！"
            return True, reason

        return False, ""

    def _generate_and_select_next_candidates(
        self,
        current_prompts: List[str],
        evaluation_results: List[Dict[str, Any]],
        scores: List[float],
        iteration: int
    ) -> List[str]:
        """生成新候选并选择下一轮候选"""
        # 生成反馈
        self.logger.info("生成反馈...")
        feedback = self._generate_feedback(current_prompts, evaluation_results, iteration)

        # 生成新候选
        self.logger.info(f"生成 {self.config.num_candidates} 个新候选...")
        new_candidates = self.generator.generate_candidates(current_prompts, feedback)
        self.logger.info(f"生成了 {len(new_candidates)} 个新候选")

        # 合并并评估所有候选
        all_candidates = current_prompts + new_candidates
        all_results = self._evaluate_candidates(all_candidates)
        all_scores = [r["accuracy"] for r in all_results]

        # 选择下一轮候选
        self.logger.info("选择下一轮候选...")
        selected = self._select_next_candidates(all_candidates, all_scores, iteration)

        return selected

    def _create_final_result(
        self, best_prompt: str, best_score: float, final_prompts: List[str], initial_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建最终结果字典"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("优化完成!")
        self.logger.info("=" * 60)
        self.logger.info(f"最终最佳分数: {best_score:.3f}")
        self.logger.info(f"最佳提示词: {best_prompt}")

        # 计算改进幅度
        if initial_score is not None and initial_score > 0:
            improvement = best_score - initial_score
        else:
            initial_score = 0.0
            improvement = best_score

        return {
            "best_prompt": best_prompt,
            "best_score": best_score,
            "initial_score": initial_score,
            "improvement": improvement,
            "iterations": len(self.history["iterations"]),
            "history": self.history,
            "final_candidates": final_prompts,
        }

    def _evaluate_candidates(
        self, candidates: List[str]
    ) -> List[Dict[str, float]]:
        """评估候选提示词列表"""
        results = []
        for i, candidate in enumerate(candidates):
            result = self.evaluator.evaluate_prompt(candidate)
            self.logger.debug(
                f"候选 {i+1}/{len(candidates)}: 准确率 {result['accuracy']:.3f}"
            )
            results.append(result)
        return results

    def _generate_feedback(
        self,
        prompts: List[str],
        evaluation_results: List[Dict[str, Any]],
        iteration: int,
    ) -> List[Dict[str, Any]]:
        """生成优化反馈"""
        feedback = []

        for prompt, result in zip(prompts, evaluation_results):
            fb = {
                "prompt": prompt,
                "score": result["accuracy"],
                "iteration": iteration,
                "suggestions": [],
            }

            # 分析问题
            if result["accuracy"] < 0.5:
                fb["suggestions"].append("提示词可能过于模糊，需要更明确的指导")
            elif result["accuracy"] < 0.8:
                fb["suggestions"].append("提示词基本有效，但可以进一步优化细节")

            # 添加LLM反馈（如果启用）
            if self.config.use_llm_feedback and "llm_feedback_score" in result:
                fb["llm_feedback"] = result["llm_feedback_score"]

            feedback.append(fb)

        return feedback

    def _select_next_candidates(
        self, candidates: List[str], scores: List[float], iteration: int
    ) -> List[str]:
        """选择下一轮的候选提示词"""
        # 使用自适应选择策略
        selected = self.selector.adaptive_selection(
            candidates, scores, iteration, self.config.max_iterations
        )

        self.logger.info(f"选择了 {len(selected)} 个候选进入下一轮")
        return selected

    def evaluate_final(
        self, prompt: str, test_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, float]:
        """
        在测试集上评估最终提示词

        Args:
            prompt: 要评估的提示词
            test_data: 测试数据，如果为None则使用验证数据

        Returns:
            评估结果
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("最终评估")
        self.logger.info("=" * 60)

        if test_data is None:
            test_data = self.task.validation_data

        result = self.evaluator.evaluate_prompt(prompt, test_data)

        self.logger.info(f"测试集准确率: {result['accuracy']:.3f}")
        self.logger.info(f"正确数量: {result['correct']}/{result['total_examples']}")

        return result


class APOFactory:
    """APO工厂类 - 便捷创建不同配置的优化器"""

    @staticmethod
    def create_simple_optimizer(task: Task, llm_api_key: Optional[str] = None) -> PromptOptimizer:
        """创建简单的优化器（快速原型）"""
        kwargs = {
            "max_iterations": 5,
            "num_candidates": 3,
            "top_k": 2,
            "generation_strategy": "llm_rewrite",
            "use_llm_feedback": False,
        }
        # 只在明确提供API key时才覆盖默认值
        if llm_api_key is not None:
            kwargs["llm_api_key"] = llm_api_key
        config = APOConfig(**kwargs)
        return PromptOptimizer(config, task)

    @staticmethod
    def create_advanced_optimizer(
        task: Task, llm_api_key: Optional[str] = None
    ) -> PromptOptimizer:
        """创建高级优化器（完整功能）"""
        kwargs = {
            "max_iterations": 15,
            "num_candidates": 8,
            "top_k": 4,
            "generation_strategy": "llm_rewrite",
            "use_llm_feedback": True,
            "early_stop_threshold": 0.90,
        }
        # 只在明确提供API key时才覆盖默认值
        if llm_api_key is not None:
            kwargs["llm_api_key"] = llm_api_key
        config = APOConfig(**kwargs)
        return PromptOptimizer(config, task)

    @staticmethod
    def create_genetic_optimizer(
        task: Task, llm_api_key: Optional[str] = None
    ) -> PromptOptimizer:
        """创建基于遗传算法的优化器"""
        kwargs = {
            "max_iterations": 20,
            "num_candidates": 10,
            "top_k": 5,
            "generation_strategy": "genetic",
            "use_llm_feedback": False,
        }
        # 只在明确提供API key时才覆盖默认值
        if llm_api_key is not None:
            kwargs["llm_api_key"] = llm_api_key
        config = APOConfig(**kwargs)
        return PromptOptimizer(config, task)

    @staticmethod
    def create_rl_optimizer(
        task: Task, llm_api_key: Optional[str] = None
    ) -> PromptOptimizer:
        """创建基于强化学习的优化器"""
        kwargs = {
            "max_iterations": 15,
            "num_candidates": 5,
            "top_k": 3,
            "generation_strategy": "rl",
            "use_llm_feedback": False,
        }
        # 只在明确提供API key时才覆盖默认值
        if llm_api_key is not None:
            kwargs["llm_api_key"] = llm_api_key
        config = APOConfig(**kwargs)
        return PromptOptimizer(config, task)


class BatchOptimizer:
    """批量优化器 - 同时优化多个任务"""

    def __init__(self, config: APOConfig):
        self.config = config

    def optimize_multiple_tasks(
        self, tasks: List[Task]
    ) -> Dict[str, Dict[str, Any]]:
        """
        优化多个任务

        Args:
            tasks: 任务列表

        Returns:
            每个任务的优化结果
        """
        results = {}

        for i, task in enumerate(tasks):
            print(f"\n优化任务 {i+1}/{len(tasks)}: {task.name}")
            print("=" * 60)

            optimizer = PromptOptimizer(self.config, task)
            result = optimizer.optimize()

            results[task.name] = result

        return results
