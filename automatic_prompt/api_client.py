"""
提示词优化API客户端
提供简洁的Python接口调用API服务
"""
import requests
import time
from typing import List, Dict, Optional


class PromptOptimizationClient:
    """提示词优化API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端

        Args:
            base_url: API服务地址
        """
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> Dict:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def optimize(
        self,
        task_name: str,
        task_description: str,
        examples: List[Dict[str, str]],
        validation_data: List[Dict[str, str]],
        initial_prompts: List[str],
        max_iterations: int = 10,
        num_candidates: int = 5,
        top_k: int = 3,
        early_stop_threshold: float = 0.95,
        wait: bool = True,
        check_interval: int = 10
    ) -> Dict:
        """
        优化提示词

        Args:
            task_name: 任务名称
            task_description: 任务描述
            examples: 训练样本 [{"input": "...", "output": "..."}, ...]
            validation_data: 验证样本
            initial_prompts: 你的初始提示词列表（1-5个）
            max_iterations: 最大迭代次数（1-50）
            num_candidates: 每轮生成候选数（2-10）
            top_k: 保留最优候选数（1-5）
            early_stop_threshold: 早停阈值（0-1）
            wait: 是否等待完成（默认True）
            check_interval: 状态检查间隔（秒）

        Returns:
            优化结果字典
        """
        # 提交任务
        response = requests.post(
            f"{self.base_url}/optimize",
            json={
                "task_name": task_name,
                "task_description": task_description,
                "examples": examples,
                "validation_data": validation_data,
                "initial_prompts": initial_prompts,
                "max_iterations": max_iterations,
                "num_candidates": num_candidates,
                "top_k": top_k,
                "early_stop_threshold": early_stop_threshold
            }
        )
        response.raise_for_status()
        result = response.json()
        task_id = result['task_id']

        print(f"✓ 任务已创建: {task_id}")

        # 如果不等待，直接返回task_id
        if not wait:
            return {"task_id": task_id, "status": "pending"}

        # 等待完成
        return self._wait_for_completion(task_id, check_interval)

    def get_status(self, task_id: str) -> Dict:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            状态信息
        """
        response = requests.get(f"{self.base_url}/status/{task_id}")
        response.raise_for_status()
        return response.json()

    def get_result(self, task_id: str) -> Dict:
        """
        获取任务结果（仅完成的任务）

        Args:
            task_id: 任务ID

        Returns:
            优化结果
        """
        response = requests.get(f"{self.base_url}/result/{task_id}")
        response.raise_for_status()
        return response.json()

    def list_tasks(self) -> Dict:
        """列出所有任务"""
        response = requests.get(f"{self.base_url}/tasks")
        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id: str) -> Dict:
        """删除任务记录"""
        response = requests.delete(f"{self.base_url}/task/{task_id}")
        response.raise_for_status()
        return response.json()

    def _wait_for_completion(self, task_id: str, check_interval: int = 10) -> Dict:
        """
        等待任务完成

        Args:
            task_id: 任务ID
            check_interval: 检查间隔（秒）

        Returns:
            完成结果
        """
        print("等待优化完成...")
        dots = 0

        while True:
            try:
                status = self.get_status(task_id)

                if status['status'] == 'completed':
                    print("\n✓ 优化完成!")
                    return status
                elif status['status'] == 'failed':
                    raise Exception(f"优化失败: {status.get('error')}")

                # 显示进度
                dots = (dots + 1) % 4
                print(f"\r  状态: {status['status']} {'.' * dots}   ", end='', flush=True)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("\n\n⚠️  等待被中断，任务仍在后台运行")
                print(f"   使用以下命令查看结果: client.get_status('{task_id}')")
                raise


# ========================================
# 便捷函数
# ========================================

def quick_optimize(
    initial_prompt: str,
    examples: List[Dict[str, str]],
    validation_data: List[Dict[str, str]],
    task_name: str = "优化任务",
    task_description: str = "提示词优化",
    **kwargs
) -> str:
    """
    快速优化单个提示词

    Args:
        initial_prompt: 你的初始提示词
        examples: 训练样本
        validation_data: 验证样本
        task_name: 任务名称
        task_description: 任务描述
        **kwargs: 其他优化参数

    Returns:
        优化后的最佳提示词
    """
    client = PromptOptimizationClient()
    result = client.optimize(
        task_name=task_name,
        task_description=task_description,
        examples=examples,
        validation_data=validation_data,
        initial_prompts=[initial_prompt],
        **kwargs
    )

    return result['best_prompt']


# ========================================
# 使用示例
# ========================================

def example_sentiment_analysis():
    """示例：情感分析任务"""
    # 创建客户端
    client = PromptOptimizationClient()

    # 检查服务状态
    health = client.health_check()
    print(f"服务状态: {health['status']}")
    print(f"API Key配置: {'✓' if health['api_key_configured'] else '✗'}")

    # 准备数据
    examples = [
        {"input": "这个产品真的很棒，我非常喜欢！", "output": "positive"},
        {"input": "质量太差了，完全不值这个价格。", "output": "negative"},
        {"input": "今天天气很好，心情不错。", "output": "positive"},
        {"input": "服务态度恶劣，再也不来了。", "output": "negative"},
        {"input": "物流速度很快，包装也很好。", "output": "positive"},
    ]

    validation_data = [
        {"input": "这家餐厅的菜很美味", "output": "positive"},
        {"input": "等了一个小时还没上菜", "output": "negative"},
        {"input": "员工态度友好专业", "output": "positive"},
        {"input": "价格太贵了不划算", "output": "negative"},
    ]

    # 你的初始提示词
    my_prompts = [
        "请判断以下文本的情感是positive还是negative",
        "分析文本情感，回答positive或negative"
    ]

    # 优化提示词
    print("\n开始优化...")
    result = client.optimize(
        task_name="情感分析",
        task_description="判断文本情感是积极还是消极",
        examples=examples,
        validation_data=validation_data,
        initial_prompts=my_prompts,
        max_iterations=10
    )

    # 打印结果
    print("\n" + "="*70)
    print("优化结果:")
    print("="*70)
    print(f"\n最佳提示词:\n{result['best_prompt']}")
    print(f"\n最佳分数: {result['best_score']:.3f}")
    print(f"初始分数: {result['initial_score']:.3f}")
    print(f"提升幅度: {result['improvement']:.3f}")
    print(f"迭代次数: {result['iterations']}")
    print("\n分数历史:", result['score_history'])
    print("="*70)

    return result


def example_quick_optimize():
    """示例：快速优化"""
    # 使用便捷函数
    best_prompt = quick_optimize(
        initial_prompt="请判断文本情感",
        examples=[
            {"input": "很好", "output": "positive"},
            {"input": "很差", "output": "negative"},
            {"input": "满意", "output": "positive"},
        ],
        validation_data=[
            {"input": "不错", "output": "positive"},
            {"input": "糟糕", "output": "negative"},
        ],
        max_iterations=5
    )

    print(f"优化后的提示词: {best_prompt}")


def example_async_usage():
    """示例：异步使用（不等待完成）"""
    client = PromptOptimizationClient()

    # 提交任务但不等待
    result = client.optimize(
        task_name="测试任务",
        task_description="测试",
        examples=[
            {"input": "a", "output": "A"},
            {"input": "b", "output": "B"},
            {"input": "c", "output": "C"},
        ],
        validation_data=[
            {"input": "d", "output": "D"},
            {"input": "e", "output": "E"},
        ],
        initial_prompts=["测试提示词"],
        wait=False  # 不等待
    )

    task_id = result['task_id']
    print(f"任务已提交: {task_id}")

    # 稍后查询状态
    time.sleep(5)
    status = client.get_status(task_id)
    print(f"当前状态: {status['status']}")


if __name__ == "__main__":
    import sys

    print("\n" + "="*70)
    print("提示词优化API客户端")
    print("="*70)

    try:
        # 运行示例
        example_sentiment_analysis()

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到API服务")
        print("   请确保API服务正在运行: python api_server.py")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)
