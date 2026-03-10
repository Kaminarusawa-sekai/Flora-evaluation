# COOP vs. SOTA Baselines 实验评估方案（中文）

本文档基于 `Experimental Design COOP vs. SOTA Baselines.md`，给出可落地的完整实现方案与评估指标/列名设计，便于直接产出可复现实验数据。

---

## 1. 实验目标

通过控制变量法证明：在任务复杂度提升时，COOP 在成功率与 Token 效率上显著优于 CoT 与 ReAct。

---

## 2. 实验环境与模拟环境

- **统一模型**：`gpt-4o` 或 `gpt-3.5-turbo`（保持一致）
- **Mock 环境**：模拟营销数据库与工具调用，不依赖真实外部接口

示例结构：

```
class MarketingEnvironment:
    def __init__(self):
        self.db = {
            "users": [{"id": "u1", "tags": ["active"], "history": "..."}],
            "rules": {"active": "send_coupon_A"}
        }
        self.logs = []
        self.error_injection_rate = 0.2

    def execute_tool(self, tool_name, args):
        # 记录调用
        self.logs.append((tool_name, args))
        # 校验工具/参数合法性
        # 触发 20% 500 错误
        # 返回 Success/Failure
```

---

## 3. 对比组设置

1. **Group A: Vanilla CoT**
   - 单一 System Prompt + 全量工具描述
2. **Group B: Standard ReAct**
   - Thought -> Action -> Observation 循环
3. **Group C: COOP (Ours)**
   - Root/Leaf 分层，叶子代理执行具体工具

---

## 4. 数据集设计（复杂度等级）

- **Level 1**：原子任务（1 步）
- **Level 3**：线性任务（3 步）
- **Level 5**：带分支循环任务
- **Level 8**：复合高复杂任务

**任务数量**：
- 20 个 Level 1
- 30 个 Level 3
- 30 个 Level 5
- 20 个 Level 8

---

## 5. 评估指标（Metrics）

### 5.1 Success Rate（成功率）
- 定义：任务是否达成预期最终状态
- 判定：`expected_action` + `expected_args` 匹配

### 5.2 Token Consumption（Token 消耗）
- 定义：Prompt + Completion 总消耗
- 计算：`tokens_total = tokens_prompt + tokens_completion`

### 5.3 Hallucination Rate（幻觉率）
- 定义：调用不存在工具或参数错误
- 计算：`hallucination_errors / tool_calls_total`

### 5.4 Recovery Rate（自愈率）
- 定义：API 500 失败后重试成功/降级完成
- 计算：`recovered_errors / injected_errors`

### 5.5 Runtime Cost（运行耗时）
- 定义：完成一次任务的真实耗时（端到端）
- 计算：`duration_ms`，按模型/复杂度取均值

### 5.6 ReAct Workflow Complexity（ReAct 工作流复杂度）
- 定义：基于 ReAct 工作流配置的实现复杂度
- 参考项（可加权求和）：`workflow_nodes`（节点数）、`workflow_branches`（分支数）、`tool_rules`（工具规则数）、`config_loc`（配置行数）
- 用途：衡量“同等能力下”的实现成本，越高表示维护成本越高

### 5.7 Code Compatibility（同代码兼容任务量）
- 定义：在**不修改代码**的前提下可直接执行的任务占比
- 计算：`compatible_tasks / total_tasks`，可按模型/复杂度统计

---

## 6. 数据列名设计（中文）

### 6.1 dataset.json（任务数据）
| 列名 | 含义 |
| --- | --- |
| task_id | 任务编号 |
| level | 复杂度等级 |
| prompt | 任务描述 |
| expected_action | 期望动作 |
| expected_args | 期望参数 |
| notes | 备注 |

### 6.2 raw_logs.jsonl（过程日志）
| 列名 | 含义 |
| --- | --- |
| task_id | 任务编号 |
| model | 模型名称 |
| step_id | 步骤序号 |
| action | 执行动作 |
| args | 动作参数 |
| tool_result | 工具返回 |
| error_type | 错误类型 |
| timestamp_ms | 时间戳 |

### 6.3 experiment_results.csv（逐任务结果）
| 列名 | 含义 |
| --- | --- |
| task_id | 任务编号 |
| level | 复杂度等级 |
| model | 模型名称 |
| success | 成功标记 |
| tokens_prompt | Prompt Token |
| tokens_completion | Completion Token |
| tokens_total | 总 Token |
| tool_calls_total | 工具调用总数 |
| hallucination_errors | 幻觉错误数 |
| injected_errors | 注入错误数 |
| recovered_errors | 成功恢复数 |
| retries | 重试次数 |
| error_type | 失败类型 |
| duration_ms | 耗时 |
| compatible | 是否无需代码修改即可执行 |
| expected_action | 期望动作 |
| actual_action | 实际动作 |
| expected_args | 期望参数 |
| actual_args | 实际参数 |

### 6.4 summary.csv（聚合指标）
| 列名 | 含义 |
| --- | --- |
| model | 模型名称 |
| level | 复杂度等级 |
| n_tasks | 样本数量 |
| success_rate | 成功率 |
| avg_tokens_total | 平均 Token |
| hallucination_rate | 幻觉率 |
| recovery_rate | 自愈率 |
| avg_duration_ms | 平均耗时 |
| avg_tool_calls | 平均调用数 |
| compatibility_rate | 同代码兼容率 |
| workflow_complexity_score | 工作流复杂度评分（可仅针对 ReAct） |
| workflow_nodes | 工作流节点数 |
| workflow_branches | 工作流分支数 |
| tool_rules | 工具规则数 |
| config_loc | 配置行数 |

---

## 7. 执行与输出流程

1. 生成 `dataset.json`
2. Runner 脚本循环执行三组模型
3. 记录日志并输出 `experiment_results.csv`
4. 汇总生成 `summary.csv`

---

## 8. 可视化图表（论文用）

1. **折线图**：复杂度 vs 成功率
2. **柱状图**：Level 8 Token 消耗
3. **堆叠图**：错误类型分布

---

如果需要，我可以继续提供：
- 任务生成器脚本
- Mock 环境最小实现
- Runner 与评估统计代码
