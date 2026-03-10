# 自动提示词优化系统 (Automatic Prompt Optimization)

基于论文《A Systematic Survey of Automatic Prompt Optimization Techniques》实现的Python自动提示词优化框架。

## 📚 项目简介

本项目实现了一个完整的自动提示词优化（APO）系统，帮助您自动优化LLM的提示词，提升任务性能。

### 核心特性

- ✅ **多种优化策略**：LLM重写、遗传算法、变异等
- ✅ **灵活的评估机制**：准确率、LLM反馈、多指标支持
- ✅ **智能候选选择**：TopK、UCB、多样性选择、自适应选择
- ✅ **自动数据合成**：从少量示例生成更多测试数据（⭐新功能）
- ✅ **早停机制**：自动检测收敛，节省计算资源
- ✅ **可视化支持**：优化曲线、候选对比图
- ✅ **易于扩展**：模块化设计，方便添加新策略

## 🏗️ 系统架构

```
APO Framework (5-Part Pipeline)
│
├── 1. Seed Initialization (种子初始化)
│   ├── Manual Instructions (手动创建)
│   └── LLM Instruction Induction (LLM指令归纳)
│
├── 2. Inference Evaluation (推理评估)
│   ├── Numeric Scores (数值评分)
│   │   ├── Accuracy (准确率)
│   │   ├── Reward Model (奖励模型)
│   │   └── Entropy-based (熵基础)
│   ├── LLM Feedback (LLM反馈)
│   └── Human Feedback (人类反馈)
│
├── 3. Candidate Generation (候选生成)
│   ├── Heuristic Edits (启发式编辑)
│   │   ├── Monte Carlo Sampling
│   │   ├── Genetic Algorithm (遗传算法)
│   │   └── Word/Phrase Edits
│   ├── LLM Rewriting (LLM重写)
│   └── Meta-prompt Design (元提示设计)
│
├── 4. Filter & Retain (过滤保留)
│   ├── TopK Greedy Search
│   ├── UCB (上置信界限)
│   ├── Diversity Selection (多样性选择)
│   └── Adaptive Selection (自适应选择)
│
└── 5. Iteration Control (迭代控制)
    ├── Fixed Steps (固定步数)
    └── Early Stopping (早停)
```

## 🚀 快速开始

### 1. 安装项目

```bash
# 克隆仓库
git clone <repo-url>
cd Automatic_prompt

# 方式一：直接安装依赖
pip install -r requirements.txt

# 方式二：以开发模式安装（推荐）
pip install -e .

# 方式三：包含开发工具
pip install -e ".[dev]"
```

### 2. 配置API密钥

**重要：必须先配置API密钥才能使用！**

```bash
# 步骤1: 复制环境变量模板
cp .env.example .env

# 步骤2: 编辑 .env 文件，填入你的千问API密钥
# QWEN_API_KEY=your_actual_api_key_here

# 步骤3: 验证配置（可选）
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('QWEN_API_KEY')[:10] + '...')"
```

**获取千问API密钥：**
1. 访问 https://dashscope.console.aliyun.com/apiKey
2. 登录/注册阿里云账号
3. 创建并复制API密钥
4. 粘贴到 `.env` 文件中

### 3. 基础使用

```python
from config import Task
from optimizer import APOFactory

# 1. 定义您的任务
task = Task(
    name="情感分析",
    description="判断文本情感是积极还是消极",
    examples=[
        {"input": "这个产品很棒！", "output": "积极"},
        {"input": "质量太差了。", "output": "消极"},
    ],
    validation_data=[
        {"input": "服务很好", "output": "积极"},
        {"input": "不推荐购买", "output": "消极"},
    ]
)

# 2. 创建优化器（API密钥会自动从.env加载）
optimizer = APOFactory.create_simple_optimizer(task)

# 3. 执行优化
result = optimizer.optimize()

# 4. 查看结果
print(f"最佳提示词: {result['best_prompt']}")
print(f"最佳分数: {result['best_score']:.3f}")
```

### 4. 运行示例

```bash
python main.py
```

