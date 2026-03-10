"""
选择模块 - 选择和过滤候选提示词
"""
from typing import List, Dict, Any
import numpy as np
from config import APOConfig


class Selector:
    """候选选择器"""

    def __init__(self, config: APOConfig):
        self.config = config
        # UCB统计信息
        self.prompt_stats = {}  # {prompt: {"count": int, "total_reward": float}}

    def select_top_k(
        self, candidates: List[str], scores: List[float], k: int = None
    ) -> List[str]:
        """
        TopK贪婪选择

        最简单的选择策略，选择得分最高的K个候选

        Args:
            candidates: 候选提示词列表
            scores: 对应的分数列表
            k: 选择的数量，默认使用config.top_k

        Returns:
            选中的候选列表
        """
        if k is None:
            k = self.config.top_k

        # 按分数排序
        sorted_indices = np.argsort(scores)[::-1]  # 降序
        top_k_indices = sorted_indices[:k]

        return [candidates[i] for i in top_k_indices]

    def ucb_selection(
        self, candidates: List[str], scores: List[float], iteration: int
    ) -> List[str]:
        """
        UCB（上置信界限）选择

        平衡探索与利用，参考ProTeGi、SPRIG等方法

        Args:
            candidates: 候选提示词列表
            scores: 当前评估分数
            iteration: 当前迭代次数

        Returns:
            选中的候选列表
        """
        ucb_scores = []

        for i, (candidate, score) in enumerate(zip(candidates, scores)):
            # 更新统计信息
            if candidate not in self.prompt_stats:
                self.prompt_stats[candidate] = {"count": 0, "total_reward": 0.0}

            stats = self.prompt_stats[candidate]
            stats["count"] += 1
            stats["total_reward"] += score

            # 计算UCB分数
            avg_reward = stats["total_reward"] / stats["count"]
            exploration_bonus = self.config.ucb_c * np.sqrt(
                np.log(iteration + 1) / stats["count"]
            )

            ucb_score = avg_reward + exploration_bonus
            ucb_scores.append(ucb_score)

        # 选择UCB分数最高的top_k
        return self.select_top_k(candidates, ucb_scores, self.config.top_k)

    def diversity_selection(
        self, candidates: List[str], scores: List[float], k: int = None
    ) -> List[str]:
        """
        多样性选择

        在保证性能的同时，选择多样化的候选
        避免过早收敛到局部最优

        Args:
            candidates: 候选提示词列表
            scores: 对应的分数列表
            k: 选择的数量

        Returns:
            选中的候选列表
        """
        if k is None:
            k = self.config.top_k

        if len(candidates) <= k:
            return candidates

        # 首先选择得分最高的
        best_idx = np.argmax(scores)
        selected = [candidates[best_idx]]
        selected_indices = {best_idx}

        # 然后选择与已选择的候选差异最大的
        while len(selected) < k:
            max_diversity = -1
            max_diversity_idx = -1

            for i, candidate in enumerate(candidates):
                if i in selected_indices:
                    continue

                # 计算与已选候选的平均差异度
                diversity = self._calculate_diversity(candidate, selected)

                # 结合分数和多样性
                combined_score = 0.7 * scores[i] + 0.3 * diversity

                if combined_score > max_diversity:
                    max_diversity = combined_score
                    max_diversity_idx = i

            if max_diversity_idx != -1:
                selected.append(candidates[max_diversity_idx])
                selected_indices.add(max_diversity_idx)
            else:
                break

        return selected

    def _calculate_diversity(
        self, candidate: str, selected_candidates: List[str]
    ) -> float:
        """
        计算候选与已选择候选的多样性

        使用简单的编辑距离或词汇重叠度
        """
        if not selected_candidates:
            return 1.0

        diversities = []
        candidate_words = set(candidate.lower().split())

        for selected in selected_candidates:
            selected_words = set(selected.lower().split())

            # Jaccard距离（1 - Jaccard相似度）
            intersection = len(candidate_words & selected_words)
            union = len(candidate_words | selected_words)

            if union == 0:
                diversity = 0.0
            else:
                jaccard_similarity = intersection / union
                diversity = 1.0 - jaccard_similarity

            diversities.append(diversity)

        # 返回平均多样性
        return np.mean(diversities)

    def ensemble_selection(
        self, candidates: List[str], multiple_scores: List[List[float]], k: int = None
    ) -> List[str]:
        """
        集成选择

        基于多个评估指标进行选择

        Args:
            candidates: 候选提示词列表
            multiple_scores: 多个评估指标的分数列表
                           [[metric1_scores], [metric2_scores], ...]
            k: 选择的数量
        Returns:
            选中的候选列表
        """
        if k is None:
            k = self.config.top_k

        # 归一化每个指标的分数
        normalized_scores = []
        for scores in multiple_scores:
            scores_array = np.array(scores)
            if scores_array.max() > scores_array.min():
                normalized = (scores_array - scores_array.min()) / (
                    scores_array.max() - scores_array.min()
                )
            else:
                normalized = scores_array
            normalized_scores.append(normalized)

        # 计算综合分数（简单平均）
        combined_scores = np.mean(normalized_scores, axis=0)

        return self.select_top_k(candidates, combined_scores.tolist(), k)

    def adaptive_selection(
        self,
        candidates: List[str],
        scores: List[float],
        iteration: int,
        total_iterations: int,
    ) -> List[str]:
        """
        自适应选择

        根据优化进度动态调整选择策略：
        - 早期：更多探索（多样性）
        - 后期：更多利用（最优化）

        Args:
            candidates: 候选提示词列表
            scores: 对应的分数列表
            iteration: 当前迭代次数
            total_iterations: 总迭代次数

        Returns:
            选中的候选列表
        """
        # 计算进度比例
        progress = iteration / total_iterations

        if progress < 0.3:
            # 早期：优先多样性
            return self.diversity_selection(candidates, scores)
        elif progress < 0.7:
            # 中期：使用UCB平衡探索与利用
            return self.ucb_selection(candidates, scores, iteration)
        else:
            # 后期：贪婪选择最优
            return self.select_top_k(candidates, scores)


class EarlyStopper:
    """早停检测器"""

    def __init__(self, patience: int = 3, min_delta: float = 0.01):
        """
        Args:
            patience: 容忍多少轮没有改进
            min_delta: 最小改进阈值
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        self.should_stop = False

    def check(self, current_score: float) -> bool:
        """
        检查是否应该早停

        Args:
            current_score: 当前分数

        Returns:
            是否应该停止
        """
        if self.best_score is None:
            self.best_score = current_score
            return False

        # 检查是否有足够的改进
        if current_score > self.best_score + self.min_delta:
            self.best_score = current_score
            self.counter = 0
        else:
            self.counter += 1

        # 检查是否达到patience
        if self.counter >= self.patience:
            self.should_stop = True
            return True

        return False

    def reset(self):
        """重置早停状态"""
        self.counter = 0
        self.best_score = None
        self.should_stop = False
