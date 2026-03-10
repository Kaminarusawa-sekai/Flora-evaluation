"""
高级评估指标模块
实现F1, Precision, Recall, BLEU, ROUGE等评估指标
"""
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import re


class AdvancedMetrics:
    """高级评估指标类"""

    @staticmethod
    def precision_recall_f1(
        predictions: List[str],
        references: List[str],
        average: str = "binary"
    ) -> Dict[str, float]:
        """
        计算Precision, Recall, F1分数

        Args:
            predictions: 预测结果列表
            references: 参考答案列表
            average: 'binary'（二分类）或'macro'（多分类）

        Returns:
            包含precision, recall, f1的字典
        """
        if len(predictions) != len(references):
            raise ValueError("predictions和references长度必须相同")

        if average == "binary":
            # 二分类场景
            return AdvancedMetrics._binary_metrics(predictions, references)
        elif average == "macro":
            # 多分类场景
            return AdvancedMetrics._macro_metrics(predictions, references)
        else:
            raise ValueError(f"不支持的average类型: {average}")

    @staticmethod
    def _binary_metrics(
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, float]:
        """二分类指标计算"""
        # 统计TP, FP, TN, FN
        tp = fp = tn = fn = 0

        # 假设第一个类别是正类
        positive_class = references[0] if references else None

        for pred, ref in zip(predictions, references):
            pred_positive = (pred.lower().strip() == positive_class.lower().strip())
            ref_positive = (ref.lower().strip() == positive_class.lower().strip())

            if pred_positive and ref_positive:
                tp += 1
            elif pred_positive and not ref_positive:
                fp += 1
            elif not pred_positive and not ref_positive:
                tn += 1
            else:
                fn += 1

        # 计算指标
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn
        }

    @staticmethod
    def _macro_metrics(
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, float]:
        """多分类宏平均指标"""
        # 获取所有类别
        all_classes = list(set(references))

        precisions = []
        recalls = []
        f1s = []

        # 对每个类别计算指标
        for cls in all_classes:
            tp = fp = fn = 0

            for pred, ref in zip(predictions, references):
                pred_cls = (pred.lower().strip() == cls.lower().strip())
                ref_cls = (ref.lower().strip() == cls.lower().strip())

                if pred_cls and ref_cls:
                    tp += 1
                elif pred_cls and not ref_cls:
                    fp += 1
                elif not pred_cls and ref_cls:
                    fn += 1

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        return {
            "precision": np.mean(precisions),
            "recall": np.mean(recalls),
            "f1": np.mean(f1s),
            "num_classes": len(all_classes)
        }

    @staticmethod
    def bleu_score(
        hypothesis: str,
        reference: str,
        max_n: int = 4
    ) -> float:
        """
        计算BLEU分数（用于生成任务）

        Args:
            hypothesis: 生成的文本
            reference: 参考文本
            max_n: 最大n-gram长度

        Returns:
            BLEU分数（0-1）
        """
        # 分词
        hyp_tokens = AdvancedMetrics._tokenize(hypothesis)
        ref_tokens = AdvancedMetrics._tokenize(reference)

        if len(hyp_tokens) == 0:
            return 0.0

        # 计算各个n-gram的精确率
        precisions = []
        for n in range(1, max_n + 1):
            hyp_ngrams = AdvancedMetrics._get_ngrams(hyp_tokens, n)
            ref_ngrams = AdvancedMetrics._get_ngrams(ref_tokens, n)

            if len(hyp_ngrams) == 0:
                break

            # 计算匹配数
            matches = 0
            for ngram in hyp_ngrams:
                if ngram in ref_ngrams:
                    matches += min(hyp_ngrams[ngram], ref_ngrams[ngram])

            precision = matches / sum(hyp_ngrams.values())
            precisions.append(precision)

        if not precisions:
            return 0.0

        # 几何平均
        geo_mean = np.exp(np.mean([np.log(p) if p > 0 else -np.inf for p in precisions]))

        # 长度惩罚
        bp = min(1.0, np.exp(1 - len(ref_tokens) / len(hyp_tokens)))

        return bp * geo_mean

    @staticmethod
    def rouge_score(
        hypothesis: str,
        reference: str,
        rouge_type: str = "rouge-1"
    ) -> Dict[str, float]:
        """
        计算ROUGE分数（用于摘要任务）

        Args:
            hypothesis: 生成的文本
            reference: 参考文本
            rouge_type: 'rouge-1', 'rouge-2', 或 'rouge-l'

        Returns:
            包含precision, recall, f1的字典
        """
        hyp_tokens = AdvancedMetrics._tokenize(hypothesis)
        ref_tokens = AdvancedMetrics._tokenize(reference)

        if rouge_type == "rouge-1":
            return AdvancedMetrics._rouge_n(hyp_tokens, ref_tokens, 1)
        elif rouge_type == "rouge-2":
            return AdvancedMetrics._rouge_n(hyp_tokens, ref_tokens, 2)
        elif rouge_type == "rouge-l":
            return AdvancedMetrics._rouge_l(hyp_tokens, ref_tokens)
        else:
            raise ValueError(f"不支持的ROUGE类型: {rouge_type}")

    @staticmethod
    def _rouge_n(
        hyp_tokens: List[str],
        ref_tokens: List[str],
        n: int
    ) -> Dict[str, float]:
        """ROUGE-N计算"""
        hyp_ngrams = AdvancedMetrics._get_ngrams(hyp_tokens, n)
        ref_ngrams = AdvancedMetrics._get_ngrams(ref_tokens, n)

        if len(ref_ngrams) == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        # 计算匹配数
        matches = 0
        for ngram in hyp_ngrams:
            if ngram in ref_ngrams:
                matches += min(hyp_ngrams[ngram], ref_ngrams[ngram])

        precision = matches / sum(hyp_ngrams.values()) if sum(hyp_ngrams.values()) > 0 else 0.0
        recall = matches / sum(ref_ngrams.values()) if sum(ref_ngrams.values()) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    @staticmethod
    def _rouge_l(
        hyp_tokens: List[str],
        ref_tokens: List[str]
    ) -> Dict[str, float]:
        """ROUGE-L计算（最长公共子序列）"""
        lcs_length = AdvancedMetrics._lcs(hyp_tokens, ref_tokens)

        if len(hyp_tokens) == 0 or len(ref_tokens) == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        precision = lcs_length / len(hyp_tokens)
        recall = lcs_length / len(ref_tokens)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    @staticmethod
    def _lcs(seq1: List[str], seq2: List[str]) -> int:
        """计算最长公共子序列长度"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """简单分词"""
        # 转小写，去除标点，分割
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return tokens

    @staticmethod
    def _get_ngrams(tokens: List[str], n: int) -> Counter:
        """获取n-gram"""
        ngrams = Counter()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams[ngram] += 1
        return ngrams

    @staticmethod
    def compute_all_metrics(
        predictions: List[str],
        references: List[str],
        task_type: str = "classification"
    ) -> Dict[str, Any]:
        """
        计算所有相关指标

        Args:
            predictions: 预测结果列表
            references: 参考答案列表
            task_type: 'classification' 或 'generation'

        Returns:
            包含所有指标的字典
        """
        results = {}

        # 基础准确率
        correct = sum(1 for p, r in zip(predictions, references)
                     if p.lower().strip() == r.lower().strip())
        results["accuracy"] = correct / len(predictions) if len(predictions) > 0 else 0.0

        if task_type == "classification":
            # 分类任务指标
            # 判断是二分类还是多分类
            unique_classes = len(set(references))
            average = "binary" if unique_classes == 2 else "macro"

            metrics = AdvancedMetrics.precision_recall_f1(
                predictions, references, average=average
            )
            results.update(metrics)

        elif task_type == "generation":
            # 生成任务指标
            if len(predictions) > 0 and len(references) > 0:
                # 计算平均BLEU
                bleu_scores = []
                rouge1_scores = []
                rouge2_scores = []
                rougel_scores = []

                for pred, ref in zip(predictions, references):
                    bleu_scores.append(AdvancedMetrics.bleu_score(pred, ref))
                    rouge1_scores.append(AdvancedMetrics.rouge_score(pred, ref, "rouge-1")["f1"])
                    rouge2_scores.append(AdvancedMetrics.rouge_score(pred, ref, "rouge-2")["f1"])
                    rougel_scores.append(AdvancedMetrics.rouge_score(pred, ref, "rouge-l")["f1"])

                results["bleu"] = np.mean(bleu_scores)
                results["rouge-1"] = np.mean(rouge1_scores)
                results["rouge-2"] = np.mean(rouge2_scores)
                results["rouge-l"] = np.mean(rougel_scores)

        return results


# 便捷函数

def evaluate_classification(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """
    便捷的分类评估函数

    Args:
        predictions: 预测结果
        references: 参考答案

    Returns:
        包含accuracy, precision, recall, f1的字典
    """
    return AdvancedMetrics.compute_all_metrics(predictions, references, "classification")


def evaluate_generation(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """
    便捷的生成评估函数

    Args:
        predictions: 生成的文本
        references: 参考文本

    Returns:
        包含accuracy, bleu, rouge等指标的字典
    """
    return AdvancedMetrics.compute_all_metrics(predictions, references, "generation")
