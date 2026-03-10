"""
强化学习优化器 - 使用RL方法优化提示词

基于RLPrompt论文实现：
- 状态：提示词的向量表示
- 动作：对提示词的修改操作
- 奖励：任务性能提升
- 策略：使用Policy Gradient训练策略网络
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import random
import logging
from collections import deque
from config import APOConfig, Task
from evaluator import Evaluator
from llm_client import create_llm_client


class PromptState:
    """提示词状态表示"""

    def __init__(self, prompt: str, score: float = 0.0):
        """
        Args:
            prompt: 当前提示词
            score: 当前得分
        """
        self.prompt = prompt
        self.score = score
        self.sentences = self._parse_sentences(prompt)

    def _parse_sentences(self, prompt: str) -> List[str]:
        """将提示词分解为句子"""
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        return sentences

    def get_feature_vector(self, vocab_size: int = 1000) -> np.ndarray:
        """
        将提示词转换为特征向量

        使用简单的词袋模型 + 统计特征
        """
        # 基础特征
        features = []

        # 1. 长度特征
        features.append(len(self.prompt) / 1000.0)  # 归一化字符长度
        features.append(len(self.sentences) / 10.0)  # 归一化句子数
        features.append(len(self.prompt.split()) / 100.0)  # 归一化单词数

        # 2. 词频特征（简化的词袋模型）
        words = self.prompt.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # 取最常见的50个词作为特征
        common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        word_features = [count / len(words) for _, count in common_words]
        # 填充到50维
        word_features = word_features + [0.0] * (50 - len(word_features))
        features.extend(word_features)

        # 3. 当前得分
        features.append(self.score)

        return np.array(features, dtype=np.float32)


class PromptAction:
    """提示词修改动作"""

    # 动作类型
    ACTION_ADD_SENTENCE = 0
    ACTION_DELETE_SENTENCE = 1
    ACTION_REPLACE_SENTENCE = 2
    ACTION_REORDER_SENTENCES = 3
    ACTION_ADD_KEYWORD = 4
    ACTION_SIMPLIFY = 5

    ACTION_NAMES = {
        0: "添加指导句",
        1: "删除句子",
        2: "替换句子",
        3: "重排序句子",
        4: "添加关键词",
        5: "简化表达"
    }

    def __init__(self, action_type: int, params: Optional[Dict[str, Any]] = None):
        """
        Args:
            action_type: 动作类型
            params: 动作参数
        """
        self.action_type = action_type
        self.params = params or {}

    @staticmethod
    def get_action_space_size() -> int:
        """获取动作空间大小"""
        return 6

    def __repr__(self):
        return f"Action({self.ACTION_NAMES[self.action_type]})"


class PolicyNetwork:
    """策略网络 - 选择动作"""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64, learning_rate: float = 0.001):
        """
        简单的两层神经网络

        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dim: 隐藏层维度
            learning_rate: 学习率
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate

        # 初始化权重（Xavier初始化）
        self.W1 = np.random.randn(state_dim, hidden_dim) * np.sqrt(2.0 / state_dim)
        self.b1 = np.zeros((1, hidden_dim))

        self.W2 = np.random.randn(hidden_dim, action_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((1, action_dim))

    def forward(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        前向传播

        Returns:
            action_probs: 动作概率分布
            hidden: 隐藏层激活
        """
        # 隐藏层
        hidden = np.maximum(0, np.dot(state, self.W1) + self.b1)  # ReLU

        # 输出层（softmax）
        logits = np.dot(hidden, self.W2) + self.b2
        logits = logits - np.max(logits)  # 数值稳定性
        exp_logits = np.exp(logits)
        action_probs = exp_logits / np.sum(exp_logits)

        return action_probs, hidden

    def select_action(self, state: np.ndarray, epsilon: float = 0.0) -> Tuple[int, float]:
        """
        根据策略选择动作

        Args:
            state: 当前状态
            epsilon: 探索率（epsilon-greedy）

        Returns:
            action: 选择的动作
            log_prob: 动作的对数概率
        """
        action_probs, _ = self.forward(state)

        # Epsilon-greedy探索
        if random.random() < epsilon:
            action = random.randint(0, self.action_dim - 1)
        else:
            action = np.random.choice(self.action_dim, p=action_probs.flatten())

        log_prob = np.log(action_probs[0, action] + 1e-10)

        return action, log_prob

    def update(self, states: List[np.ndarray], actions: List[int],
               advantages: List[float]) -> float:
        """
        使用Policy Gradient更新策略

        Args:
            states: 状态序列
            actions: 动作序列
            advantages: 优势函数值

        Returns:
            loss: 策略损失
        """
        total_loss = 0.0

        for state, action, advantage in zip(states, actions, advantages):
            # 前向传播
            action_probs, hidden = self.forward(state)

            # 计算损失
            log_prob = np.log(action_probs[0, action] + 1e-10)
            loss = -log_prob * advantage
            total_loss += loss

            # 反向传播（简化版）
            # ∇log π(a|s) = grad_output / π(a|s)
            grad_output = np.zeros((1, self.action_dim))
            grad_output[0, action] = -advantage / (action_probs[0, action] + 1e-10)

            # 输出层梯度
            grad_W2 = np.dot(hidden.T, grad_output)
            grad_b2 = grad_output

            # 隐藏层梯度
            grad_hidden = np.dot(grad_output, self.W2.T)
            grad_hidden[hidden <= 0] = 0  # ReLU梯度

            grad_W1 = np.dot(state.T, grad_hidden)
            grad_b1 = grad_hidden

            # 更新参数
            self.W2 -= self.learning_rate * grad_W2
            self.b2 -= self.learning_rate * grad_b2
            self.W1 -= self.learning_rate * grad_W1
            self.b1 -= self.learning_rate * grad_b1

        return total_loss / len(states)


class ValueNetwork:
    """值网络 - 评估状态价值"""

    def __init__(self, state_dim: int, hidden_dim: int = 64, learning_rate: float = 0.001):
        """
        Args:
            state_dim: 状态维度
            hidden_dim: 隐藏层维度
            learning_rate: 学习率
        """
        self.learning_rate = learning_rate

        # 初始化权重
        self.W1 = np.random.randn(state_dim, hidden_dim) * np.sqrt(2.0 / state_dim)
        self.b1 = np.zeros((1, hidden_dim))

        self.W2 = np.random.randn(hidden_dim, 1) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((1, 1))

    def forward(self, state: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        前向传播

        Returns:
            value: 状态价值
            hidden: 隐藏层激活
        """
        hidden = np.maximum(0, np.dot(state, self.W1) + self.b1)  # ReLU
        value = np.dot(hidden, self.W2) + self.b2

        return value[0, 0], hidden

    def update(self, states: List[np.ndarray], targets: List[float]) -> float:
        """
        使用TD误差更新值函数

        Args:
            states: 状态序列
            targets: 目标值序列

        Returns:
            loss: 值函数损失
        """
        total_loss = 0.0

        for state, target in zip(states, targets):
            # 前向传播
            value, hidden = self.forward(state)

            # 计算损失（MSE）
            loss = 0.5 * (value - target) ** 2
            total_loss += loss

            # 反向传播
            grad_output = value - target

            # 输出层梯度
            grad_W2 = np.dot(hidden.T, [[grad_output]])
            grad_b2 = np.array([[grad_output]])

            # 隐藏层梯度
            grad_hidden = np.dot([[grad_output]], self.W2.T)
            grad_hidden[hidden <= 0] = 0  # ReLU梯度

            grad_W1 = np.dot(state.T, grad_hidden)
            grad_b1 = grad_hidden

            # 更新参数
            self.W2 -= self.learning_rate * grad_W2
            self.b2 -= self.learning_rate * grad_b2
            self.W1 -= self.learning_rate * grad_W1
            self.b1 -= self.learning_rate * grad_b1

        return total_loss / len(states)


class RLPromptEnvironment:
    """RL提示词优化环境"""

    def __init__(self, task: Task, evaluator: Evaluator, llm_client: Any):
        """
        Args:
            task: 任务定义
            evaluator: 评估器
            llm_client: LLM客户端
        """
        self.task = task
        self.evaluator = evaluator
        self.llm_client = llm_client

        # 预定义的修改模板
        self.addition_templates = [
            "Think step by step.",
            "Provide a detailed explanation.",
            "Be precise and accurate.",
            "Consider all possible cases.",
            "Double-check your answer.",
            "Format your response clearly.",
            "Explain your reasoning."
        ]

        self.keywords = [
            "carefully", "precisely", "clearly", "step-by-step",
            "detailed", "accurate", "thorough"
        ]

    def reset(self, initial_prompt: str) -> PromptState:
        """
        重置环境

        Args:
            initial_prompt: 初始提示词

        Returns:
            初始状态
        """
        # 评估初始提示词
        result = self.evaluator.evaluate_prompt(initial_prompt)
        score = result['accuracy']

        return PromptState(initial_prompt, score)

    def step(self, state: PromptState, action: PromptAction) -> Tuple[PromptState, float, bool]:
        """
        执行动作，返回新状态和奖励

        Args:
            state: 当前状态
            action: 要执行的动作

        Returns:
            new_state: 新状态
            reward: 奖励
            done: 是否结束
        """
        # 执行动作，生成新提示词
        new_prompt = self._apply_action(state.prompt, action)

        # 评估新提示词
        result = self.evaluator.evaluate_prompt(new_prompt)
        new_score = result['accuracy']

        # 计算奖励（分数提升）
        reward = new_score - state.score

        # 创建新状态
        new_state = PromptState(new_prompt, new_score)

        # 判断是否结束（达到高分或无改进）
        done = new_score >= 0.95 or new_score <= state.score - 0.05

        return new_state, reward, done

    def _apply_action(self, prompt: str, action: PromptAction) -> str:
        """
        应用动作到提示词

        Args:
            prompt: 当前提示词
            action: 动作

        Returns:
            修改后的提示词
        """
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]

        if action.action_type == PromptAction.ACTION_ADD_SENTENCE:
            # 添加指导句
            new_sentence = random.choice(self.addition_templates)
            sentences.append(new_sentence)

        elif action.action_type == PromptAction.ACTION_DELETE_SENTENCE and len(sentences) > 1:
            # 删除随机句子
            sentences.pop(random.randint(0, len(sentences) - 1))

        elif action.action_type == PromptAction.ACTION_REPLACE_SENTENCE and len(sentences) > 0:
            # 替换句子（使用LLM）
            idx = random.randint(0, len(sentences) - 1)
            replacement = self._llm_replace_sentence(sentences[idx], prompt)
            if replacement:
                sentences[idx] = replacement

        elif action.action_type == PromptAction.ACTION_REORDER_SENTENCES and len(sentences) > 1:
            # 重新排序
            random.shuffle(sentences)

        elif action.action_type == PromptAction.ACTION_ADD_KEYWORD:
            # 添加关键词
            keyword = random.choice(self.keywords)
            if sentences:
                sentences[0] = f"{sentences[0]} {keyword}"

        elif action.action_type == PromptAction.ACTION_SIMPLIFY:
            # 简化（使用LLM）
            simplified = self._llm_simplify(prompt)
            if simplified:
                return simplified

        new_prompt = '. '.join(sentences)
        if not new_prompt.endswith('.'):
            new_prompt += '.'

        return new_prompt

    def _llm_replace_sentence(self, sentence: str, context: str) -> Optional[str]:
        """使用LLM替换句子"""
        try:
            request = f"Improve this sentence in the context of a prompt:\n\nSentence: {sentence}\nContext: {context}\n\nImproved sentence:"
            response = self.llm_client.call(request)
            if response and len(response) < 200:
                return response.strip()
        except:
            pass
        return None

    def _llm_simplify(self, prompt: str) -> Optional[str]:
        """使用LLM简化提示词"""
        try:
            request = f"Simplify and make this prompt more concise while keeping its meaning:\n\n{prompt}\n\nSimplified prompt:"
            response = self.llm_client.call(request)
            if response and len(response) > 10:
                return response.strip()
        except:
            pass
        return None


class RLPromptOptimizer:
    """基于强化学习的提示词优化器"""

    def __init__(self, config: APOConfig, task: Task):
        """
        Args:
            config: 配置
            task: 任务
        """
        self.config = config
        self.task = task

        # 初始化组件
        self.evaluator = Evaluator(config, task)
        self.llm_client = create_llm_client(config)
        self.env = RLPromptEnvironment(task, self.evaluator, self.llm_client)

        # RL参数
        self.state_dim = 54  # 特征维度
        self.action_dim = PromptAction.get_action_space_size()
        self.gamma = 0.95  # 折扣因子
        self.epsilon_start = 0.3  # 初始探索率
        self.epsilon_end = 0.05  # 最终探索率
        self.epsilon_decay = 0.95  # 探索率衰减

        # 初始化网络
        self.policy_net = PolicyNetwork(self.state_dim, self.action_dim)
        self.value_net = ValueNetwork(self.state_dim)

        # 经验回放
        self.memory = deque(maxlen=1000)

        # 日志
        self.logger = self._setup_logger()

        # 优化历史
        self.history = {
            "episodes": [],
            "rewards": [],
            "scores": [],
            "best_prompts": []
        }

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("RLPromptOptimizer")
        logger.setLevel(logging.INFO if self.config.verbose else logging.WARNING)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def optimize(self,
                 initial_prompt: str,
                 num_episodes: int = 20,
                 max_steps_per_episode: int = 10) -> Dict[str, Any]:
        """
        使用RL优化提示词

        Args:
            initial_prompt: 初始提示词
            num_episodes: 训练回合数
            max_steps_per_episode: 每回合最大步数

        Returns:
            优化结果
        """
        self.logger.info("=" * 60)
        self.logger.info("开始强化学习提示词优化")
        self.logger.info(f"任务: {self.task.name}")
        self.logger.info(f"训练回合: {num_episodes}")
        self.logger.info("=" * 60)

        best_prompt = initial_prompt
        best_score = 0.0
        epsilon = self.epsilon_start

        for episode in range(num_episodes):
            self.logger.info(f"\n--- Episode {episode + 1}/{num_episodes} ---")

            # 重置环境
            state = self.env.reset(initial_prompt)
            episode_states = []
            episode_actions = []
            episode_rewards = []
            episode_log_probs = []

            total_reward = 0.0

            # 一个回合
            for step in range(max_steps_per_episode):
                # 获取状态特征
                state_vector = state.get_feature_vector()
                state_vector = state_vector.reshape(1, -1)

                # 选择动作
                action_idx, log_prob = self.policy_net.select_action(state_vector, epsilon)
                action = PromptAction(action_idx)

                self.logger.info(f"Step {step + 1}: {action} (score={state.score:.3f})")

                # 执行动作
                next_state, reward, done = self.env.step(state, action)

                # 记录经验
                episode_states.append(state_vector)
                episode_actions.append(action_idx)
                episode_rewards.append(reward)
                episode_log_probs.append(log_prob)

                total_reward += reward

                # 更新状态
                state = next_state

                # 检查是否结束
                if done:
                    self.logger.info(f"Episode ended at step {step + 1}")
                    break

            # 更新最佳结果
            if state.score > best_score:
                best_score = state.score
                best_prompt = state.prompt
                self.logger.info(f"✓ 新的最佳分数: {best_score:.3f}")

            # 训练网络
            if len(episode_rewards) > 0:
                self._train_networks(
                    episode_states, episode_actions,
                    episode_rewards, episode_log_probs
                )

            # 衰减探索率
            epsilon = max(self.epsilon_end, epsilon * self.epsilon_decay)

            # 记录历史
            self.history["episodes"].append(episode + 1)
            self.history["rewards"].append(total_reward)
            self.history["scores"].append(state.score)
            self.history["best_prompts"].append(best_prompt)

            self.logger.info(f"Episode {episode + 1}: Total Reward={total_reward:.3f}, Final Score={state.score:.3f}, Epsilon={epsilon:.3f}")

        # 返回结果
        self.logger.info("\n" + "=" * 60)
        self.logger.info("RL优化完成!")
        self.logger.info(f"最佳分数: {best_score:.3f}")
        self.logger.info(f"最佳提示词: {best_prompt}")
        self.logger.info("=" * 60)

        return {
            "best_prompt": best_prompt,
            "best_score": best_score,
            "initial_prompt": initial_prompt,
            "episodes": num_episodes,
            "history": self.history
        }

    def _train_networks(self,
                       states: List[np.ndarray],
                       actions: List[int],
                       rewards: List[float],
                       log_probs: List[float]) -> None:
        """训练策略网络和值网络"""

        # 计算折扣回报
        returns = self._compute_returns(rewards)

        # 计算优势函数
        values = [self.value_net.forward(state)[0] for state in states]
        advantages = [ret - val for ret, val in zip(returns, values)]

        # 归一化优势函数
        if len(advantages) > 1:
            advantages = (np.array(advantages) - np.mean(advantages)) / (np.std(advantages) + 1e-8)
            advantages = advantages.tolist()

        # 更新策略网络
        policy_loss = self.policy_net.update(states, actions, advantages)

        # 更新值网络
        value_loss = self.value_net.update(states, returns)

        self.logger.debug(f"Policy Loss: {policy_loss:.4f}, Value Loss: {value_loss:.4f}")

    def _compute_returns(self, rewards: List[float]) -> List[float]:
        """
        计算折扣回报

        Args:
            rewards: 奖励序列

        Returns:
            折扣回报序列
        """
        returns = []
        R = 0.0

        for reward in reversed(rewards):
            R = reward + self.gamma * R
            returns.insert(0, R)

        return returns


class RLPromptGenerator:
    """RL提示词生成器 - 集成到生成器框架"""

    def __init__(self, config: APOConfig, task: Task):
        self.config = config
        self.task = task
        self.rl_optimizer = RLPromptOptimizer(config, task)

    def generate_with_rl(self,
                        current_prompts: List[str],
                        num_episodes: int = 10,
                        max_steps: int = 5) -> List[str]:
        """
        使用RL生成改进的提示词

        Args:
            current_prompts: 当前提示词列表
            num_episodes: RL训练回合数
            max_steps: 每回合最大步数

        Returns:
            改进的提示词列表
        """
        improved_prompts = []

        for prompt in current_prompts:
            result = self.rl_optimizer.optimize(
                initial_prompt=prompt,
                num_episodes=num_episodes,
                max_steps_per_episode=max_steps
            )
            improved_prompts.append(result["best_prompt"])

        return improved_prompts
