"""
候选生成模块 - 生成优化后的提示词候选
"""
from typing import List, Dict, Any
import random
from config import APOConfig, Task
from llm_client import create_llm_client


class CandidateGenerator:
    """候选提示词生成器"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)

    def generate_candidates(
        self, current_prompts: List[str], feedback: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        生成新的候选提示词

        Args:
            current_prompts: 当前的提示词列表
            feedback: 评估反馈信息

        Returns:
            新的候选提示词列表
        """
        strategy = self.config.generation_strategy

        if strategy == "llm_rewrite":
            return self._llm_rewrite(current_prompts, feedback)
        elif strategy == "genetic":
            return self._genetic_algorithm(current_prompts)
        elif strategy == "mutation":
            return self._mutation_based(current_prompts)
        elif strategy == "rl":
            return self._rl_based(current_prompts)
        else:
            raise ValueError(f"未知的生成策略: {strategy}")

    def _llm_rewrite(
        self, prompts: List[str], feedback: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        使用LLM重写提示词（类似OPRO、ProTeGi方法）

        这是最常用和最有效的方法
        """
        new_candidates = []

        for prompt in prompts:
            # 构建元提示
            meta_prompt = self._build_meta_prompt(prompt, feedback)

            # 调用LLM生成改进的提示词
            improved_prompt = self._call_llm(meta_prompt)

            if improved_prompt:
                new_candidates.append(improved_prompt)

            # 如果候选不够，生成一些变体
            while len(new_candidates) < self.config.num_candidates // len(prompts):
                variant = self._create_variant(prompt, len(new_candidates))
                new_candidates.append(variant)

        return new_candidates[: self.config.num_candidates]

    def _build_meta_prompt(
        self, current_prompt: str, feedback: List[Dict[str, Any]] = None
    ) -> str:
        """
        构建用于提示词优化的元提示（meta-prompt）

        注意：我们优化的是核心指令部分，动态上下文和示例不在优化范围内

        灵感来自OPRO论文
        """
        task_desc = self.task.description

        # 构建示例
        examples_str = "\n".join(
            [
                f"Input: {ex['input']}\nOutput: {ex['output']}"
                for ex in self.task.examples[:3]
            ]
        )

        # 构建反馈信息
        feedback_str = ""
        if feedback:
            feedback_str = "\n当前提示词的问题：\n"
            for fb in feedback[:3]:  # 只取前3个
                if "error_analysis" in fb:
                    feedback_str += f"- {fb['error_analysis']}\n"

        # 获取准确率（兼容不同的反馈格式）
        accuracy = '未知'
        if feedback and len(feedback) > 0:
            if 'score' in feedback[0]:
                accuracy = f"{feedback[0]['score']:.3f}"
            elif 'accuracy' in feedback[0]:
                accuracy = f"{feedback[0]['accuracy']:.3f}"

        meta_prompt = f"""
你是一个提示词优化专家。你的任务是改进给定的核心指令，使其在以下任务上表现更好。

注意：你只需要优化核心指令部分，不要包含具体的示例或上下文，那些会在运行时动态注入。

任务描述：{task_desc}

任务示例：
{examples_str}

当前核心指令：
"{current_prompt}"

当前指令的准确率：{accuracy}
{feedback_str}

请生成一个改进的核心指令，要求：
1. 保持任务目标不变
2. 更加清晰和具体
3. 包含必要的指导和约束
4. 长度控制在50-100词
5. 不要包含具体示例，只需要核心指令

只返回改进后的核心指令，不要包含其他解释。
"""
        return meta_prompt

    def _genetic_algorithm(self, prompts: List[str]) -> List[str]:
        """
        遗传算法生成候选（类似PromptBreeder、EvoPrompt）

        操作：变异 + 交叉
        """
        new_candidates = []

        # 变异操作
        for prompt in prompts:
            mutated = self._mutate_prompt(prompt)
            new_candidates.append(mutated)

        # 交叉操作
        if len(prompts) >= 2:
            for i in range(len(prompts) - 1):
                crossed = self._crossover_prompts(prompts[i], prompts[i + 1])
                new_candidates.append(crossed)

        return new_candidates[: self.config.num_candidates]

    def _mutate_prompt(self, prompt: str) -> str:
        """
        变异操作：对提示词进行小幅修改

        策略：
        - 添加词语
        - 删除词语
        - 替换词语
        - 重新排序句子
        """
        sentences = prompt.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return prompt

        mutation_type = random.choice(["add", "delete", "replace", "reorder"])

        if mutation_type == "add" and len(sentences) > 0:
            # 添加指导性句子
            additions = [
                "Think step by step",
                "Provide a detailed explanation",
                "Consider all possible cases",
                "Double-check your answer",
            ]
            sentences.append(random.choice(additions))

        elif mutation_type == "delete" and len(sentences) > 1:
            # 删除一个句子
            sentences.pop(random.randint(0, len(sentences) - 1))

        elif mutation_type == "replace" and len(sentences) > 0:
            # 替换一个句子
            idx = random.randint(0, len(sentences) - 1)
            replacements = [
                "Be precise and accurate",
                "Format your answer clearly",
                "Explain your reasoning",
            ]
            sentences[idx] = random.choice(replacements)

        elif mutation_type == "reorder" and len(sentences) > 1:
            # 重新排序
            random.shuffle(sentences)

        return ". ".join(sentences) + "."

    def _crossover_prompts(self, prompt1: str, prompt2: str) -> str:
        """
        交叉操作：组合两个提示词的部分

        策略：
        - 取prompt1的前半部分 + prompt2的后半部分
        - 或混合关键句子
        """
        sentences1 = [s.strip() for s in prompt1.split(".") if s.strip()]
        sentences2 = [s.strip() for s in prompt2.split(".") if s.strip()]

        # 简单交叉：前一半 + 后一半
        mid1 = len(sentences1) // 2
        mid2 = len(sentences2) // 2

        new_sentences = sentences1[:mid1] + sentences2[mid2:]

        return ". ".join(new_sentences) + "."

    def _mutation_based(self, prompts: List[str]) -> List[str]:
        """
        基于变异的生成（类似LMEA、StraGo）

        使用LLM进行变异
        """
        new_candidates = []

        mutation_prompts = [
            "Make this prompt more specific:",
            "Simplify this prompt:",
            "Add step-by-step guidance to this prompt:",
            "Make this prompt more formal:",
            "Add examples to this prompt:",
        ]

        for prompt in prompts:
            for mutation_type in random.sample(
                mutation_prompts, min(3, len(mutation_prompts))
            ):
                mutation_request = f"{mutation_type}\n\n{prompt}\n\nImproved prompt:"

                # 调用LLM生成变异后的提示词
                mutated = self._call_llm(mutation_request)
                if mutated and mutated.strip():
                    new_candidates.append(mutated.strip())
                else:
                    # 如果LLM调用失败，使用简单变异作为后备
                    new_candidates.append(prompt + " [Mutated]")

        return new_candidates[: self.config.num_candidates]

    def _rl_based(self, prompts: List[str]) -> List[str]:
        """
        基于强化学习的生成（RLPrompt方法）

        使用RL训练策略网络来生成提示词
        """
        try:
            from rl_optimizer import RLPromptGenerator

            # 创建RL生成器
            rl_generator = RLPromptGenerator(self.config, self.task)

            # 使用RL优化每个提示词
            new_candidates = rl_generator.generate_with_rl(
                prompts,
                num_episodes=5,  # 较少的回合数用于生成阶段
                max_steps=3      # 较少的步数
            )

            return new_candidates[: self.config.num_candidates]

        except ImportError:
            # 如果RL模块不可用，回退到变异方法
            print("警告: RL优化器不可用，回退到变异方法")
            return self._mutation_based(prompts)

    def _create_variant(self, prompt: str, variant_id: int) -> str:
        """创建提示词变体（占位符方法）"""
        variants = [
            f"{prompt} Think carefully.",
            f"{prompt} Provide a detailed answer.",
            f"{prompt} Explain your reasoning step by step.",
            f"Please solve this carefully: {prompt}",
            f"{prompt} Format your response clearly.",
        ]
        return variants[variant_id % len(variants)]

    def initialize_seed_prompts(self, num_seeds: int = 3) -> List[str]:
        """
        初始化种子提示词（核心指令）

        策略：
        1. 使用任务的核心指令作为基础
        2. 使用LLM归纳（instruction induction）
        3. 手动创建的模板
        """
        seed_prompts = []

        # 策略1：直接使用核心指令
        core_instruction = self.task.get_core_instruction()
        seed_prompts.append(core_instruction)

        # 策略2：基础模板
        templates = [
            f"Task: {self.task.description}\nPlease provide your answer.",
            f"You are asked to: {self.task.description}\nThink step by step.",
            f"Given the task: {self.task.description}\nProvide a clear and accurate response.",
        ]

        seed_prompts.extend(templates[: num_seeds - 1])

        # 策略3：使用instruction induction（需要LLM）
        if len(seed_prompts) < num_seeds:
            induced_prompt = self._instruction_induction()
            seed_prompts.append(induced_prompt)

        return seed_prompts[:num_seeds]

    def _instruction_induction(self) -> str:
        """
        指令归纳：从示例中推断核心任务指令

        参考Instruction Induction论文
        """
        examples_str = "\n".join(
            [
                f"Input: {ex['input']}\nOutput: {ex['output']}"
                for ex in self.task.examples[:5]
            ]
        )

        induction_prompt = f"""
给定以下输入-输出示例对：

{examples_str}

这些示例执行的是什么任务？请用一句清晰简洁的核心指令描述这个任务。
不要包含具体示例，只需要核心指令。

核心指令：
"""
        # 调用LLM
        induced_instruction = self._call_llm(induction_prompt)
        if induced_instruction:
            return induced_instruction

        # 占位符
        return f"Complete the following task: {self.task.description}"

    def _call_llm(self, prompt: str) -> str:
        """
        调用LLM API

        Args:
            prompt: 输入提示词

        Returns:
            LLM生成的文本
        """
        return self.llm_client.call(prompt)


class FeedbackCollector:
    """反馈收集器 - 分析错误并生成反馈"""

    @staticmethod
    def analyze_errors(
        predictions: List[str], references: List[str], inputs: List[str]
    ) -> List[Dict[str, Any]]:
        """分析预测错误，生成反馈"""
        feedback = []

        for i, (pred, ref, inp) in enumerate(zip(predictions, references, inputs)):
            if pred.strip() != ref.strip():
                feedback.append(
                    {
                        "index": i,
                        "input": inp,
                        "predicted": pred,
                        "expected": ref,
                        "error_type": "mismatch",
                        "error_analysis": f"模型输出'{pred}'与期望'{ref}'不匹配",
                    }
                )

        return feedback

    @staticmethod
    def generate_improvement_suggestions(
        feedback: List[Dict[str, Any]]
    ) -> List[str]:
        """根据反馈生成改进建议"""
        suggestions = []

        # 分析常见错误模式
        if len(feedback) > 0:
            suggestions.append("提示词可能不够明确，建议添加更详细的指导")

        if len(feedback) > len(feedback) * 0.5:
            suggestions.append("大量错误，考虑重新设计提示词结构")

        return suggestions


class OptionsOptimizer:
    """选项描述优化器 - 专门用于优化多选题的ABCD选项描述"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.llm_client = create_llm_client(config)

    def optimize_options(
        self,
        question: str,
        original_options: List[str],
        correct_answer: str,
        feedback: str = None
    ) -> List[str]:
        """
        优化选项描述

        Args:
            question: 题目问题
            original_options: 原始选项列表，如 ["A. Python", "B. Java", "C. C++"]
            correct_answer: 正确答案，如 "A"
            feedback: 优化反馈（可选）

        Returns:
            优化后的选项列表
        """
        # 构建优化提示词
        optimization_prompt = self._build_optimization_prompt(
            question, original_options, correct_answer, feedback
        )

        # 调用LLM生成优化后的选项
        response = self.llm_client.call(optimization_prompt)

        # 解析响应，提取优化后的选项
        optimized_options = self._parse_optimized_options(response, len(original_options))

        return optimized_options if optimized_options else original_options

    def _build_optimization_prompt(
        self,
        question: str,
        options: List[str],
        correct_answer: str,
        feedback: str = None
    ) -> str:
        """构建选项优化的元提示"""
        options_str = "\n".join(options)
        feedback_str = f"\n\n问题反馈：\n{feedback}" if feedback else ""

        prompt = f"""
你是一个多选题选项优化专家。你的任务是优化以下题目的选项描述，使其更加清晰、准确、易懂。

题目：
{question}

当前选项：
{options_str}

正确答案：{correct_answer}
{feedback_str}

请优化这些选项的描述，要求：
1. 保持选项的编号（A、B、C等）不变
2. 让选项描述更清晰、简洁
3. 避免歧义和混淆
4. 保持正确���案不变
5. 选项之间应有明显区分度
6. 干扰项要合理但可辨别

请直接返回优化后的选项列表���每行一个选项，格式与原选项一致。
"""
        return prompt

    def _parse_optimized_options(self, response: str, expected_count: int) -> List[str]:
        """
        从LLM响应中解析优化后的选项

        Args:
            response: LLM响应
            expected_count: 期望的选项数量

        Returns:
            解析出的选项列表
        """
        if not response:
            return []

        lines = response.strip().split('\n')
        options = []

        for line in lines:
            line = line.strip()
            # 检查是否是选项格式（以A. B. C.等开头）
            if line and len(line) > 2 and line[0].isalpha() and line[1] == '.':
                options.append(line)

        # 如果解析出的选项数量正确，返回
        if len(options) == expected_count:
            return options

        return []

    def batch_optimize_dataset(
        self,
        validation_data: List[Dict[str, Any]],
        optimize_incorrect_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        批量优化数据集中的选项

        Args:
            validation_data: 验证数据集，每个item应包含 'input', 'options', 'output'
            optimize_incorrect_only: 是否仅优化答错的题目

        Returns:
            优化后的数据集
        """
        optimized_data = []

        for item in validation_data:
            if "options" not in item:
                # 如果没有选项，直接保留原数据
                optimized_data.append(item)
                continue

            # 优化选项
            optimized_options = self.optimize_options(
                question=item["input"],
                original_options=item["options"],
                correct_answer=item["output"]
            )

            # 创建新的item
            new_item = item.copy()
            new_item["options"] = optimized_options
            new_item["original_options"] = item["options"]  # 保留原始选项

            optimized_data.append(new_item)

        return optimized_data

