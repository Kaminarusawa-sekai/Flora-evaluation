"""
示例代码 - 展示如何使用APO系统
"""
from config import APOConfig, Task
from optimizer import PromptOptimizer, APOFactory
from utils import print_summary, Visualizer, ResultSaver, ReportGenerator


def example_sentiment_analysis():
    """示例1：情感分析任务"""
    print("\n" + "=" * 70)
    print("示例1：情感分析任务优化")
    print("=" * 70)

    # 1. 定义任务
    task = Task(
        name="情感分析",
        description="判断给定文本的情感是积极(positive)还是消极(negative)",
        examples=[
            {"input": "这个产品真的很棒，我非常喜欢！", "output": "positive"},
            {"input": "质量太差了，完全不值这个价格。", "output": "negative"},
            {"input": "今天天气很好，心情不错。", "output": "positive"},
            {"input": "服务态度恶劣，再也不来了。", "output": "negative"},
            {"input": "物流速度很快，包装也很好。", "output": "positive"},
        ],
        validation_data=[
            {"input": "这家餐厅的菜很美味", "output": "positive"},
            {"input": "等了一个小时还没上菜", "output": "negative"},
            {"input": "员工态度友好专业", "output": "positive"},
            {"input": "价格太贵了不划算", "output": "negative"},
            {"input": "环境优雅舒适", "output": "positive"},
            {"input": "东西坏了也不给退", "output": "negative"},
            {"input": "性价比很高推荐", "output": "positive"},
            {"input": "质量堪忧不推荐", "output": "negative"},
        ],
    )

    # 2. 创建优化器（使用工厂方法）
    optimizer = APOFactory.create_simple_optimizer(task)

    # 3. 执行优化
    result = optimizer.optimize(num_seeds=3)

    # 4. 打印结果
    print_summary(result)

    # 5. 保存结果
    ResultSaver.save_optimization_result(result, "results/sentiment_analysis.json")

    # 6. 可视化
    # Visualizer.plot_optimization_history(result["history"], "results/sentiment_plot.png")

    return result


def example_math_reasoning():
    """示例2：数学推理任务"""
    print("\n" + "=" * 70)
    print("示例2：数学推理任务优化")
    print("=" * 70)

    # 1. 定义任务
    task = Task(
        name="数学推理",
        description="解决数学应用题并给出答案",
        examples=[
            {"input": "小明有5个苹果，小红给了他3个，他现在有多少个？", "output": "8"},
            {"input": "一个班有30个学生，其中12个是女生，男生有多少个？", "output": "18"},
            {"input": "买3支笔需要15元，买1支笔需要多少元？", "output": "5"},
        ],
        validation_data=[
            {"input": "一本书50页，看了20页，还剩多少页？", "output": "30"},
            {"input": "5个人分10个苹果，每人分几个？", "output": "2"},
            {"input": "一周有7天，3周有多少天？", "output": "21"},
            {"input": "100减去45等于多少？", "output": "55"},
        ],
    )

    # 2. 创建配置
    config = APOConfig(
        max_iterations=8,
        num_candidates=5,
        top_k=3,
        generation_strategy="llm_rewrite",
        use_llm_feedback=True,
        verbose=True,
    )

    # 3. 创建并运行优化器
    optimizer = PromptOptimizer(config, task)
    result = optimizer.optimize()

    # 4. 显示结果
    print_summary(result)

    return result


def example_text_classification():
    """示例3：文本分类任务"""
    print("\n" + "=" * 70)
    print("示例3：文本分类任务优化")
    print("=" * 70)

    task = Task(
        name="新闻分类",
        description="将新闻分类为：科技、体育、娱乐、财经",
        examples=[
            {"input": "苹果发布新款iPhone，搭载最新芯片", "output": "科技"},
            {"input": "NBA总决赛今晚开打，勇士对阵湖人", "output": "体育"},
            {"input": "新电影票房破10亿，导演发表感言", "output": "娱乐"},
            {"input": "股市今日上涨2%，创年内新高", "output": "财经"},
        ],
        validation_data=[
            {"input": "AI技术取得重大突破", "output": "科技"},
            {"input": "足球世界杯小组赛结束", "output": "体育"},
            {"input": "明星结婚引发热议", "output": "娱乐"},
            {"input": "央行宣布降息政策", "output": "财经"},
            {"input": "特斯拉推出新能源车型", "output": "科技"},
            {"input": "奥运会金牌得主接受采访", "output": "体育"},
        ],
    )

    # 使用遗传算法优化器
    optimizer = APOFactory.create_genetic_optimizer(task)
    result = optimizer.optimize(num_seeds=4)

    print_summary(result)

    # 生成报告
    ReportGenerator.generate_markdown_report(result, "results/classification_report.md")

    return result