## 📖 详细文档

### 核心模块说明

#### 1. **config.py** - 配置模块
定义优化配置和任务结构。

```python
from config import APOConfig, Task

config = APOConfig(
    max_iterations=10,      # 最大迭代次数
    num_candidates=5,       # 每轮生成候选数
    top_k=3,               # 保留的最优候选数
    generation_strategy="llm_rewrite",  # 生成策略
    use_llm_feedback=True, # 使用LLM反馈
    early_stop_threshold=0.90  # 早停阈值
)
```

#### 2. **evaluator.py** - 评估模块
评估提示词性能。

```python
from evaluator import Evaluator

evaluator = Evaluator(config, task)
result = evaluator.evaluate_prompt("Your prompt here")
print(f"准确率: {result['accuracy']:.3f}")
```

#### 3. **generator.py** - 生成模块
生成优化后的候选提示词。

```python
from generator import CandidateGenerator

generator = CandidateGenerator(config, task)

# 生成初始种子
seeds = generator.initialize_seed_prompts(num_seeds=3)

# 生成新候选
candidates = generator.generate_candidates(seeds)
```

#### 4. **selector.py** - 选择模块
选择和过滤候选提示词。

```python
from selector import Selector

selector = Selector(config)

# TopK选择
top_candidates = selector.select_top_k(candidates, scores, k=3)

# UCB选择（平衡探索与利用）
selected = selector.ucb_selection(candidates, scores, iteration)

# 多样性选择
diverse_candidates = selector.diversity_selection(candidates, scores)
```

#### 5. **optimizer.py** - 主优化器
整合所有模块的核心优化器。

```python
from optimizer import PromptOptimizer, APOFactory

# 方式1：使用工厂创建
optimizer = APOFactory.create_simple_optimizer(task)
optimizer = APOFactory.create_advanced_optimizer(task)
optimizer = APOFactory.create_genetic_optimizer(task)

# 方式2：自定义配置
optimizer = PromptOptimizer(custom_config, task)

# 执行优化
result = optimizer.optimize()
```

#### 6. **utils.py** - 工具模块
提供可视化、保存、分析等功能。

```python
from utils import Visualizer, ResultSaver, ReportGenerator

# 可视化
Visualizer.plot_optimization_history(result['history'])
Visualizer.plot_candidates_comparison(candidates, scores)

# 保存结果
ResultSaver.save_optimization_result(result, 'result.json')

# 生成报告
ReportGenerator.generate_markdown_report(result, 'report.md')
```

## 🎯 使用示例

### 示例1：情感分析

```python
from main import example_sentiment_analysis

result = example_sentiment_analysis()
```

### 示例2：数学推理

```python
from main import example_math_reasoning

result = example_math_reasoning()
```

### 示例3：文本分类

```python
from main import example_text_classification

result = example_text_classification()
```

### 示例4：比较不同策略

```python
from main import compare_strategies

results = compare_strategies()
```

### 示例5：自动数据合成（⭐ 新功能）

当您只有少量示例时，系统会自动生成更多测试数据：

```python
from config import Task
from optimizer import APOFactory

# 用户只提供3个示例
task = Task(
    name="情感分析",
    description="判断情感",
    examples=[
        {"input": "很好", "output": "positive"},
        {"input": "很差", "output": "negative"},
        {"input": "不错", "output": "positive"},
    ],
    validation_data=[  # 只有2个验证样本
        {"input": "满意", "output": "positive"},
        {"input": "失望", "output": "negative"},
    ]
)

# 创建优化器
optimizer = APOFactory.create_simple_optimizer(task)

# 执行优化（自动扩充数据到30个样本）
result = optimizer.optimize(
    auto_augment_data=True,  # 启用自动数据增强
    target_validation_size=30  # 目标验证集大小
)

print(f"原始验证数据: 2个")
print(f"增强后数据: {len(task.validation_data)}个")
print(f"最佳分数: {result['best_score']:.3f}")
```

**运行数据合成示例**：
```bash
python example_data_synthesis.py
```

#### 数据合成的优势

