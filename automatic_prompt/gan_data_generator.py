"""
GAN启发的数据生成模块
使用生成对抗网络的思想生成高质量测试数据

核心思想：
- Generator (生成器): 生成新的测试样本
- Discriminator (判别器): 评估生成样本的质量
- Adversarial Training (对抗训练): 迭代优化生成器和判别器
"""
from typing import List, Dict, Any, Tuple
import random
import numpy as np
from config import Task, APOConfig
from llm_client import create_llm_client
from evaluator import Evaluator
import re


class DataGenerator:
    """
    数据生成器 (Generator)

    负责从少量示例生成新的测试样本
    """

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)
        self.generation_temperature = 0.9  # 初始温度

    def generate_samples(
        self,
        num_samples: int,
        reference_examples: List[Dict[str, str]] = None,
        diversity_boost: float = 0.0
    ) -> List[Dict[str, str]]:
        """
        生成新样本

        Args:
            num_samples: 要生成的样本数量
            reference_examples: 参考示例（如果为None则使用task.examples）
            diversity_boost: 多样性提升系数 (0.0-1.0)

        Returns:
            生成的样本列表
        """
        if reference_examples is None:
            reference_examples = self.task.examples

        # 调整温度以增加多样性
        temperature = min(1.5, self.generation_temperature + diversity_boost)

        print(f"\n🎲 生成器: 生成 {num_samples} 个样本 (温度={temperature:.2f})")

        # 构建生成提示
        examples_str = self._format_examples(reference_examples)

        generation_prompt = f"""
你是一个专业的测试数据生成专家。你的任务是根据给定的示例，生成更多高质量的测试样本。

任务描述: {self.task.description}

参考示例:
{examples_str}

要求:
1. 生成 {num_samples} 个新样本
2. 样本要与任务相关，但要有足够的多样性
3. 输入要覆盖不同的场景和边界情况
4. 输出必须正确且符合任务要求
5. 格式: 每行一个样本，格式为 "输入|||输出"
6. 不要重复参考示例中的内容

现在生成 {num_samples} 个样本:
"""

        # 调用LLM生成
        response = self.llm_client.call(
            generation_prompt,
            temperature=temperature,
            max_tokens=self.config.llm_max_tokens * 2
        )

        # 解析生成的样本
        samples = self._parse_samples(response)

        print(f"  ✓ 成功生成 {len(samples)} 个样本")

        return samples

    def improve_generation(self, feedback_score: float):
        """
        根据判别器反馈改进生成策略

        Args:
            feedback_score: 判别器给出的分数 (0.0-1.0)
        """
        # 如果分数低，增加多样性（提高温度）
        if feedback_score < 0.5:
            self.generation_temperature = min(1.5, self.generation_temperature + 0.1)
            print(f"  📈 生成器: 提高多样性 (温度 -> {self.generation_temperature:.2f})")
        # 如果分数高，保持或略微降低温度以提高质量
        elif feedback_score > 0.8:
            self.generation_temperature = max(0.7, self.generation_temperature - 0.05)
            print(f"  📉 生成器: 提高精确性 (温度 -> {self.generation_temperature:.2f})")

    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """格式化示例"""
        return "\n".join([
            f"  {i+1}. 输入: {ex['input']}\n     输出: {ex['output']}"
            for i, ex in enumerate(examples)
        ])

    def _parse_samples(self, response: str) -> List[Dict[str, str]]:
        """解析LLM生成的样本"""
        samples = []
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if "|||" in line:
                parts = line.split("|||")
                if len(parts) == 2:
                    samples.append({
                        "input": parts[0].strip(),
                        "output": parts[1].strip()
                    })

        return samples


