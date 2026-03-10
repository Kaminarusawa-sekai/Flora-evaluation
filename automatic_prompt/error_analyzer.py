"""
错误分析模块
分析提示词的失败案例，提供改进建议
"""
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import numpy as np
from config import APOConfig, Task
from evaluator import Evaluator
from llm_client import create_llm_client


class ErrorAnalyzer:
    """错误分析器"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)

    def analyze_errors(
        self,
        prompt: str,
        validation_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析提示词的错误

        Args:
            prompt: 待分析的提示词
            validation_data: 验证数据

        Returns:
            错误分析报告
        """
        if validation_data is None:
            validation_data = self.task.validation_data

        # 收集所有预测和实际结果
        errors = []
        correct_cases = []

        for example in validation_data:
            full_prompt = self._construct_prompt(prompt, example["input"])
            response = self.llm_client.call(full_prompt)

            extracted_answer = self._extract_answer(response)
            expected = example["output"]

            if not self._is_correct(extracted_answer, expected):
                errors.append({
                    "input": example["input"],
                    "expected": expected,
                    "predicted": extracted_answer,
                    "raw_response": response
                })
            else:
                correct_cases.append({
                    "input": example["input"],
                    "output": expected,
                    "response": response
                })

        # 生成分析报告
        report = {
            "total_examples": len(validation_data),
            "num_errors": len(errors),
            "num_correct": len(correct_cases),
            "error_rate": len(errors) / len(validation_data) if validation_data else 0,
            "errors": errors,
            "error_patterns": self._analyze_error_patterns(errors),
            "suggestions": self._generate_suggestions(errors, correct_cases, prompt)
        }

        return report

    def _analyze_error_patterns(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析错误模式

        Args:
            errors: 错误案例列表

        Returns:
            错误模式分析
        """
        if not errors:
            return {}

        patterns = {
            "most_common_mistakes": Counter(),
            "error_by_expected": defaultdict(list),
            "error_by_predicted": defaultdict(list),
            "input_characteristics": {}
        }

        # 统计错误类型
        for error in errors:
            expected = error["expected"]
            predicted = error["predicted"]

            # 记录期望->实际的映射
            patterns["error_by_expected"][expected].append(predicted)

            # 记录预测值
            patterns["most_common_mistakes"][(expected, predicted)] += 1

            # 记录按预测值分组的错误
            patterns["error_by_predicted"][predicted].append(expected)

        # 分析输入特征
        patterns["input_characteristics"] = self._analyze_input_characteristics(errors)

        return patterns

    def _analyze_input_characteristics(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析错误案例的输入特征"""
        if not errors:
            return {}

        # 分析输入长度
        lengths = [len(error["input"].split()) for error in errors]

        # 分析输入中的关键词
        all_words = []
        for error in errors:
            words = error["input"].lower().split()
            all_words.extend(words)

        word_freq = Counter(all_words)

        return {
            "avg_input_length": np.mean(lengths),
            "min_input_length": min(lengths),
            "max_input_length": max(lengths),
            "common_words": word_freq.most_common(10)
        }

    def _generate_suggestions(
        self,
        errors: List[Dict[str, Any]],
        correct_cases: List[Dict[str, Any]],
        current_prompt: str
    ) -> List[str]:
        """
        生成改进建议

        Args:
            errors: 错误案例
            correct_cases: 正确案例
            current_prompt: 当前提示词

        Returns:
            改进建议列表
        """
        suggestions = []

        if not errors:
            suggestions.append("当前提示词表现完美，无需改进！")
            return suggestions

        error_rate = len(errors) / (len(errors) + len(correct_cases))

        # 基于错误率的建议
        if error_rate > 0.5:
            suggestions.append("错误率较高，建议从根本上重新设计提示词")
            suggestions.append("考虑添加更详细的任务说明和示例")

        # 基于错误模式的建议
        error_patterns = self._analyze_error_patterns(errors)

        # 检查是否有混淆的类别
        error_by_expected = error_patterns.get("error_by_expected", {})
        for expected, predicted_list in error_by_expected.items():
            predicted_counter = Counter(predicted_list)
            most_common_mistake = predicted_counter.most_common(1)[0]
            if most_common_mistake[1] > 1:  # 多次犯同样的错误
                suggestions.append(
                    f"模型经常将'{expected}'误判为'{most_common_mistake[0]}'，"
                    f"建议在提示词中明确区分这两个类别"
                )

        # 基于输入特征的建议
        input_chars = error_patterns.get("input_characteristics", {})
        if input_chars:
            avg_length = input_chars.get("avg_input_length", 0)
            if avg_length > 20:
                suggestions.append("错误案例的输入较长，考虑添加'仔细阅读'等指导")
            elif avg_length < 5:
                suggestions.append("错误案例的输入较短，可能需要更多上下文理解")

        # 使用LLM生成建议（如果启用）
        if self.config.use_llm_feedback and len(errors) > 0:
            llm_suggestions = self._get_llm_suggestions(errors, current_prompt)
            if llm_suggestions:
                suggestions.extend(llm_suggestions)

        return suggestions if suggestions else ["无具体建议"]

    def _get_llm_suggestions(
        self,
        errors: List[Dict[str, Any]],
        current_prompt: str
    ) -> List[str]:
        """使用LLM生成改进建议"""
        # 选择最多3个错误案例
        sample_errors = errors[:3]

        error_examples = "\n".join([
            f"输入: {e['input']}\n期望: {e['expected']}\n实际: {e['predicted']}\n"
            for e in sample_errors
        ])

        analysis_prompt = f"""
作为提示词优化专家，请分析以下提示词的错误案例并提供改进建议。

当前提示词:
{current_prompt}

错误案例:
{error_examples}

请提供3-5条具体的改进建议，每条建议一行。
只输出建议，不需要解释。
"""

        try:
            response = self.llm_client.call(analysis_prompt)
            # 解析建议
            suggestions = [
                line.strip().lstrip('0123456789.-) ')
                for line in response.split('\n')
                if line.strip() and len(line.strip()) > 10
            ]
            return suggestions[:5]
        except Exception as e:
            return [f"LLM分析失败: {str(e)}"]

    def compare_prompts(
        self,
        prompt1: str,
        prompt2: str,
        validation_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        对比两个提示词的表现

        Args:
            prompt1: 第一个提示词
            prompt2: 第二个提示词
            validation_data: 验证数据

        Returns:
            对比报告
        """
        if validation_data is None:
            validation_data = self.task.validation_data

        # 分析两个提示词
        report1 = self.analyze_errors(prompt1, validation_data)
        report2 = self.analyze_errors(prompt2, validation_data)

        # 找出差异
        errors1_inputs = set(e["input"] for e in report1["errors"])
        errors2_inputs = set(e["input"] for e in report2["errors"])

        # 只有prompt1错误的
        only_prompt1_errors = errors1_inputs - errors2_inputs

        # 只有prompt2错误的
        only_prompt2_errors = errors2_inputs - errors1_inputs

        # 都错误的
        both_errors = errors1_inputs & errors2_inputs

        comparison = {
            "prompt1_error_rate": report1["error_rate"],
            "prompt2_error_rate": report2["error_rate"],
            "improvement": report1["error_rate"] - report2["error_rate"],
            "only_prompt1_errors": len(only_prompt1_errors),
            "only_prompt2_errors": len(only_prompt2_errors),
            "both_errors": len(both_errors),
            "winner": "prompt2" if report2["error_rate"] < report1["error_rate"] else "prompt1",
            "prompt1_details": report1,
            "prompt2_details": report2
        }

        return comparison

    def explain_prediction(
        self,
        prompt: str,
        input_text: str,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        解释单个预测

        Args:
            prompt: 提示词
            input_text: 输入文本
            use_llm: 是否使用LLM解释

        Returns:
            解释报告
        """
        # 获取预测
        full_prompt = self._construct_prompt(prompt, input_text)
        response = self.llm_client.call(full_prompt)
        prediction = self._extract_answer(response)

        explanation = {
            "input": input_text,
            "prompt": prompt,
            "prediction": prediction,
            "raw_response": response
        }

        # 使用LLM生成解释
        if use_llm:
            explain_prompt = f"""
解释以下AI预测的reasoning过程：

提示词: {prompt}
输入: {input_text}
输出: {prediction}

请简要说明AI可能是基于什么理由做出这个预测的。
"""
            try:
                llm_explanation = self.llm_client.call(explain_prompt)
                explanation["llm_explanation"] = llm_explanation
            except Exception as e:
                explanation["llm_explanation"] = f"解释生成失败: {str(e)}"

        return explanation

    def _construct_prompt(self, prompt_template: str, input_text: str) -> str:
        """构建完整提示词"""
        return f"{prompt_template}\n\nInput: {input_text}\nOutput:"

    def _extract_answer(self, response: str) -> str:
        """从响应中提取答案"""
        if not response:
            return ""
        first_line = response.strip().split('\n')[0].strip()
        return first_line if first_line else response.strip()

    def _is_correct(self, prediction: str, expected: str) -> bool:
        """判断预测是否正确"""
        return prediction.lower().strip() == expected.lower().strip()


# 便捷函数

def analyze_prompt_errors(
    config: APOConfig,
    task: Task,
    prompt: str
) -> Dict[str, Any]:
    """
    便捷的错误分析函数

    Args:
        config: 配置
        task: 任务
        prompt: 提示词

    Returns:
        错误分析报告
    """
    analyzer = ErrorAnalyzer(config, task)
    return analyzer.analyze_errors(prompt)


def print_error_report(report: Dict[str, Any]):
    """
    打印错误报告

    Args:
        report: 错误分析报告
    """
    print("\n" + "="*70)
    print("错误分析报告")
    print("="*70)
    print(f"\n总样本数: {report['total_examples']}")
    print(f"错误数: {report['num_errors']}")
    print(f"正确数: {report['num_correct']}")
    print(f"错误率: {report['error_rate']:.2%}")

    if report['errors']:
        print("\n错误案例示例:")
        for i, error in enumerate(report['errors'][:3], 1):
            print(f"\n  {i}. 输入: {error['input']}")
            print(f"     期望: {error['expected']}")
            print(f"     实际: {error['predicted']}")

    if report.get('suggestions'):
        print("\n改进建议:")
        for i, suggestion in enumerate(report['suggestions'], 1):
            print(f"  {i}. {suggestion}")

    print("="*70)
