"""
评估模块 - 评估提示词性能
"""
from typing import List, Dict, Any, Callable, Optional
import numpy as np
import hashlib
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import APOConfig, Task
from llm_client import create_llm_client
from advanced_metrics import AdvancedMetrics


class ResponseCache:
    """LLM响应缓存 - 避免重复调用相同的提示词"""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode('utf-8')).hexdigest()

    def get(self, prompt: str) -> Optional[str]:
        """从缓存获取响应"""
        key = self._get_cache_key(prompt)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, prompt: str, response: str):
        """设置缓存"""
        if len(self.cache) >= self.max_size:
            # 简单的FIFO策略：删除第一个
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        key = self._get_cache_key(prompt)
        self.cache[key] = response

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }


class Evaluator:
    """提示词评估器 - 支持并行评估和响应缓存"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)
        self.cache = ResponseCache(max_size=1000)
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def evaluate_prompt(
        self, prompt: str, validation_data: List[Dict[str, Any]] = None,
        use_advanced_metrics: bool = True, task_type: str = "classification",
        use_parallel: bool = False, max_workers: int = 4
    ) -> Dict[str, float]:
        """
        评估单个提示词的性能

        Args:
            prompt: 待评估的提示词
            validation_data: 验证数据，如果为None则使用task.validation_data
            use_advanced_metrics: 是否使用高级评估指标
            task_type: 任务类型 'classification' 或 'generation'
            use_parallel: 是否使用并行评估（加速）
            max_workers: 并行线程数

        Returns:
            评估结果字典，包含各种指标
        """
        if validation_data is None:
            validation_data = self.task.validation_data

        if use_parallel and len(validation_data) > 1:
            # 使用并行评估
            return self._evaluate_parallel(
                prompt, validation_data, use_advanced_metrics, task_type, max_workers
            )
        else:
            # 使用串行评估
            return self._evaluate_sequential(
                prompt, validation_data, use_advanced_metrics, task_type
            )

    def _evaluate_sequential(
        self, prompt: str, validation_data: List[Dict[str, Any]],
        use_advanced_metrics: bool, task_type: str
    ) -> Dict[str, float]:
        """串行评估（原始实现）"""

        results = {
            "accuracy": 0.0,
            "total_examples": len(validation_data),
            "correct": 0,
            "llm_feedback_score": 0.0,
        }

        correct_count = 0
        llm_feedback_scores = []

        # 收集所有预测和参考答案（用于高级指标）
        predictions = []
        references = []

        for example in validation_data:
            # 构建完整提示词（传入完整的example数据以支持动态内容）
            full_prompt = self._construct_prompt(prompt, example["input"], example)

            # 获取模型响应
            response = self._get_llm_response(full_prompt)

            # 提取答案
            extracted_answer = self._extract_answer(response)
            predictions.append(extracted_answer)
            references.append(example["output"])

            # 评估准确性
            is_correct = self._check_correctness(response, example["output"])
            if is_correct:
                correct_count += 1

            # LLM反馈评分（可选）
            if self.config.use_llm_feedback:
                feedback_score = self._get_llm_feedback(
                    prompt, example["input"], response, example["output"]
                )
                llm_feedback_scores.append(feedback_score)

        # 计算基础指标
        results["accuracy"] = correct_count / len(validation_data)
        results["correct"] = correct_count

        if llm_feedback_scores:
            results["llm_feedback_score"] = np.mean(llm_feedback_scores)

        # 计算高级指标
        if use_advanced_metrics and len(predictions) > 0:
            advanced_results = AdvancedMetrics.compute_all_metrics(
                predictions, references, task_type
            )
            results.update(advanced_results)

        return results

    def _evaluate_parallel(
        self, prompt: str, validation_data: List[Dict[str, Any]],
        use_advanced_metrics: bool, task_type: str, max_workers: int
    ) -> Dict[str, float]:
        """
        并行评估 - 使用多线程加速评估过程

        Args:
            prompt: 提示词
            validation_data: 验证数据
            use_advanced_metrics: 是否使用高级指标
            task_type: 任务类型
            max_workers: 线程数

        Returns:
            评估结果
        """
        results = {
            "accuracy": 0.0,
            "total_examples": len(validation_data),
            "correct": 0,
            "llm_feedback_score": 0.0,
        }

        correct_count = 0
        llm_feedback_scores = []
        predictions = []
        references = []

        # 使用线程池并行评估
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_example = {
                executor.submit(self._evaluate_single_example, prompt, example): example
                for example in validation_data
            }

            # 收集结果
            for future in as_completed(future_to_example):
                example = future_to_example[future]
                try:
                    result = future.result()
                    predictions.append(result['prediction'])
                    references.append(result['reference'])

                    if result['is_correct']:
                        correct_count += 1

                    if result.get('llm_feedback_score'):
                        llm_feedback_scores.append(result['llm_feedback_score'])

                except Exception as e:
                    self.logger.error(f"评估示例失败: {str(e)}")

        # 计算指标
        results["accuracy"] = correct_count / len(validation_data) if validation_data else 0.0
        results["correct"] = correct_count

        if llm_feedback_scores:
            results["llm_feedback_score"] = np.mean(llm_feedback_scores)

        # 高级指标
        if use_advanced_metrics and len(predictions) > 0:
            advanced_results = AdvancedMetrics.compute_all_metrics(
                predictions, references, task_type
            )
            results.update(advanced_results)

        return results

    def _evaluate_single_example(
        self, prompt: str, example: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估单个示例（用于并行评估）

        Args:
            prompt: 提示词
            example: 单个示例数据

        Returns:
            包含预测、参考答案、正确性等的字典
        """
        # 构建完整提示词
        full_prompt = self._construct_prompt(prompt, example["input"], example)

        # 获取模型响应（使用缓存）
        response = self._get_llm_response(full_prompt)

        # 提取答案
        extracted_answer = self._extract_answer(response)

        # 评估准确性
        is_correct = self._check_correctness(response, example["output"])

        result = {
            'prediction': extracted_answer,
            'reference': example["output"],
            'is_correct': is_correct,
            'response': response
        }

        # LLM反馈评分（可选）
        if self.config.use_llm_feedback:
            feedback_score = self._get_llm_feedback(
                prompt, example["input"], response, example["output"]
            )
            result['llm_feedback_score'] = feedback_score

        return result

    def _construct_prompt(self, prompt_template: str, input_text: str, example_data: Dict[str, Any] = None) -> str:
        """
        构建完整提示词（支持分层提示词架构）

        Args:
            prompt_template: 提示词模板（核心指令，待优化部分）
            input_text: 输入文本
            example_data: 完整的example数据（可能包含dynamic_context, dynamic_examples等）

        Returns:
            完整的提示词
        """
        parts = []
        structure = self.task.get_prompt_structure()

        for part_type in structure:
            if part_type == "core":
                # 核心指令（待优化部分）
                parts.append(prompt_template)

            elif part_type == "context":
                # 动态上下文（如果提供）
                if example_data and "dynamic_context" in example_data:
                    if self.task.context_template:
                        context_text = self.task.context_template.format(context=example_data["dynamic_context"])
                    else:
                        context_text = f"Context: {example_data['dynamic_context']}"
                    parts.append(context_text)

            elif part_type == "examples":
                # 动态示例（如果提供）
                if example_data and "dynamic_examples" in example_data:
                    examples_text = self._format_dynamic_examples(example_data["dynamic_examples"])
                    if examples_text:
                        parts.append(examples_text)

            elif part_type == "input":
                # 当前输入
                parts.append(f"Input: {input_text}\nOutput:")

            elif part_type == "options":
                # 动态选项（如果提供）
                if example_data and "options" in example_data:
                    options_text = self._format_options(example_data["options"])
                    if options_text:
                        parts.append(options_text)

        # 拼接所有非空部分
        return "\n\n".join([p for p in parts if p])

    def _format_dynamic_examples(self, examples: List[Dict[str, Any]]) -> str:
        """
        格式化动态示例

        Args:
            examples: 动态示例列表

        Returns:
            格式化后的示例文本
        """
        if not examples:
            return ""

        formatted_examples = []

        for idx, ex in enumerate(examples, 1):
            if self.task.example_template:
                # 使用自定义模板
                formatted = self.task.example_template.format(
                    index=idx,
                    input=ex.get("input", ""),
                    output=ex.get("output", ""),
                    **ex  # 支持其他字段
                )
            else:
                # 默认格式
                formatted = f"Example {idx}:\nInput: {ex.get('input', '')}\nOutput: {ex.get('output', '')}"

            formatted_examples.append(formatted)

        return "\n\n".join(formatted_examples)

    def _format_options(self, options: List[str]) -> str:
        """
        格式化选项

        Args:
            options: 选项列表，如 ["A. Python", "B. Java", "C. C++"]

        Returns:
            格式化后的选项文本
        """
        if not options:
            return ""

        if self.task.options_template:
            # 使用自定义模板
            options_str = "\n".join(options)
            return self.task.options_template.format(options=options_str)
        else:
            # 默认格式
            return "选项：\n" + "\n".join(options)

    def _get_llm_response(self, prompt: str) -> str:
        """
        调用LLM获取响应（使用缓存）

        Args:
            prompt: 输入提示词

        Returns:
            LLM响应
        """
        # 尝试从缓存获取
        cached_response = self.cache.get(prompt)
        if cached_response is not None:
            return cached_response

        # 缓存未命中，调用LLM
        response = self.llm_client.call(prompt)

        # 保存到缓存
        if response:
            self.cache.set(prompt, response)

        return response

    def _extract_answer(self, response: str) -> str:
        """
        从LLM响应中提取答案

        Args:
            response: LLM的原始响应

        Returns:
            提取的答案
        """
        if not response:
            return ""

        # 清理响应
        response_clean = response.strip()

        # 优先提取第一行
        first_line = response_clean.split('\n')[0].strip()

        # 如果第一行为空，提取第一个词
        if not first_line and response_clean.split():
            return response_clean.split()[0]

        return first_line if first_line else response_clean

    def _check_correctness(self, response: str, expected: str) -> bool:
        """检查响应是否正确"""
        if not response:
            return False

        # 清理响应
        response_clean = response.strip()

        # 方法1: 提取第一行（LLM通常在第一行给出答案）
        first_line = response_clean.split('\n')[0].strip()

        # 方法2: 提取第一个词
        first_word = response_clean.split()[0] if response_clean.split() else ""

        # 清理预期答案
        expected_clean = expected.strip().lower()

        # 尝试多种匹配方式
        # 1. 第一行完全匹配
        if first_line.lower() == expected_clean:
            return True

        # 2. 第一个词匹配
        if first_word.lower() == expected_clean:
            return True

        # 3. 包含匹配（作为最后手段）
        if expected_clean in response_clean.lower():
            return True

        return False

    def _get_llm_feedback(
        self, prompt: str, input_text: str, response: str, expected: str
    ) -> float:
        """
        使用LLM生成反馈评分

        Returns:
            0-1之间的分数
        """
        feedback_prompt = f"""
评估以下提示词和响应的质量：

提示词模板：{prompt}

输入：{input_text}
模型响应：{response}
期望输出：{expected}

请给出0-10的评分，并说明原因。仅返回数字评分。
"""
        # 调用LLM获取反馈评分
        feedback_response = self._get_llm_response(feedback_prompt)

        # 解析评分
        try:
            score = float(feedback_response.strip())
            return min(max(score / 10.0, 0.0), 1.0)  # 归一化到0-1
        except ValueError:
            return 0.5  # 默认中等分数

    def batch_evaluate(self, prompts: List[str], use_parallel: bool = False) -> List[Dict[str, float]]:
        """
        批量评估多个提示词

        Args:
            prompts: 提示词列表
            use_parallel: 是否使用并行评估

        Returns:
            评估结果列表
        """
        return [self.evaluate_prompt(prompt, use_parallel=use_parallel) for prompt in prompts]

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self.cache.get_stats()

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()

    def get_best_prompt(self, prompts: List[str]) -> str:
        """从候选中选择最佳提示词"""
        results = self.batch_evaluate(prompts)

        # 根据准确率排序
        best_idx = max(range(len(results)), key=lambda i: results[i]["accuracy"])

        return prompts[best_idx]