class DataDiscriminator:
    """
    数据判别器 (Discriminator)

    使用多重机制评估生成样本的质量：
    1. LLM判别
    2. 特征相似度
    3. 任务性能评估
    """

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)
        self.evaluator = Evaluator(config, task)

        # 各评估方法的权重
        self.weights = {
            "llm_score": 0.4,
            "similarity_score": 0.3,
            "task_performance": 0.3
        }

    def discriminate(
        self,
        generated_samples: List[Dict[str, str]],
        real_samples: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        判别生成样本的质量

        Args:
            generated_samples: 生成的样本
            real_samples: 真实样本（用于对比）

        Returns:
            判别结果，包含总分和各项详细分数
        """
        if real_samples is None:
            real_samples = self.task.examples

        print(f"\n🔍 判别器: 评估 {len(generated_samples)} 个样本")

        results = {
            "llm_score": 0.0,
            "similarity_score": 0.0,
            "task_performance": 0.0,
            "overall_score": 0.0,
            "details": {}
        }

        # 1. LLM判别
        results["llm_score"] = self._llm_discriminate(generated_samples, real_samples)

        # 2. 特征相似度
        results["similarity_score"] = self._similarity_discriminate(
            generated_samples, real_samples
        )

        # 3. 任务性能评估
        results["task_performance"] = self._task_performance_discriminate(
            generated_samples
        )

        # 计算总分
        results["overall_score"] = (
            self.weights["llm_score"] * results["llm_score"] +
            self.weights["similarity_score"] * results["similarity_score"] +
            self.weights["task_performance"] * results["task_performance"]
        )

        self._print_discrimination_results(results)

        return results

    def _llm_discriminate(
        self,
        generated_samples: List[Dict[str, str]],
        real_samples: List[Dict[str, str]]
    ) -> float:
        """
        使用LLM判别样本质量

        让LLM判断生成的样本是否与真实样本相似，是否符合任务要求
        """
        # 随机选择几个样本进行判别（避免token过多）
        sample_size = min(5, len(generated_samples))
        samples_to_judge = random.sample(generated_samples, sample_size)

        real_examples_str = self._format_examples_for_discrimination(real_samples)
        generated_examples_str = self._format_examples_for_discrimination(
            samples_to_judge
        )

        discrimination_prompt = f"""
你是一个数据质量评估专家。请评估生成的测试样本质量。

任务描述: {self.task.description}

真实样本（参考标准）:
{real_examples_str}

生成的样本（待评估）:
{generated_examples_str}

请从以下几个维度评估生成样本的质量：
1. 相关性: 是否与任务相关
2. 正确性: 输出是否正确
3. 多样性: 是否覆盖不同场景
4. 真实性: 是否看起来像真实数据

请给出0-10分的评分，并简要说明理由。
格式: 分数|||理由

评估:
"""

        try:
            response = self.llm_client.call(discrimination_prompt, temperature=0.3)

            # 解析评分
            if "|||" in response:
                score_str = response.split("|||")[0].strip()
                # 提取数字
                score_match = re.search(r'(\d+(?:\.\d+)?)', score_str)
                if score_match:
                    score = float(score_match.group(1))
                    return min(1.0, score / 10.0)  # 归一化到 0-1

            # 如果解析失败，使用默认的启发式方法
            return self._heuristic_llm_score(samples_to_judge, real_samples)

        except Exception as e:
            print(f"  ⚠️  LLM判别失败: {e}")
            return self._heuristic_llm_score(samples_to_judge, real_samples)

    def _similarity_discriminate(
        self,
        generated_samples: List[Dict[str, str]],
        real_samples: List[Dict[str, str]]
    ) -> float:
        """
        基于特征相似度判别

        计算生成样本与真实样本的文本特征相似度
        """
        # 计算生成样本的特征统计
        gen_stats = self._compute_text_statistics(generated_samples)
        real_stats = self._compute_text_statistics(real_samples)

        # 计算各维度的相似度
        similarity_scores = []

        # 1. 平均长度相似度
        len_sim = 1.0 - abs(gen_stats["avg_input_len"] - real_stats["avg_input_len"]) / max(
            gen_stats["avg_input_len"], real_stats["avg_input_len"], 1
        )
        similarity_scores.append(len_sim)

        # 2. 输出分布相似度
        output_sim = self._compute_output_distribution_similarity(
            gen_stats["output_distribution"],
            real_stats["output_distribution"]
        )
        similarity_scores.append(output_sim)

        # 3. 词汇多样性相似度
        vocab_sim = 1.0 - abs(gen_stats["vocab_diversity"] - real_stats["vocab_diversity"])
        similarity_scores.append(vocab_sim)

        return sum(similarity_scores) / len(similarity_scores)

    def _task_performance_discriminate(
        self,
        generated_samples: List[Dict[str, str]]
    ) -> float:
        """
        基于任务性能判别

        使用当前最佳提示词在生成样本上测试，看性能是否合理
        """
        # 这里我们检查生成样本的内部一致性
        # 使用简单的提示词测试

        test_prompt = f"""
任务: {self.task.description}

请根据以上任务描述处理以下输入:
{{input}}

输出:
"""

        # 随机选择几个样本测试
        sample_size = min(3, len(generated_samples))
        test_samples = random.sample(generated_samples, sample_size)

        correct = 0
        for sample in test_samples:
            try:
                prompt = test_prompt.replace("{input}", sample["input"])
                response = self.llm_client.call(prompt, temperature=0.3)

                # 检查输出是否包含期望的答案
                if sample["output"].lower() in response.lower():
                    correct += 1
            except:
                pass

        return correct / sample_size if sample_size > 0 else 0.5

    def _compute_text_statistics(
        self,
        samples: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """计算文本统计特征"""
        if not samples:
            return {
                "avg_input_len": 0,
                "avg_output_len": 0,
                "output_distribution": {},
                "vocab_diversity": 0
            }

        input_lens = [len(s["input"]) for s in samples]
        output_lens = [len(s["output"]) for s in samples]

        # 输出分布
        output_dist = {}
        for s in samples:
            output = s["output"]
            output_dist[output] = output_dist.get(output, 0) + 1

        # 归一化
        total = len(samples)
        output_dist = {k: v/total for k, v in output_dist.items()}

        # 词汇多样性（唯一输出数 / 总样本数）
        vocab_diversity = len(output_dist) / total if total > 0 else 0

        return {
            "avg_input_len": sum(input_lens) / len(input_lens),
            "avg_output_len": sum(output_lens) / len(output_lens),
            "output_distribution": output_dist,
            "vocab_diversity": vocab_diversity
        }

    def _compute_output_distribution_similarity(
        self,
        dist1: Dict[str, float],
        dist2: Dict[str, float]
    ) -> float:
        """计算输出分布的相似度（使用KL散度的简化版本）"""
        if not dist1 or not dist2:
            return 0.0

        all_keys = set(dist1.keys()) | set(dist2.keys())

        # 计算差异
        diff = 0.0
        for key in all_keys:
            p1 = dist1.get(key, 0.0)
            p2 = dist2.get(key, 0.0)
            diff += abs(p1 - p2)

        # 转换为相似度
        return 1.0 - (diff / 2.0)

    def _heuristic_llm_score(
        self,
        generated_samples: List[Dict[str, str]],
        real_samples: List[Dict[str, str]]
    ) -> float:
        """启发式LLM评分（当LLM调用失败时使用）"""
        # 检查基本质量
        score = 0.5  # 基础分

        # 检查是否有空样本
        has_empty = any(
            not s["input"].strip() or not s["output"].strip()
            for s in generated_samples
        )
        if not has_empty:
            score += 0.2

        # 检查是否有重复
        inputs = [s["input"] for s in generated_samples]
        if len(inputs) == len(set(inputs)):
            score += 0.2

        # 检查输出是否合理
        real_outputs = set(s["output"] for s in real_samples)
        gen_outputs = set(s["output"] for s in generated_samples)

        # 生成样本的输出应该在真实样本的输出范围内（或接近）
        overlap = len(real_outputs & gen_outputs) / len(real_outputs) if real_outputs else 0
        score += 0.1 * overlap

        return min(1.0, score)

    def _format_examples_for_discrimination(
        self,
        examples: List[Dict[str, str]]
    ) -> str:
        """格式化示例用于判别"""
        return "\n".join([
            f"  输入: {ex['input']} -> 输出: {ex['output']}"
            for ex in examples
        ])

    def _print_discrimination_results(self, results: Dict[str, Any]):
        """打印判别结果"""
        print(f"  - LLM判别分数: {results['llm_score']:.3f}")
        print(f"  - 特征相似度: {results['similarity_score']:.3f}")
        print(f"  - 任务性能: {results['task_performance']:.3f}")
        print(f"  - 综合评分: {results['overall_score']:.3f}")


class GANDataGenerator:
    """
    GAN启发的数据生成器（主类）

    整合生成器和判别器，进行对抗训练
    """

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.generator = DataGenerator(config, task)
        self.discriminator = DataDiscriminator(config, task)

        # 训练历史
        self.training_history = []

    def generate_adversarial_data(
        self,
        target_size: int = 50,
        num_rounds: int = 3,
        quality_threshold: float = 0.7
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        使用对抗训练生成高质量数据

        Args:
            target_size: 目标生成的样本总数
            num_rounds: 对抗训练轮数
            quality_threshold: 质量阈值，低于此值的样本会被过滤

        Returns:
            (生成的高质量样本, 训练报告)
        """
        print("\n" + "="*70)
        print("🎯 GAN数据生成器 - 对抗训练开始")
        print("="*70)
        print(f"目标数量: {target_size}")
        print(f"训练轮数: {num_rounds}")
        print(f"质量阈值: {quality_threshold}")

        all_generated_samples = []

        for round_idx in range(num_rounds):
            print(f"\n{'='*70}")
            print(f"第 {round_idx + 1}/{num_rounds} 轮对抗训练")
            print(f"{'='*70}")

            # 计算本轮需要生成的样本数
            remaining = target_size - len(all_generated_samples)
            if remaining <= 0:
                break

            # 每轮生成一部分样本
            samples_this_round = min(remaining + 10, target_size // num_rounds + 10)

            # 生成器生成样本
            diversity_boost = round_idx * 0.1  # 每轮增加多样性
            generated = self.generator.generate_samples(
                num_samples=samples_this_round,
                diversity_boost=diversity_boost
            )

            if not generated:
                print("  ⚠️  生成失败，跳过本轮")
                continue

            # 判别器评估样本
            discrimination_result = self.discriminator.discriminate(
                generated,
                self.task.examples
            )

            # 记录训练历史
            self.training_history.append({
                "round": round_idx + 1,
                "generated_count": len(generated),
                "discrimination_score": discrimination_result["overall_score"]
            })

            # 生成器根据反馈调整
            self.generator.improve_generation(discrimination_result["overall_score"])

            # 过滤高质量样本
            if discrimination_result["overall_score"] >= quality_threshold:
                # 如果整体质量好，保留所有样本
                all_generated_samples.extend(generated)
                print(f"  ✓ 本轮样本质量优秀，保留全部 {len(generated)} 个样本")
            else:
                # 如果质量不够，只保留一部分
                kept = int(len(generated) * discrimination_result["overall_score"])
                all_generated_samples.extend(generated[:kept])
                print(f"  ⚠️  本轮样本质量一般，保留 {kept}/{len(generated)} 个样本")

        # 去重和最终质量控制
        final_samples = self._final_quality_control(
            all_generated_samples,
            target_size
        )

        # 生成报告
        report = self._generate_training_report(final_samples)

        print(f"\n{'='*70}")
        print(f"✅ 对抗训练完成")
        print(f"{'='*70}")
        print(f"生成样本总数: {len(final_samples)}")
        print(f"最终质量评分: {report['final_quality_score']:.3f}")

        return final_samples, report

    def _final_quality_control(
        self,
        samples: List[Dict[str, str]],
        target_size: int
    ) -> List[Dict[str, str]]:
        """最终质量控制"""
        print(f"\n🔧 执行最终质量控制...")

        # 去重
        unique_samples = []
        seen = set()

        for sample in samples:
            key = sample["input"] + "|||" + sample["output"]
            if key not in seen:
                seen.add(key)
                unique_samples.append(sample)

        removed_duplicates = len(samples) - len(unique_samples)
        if removed_duplicates > 0:
            print(f"  - 去除重复样本: {removed_duplicates} 个")

        # 过滤低质量样本
        quality_samples = [
            s for s in unique_samples
            if len(s["input"].strip()) >= 5 and len(s["output"].strip()) >= 1
        ]

        removed_low_quality = len(unique_samples) - len(quality_samples)
        if removed_low_quality > 0:
            print(f"  - 过滤低质量样本: {removed_low_quality} 个")

        # 如果样本过多，随机选择
        if len(quality_samples) > target_size:
            quality_samples = random.sample(quality_samples, target_size)
            print(f"  - 随机选择 {target_size} 个样本")

        print(f"  ✓ 最终保留: {len(quality_samples)} 个高质量样本")

        return quality_samples

    def _generate_training_report(
        self,
        final_samples: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """生成训练报告"""
        # 最终质量评估
        final_discrimination = self.discriminator.discriminate(
            final_samples,
            self.task.examples
        )

        report = {
            "total_rounds": len(self.training_history),
            "final_sample_count": len(final_samples),
            "final_quality_score": final_discrimination["overall_score"],
            "quality_breakdown": {
                "llm_score": final_discrimination["llm_score"],
                "similarity_score": final_discrimination["similarity_score"],
                "task_performance": final_discrimination["task_performance"]
            },
            "training_history": self.training_history
        }

        return report


def print_gan_report(report: Dict[str, Any]):
    """打印GAN训练报告"""
    print("\n" + "="*70)
    print("📊 GAN数据生成报告")
    print("="*70)
    print(f"\n训练轮数: {report['total_rounds']}")
    print(f"生成样本数: {report['final_sample_count']}")
    print(f"\n最终质量评分: {report['final_quality_score']:.3f}")
    print(f"  - LLM判别: {report['quality_breakdown']['llm_score']:.3f}")
    print(f"  - 特征相似度: {report['quality_breakdown']['similarity_score']:.3f}")
    print(f"  - 任务性能: {report['quality_breakdown']['task_performance']:.3f}")

    print(f"\n训练历史:")
    for record in report['training_history']:
        print(f"  轮次 {record['round']}: "
              f"生成 {record['generated_count']} 个, "
              f"质量 {record['discrimination_score']:.3f}")

    # 评级
    score = report['final_quality_score']
    if score >= 0.8:
        rating = "优秀 ⭐⭐⭐⭐⭐"
    elif score >= 0.7:
        rating = "良好 ⭐⭐⭐⭐"
    elif score >= 0.6:
        rating = "及格 ⭐⭐⭐"
    else:
        rating = "需改进 ⭐⭐"

    print(f"\n综合评级: {rating}")
    print("="*70)
