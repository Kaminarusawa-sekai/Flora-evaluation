"""
数据合成模块 - 自动生成测试样例

支持多种合成策略：
1. LLM生成
2. 模板变换
3. GAN对抗生成（新增）
"""
from typing import List, Dict, Any
from config import Task, APOConfig
from llm_client import create_llm_client
import random


class DataSynthesizer:
    """数据合成器 - 从少量示例生成更多测试数据"""

    def __init__(self, config: APOConfig):
        self.config = config
        self.llm_client = create_llm_client(config)

    def synthesize_data(
        self, task: Task, num_samples: int = 20, diversity_level: str = "medium",
        use_gan: bool = False
    ) -> List[Dict[str, str]]:
        """
        从少量示例合成更多测试数据

        Args:
            task: 任务定义（包含少量示例）
            num_samples: 要生成的样本数量
            diversity_level: 多样性级别 - "low", "medium", "high"
            use_gan: 是否使用GAN对抗生成（推荐）

        Returns:
            合成的数据列表 [{"input": "...", "output": "..."}, ...]
        """
        print(f"\n{'='*60}")
        print(f"开始数据合成：从 {len(task.examples)} 个示例生成 {num_samples} 个样本")
        if use_gan:
            print("使用策略: GAN对抗生成 ⚡")
        print(f"{'='*60}")

        # 策略1: 使用GAN对抗生成（最先进）
        if use_gan:
            synthetic_data = self._gan_based_synthesis(
                task, num_samples, diversity_level
            )
        # 策略2：使用LLM生成（最有效）
        elif self.config.llm_api_key:
            synthetic_data = self._llm_based_synthesis(
                task, num_samples, diversity_level
            )
        else:
            # 策略3：基于模板的变换（不需要LLM）
            print("⚠️  未提供LLM API，使用模板生成（质量较低）")
            synthetic_data = self._template_based_synthesis(task, num_samples)

        # 去重和质量检查
        synthetic_data = self._deduplicate(synthetic_data)
        synthetic_data = self._quality_filter(synthetic_data, task)

        print(f"✓ 成功生成 {len(synthetic_data)} 个高质量样本")

        return synthetic_data

    def _gan_based_synthesis(
        self, task: Task, num_samples: int, diversity_level: str
    ) -> List[Dict[str, str]]:
        """
        使用GAN对抗生成合成数据（推荐方法）

        策略：
        1. 使用生成器生成样本
        2. 使用判别器评估质量
        3. 迭代优化，确保高质量
        """
        try:
            # 延迟导入，避免循环依赖
            from gan_data_generator import GANDataGenerator

            print("📊 使用GAN对抗生成...")

            # 创建GAN生成器
            gan_generator = GANDataGenerator(self.config, task)

            # 根据多样性级别设置参数
            diversity_params = {
                "low": {"num_rounds": 2, "quality_threshold": 0.8},
                "medium": {"num_rounds": 3, "quality_threshold": 0.7},
                "high": {"num_rounds": 4, "quality_threshold": 0.6},
            }

            params = diversity_params.get(diversity_level, diversity_params["medium"])

            # 执行对抗训练生成
            synthetic_data, report = gan_generator.generate_adversarial_data(
                target_size=num_samples,
                num_rounds=params["num_rounds"],
                quality_threshold=params["quality_threshold"]
            )

            print(f"  GAN生成完成，质量评分: {report['final_quality_score']:.3f}")

            return synthetic_data

        except ImportError as e:
            print(f"⚠️  GAN模块导入失败: {e}")
            print("  回退到LLM生成方法...")
            return self._llm_based_synthesis(task, num_samples, diversity_level)
        except Exception as e:
            print(f"⚠️  GAN生成失败: {e}")
            print("  回退到LLM生成方法...")
            return self._llm_based_synthesis(task, num_samples, diversity_level)

    def _llm_based_synthesis(
        self, task: Task, num_samples: int, diversity_level: str
    ) -> List[Dict[str, str]]:
        """
        使用LLM生成合成数据（推荐方法）

        策略：
        1. 分析现有示例的模式
        2. 让LLM生成类似但不同的样例
        3. 确保多样性（通过温度参数和提示词）
        """
        # 构建示例字符串
        examples_str = "\n".join(
            [
                f"示例{i+1}:\n  输入: {ex['input']}\n  输出: {ex['output']}"
                for i, ex in enumerate(task.examples)
            ]
        )

        # 根据多样性级别设置参数
        diversity_params = {
            "low": {"temperature": 0.7, "variety_instruction": "保持相似风格"},
            "medium": {"temperature": 0.9, "variety_instruction": "适度变化，涵盖不同场景"},
            "high": {"temperature": 1.1, "variety_instruction": "最大化多样性，探索边界情况"},
        }

        params = diversity_params.get(diversity_level, diversity_params["medium"])

        # 构建生成提示词
        synthesis_prompt = f"""
你是一个数据生成专家。给定以下任务和示例，请生成{num_samples}个新的测试样例。

任务描述：{task.description}

现有示例：
{examples_str}

要求：
1. 生成的样例要与任务相关
2. {params['variety_instruction']}
3. 输入要有代表性，覆盖不同情况
4. 输出必须正确
5. 每个样例格式：输入|||输出

请直接生成{num_samples}个样例，每行一个，格式严格为：输入|||输出
不要包含编号、解释或其他内容。

样例：
"""

        # 调用LLM生成
        response = self._call_llm(synthesis_prompt, temperature=params['temperature'])
        if response:
            print(f"📝 使用LLM生成数据（温度={params['temperature']}）...")
            return self._parse_generated_samples(response)
        else:
            # 如果API调用失败，使用模拟生成
            print("⚠️  LLM调用失败，使用模拟生成...")
            return self._mock_llm_generation(task, num_samples)

    def _parse_generated_samples(self, llm_response: str) -> List[Dict[str, str]]:
        """
        解析LLM生成的样本

        期望格式：
        输入1|||输出1
        输入2|||输出2
        ...
        """
        samples = []
        lines = llm_response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if "|||" in line:
                parts = line.split("|||")
                if len(parts) == 2:
                    samples.append(
                        {"input": parts[0].strip(), "output": parts[1].strip()}
                    )

        return samples

    def _template_based_synthesis(
        self, task: Task, num_samples: int
    ) -> List[Dict[str, str]]:
        """
        基于模板的数据生成（不需要LLM，但质量较低）

        策略：
        1. 提取示例中的模式
        2. 使用变换规则生成新样例
        3. 词汇替换、句式变换等
        """
        synthetic_data = []

        # 简单策略：基于现有示例进行变换
        transformations = [
            self._paraphrase_simple,
            self._synonym_replacement,
            self._sentence_reorder,
            self._add_modifiers,
        ]

        examples = task.examples
        while len(synthetic_data) < num_samples:
            # 随机选择一个示例
            base_example = random.choice(examples)

            # 随机选择一个变换
            transform = random.choice(transformations)

            # 应用变换
            new_example = transform(base_example)

            if new_example and new_example not in synthetic_data:
                synthetic_data.append(new_example)

        return synthetic_data[:num_samples]

    def _paraphrase_simple(self, example: Dict[str, str]) -> Dict[str, str]:
        """简单的改写"""
        # 这里需要更复杂的NLP技术，这只是占位符
        input_text = example["input"]

        # 简单的词汇替换
        replacements = {
            "很": "非常",
            "好": "不错",
            "差": "糟糕",
            "喜欢": "满意",
            "不喜欢": "不满意",
        }

        new_input = input_text
        for old, new in replacements.items():
            if old in new_input:
                new_input = new_input.replace(old, new, 1)
                break

        if new_input != input_text:
            return {"input": new_input, "output": example["output"]}

        return None

    def _synonym_replacement(self, example: Dict[str, str]) -> Dict[str, str]:
        """同义词替换"""
        # 简化实现
        synonyms = {
            "产品": ["商品", "货物"],
            "服务": ["接待", "待遇"],
            "质量": ["品质", "质地"],
            "价格": ["价钱", "费用"],
        }

        input_text = example["input"]
        new_input = input_text

        for word, syns in synonyms.items():
            if word in new_input:
                new_input = new_input.replace(word, random.choice(syns), 1)
                break

        if new_input != input_text:
            return {"input": new_input, "output": example["output"]}

        return None

    def _sentence_reorder(self, example: Dict[str, str]) -> Dict[str, str]:
        """句子重排（适用于多句输入）"""
        input_text = example["input"]
        sentences = [s.strip() for s in input_text.split("。") if s.strip()]

        if len(sentences) > 1:
            random.shuffle(sentences)
            new_input = "。".join(sentences) + "。"
            return {"input": new_input, "output": example["output"]}

        return None

    def _add_modifiers(self, example: Dict[str, str]) -> Dict[str, str]:
        """添加修饰语"""
        modifiers = ["真的", "确实", "实在是", "非常", "特别"]

        input_text = example["input"]
        modifier = random.choice(modifiers)

        # 简单地在开头添加
        new_input = modifier + input_text

        return {"input": new_input, "output": example["output"]}

    def _deduplicate(self, samples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """去重"""
        seen = set()
        unique_samples = []

        for sample in samples:
            key = sample["input"] + "|||" + sample["output"]
            if key not in seen:
                seen.add(key)
                unique_samples.append(sample)

        removed = len(samples) - len(unique_samples)
        if removed > 0:
            print(f"  去除了 {removed} 个重复样本")

        return unique_samples

    def _quality_filter(
        self, samples: List[Dict[str, str]], task: Task
    ) -> List[Dict[str, str]]:
        """
        质量过滤

        检查：
        1. 输入输出不为空
        2. 长度合理
        3. 与原始示例不太相似（避免过拟合）
        """
        filtered = []

        for sample in samples:
            # 检查1：非空
            if not sample["input"].strip() or not sample["output"].strip():
                continue

            # 检查2：长度合理
            if len(sample["input"]) < 5 or len(sample["input"]) > 500:
                continue

            # 检查3：与原始示例不完全相同
            is_duplicate = any(
                sample["input"] == ex["input"] for ex in task.examples
            )
            if is_duplicate:
                continue

            filtered.append(sample)

        removed = len(samples) - len(filtered)
        if removed > 0:
            print(f"  过滤了 {removed} 个低质量样本")

        return filtered

    def _mock_llm_generation(
        self, task: Task, num_samples: int
    ) -> List[Dict[str, str]]:
        """
        模拟LLM生成（实际使用时应该调用真实LLM）

        这是一个占位符实现，用于演示
        """
        print("  [模拟模式] 实际使用时请配置LLM API")

        # 基于示例生成一些变体
        synthetic = []
        base_examples = task.examples

        # 如果是情感分析任务
        if "情感" in task.name.lower() or "sentiment" in task.name.lower():
            positive_templates = [
                "这个{}非常好",
                "{}的体验很棒",
                "对{}很满意",
                "{}质量上乘",
                "推荐这个{}",
            ]
            negative_templates = [
                "这个{}很差",
                "{}让人失望",
                "不满意这个{}",
                "{}质量堪忧",
                "不推荐{}",
            ]

            items = ["产品", "服务", "体验", "店铺", "餐厅", "商品", "课程", "软件"]

            for _ in range(num_samples // 2):
                item = random.choice(items)
                synthetic.append(
                    {
                        "input": random.choice(positive_templates).format(item),
                        "output": "positive"
                        if "积极" in task.description
                        else "积极",
                    }
                )
                synthetic.append(
                    {
                        "input": random.choice(negative_templates).format(item),
                        "output": "negative"
                        if "消极" in task.description
                        else "消极",
                    }
                )

        # 如果是数学任务
        elif "数学" in task.name.lower() or "math" in task.name.lower():
            for _ in range(num_samples):
                a, b = random.randint(1, 20), random.randint(1, 20)
                ops = [
                    (f"{a}加{b}等于多少？", a + b),
                    (f"{a + b}减{b}等于多少？", a),
                    (f"{a}乘以{b}等于多少？", a * b),
                ]
                op = random.choice(ops)
                synthetic.append({"input": op[0], "output": str(op[1])})

        else:
            # 通用方法：复制和轻微变换现有示例
            for _ in range(num_samples):
                base = random.choice(base_examples)
                # 简单复制（实际应该更智能）
                synthetic.append(base.copy())

        return synthetic[:num_samples]

    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """
        调用LLM API

        Args:
            prompt: 输入提示词
            temperature: 温度参数

        Returns:
            LLM生成的文本
        """
        # 数据合成需要更多token
        max_tokens = self.config.llm_max_tokens * 3
        return self.llm_client.call(prompt, temperature=temperature, max_tokens=max_tokens)

    def augment_validation_data(
        self, task: Task, target_size: int = 50
    ) -> List[Dict[str, str]]:
        """
        增强验证数据

        如果现有验证数据不足，自动生成更多

        Args:
            task: 任务定义
            target_size: 目标验证集大小

        Returns:
            增强后的验证数据
        """
        current_size = len(task.validation_data)

        if current_size >= target_size:
            print(f"验证数据已足够（{current_size}个），无需增强")
            return task.validation_data

        needed = target_size - current_size
        print(f"验证数据不足，需要生成 {needed} 个额外样本")

        # 生成新样本
        synthetic = self.synthesize_data(task, num_samples=needed, diversity_level="high")

        # 合并
        augmented = task.validation_data + synthetic

        print(f"✓ 验证数据增强完成：{current_size} -> {len(augmented)}")

        return augmented


class DataQualityChecker:
    """数据质量检查器"""

    @staticmethod
    def check_data_quality(data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        检查数据质量

        Returns:
            质量报告
        """
        report = {
            "total_samples": len(data),
            "avg_input_length": 0,
            "avg_output_length": 0,
            "unique_outputs": 0,
            "empty_samples": 0,
            "quality_score": 0.0,
        }

        if not data:
            return report

        input_lengths = [len(d["input"]) for d in data]
        output_lengths = [len(d["output"]) for d in data]

        report["avg_input_length"] = sum(input_lengths) / len(input_lengths)
        report["avg_output_length"] = sum(output_lengths) / len(output_lengths)
        report["unique_outputs"] = len(set(d["output"] for d in data))
        report["empty_samples"] = sum(
            1 for d in data if not d["input"].strip() or not d["output"].strip()
        )

        # 计算质量分数（0-1）
        quality_factors = []

        # 因素1：样本数量
        quality_factors.append(min(len(data) / 50, 1.0))

        # 因素2：输出多样性
        diversity = report["unique_outputs"] / len(data) if len(data) > 0 else 0
        quality_factors.append(diversity)

        # 因素3：无空样本
        no_empty = 1.0 - (report["empty_samples"] / len(data))
        quality_factors.append(no_empty)

        report["quality_score"] = sum(quality_factors) / len(quality_factors)

        return report

    @staticmethod
    def print_quality_report(report: Dict[str, Any]):
        """打印质量报告"""
        print("\n" + "=" * 60)
        print("数据质量报告")
        print("=" * 60)
        print(f"总样本数: {report['total_samples']}")
        print(f"平均输入长度: {report['avg_input_length']:.1f}")
        print(f"平均输出长度: {report['avg_output_length']:.1f}")
        print(f"唯一输出数: {report['unique_outputs']}")
        print(f"空样本数: {report['empty_samples']}")
        print(f"质量分数: {report['quality_score']:.2f} {'✓' if report['quality_score'] > 0.7 else '⚠️'}")
        print("=" * 60)
