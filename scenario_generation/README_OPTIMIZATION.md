# 场景生成模块优化说明

## 核心改进

### 1. 解决"参数幻觉"问题

**新增 `ParameterConstraint` 模型**，区分三种参数类型：
- `static`: 静态数据（LLM生成的合理值）
- `dynamic_ref`: 动态引用（使用 `{step.response.field}` 格式）
- `fake_data`: 假数据占位符（如 `{{fake_email}}`）

**示例**：
```python
"parameter_bindings": {
    "cancel_order": {
        "order_id": {"type": "dynamic_ref", "value": "{list_orders.response.orders[0].id}"},
        "reason": {"type": "static", "value": "用户主动取消"},
        "token": {"type": "dynamic_ref", "value": "{login.response.token}"}
    }
}
```

### 2. 异常场景逻辑增强

**新增 `InjectionPoint` 模型**，明确错误注入点：
- 指定注入步骤索引
- 定义注入类型（missing_link, state_conflict, permission_gap, invalid_data）
- 描述预期错误

**Validator 增强**：
- 检查异常场景是否有 `injection_point`
- 验证 `expected_outcome` 不应包含"成功"字样

### 3. 上下文窗口优化

**按需注入策略**：
- 只提取关键字段（top 3）而非完整 Schema
- 使用 `parameter_flow` 替代完整参数定义
- 分离 API 摘要和详细信息

### 4. 场景类型扩展

支持 6 种场景类型：
- `normal`: 正常流程
- `exception`: 异常注入
- `boundary`: 边界测试
- `info_missing`: 信息缺失（测试 Agent 追问能力）
- `logic_nested`: 逻辑嵌套
- `conflict_prevention`: 冲突预防

### 5. 验证器硬指标

新增验证规则：
- **路径覆盖检查**：验证写操作是否在描述中体现
- **前置条件检查**：如路径以 login 开始，描述应提及认证
- **参数引用格式检查**：动态引用必须使用 `{}` 格式
- **异常场景合理性**：必须有明确的错误注入点和预期错误

## 使用方式

```python
from scenario_generation import ScenarioGenerationService

service = ScenarioGenerationService()

scenarios = service.generate_scenarios(
    api_path=["login", "list_orders", "cancel_order"],
    api_details={...},  # API 详情
    parameter_flow={...},  # 参数依赖关系（来自 topology 模块）
    scenario_types=['normal', 'exception'],
    count_per_type=1
)
```

## 待集成功能

1. **真实 LLM 调用**：当前使用模板生成，需替换为实际 LLM API
2. **闭环校验**：将生成的问题反馈给 Agent 验证路径一致性
3. **Faker 集成**：自动生成真实的假数据
4. **Neo4j 拓扑查询**：检测是否存在更短路径
