# 评估实验

本节整理 COOP 的真实执行评估结果（基于 `coop_eval_actual/output/summary.csv`），并给出趋势分析与可视化图表索引。

## 实验内容与设置

- **任务来源**：由 `records (1)(4)(1).json` 解析 agent tree，生成带 `[agent:xxx]` 标签的任务数据集。
- **难度分层**：L1 / L3 / L5 / L8 四个层级，共 100 个任务（20 / 30 / 30 / 20）。
- **被评方法**：COOP、LangChain（工作流基线）、CoT、ReAct。
- **执行环境**：本地 Mock 工具环境；COOP 通过 `mock_task_planning` + `eval_execution` 走真实执行路径，但不依赖外部服务。
- **错误注入**：Mock 工具环境支持 500 错误注入（实验脚本默认 `error_injection_rate=0.2`，若运行时改动需同步更新）。
- **成功判定**：任务执行成功且满足预期 agent 路由（COOP 需同时满足执行成功与 `expected_agents` 一致）。
- **工作流基线**：固定顺序执行，无重试，最大执行步数为 5（模拟固定流程模板）。

## 指标与统计口径

- **成功率**：成功任务数 / 任务总数。
- **Token 开销**：`tokens_total` 平均值。
- **恢复率**：被注入 500 错误后成功恢复的比例。
- **工具调用次数**：`tool_calls_total` 平均值。
- **运行耗时**：COOP 记录 `duration_ms`，Baseline 当前未埋点（0 表示未记录）。

## 实验结果

> 聚合指标见 `coop_eval_actual/output/summary.csv`。

| 模型 | 难度 | 任务数 | 成功率 | Avg Tokens | 恢复率 | Avg Tool Calls | Avg Duration (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| COOP | L1 | 20 | 1.00 | 48.00 | 1.00 | 1.10 | 6.30 |
| COOP | L3 | 30 | 1.00 | 145.07 | 1.00 | 3.57 | 17.73 |
| COOP | L5 | 30 | 1.00 | 238.40 | 1.00 | 6.17 | 29.27 |
| COOP | L8 | 20 | 0.95 | 371.95 | 0.9091 | 10.10 | 60.35 |
| CoT | L1 | 20 | 0.80 | 52.00 | 0.00 | 1.00 | 0.00 |
| CoT | L3 | 30 | 0.60 | 157.07 | 0.00 | 2.50 | 0.00 |
| CoT | L5 | 30 | 0.00 | 218.40 | 0.00 | 2.97 | 0.00 |
| CoT | L8 | 20 | 0.00 | 247.55 | 0.00 | 3.05 | 0.00 |
| LangChain | L1 | 20 | 0.80 | 48.00 | 0.00 | 1.00 | 0.00 |
| LangChain | L3 | 30 | 0.50 | 145.07 | 0.00 | 2.47 | 0.00 |
| LangChain | L5 | 30 | 0.2667 | 238.40 | 0.00 | 3.40 | 0.00 |
| LangChain | L8 | 20 | 0.00 | 267.55 | 0.00 | 3.55 | 0.00 |
| ReAct | L1 | 20 | 1.00 | 56.00 | 1.00 | 1.10 | 0.00 |
| ReAct | L3 | 30 | 0.80 | 169.07 | 0.70 | 3.50 | 0.00 |
| ReAct | L5 | 30 | 0.70 | 278.40 | 0.5909 | 4.83 | 0.00 |
| ReAct | L8 | 20 | 0.00 | 439.55 | 0.55 | 5.70 | 0.00 |

## 结果分析

- **成功率趋势**：COOP 在 L1/L3/L5 保持 1.0，L8 仍为 0.95；LangChain 在 L5/L8 下降明显（L8 为 0）；ReAct 在 L8 为 0；CoT 在 L5/L8 为 0。
- **Token 开销**：随难度上升；L8 时 ReAct 最高（≈439.55），COOP 次之（≈371.95），LangChain 与 CoT 较低但成功率下降明显。
- **恢复率**：COOP 维持高恢复（L8 ≈0.9091），ReAct 随难度递减（至 0.55），LangChain/CoT 为 0。
- **工具调用**：COOP 难度越高调用次数上升更明显（L8 ≈10.1），ReAct 稳步上升，LangChain/CoT 较少。
- **运行耗时**：COOP 难度提升时耗时增长明显（L1≈6.3ms → L8≈60.35ms）；Baseline 当前无耗时埋点（0 表示缺失）。

## 图表索引

- 成功率趋势图：`coop_eval_actual/output/figure_success_rate.png`
- L8 Token 对比图：`coop_eval_actual/output/figure_tokens_level8.png`
- 错误类型分布图：`coop_eval_actual/output/figure_error_types.png`

如需补齐 baseline 耗时、扩展难度层级，或切换为论文版式图表，可在此节基础上补充。