| 场景 | 不使用数据合成 | 使用数据合成 |
|------|--------------|-------------|
| 验证数据量 | 3-5个（不足） | 30+个（充足） |
| 评估准确性 | ⚠️  不可靠 | ✅ 可靠 |
| 优化效果 | 可能过拟合 | 泛化性好 |
| 用户负担 | 需要手动准备大量数据 | 只需提供少量示例 |


## 🔧 高级配置

### 自定义生成策略

```python
from generator import CandidateGenerator

class MyGenerator(CandidateGenerator):
    def my_custom_strategy(self, prompts):
        # 实现您的生成策略
        pass
```

### 自定义评估指标

```python
from evaluator import Evaluator

class MyEvaluator(Evaluator):
    def custom_metric(self, prediction, reference):
        # 实现您的评估指标
        pass
```

### 自定义选择策略

```python
from selector import Selector

class MySelector(Selector):
    def custom_selection(self, candidates, scores):
        # 实现您的选择策略
        pass
```

## 📊 优化策略对比

| 策略 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **LLM重写** | 通用任务 | 效果好，可解释性强 | 需要LLM API |
| **遗传算法** | 探索式优化 | 避免局部最优 | 收敛较慢 |
| **变异法** | 快速迭代 | 简单高效 | 可能陷入局部最优 |

## 🎨 可视化示例

系统支持多种可视化：

1. **优化历史曲线**：展示分数随迭代的变化
2. **候选对比图**：比较不同候选的性能
3. **提示词演化图**：展示提示词的变化轨迹

```python
from utils import Visualizer

# 绘制优化历史
Visualizer.plot_optimization_history(
    result['history'],
    save_path='optimization_history.png'
)

# 绘制候选对比
Visualizer.plot_candidates_comparison(
    candidates,
    scores,
    save_path='candidates_comparison.png'
)
```

## 🔍 常见问题

### Q: 如何集成真实的LLM API？

A: 在`evaluator.py`中的`_get_llm_response`方法中添加您的API调用：

```python
def _get_llm_response(self, prompt: str) -> str:
    import openai
    openai.api_key = self.config.llm_api_key

    response = openai.ChatCompletion.create(
        model=self.config.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=self.config.llm_temperature
    )
    return response.choices[0].message.content
```

### Q: 如何添加自定义评估指标？

A: 在`MetricCalculator`类中添加新方法：

```python
@staticmethod
def my_metric(predictions, references):
    # 您的实现
    return score
```

### Q: 优化需要多长时间？

A: 取决于：
- 迭代次数（配置中的`max_iterations`）
- 候选数量（`num_candidates`）
- LLM响应速度
- 验证数据大小

通常5-15分钟可以完成一次优化。

### Q: 如何保存和加载优化结果？

```python
from utils import ResultSaver

# 保存
ResultSaver.save_optimization_result(result, 'my_result.json')

# 加载
result = ResultSaver.load_optimization_result('my_result.json')
```

## 📈 性能优化建议

1. **使用缓存**：缓存LLM响应避免重复调用
2. **并行评估**：多线程评估候选提示词
3. **早停**：设置合理的早停阈值
4. **分阶段优化**：先粗略优化，再精细调整

## 🤝 贡献指南

欢迎提交PR和Issue！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

MIT License

## 📚 参考文献

本项目基于以下论文实现：

```
Kiran Ramnath et al. (2025). A Systematic Survey of Automatic Prompt
Optimization Techniques. arXiv:2502.16923v2 [cs.CL]
```

其他重要参考：
- APE (Zhou et al., 2022): Automatic Prompt Engineer
- OPRO (Yang et al., 2024): Large Language Models as Optimizers
- ProTeGi (Pryzant et al., 2023): Gradient Descent with Text
- PromptBreeder (Fernando et al., 2023): Self-Referential Self-Improvement
- DSPY (Khattab et al., 2024): Compiling Declarative Language Model Calls

## 📧 联系方式

如有问题或建议，请通过Issue或Email联系。

---

**⭐ 如果这个项目对您有帮助，请给个Star！**