def example_custom_task():
    """示例4：自定义任务"""
    print("\n" + "=" * 70)
    print("示例4：自定义任务（可以替换为您的任务）")
    print("=" * 70)

    # 创建您的任务
    task = Task(
        name="您的任务名称",
        description="任务描述",
        examples=[
            # 添加您的示例
            {"input": "示例输入1", "output": "示例输出1"},
            {"input": "示例输入2", "output": "示例输出2"},
        ],
        validation_data=[
            # 添加验证数据
            {"input": "验证输入1", "output": "验证输出1"},
            {"input": "验证输入2", "output": "验证输出2"},
        ],
    )

    # 创建自定义配置
    config = APOConfig(
        llm_api_key="your-api-key-here",  # 替换为您的API密钥
        llm_model="gpt-3.5-turbo",
        max_iterations=10,
        num_candidates=6,
        top_k=3,
        generation_strategy="llm_rewrite",  # 或 "genetic", "mutation"
        use_llm_feedback=True,
        early_stop_threshold=0.90,
        verbose=True,
    )

    # 运行优化
    optimizer = PromptOptimizer(config, task)
    result = optimizer.optimize()

    print_summary(result)

    return result


def compare_strategies():
    """示例5：比较不同的优化策略"""
    print("\n" + "=" * 70)
    print("示例5：比较不同优化策略")
    print("=" * 70)

    # 创建一个简单任务
    task = Task(
        name="简单分类",
        description="判断数字是奇数还是偶数",
        examples=[
            {"input": "2", "output": "偶数"},
            {"input": "3", "output": "奇数"},
            {"input": "10", "output": "偶数"},
        ],
        validation_data=[
            {"input": "5", "output": "奇数"},
            {"input": "8", "output": "偶数"},
            {"input": "15", "output": "奇数"},
        ],
    )

    strategies = ["llm_rewrite", "genetic", "mutation"]
    results = {}

    for strategy in strategies:
        print(f"\n测试策略: {strategy}")
        print("-" * 60)

        config = APOConfig(
            max_iterations=5,
            num_candidates=4,
            top_k=2,
            generation_strategy=strategy,
            verbose=False,
        )

        optimizer = PromptOptimizer(config, task)
        result = optimizer.optimize()

        results[strategy] = result
        print(
            f"策略 {strategy}: 最终分数 = {result['best_score']:.3f}, "
            f"迭代次数 = {result['iterations']}"
        )

    # 比较结果
    print("\n" + "=" * 70)
    print("策略对比总结:")
    print("=" * 70)
    for strategy, result in results.items():
        print(f"{strategy:15s}: {result['best_score']:.3f}")

    return results


def main():
    """主函数 - 运行所有示例"""
    import sys

    print("\n")
    print("*" * 70)
    print(" " * 15 + "自动提示词优化系统 (APO)")
    print(" " * 20 + "使用示例")
    print("*" * 70)

    # 菜单
    print("\n请选择要运行的示例:")
    print("1. 情感分析任务")
    print("2. 数学推理任务")
    print("3. 文本分类任务")
    print("4. 自定义任务")
    print("5. 比较不同策略")
    print("6. 运行所有示例")
    print("0. 退出")

    try:
        choice = input("\n请输入选项 (0-6): ").strip()

        if choice == "1":
            example_sentiment_analysis()
        elif choice == "2":
            example_math_reasoning()
        elif choice == "3":
            example_text_classification()
        elif choice == "4":
            example_custom_task()
        elif choice == "5":
            compare_strategies()
        elif choice == "6":
            example_sentiment_analysis()
            example_math_reasoning()
            example_text_classification()
        elif choice == "0":
            print("\n再见！")
            sys.exit(0)
        else:
            print("\n无效选项，请重新运行程序。")

    except KeyboardInterrupt:
        print("\n\n程序被中断。再见！")
        sys.exit(0)


if __name__ == "__main__":
    # 创建结果目录
    import os

    os.makedirs("results", exist_ok=True)

    # 运行主程序
    main()

    print("\n" + "=" * 70)
    print("感谢使用自动提示词优化系统！")
    print("=" * 70)
