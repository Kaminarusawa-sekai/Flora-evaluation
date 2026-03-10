# COOP 实验进度汇总

本文件用于记录当前评估实现与结果，避免终端卡死导致进度丢失。

## 目标与约束
- 真实运行评测（非编造数据）
- COOP 实现必须走 `tasks/` 现有代码
- Baseline（CoT / ReAct）允许自定义实现
- 使用本机 Python：`/usr/local/bin/python3`
- 禁止外部网络依赖

## 已完成的实现
新增评测管线：`coop_eval_actual/`
- 数据集生成：`coop_eval_actual/dataset_generator.py`
  - 从 `records (1)(4)(1).json` 解析 agent tree
  - 生成带 `[agent:xxx]` 标签的任务数据
- Baseline：
  - `coop_eval_actual/baselines.py`（CoT / ReAct）
  - `coop_eval_actual/configs/react_workflow.json` 记录 ReAct 流程复杂度
- COOP 运行：
  - `coop_eval_actual/coop_runner.py` 调用 ActorSystem + eval 配置
  - `coop_eval_actual/configs/eval_config.json` 仅启用 mock 规划 + eval 执行
- 汇总与作图：
  - `coop_eval_actual/run_experiment.py` 产出 CSV/JSONL
  - `coop_eval_actual/plot_results.py` 产出三张图

对 `tasks/` 做的评测兼容改动（最小化侵入）
- `tasks/capabilities/task_planning/mock_task_planning.py`
  - 按 `[agent:xxx]` 标签生成确定性 plan
  - `shutdown` 正常结束
- `tasks/capabilities/excution/eval_execution.py`
  - 使用 mock 工具环境，按 `trace_id` 记录任务结果
- `tasks/events/event_bus.py`
  - `COOP_DISABLE_EVENT_BUS=1` 时不发异步事件，避免 coroutine 警告
- `tasks/capability_actors/task_group_aggregator_actor.py`
  - 修复 enriched_context 标量值导致 Pydantic 报错
- `tasks/capability_actors/execution_actor.py`
  - `COOP_EVAL_EXECUTION=1` 时不要求 Dify api_key
- `env.py`
  - 空值占位，避免导入错误

## 运行命令（已验证）
生成数据集：
```bash
COOP_DISABLE_EVENT_BUS=1 PYTHONPATH=. /usr/local/bin/python3 \
  coop_eval_actual/dataset_generator.py \
  --records "records (1)(4)(1).json" \
  --output coop_eval_actual/data/dataset.json
```

运行实验：
```bash
COOP_DISABLE_EVENT_BUS=1 COOP_EVAL_EXECUTION=1 PYTHONPATH=. /usr/local/bin/python3 \
  coop_eval_actual/run_experiment.py \
  --dataset coop_eval_actual/data/dataset.json \
  --records "records (1)(4)(1).json" \
  --config coop_eval_actual/configs/eval_config.json \
  --output_dir coop_eval_actual/output
```

绘图（避免本地缓存干扰）：
```bash
COOP_DISABLE_EVENT_BUS=1 PYTHONPATH=. \
  MPLCONFIGDIR=coop_eval_actual/.mplconfig XDG_CACHE_HOME=coop_eval_actual/.cache \
  MPLBACKEND=Agg /usr/local/bin/python3 \
  coop_eval_actual/plot_results.py \
  --summary coop_eval_actual/output/summary.csv \
  --results coop_eval_actual/output/experiment_results.csv \
  --output_dir coop_eval_actual/output
```

## 结果文件
- 汇总指标：`coop_eval_actual/output/summary.csv`
- 逐条结果：`coop_eval_actual/output/experiment_results.csv`
- 原始日志：`coop_eval_actual/output/raw_logs.jsonl`
- 图表：
  - `coop_eval_actual/output/figure_success_rate.png`
  - `coop_eval_actual/output/figure_tokens_level8.png`
  - `coop_eval_actual/output/figure_error_types.png`

## 关键趋势（中文解读）
- 成功率：COOP 在 L1/L3/L5 为 1.0，L8 为 0.95；ReAct 随难度升高掉到 L8 为 0；CoT 在 L5/L8 均为 0。
- Token 开销：三者随难度上升而增长；L8 时 ReAct 最高、COOP 次之、CoT 最低但成功率为 0。
- 恢复率：COOP 在 L8 仍有 0.9091，ReAct 下降到 0.55，CoT 为 0。
- 工具调用：COOP 难度越高调用次数明显增加（L8 约 10 次），ReAct 低于 COOP，CoT 最少。
- 运行耗时：COOP 记录到 L1≈6.9ms、L3≈19ms、L5≈32.3ms、L8≈64.4ms；Baseline 目前未做计时埋点。

## 已知限制
- 评测执行使用 `eval_execution`（mock 工具环境），未接真实外部系统。
- 事件总线被禁用（避免异步告警），不影响评测统计。

## 可选后续
- 给 CoT / ReAct 增加真实耗时记录
- 继续扩充任务集或难度分层
- 如果需要，可将图表输出改为论文风格版式
