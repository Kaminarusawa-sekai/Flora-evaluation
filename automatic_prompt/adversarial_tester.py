"""
对抗性测试模块
测试提示词的鲁棒性和泛化能力
"""
from typing import List, Dict, Any, Callable
import random
import re
from config import APOConfig, Task
from evaluator import Evaluator
from llm_client import create_llm_client


class AdversarialTester:
    """对抗性测试器"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)
        self.evaluator = Evaluator(config, task)

    def test_robustness(
        self,
        prompt: str,
        test_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        全面测试提示词的鲁棒性

        Args:
            prompt: 待测试的提示词
            test_types: 测试类型列表，如果为None则运行所有测试

        Returns:
            鲁棒性测试报告
        """
        if test_types is None:
            test_types = [
                "noise",
                "paraphrase",
                "length_variation",
                "case_variation",
                "adversarial_examples"
            ]

        report = {
            "original_prompt": prompt,
            "baseline_score": None,
            "robustness_tests": {}
        }

        # 基线性能
        baseline_result = self.evaluator.evaluate_prompt(prompt)
        report["baseline_score"] = baseline_result.get("accuracy", 0.0)

        # 运行各种测试
        if "noise" in test_types:
            report["robustness_tests"]["noise"] = self.test_with_noise(prompt)

        if "paraphrase" in test_types:
            report["robustness_tests"]["paraphrase"] = self.test_with_paraphrase(prompt)

        if "length_variation" in test_types:
            report["robustness_tests"]["length_variation"] = self.test_length_variation(prompt)

        if "case_variation" in test_types:
            report["robustness_tests"]["case_variation"] = self.test_case_variation(prompt)

        if "adversarial_examples" in test_types:
            report["robustness_tests"]["adversarial"] = self.test_adversarial_examples(prompt)

        # 计算总体鲁棒性分数
        report["robustness_score"] = self._compute_robustness_score(report)

        return report

    def test_with_noise(self, prompt: str) -> Dict[str, Any]:
        """
        测试输入噪声的鲁棒性

        Args:
            prompt: 提示词

        Returns:
            噪声测试结果
        """
        # 创建带噪声的验证数据
        noisy_data = []
        for example in self.task.validation_data:
            # 添加不同类型的噪声
            noisy_inputs = [
                self._add_typos(example["input"]),
                self._add_extra_spaces(example["input"]),
                self._add_punctuation_noise(example["input"])
            ]

            for noisy_input in noisy_inputs:
                noisy_data.append({
                    "input": noisy_input,
                    "output": example["output"]
                })

        # 在带噪声的数据上评估
        result = self.evaluator.evaluate_prompt(prompt, noisy_data)

        return {
            "score": result.get("accuracy", 0.0),
            "num_examples": len(noisy_data),
            "description": "测试对输入噪声的鲁棒性（拼写错误、多余空格等）"
        }

    def test_with_paraphrase(self, prompt: str) -> Dict[str, Any]:
        """
        测试对改写输入的鲁棒性

        Args:
            prompt: 提示词

        Returns:
            改写测试结果
        """
        # 使用LLM生成改写版本
        paraphrased_data = []

        for example in self.task.validation_data[:5]:  # 限制数量以节省API调用
            try:
                paraphrase_prompt = f"""
请将以下文本改写，保持原意但使用不同的表达方式：

原文: {example["input"]}

改写（只输出改写后的文本，不要任何解释）:
"""
                paraphrased = self.llm_client.call(paraphrase_prompt)
                paraphrased_data.append({
                    "input": paraphrased.strip(),
                    "output": example["output"]
                })
            except Exception:
                # 如果LLM调用失败，使用简单的改写
                paraphrased_data.append({
                    "input": self._simple_paraphrase(example["input"]),
                    "output": example["output"]
                })

        if paraphrased_data:
            result = self.evaluator.evaluate_prompt(prompt, paraphrased_data)
            score = result.get("accuracy", 0.0)
        else:
            score = 0.0

        return {
            "score": score,
            "num_examples": len(paraphrased_data),
            "description": "测试对改写输入的鲁棒性"
        }

    def test_length_variation(self, prompt: str) -> Dict[str, Any]:
        """
        测试对不同输入长度的鲁棒性

        Args:
            prompt: 提示词

        Returns:
            长度变化测试结果
        """
        # 创建不同长度的输入
        varied_data = []

        for example in self.task.validation_data:
            original_input = example["input"]

            # 缩短版本
            shortened = self._shorten_text(original_input)
            if shortened != original_input:
                varied_data.append({
                    "input": shortened,
                    "output": example["output"]
                })

            # 扩展版本
            extended = self._extend_text(original_input)
            varied_data.append({
                "input": extended,
                "output": example["output"]
            })

        result = self.evaluator.evaluate_prompt(prompt, varied_data)

        return {
            "score": result.get("accuracy", 0.0),
            "num_examples": len(varied_data),
            "description": "测试对不同输入长度的鲁棒性"
        }

    def test_case_variation(self, prompt: str) -> Dict[str, Any]:
        """
        测试对大小写变化的鲁棒性

        Args:
            prompt: 提示词

        Returns:
            大小写测试结果
        """
        # 创建不同大小写的输入
        case_data = []

        for example in self.task.validation_data:
            # 全大写
            case_data.append({
                "input": example["input"].upper(),
                "output": example["output"]
            })

            # 全小写
            case_data.append({
                "input": example["input"].lower(),
                "output": example["output"]
            })

            # 随机大小写
            case_data.append({
                "input": self._random_case(example["input"]),
                "output": example["output"]
            })

        result = self.evaluator.evaluate_prompt(prompt, case_data)

        return {
            "score": result.get("accuracy", 0.0),
            "num_examples": len(case_data),
            "description": "测试对大小写变化的鲁棒性"
        }

    def test_adversarial_examples(self, prompt: str) -> Dict[str, Any]:
        """
        测试对抗样本

        Args:
            prompt: 提示词

        Returns:
            对抗样本测试结果
        """
        # 生成对抗样本
        adversarial_data = []

        for example in self.task.validation_data[:3]:  # 限制数量
            # 添加混淆信息
            adversarial_input = self._add_confusing_info(example["input"])
            adversarial_data.append({
                "input": adversarial_input,
                "output": example["output"]
            })

        if adversarial_data:
            result = self.evaluator.evaluate_prompt(prompt, adversarial_data)
            score = result.get("accuracy", 0.0)
        else:
            score = 0.0

        return {
            "score": score,
            "num_examples": len(adversarial_data),
            "description": "测试对抗样本（包含混淆信息）"
        }

    # 辅助方法：添加各种扰动

    def _add_typos(self, text: str) -> str:
        """添加拼写错误"""
        words = text.split()
        if len(words) < 2:
            return text

        # 随机选择一个词添加错误
        idx = random.randint(0, len(words) - 1)
        word = words[idx]

        if len(word) > 2:
            # 交换两个相邻字符
            pos = random.randint(0, len(word) - 2)
            word_list = list(word)
            word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
            words[idx] = ''.join(word_list)

        return ' '.join(words)

    def _add_extra_spaces(self, text: str) -> str:
        """添加额外空格"""
        words = text.split()
        # 在随机位置添加双空格
        return '  '.join(words)

    def _add_punctuation_noise(self, text: str) -> str:
        """添加标点噪声"""
        # 随机添加或删除标点
        if random.random() > 0.5:
            return text + random.choice(['!', '?', '...', ''])
        else:
            return text.rstrip(',.!?')

    def _simple_paraphrase(self, text: str) -> str:
        """简单改写"""
        # 替换一些常见词
        replacements = {
            '好': '不错',
            '差': '糟糕',
            '很': '非常',
            '的': '之',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def _shorten_text(self, text: str) -> str:
        """缩短文本"""
        words = text.split()
        if len(words) <= 3:
            return text

        # 保留前一半
        return ' '.join(words[:len(words)//2])

    def _extend_text(self, text: str) -> str:
        """扩展文本"""
        extensions = [
            "请注意这一点。",
            "这很重要。",
            "需要仔细考虑。"
        ]
        return text + " " + random.choice(extensions)

    def _random_case(self, text: str) -> str:
        """随机大小写"""
        return ''.join(
            c.upper() if random.random() > 0.5 else c.lower()
            for c in text
        )

    def _add_confusing_info(self, text: str) -> str:
        """添加混淆信息"""
        confusing_phrases = [
            "虽然有人认为不是这样，但",
            "尽管看起来相反，",
            "与通常的看法不同，"
        ]
        return random.choice(confusing_phrases) + text

    def _compute_robustness_score(self, report: Dict[str, Any]) -> float:
        """计算总体鲁棒性分数"""
        baseline = report["baseline_score"]
        tests = report["robustness_tests"]

        if not tests:
            return 0.0

        # 计算各测试的平均分数
        scores = [test_result["score"] for test_result in tests.values()]
        avg_score = sum(scores) / len(scores)

        # 鲁棒性 = 测试平均分 / 基线分（避免除零）
        if baseline > 0:
            robustness = avg_score / baseline
        else:
            robustness = 0.0

        return robustness


def print_robustness_report(report: Dict[str, Any]):
    """
    打印鲁棒性测试报告

    Args:
        report: 测试报告
    """
    print("\n" + "="*70)
    print("鲁棒性测试报告")
    print("="*70)
    print(f"\n基线性能: {report['baseline_score']:.2%}")
    print(f"鲁棒性分数: {report['robustness_score']:.2%}")

    print("\n各项测试结果:")
    for test_name, test_result in report["robustness_tests"].items():
        print(f"\n  {test_name}:")
        print(f"    分数: {test_result['score']:.2%}")
        print(f"    样本数: {test_result['num_examples']}")
        print(f"    说明: {test_result['description']}")

    print("\n" + "="*70)

    # 给出评级
    robustness = report['robustness_score']
    if robustness >= 0.9:
        rating = "优秀 ⭐⭐⭐⭐⭐"
    elif robustness >= 0.7:
        rating = "良好 ⭐⭐⭐⭐"
    elif robustness >= 0.5:
        rating = "一般 ⭐⭐⭐"
    elif robustness >= 0.3:
        rating = "较差 ⭐⭐"
    else:
        rating = "很差 ⭐"

    print(f"\n鲁棒性评级: {rating}")
    print("="*70)