class MetricCalculator:
    """度量计算器 - 支持多种评估指标"""

    @staticmethod
    def accuracy(predictions: List[str], references: List[str]) -> float:
        """准确率"""
        if not predictions or len(predictions) != len(references):
            return 0.0
        correct = sum(p.strip() == r.strip() for p, r in zip(predictions, references))
        return correct / len(predictions)

    @staticmethod
    def f1_score(predictions: List[str], references: List[str]) -> float:
        """F1分数（简化版，适用于分类）"""
        # 实际使用时可以用sklearn的f1_score
        from collections import Counter

        pred_counter = Counter(predictions)
        ref_counter = Counter(references)

        # 简化的F1计算
        common = sum((pred_counter & ref_counter).values())
        if common == 0:
            return 0.0

        precision = common / sum(pred_counter.values())
        recall = common / sum(ref_counter.values())

        return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def bleu_score(predictions: List[str], references: List[str]) -> float:
        """
        BLEU分数（用于生成任务）

        Returns:
            平均BLEU分数
        """
        if len(predictions) != len(references):
            return 0.0

        scores = []
        for pred, ref in zip(predictions, references):
            score = AdvancedMetrics.bleu_score(pred, ref)
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    @staticmethod
    def rouge_score(predictions: List[str], references: List[str]) -> float:
        """
        ROUGE分数（用于摘要任务）

        Returns:
            平均ROUGE-L F1分数
        """
        if len(predictions) != len(references):
            return 0.0

        scores = []
        for pred, ref in zip(predictions, references):
            rouge_result = AdvancedMetrics.rouge_score(pred, ref, rouge_type="rouge-l")
            scores.append(rouge_result['f1'])

        return sum(scores) / len(scores) if scores else 0.0
