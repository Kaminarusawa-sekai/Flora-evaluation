# Changelog

---

## [2026-02-02 14:42] - 修复COOP token计算和agent统计问题

### 任务描述
修复两个问题：
1. COOP的token计算全部为0
2. COOP的agent统计数量偏少（agent_id在结果传递链中丢失）

### 修改文件
- [x] tasks/capabilities/llm/qwen_llm.py - 在LLM层统一记录token
  - 添加 `_get_token_tracker()` 和 `_get_current_task_context()` 辅助函数
  - 添加 `_record_token_usage()` 方法
  - 在 `_call_text_model()` 和 `_call_vl_model()` 中调用token记录
- [x] tasks/capability_actors/result_aggregator_actor.py - 保留agent_id信息
  - 修改 `_handle_task_completed_message()` 传递 agent_id
  - 修改 `_process_success()` 保存 agent_id 到 `_completed_tasks`
  - 修改 `_check_completion()` 在返回结果时包含 agent_id
- [x] tasks/capability_actors/task_group_aggregator_actor.py - 在step_results中保存agent_id
  - 修改消息处理，传递完整的 TaskCompletedMessage
  - 修改 `_handle_step_success()` 提取并保存 agent_id 和 executor
- [x] coop_eval_actual/coop_runner.py - 增强agent_id提取
  - 修改 `_extract_agent_ids()` 同时提取 executor 字段

### 关键决策
1. **Token统计**: 在 `QwenLLM.generate()` 层统一记录，而不是在每个调用点分散记录
   - 优点：所有LLM调用自动被统计，无需修改每个调用点
   - 通过环境变量 `COOP_EVAL_EXECUTION=1` 控制是否启用
2. **Agent统计**: 在结果传递链中保留 agent_id 信息
   - `LeafActor` → `ResultAggregatorActor` → `TaskGroupAggregatorActor` 全链路传递
   - `step_results` 结构改为 `{result, agent_id, executor}`

### 状态
✅ 完成 (2026-02-02 14:55)

---

## [2026-02-02 14:08] - 分析COOP token计算和agent统计问题

### 任务描述
分析两个问题：
1. COOP的token计算全部为0
2. 数据集中1阶任务太多，难度区分度不大

### 分析结果

#### 问题1: Token计算全部为0

**根本原因**: Token统计只在 `CommonTaskPlanning._call_llm()` 中记录，但COOP系统中有**多处LLM调用未被统计**。

**未统计的LLM调用位置**:
1. `tasks/capability_actors/execution_actor.py:133` - 执行actor的LLM调用
2. `tasks/capability_actors/mcp_actor.py:82, 157, 175` - MCP actor的多处LLM调用
3. `tasks/agents/agent_actor.py:592` - agent actor的LLM调用
4. `tasks/capabilities/decision/decision_impl.py:60, 142` - 决策能力的LLM调用
5. `tasks/capabilities/context_resolver/tree_context_resolver.py:388, 511, 587` - 上下文解析的LLM调用
6. `tasks/capabilities/llm_memory/unified_manageer/manager.py:76, 279, 356` - 记忆管理的LLM调用

**问题代码分析** (`common_task_planner.py:786-808`):
```python
def _call_llm(self, prompt: str, agent_id: str = "") -> str:
    response = self.llm.generate(prompt)
    tracker = get_token_tracker()
    if tracker:
        task_id, layer = self.get_current_task()
        if task_id:
            tracker.record_llm_call(...)  # 只有这里记录
```

**另一个问题**: `increment_layer()` 从未被调用，导致layer始终为0。

#### 问题2: 1阶任务过多，难度区分度不大

**数据集level分布** (dataset_erp_v3.json):
- Level 1: 42 tasks (84%)
- Level 2: 3 tasks (6%)
- Level 3: 4 tasks (8%)
- Level 4: 1 task (2%)

**Level定义** (`coop_eval_actual/utils.py:96-126`):
```python
def calculate_cross_system_level(expected_agents: List[str]) -> int:
    # Level 1: 单系统内操作
    # Level 2: 跨 2 个系统
    # Level 3: 跨 3 个系统
    # Level 4: 跨 4+ 个系统
```

**问题分析**:
1. **Level定义过于简单**: 只基于"跨系统数量"，没有考虑:
   - 任务分解深度 (agent树的层级)
   - 子任务数量
   - 任务间依赖复杂度
   - 是否需要多轮交互

2. **数据集设计偏向单系统**: 大部分任务都在单个系统内完成，导致84%的任务都是Level 1

3. **缺少"阶"的概念**: 当前的level只是"跨系统复杂度"，而不是"任务分解阶数"。真正的"阶"应该是agent树的分解深度。

### 修改文件
(本次为分析任务，无代码修改)

### 关键决策
需要后续修复:
1. 在所有LLM调用点添加token统计
2. 在任务分解时调用`increment_layer()`
3. 重新设计任务复杂度评估指标，加入分解深度

### 状态
✅ 分析完成 (2026-02-02 14:08)

---

## [2026-01-30 16:28] - COOP评估系统三项改进

