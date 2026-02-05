# COOP 真实评估（本地执行版）

此目录用于 **真实运行** COOP 架构与基线（CoT/ReAct），不再生成模拟数据。
Agent 树来自 `records (1)(4)(1).json`，执行走本地 Mock 执行器。

## 环境要求

- Python: `/usr/local/bin/python3`
- 本地无需 Neo4j/Dify
- 如需禁用事件上报（推荐）：设置 `COOP_DISABLE_EVENT_BUS=1`

## 快速开始

1) 生成数据集

```bash
COOP_DISABLE_EVENT_BUS=1 /usr/local/bin/python3 coop_eval_actual/dataset_generator.py \
  --records "records (1)(4)(1).json" \
  --output coop_eval_actual/data/dataset.json
```

2) 运行评估（包含 CoT / ReAct / COOP）

```bash
COOP_DISABLE_EVENT_BUS=1 /usr/local/bin/python3 coop_eval_actual/run_experiment.py \
  --dataset coop_eval_actual/data/dataset.json \
  --records "records (1)(4)(1).json" \
  --config coop_eval_actual/configs/eval_config.json \
  --output_dir coop_eval_actual/output
```

## 输出

- `coop_eval_actual/output/experiment_results.csv`：逐任务结果
- `coop_eval_actual/output/summary.csv`：按模型/复杂度聚合
- `coop_eval_actual/output/raw_logs.jsonl`：工具调用日志

## 说明

- COOP 侧使用 `mock_task_planning` 与 `eval_execution`（真实运行路径，但不依赖外部服务）。
- Baseline 行为为确定性逻辑（非随机），用于稳定复现实验曲线。
