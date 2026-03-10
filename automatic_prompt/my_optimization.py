"""
快速入门：使用你自己的提示词进行优化
"""
from config import APOConfig, Task
from optimizer import PromptOptimizer
from utils import print_summary


# ============================================
# 第1步：定义你的任务
# ============================================
task = Task(
    name="你的任务名称",  # 例如：情感分析、文本分类、问答等
    description="任务描述",

    # 提供一些示例（用于生成新的候选提示词）
    examples=[
        {"input": "示例输入1", "output": "示例输出1"},
        {"input": "示例输入2", "output": "示例输出2"},
        {"input": "示例输入3", "output": "示例输出3"},
    ],

    # 验证数据（用于评估提示词效果）
    validation_data=[
        {"input": "验证输入1", "output": "验证输出1"},
        {"input": "验证输入2", "output": "验证输出2"},
        {"input": "验证输入3", "output": "验证输出3"},
    ],
)


# ============================================
# 第2步：定义你自己的初始提示词
# ============================================
# 方式1：使用单个提示词
my_prompt = """
在这里写你自己的提示词...
可以是多行的。
"""

# 方式2：使用多个提示词（系统会从这些提示词开始优化）
my_prompts = [
    "你的第一个提示词版本...",
    "你的第二个提示词版本...",
    "你的第三个提示词版本...",
]


# ============================================
# 第3步：创建配置和优化器
# ============================================
config = APOConfig(
    max_iterations=10,      # 最多优化多少轮
    num_candidates=5,       # 每轮生成多少个候选
    top_k=3,               # 保留多少个最优候选
    verbose=True,          # 显示详细日志
)

optimizer = PromptOptimizer(config, task)


# ============================================
# 第4步：运行优化
# ============================================
# 使用单个提示词
result = optimizer.optimize(initial_prompts=[my_prompt])

# 或者使用多个提示词
# result = optimizer.optimize(initial_prompts=my_prompts)


# ============================================
# 第5步：查看结果
# ============================================
print_summary(result)

# 获取最佳提示词
best_prompt = result["best_prompt"]
best_score = result["best_score"]

print(f"\n最佳提示词:")
print(f"{best_prompt}")
print(f"\n分数: {best_score}")