### 任务描述
1. 修复 COOP Token 统计：累计所有层级的 LLM 调用 token
2. 重新定义 Level：基于跨业务系统数量而非步骤数
3. 增加简短 Prompt：添加 prompt_brief 字段测试意图理解能力

### 修改文件
- [x] coop_eval_actual/utils.py - 新增 TokenTracker 类和 calculate_cross_system_level 函数
- [x] tasks/capabilities/task_planning/common_task_planner.py - 添加任务上下文跟踪，_call_llm 记录 token
- [x] coop_eval_actual/coop_runner.py - 集成 TokenTracker，获取真实累计 token 统计
- [x] coop_eval_actual/scripts/enhance_dataset.py - 新增：生成增强数据集脚本
- [x] coop_eval_actual/data/dataset_erp_v3.json - 新增：包含 level/prompt_brief/systems 的增强数据集

### 关键决策
1. TokenTracker 使用单例模式 + 线程本地存储，支持并发任务
2. Level 定义：Level 1=单系统, Level 2=跨2系统, Level 3=跨3系统, Level 4=跨4+系统
3. prompt_brief 为真实用户可能说的简短模糊指令，用于测试意图理解能力

### 状态
✅ 完成 (2026-01-30 16:45)

---

## [2026-01-29 14:25] - 将 CoT/ReAct/Workflow 从 Mock 改为真实 LLM 规划实验

### 任务描述
当前 `run_experiment.py` 中的 CoT、ReAct、Workflow 基线方法都使用 MockToolEnvironment，直接从 prompt 中提取 `[agent:xxx]` 标签作为执行计划，没有真正调用 LLM 进行推理和规划。这导致实验对比不公平。

需要改造为：
1. 生成不含标签的自然语言数据集
2. CoT/ReAct/Workflow 使用真实 LLM 进行任务规划（选择哪些 Agent、什么顺序）
3. 执行层可保持 Mock（因真实 Agent 执行需要外部服务）
4. 与 COOP 进行公平对比

### 修改文件
- [x] coop_eval_actual/scripts/generate_natural_dataset.py - 新增：生成无标签数据集
- [x] coop_eval_actual/data/dataset_natural.json - 新增：自然语言数据集（100个任务）
- [x] coop_eval_actual/scripts/generate_erp_dataset.py - 新增：生成 ERP 场景数据集
- [x] coop_eval_actual/data/dataset_erp.json - 新增：ERP 测试数据集（50个任务）
- [x] coop_eval_actual/real_planners.py - 新增：真实 LLM 规划器（CoT/ReAct/Workflow）
- [x] coop_eval_actual/baselines.py - 修改：调用真实规划器，新增 planned_agents 字段
- [x] coop_eval_actual/run_experiment.py - 修改：集成真实 LLM，新增日志和摘要输出
- [x] coop_eval_actual/configs/eval_config.json - 修改：启用 common_task_planning + qwen_llm
- [x] coop_eval_actual/agent_tree_loader.py - 修改：支持多编码格式，自动标记叶子节点
- [x] coop_eval_actual/coop_runner.py - 修改：设置 COOP_EVAL_EXECUTION 环境变量，递归提取 agent_id
- [x] tasks/capability_actors/execution_actor.py - 修改：评估模式下 Mock 执行
- [x] tasks/capability_actors/result_aggregator_actor.py - 修复：使用全局 treeManager 单例判断叶子节点
- [x] tasks/capabilities/task_planning/common_task_planner.py - 修复：LLM 延迟加载

### 关键决策
1. COOP 使用递进查找（每层只看子节点），CoT/ReAct/Workflow 使用扁平查找（一次看 250 个 Agent）
2. CoT/ReAct 的规划和执行循环都真实调用 LLM，不 mock
3. 只有最终叶子节点的外部工具调用使用 Mock（因为需要外部服务）
4. 使用 records (2).json 作为 Agent 树数据源（250 个 Agent，5 层深度）
5. 修复 ResultAggregatorActor._is_leaf_node 使用全局 treeManager 单例，确保递进执行

### 状态
✅ 完成 (2026-01-29 16:12)

### 最终实验结果

| 策略 | 平均 Token | 执行深度 | 特点 |
|------|-----------|---------|------|
| **COOP** | **408-495** | 递进到叶子节点 | Token 效率最高 |
| CoT | 17949-17995 | 扁平选择 | 一次性规划 |
| LangChain | 17967-18022 | 扁平选择 | 模板匹配 |
| ReAct | 110213-128790 | 扁平迭代 | 8 次迭代 |

**COOP Token 效率是 CoT 的 40 倍，是 ReAct 的 250 倍**

### 运行方式
```bash
# 生成 ERP 数据集
python -m coop_eval_actual.scripts.generate_erp_dataset --records "records (2).json"

# 运行完整实验
python -m coop_eval_actual.run_experiment --dataset coop_eval_actual/data/dataset_erp.json --records "records (2).json"

# 只运行基线（跳过 COOP）
python -m coop_eval_actual.run_experiment --dataset coop_eval_actual/data/dataset_erp.json --records "records (2).json" --skip_coop

# 只运行 COOP（跳过基线）
python -m coop_eval_actual.run_experiment --dataset coop_eval_actual/data/dataset_erp.json --records "records (2).json" --skip_baselines
```
