# 有状态Mock服务优化说明

## 核心改进

### 1. Schema 校验 (解决数据校验缺失)

**新增 `_validate_schema` 方法**：
- 在处理请求前校验参数类型和必填字段
- 返回标准 422 错误，模拟真实 API 行为
- 防止 Agent 误判非法输入为合法

**示例**：
```python
"request_schema": {
    "required": ["name", "email"],
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}
```

### 2. 混沌工程增强 (解决不可控和不可复现)

**新增 `ChaosEngine` 类**：
- 支持基于计数的注入（`trigger_count`）：第 N 次调用必定失败
- 支持概率注入（`probability`）：随机失败率
- 支持随机种子（`seed`）：确保测试可复现
- 支持多种故障类型：500/400/401/503

**示例**：
```python
ChaosRule(
    api_pattern="/orders/*",
    method="DELETE",
    trigger_count=1,  # 第一次调用失败
    action="fail_500"
)
```

### 3. 外键约束 (解决实体关系问题)

**新增 `set_foreign_key` 方法**：
- 在创建资源时检查父资源是否存在
- 模拟真实数据库的外键约束
- 返回 400 错误防止无效关联

**示例**：
```python
state_manager.set_foreign_key("order", "user", "id")
# 创建订单时会检查 user_id 是否存在
```

### 4. 状态约束 (解决业务规则缺失)

**新增 `set_status_constraint` 方法**：
- 定义基于状态的操作限制
- 模拟真实业务逻辑（如已支付订单不可删除）
- 返回 400 错误并说明原因

**示例**：
```python
state_manager.set_status_constraint("order", "delete", ["PENDING", "CANCELLED"])
# 只有 PENDING 或 CANCELLED 状态的订单可删除
```

### 5. 会话隔离 (解决并发测试污染)

**新增 `session` 上下文管理器**：
- 每个测试会话拥有独立的数据空间
- 通过 `X-Session-ID` Header 或上下文管理器隔离
- 支持并行测试不互相干扰

**示例**：
```python
with service.session("test_001"):
    # 独立的数据空间
    pass
```

### 6. 请求日志 (解决调试困难)

**新增 `request_log` 列表**：
- 记录所有 API 调用
- 用于复盘和分析 Agent 行为
- 可导出为测试报告

### 7. 列表查询支持

**新增 `list_resources` 方法**：
- GET 请求不带 ID 时返回资源列表
- 支持 Agent 查询所有资源
- 返回标准格式 `{"items": [...], "total": N}`

## 使用方式

```python
from stateful_mock import MockService, ChaosRule

# 初始化（使用内存数据库和随机种子）
service = MockService(db_path=":memory:", chaos_seed=42)

# 配置约束
service.configure_constraints(
    foreign_keys={"order": {"parent_type": "user"}},
    status_constraints={"order": {"delete": ["PENDING"]}}
)

# 添加混沌规则
service.add_chaos_rule("test_retry", ChaosRule(
    api_pattern="/orders/*",
    trigger_count=1,
    action="fail_500"
))

# 启动服务
service.start_server(capabilities, port=8000)
```

## 待集成功能

所有功能已实现：

1. ✅ **高级 Schema 校验**：集成 jsonschema 库（可选），支持复杂验证规则
2. ✅ **陈旧数据模拟**：GET 请求首次返回缓存的旧数据，模拟主从延迟
3. ✅ **级联删除**：删除父资源时自动删除关联的子资源
4. ✅ **请求日志导出**：`export_logs()` 方法导出所有请求记录
5. ✅ **数据种子**：`seed_data()` 方法从测试场景初始化数据

## 新增功能详解

### 陈旧数据模拟
```python
# GET 第一次返回旧数据，第二次返回新数据
# 模拟主从数据库延迟场景
```

### 级联删除
```python
service.configure_constraints(
    foreign_keys={"order": {"parent_type": "user"}}
)
# 删除 user 时自动删除其所有 orders
```

### 数据种子
```python
service.seed_data({
    "user": [{"id": "u1", "name": "Alice"}],
    "order": [{"id": "o1", "user_id": "u1", "amount": 100}]
})
```

