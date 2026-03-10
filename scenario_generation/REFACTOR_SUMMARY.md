# Scenario Generation 重构总结

## 修复的问题

### 1. 导入错误
- 修复了 `scenario_generation_service.py` 中的相对导入错误
- 修复了 `scenario_generator.py` 中的相对导入错误
- 将相对导入改为绝对导入，使模块可以独立运行

### 2. 方法定义缺失
- 修复了 `scenario_validator.py` 中缺失的 `_calculate_score` 方法定义
- 该方法被错误地合并到了 `_validate_path_coverage` 方法中

### 3. 编码问题
- 移除了示例代码中的特殊 Unicode 字符（✓）
- 避免 Windows 控制台编码错误

## 核心逻辑重构

### 原来的错误逻辑
```
用户提供测试目标 → 生成路径 → 生成场景
```
这是"先有题目再找答案"的方式，不符合实际需求。

### 正确的逻辑（对着答案编题目）
```
拓扑数据（实体 + 依赖关系）
    ↓
发现可能的 API 路径（答案）
    ↓
LLM 生成测试主题（题目）
    ↓
生成具体测试场景
```

## PathGenerator 重构

### 核心改变

1. **移除 `test_objectives` 参数**
   - 不再需要用户提供测试目标
   - 系统自动从拓扑中发现路径

2. **新增路径发现策略**
   - 在实体内生成路径（基于依赖关系）
   - 跨实体路径（基于强依赖）
   - 随机路径（补充覆盖率）

3. **新增主题生成功能**
   - 使用 LLM 分析路径功能
   - 为每条路径生成测试主题和描述
   - 启发式方法作为 fallback

### 新的 API

```python
# 旧 API（已废弃）
paths = path_generator.generate_paths(
    topology_data=topology_data,
    test_objectives=["测试订单流程"],  # 不再需要
    max_paths=5
)

# 新 API
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6,
    min_path_length=2
)

# 返回的路径包含自动生成的主题
# {
#   "path": ["login", "list_orders", "cancel_order"],
#   "test_objective": "测试用户取消订单流程",  # LLM 生成
#   "description": "验证用户登录后查询订单并成功取消",  # LLM 生成
#   "scenario_type": "normal",
#   "parameter_flow": {...}
# }
```

## 路径发现策略

### 1. 实体内路径
- 在每个实体内，基于依赖关系生成路径
- 找到入口点（没有被依赖的 API）
- 沿着依赖关系构建路径

### 2. 跨实体路径
- 识别跨实体的强依赖关系（score > 0.7）
- 构建跨实体的调用路径
- 例如：User.login → Order.listOrders → Order.cancelOrder

### 3. 随机路径
- 用于补充覆盖率
- 从随机入口点开始
- 跟随依赖关系扩展

## 主题生成

### LLM 模式
```python
# LLM 分析路径中的 API
路径: [login, list_orders, get_order_detail, cancel_order]

# LLM 生成主题
test_objective: "测试用户取消订单的完整流程"
description: "验证用户登录后查询订单列表，选择订单查看详情，最后成功取消订单"
scenario_type: "normal"
```

### 启发式模式（Fallback）
```python
# 基于 API 摘要生成简单主题
路径: [login, list_orders, cancel_order]

# 启发式生成
test_objective: "测试 用户登录 到 取消订单 的流程"
description: "验证 用户登录 -> 查询订单列表 -> 取消订单 的业务流程"
```

## 拓扑的作用

### 1. 提供实体信息
- 告诉系统有哪些业务实体（User, Order, Product 等）
- 每个实体包含哪些 API

### 2. 提供依赖关系
- API 之间的依赖关系和强度（score）
- 用于指导路径生成

### 3. 辅助路径发现
- 实体内的强关联 API 优先组合
- 跨实体的强依赖关系作为路径扩展依据

## 示例对比

### 旧方式（错误）
```python
# 用户需要提供测试目标
test_objectives = [
    "测试订单取消流程",
    "测试用户认证流程"
]

# 系统根据目标生成路径（困难）
paths = generator.generate_paths(
    topology_data=topology_data,
    test_objectives=test_objectives
)
```

### 新方式（正确）
```python
# 系统自动从拓扑中发现路径
paths = generator.generate_paths(
    topology_data=topology_data,
    max_paths=10
)

# 每条路径都有自动生成的主题
for path in paths:
    print(f"Path: {' -> '.join(path['path'])}")
    print(f"Theme: {path['test_objective']}")  # LLM 生成
```

## 工作流程

```
1. API Normalization
   ↓
   规范化的 API 列表

2. API Topology
   ↓
   实体 + 依赖关系图

3. Path Discovery
   ↓
   候选路径列表
   [
     ["login", "list_orders", "cancel_order"],
     ["login", "get_order_detail"],
     ...
   ]

4. Theme Generation (LLM)
   ↓
   路径 + 测试主题
   [
     {
       "path": ["login", "list_orders", "cancel_order"],
       "test_objective": "测试用户取消订单流程",
       "description": "验证用户登录后查询订单并成功取消"
     },
     ...
   ]

5. Scenario Generation
   ↓
   具体测试场景（正常/异常）
```

## 优势

1. **更自然的流程** - 先发现路径，再生成主题
2. **更高的覆盖率** - 系统自动发现所有可能的路径
3. **更准确的主题** - LLM 根据实际路径生成主题
4. **更少的人工输入** - 不需要用户提供测试目标
5. **更好的可扩展性** - 易于添加新的路径发现策略

## 文件变更

### 修改的文件
- `scenario_generation/path_generator.py` - 完全重写
- `scenario_generation/scenario_generation_service.py` - 修复导入
- `scenario_generation/scenario_generator.py` - 修复导入
- `scenario_generation/scenario_validator.py` - 修复方法定义
- `scenario_generation/example_with_topology.py` - 更新示例
- `scenario_generation/README.md` - 更新文档
- `WORKFLOW.md` - 更新工作流程说明

### 新增的文件
- 无（重构现有文件）

## 测试结果

运行 `example_with_topology.py` 成功生成：
- 5 条路径（从拓扑中发现）
- 每条路径都有自动生成的测试主题
- 10 个测试场景（每条路径 2 个：正常 + 异常）
- 所有场景验证通过（score: 1.0）

## 下一步

1. 优化路径发现算法（更智能的路径选择）
2. 改进 LLM prompt（生成更准确的主题）
3. 添加路径质量评分（优先选择高质量路径）
4. 支持更多路径发现策略（基于业务规则等）
