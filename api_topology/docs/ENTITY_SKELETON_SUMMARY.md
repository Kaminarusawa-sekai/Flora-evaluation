# 实体级逻辑骨架 - 实现总结

## 完成的功能

### 1. 核心实现

#### EntityRelationshipBuilder (`entity_relationship_builder.py`)
- **实体关系聚合**：从 API 级边聚合到实体级边
- **API 角色识别**：Producer / Consumer / Bridge / Internal
- **能力契约构建**：包含前置要求、推荐来源、入口点

#### GraphBuilder 集成 (`graph_builder.py`)
- 自动构建实体骨架
- 创建 Entity 节点和 REQUIRES_DATA 关系
- 标注 API 角色
- 存储 Capability 契约

### 2. 三层架构

```
L1: Entity Layer (实体层)
    ├─ Entity nodes
    └─ REQUIRES_DATA relationships
        ├─ edge_count: API 依赖数量
        ├─ avg_confidence: 平均置信度
        ├─ data_fields: 数据字段
        ├─ producer_apis: 生产者 API 列表
        └─ consumer_apis: 消费者 API 列表

L2: Capability Layer (能力层)
    ├─ Capability contracts
    ├─ required_inputs: 前置要求
    ├─ entry_points: 入口点
    ├─ producers: 生产者列表
    └─ recommended_sources: 推荐来源

L3: API Layer (接口层)
    ├─ API nodes with roles
    ├─ role: PRODUCER/CONSUMER/BRIDGE/INTERNAL
    ├─ incoming_cross_entity: 跨实体入边数
    ├─ outgoing_cross_entity: 跨实体出边数
    └─ DEPENDS_ON relationships
```

## 文件清单

### 核心实现
- `api_topology/entity_relationship_builder.py` - 实体关系构建器
- `api_topology/graph_builder.py` - 集成实体骨架构建
- `api_topology/dynamic_entity_inferrer.py` - 实体推断（已更新）

### 测试文件
- `test_entity_skeleton.py` - 实体骨架测试
- `test_entity_propagation.py` - 实体传递测试
- `api_topology/example_agent_query.py` - Agent 查询示例

### 文档
- `api_topology/ENTITY_SKELETON.md` - 详细设计文档
- `ENTITY_INFERENCE_STRATEGY.md` - 推断策略对比

## 使用示例

### 基本用法

```python
from api_normalization import NormalizationService
from api_topology import TopologyService

# 1. 规范化
norm_service = NormalizationService(use_entity_clustering=True)
result = norm_service.normalize_swagger('api.json')

# 2. 构建拓扑（自动构建实体骨架）
service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    use_entity_inference=True
)

build_result = service.build_graph(result['capabilities'])

# 3. 查看结果
print(f"Entity relationships: {build_result['entity_relationships']}")
print(f"Capability contracts: {build_result['capability_contracts']}")
```

### Agent 查询流程

```python
# Step 1: 查找能力
MATCH (c:Capability)
WHERE c.name CONTAINS 'order'
RETURN c.required_inputs, c.recommended_sources

# Step 2: 查找数据来源（实体级）
MATCH (e:Entity {name: 'order'})-[r:REQUIRES_DATA]->(f:Entity)
RETURN f.name, r.data_fields, r.producer_apis

# Step 3: 查找具体 API
MATCH (a:API {entity: 'customer'})
WHERE a.role = 'PRODUCER'
RETURN a.operation_id, a.output_fields_list

# Step 4: 执行
1. 调用 Producer API 获取数据
2. 调用 Consumer API 完成任务
```

## 关键特性

### 1. API 角色化

每个 API 被自动标记为：
- **Producer**: 提供数据给其他实体（如 `getCustomer`）
- **Consumer**: 消费其他实体数据（如 `createOrder`）
- **Bridge**: 既产出又消费（如 `updateOrder`）
- **Internal**: 仅内部使用（如 `validateOrder`）

### 2. 实体关系聚合

自动聚合 API 级依赖到实体级：
- 统计边数量（edge_count）
- 计算平均置信度（avg_confidence）
- 提取数据字段（data_fields）
- 记录相关 API（producer_apis, consumer_apis）

### 3. 能力契约

每个能力都有完整的"说明书"：
- 需要什么数据（required_inputs）
- 从哪里获取（recommended_sources）
- 如何调用（entry_points）
- 谁能提供（producers）

## 优势对比

### 传统方式
```
Agent: "取消订单"
  ↓
查找 cancelOrder API
  ↓
发现需要 order_id
  ↓
❌ 不知道从哪里获取
```

### 实体骨架方式
```
Agent: "取消订单"
  ↓
L2: 查询 Capability "订单取消"
  ├─ 需要: order_id
  └─ 推荐: Order.listOrders
  ↓
L1: 查询 Entity 关系
  Order -> Order (producer_apis: [listOrders])
  ↓
L3: 执行
  1. listOrders → order_id
  2. cancelOrder(order_id)
  ↓
✓ 成功
```

## 配置选项

```python
from api_topology.entity_relationship_builder import EntityRelationshipBuilder

# 自定义聚合阈值
builder = EntityRelationshipBuilder(
    min_edge_count=2,      # 最少 API 边数
    min_confidence=0.7     # 最低平均置信度
)
```

## 测试

```bash
# 测试实体骨架构建
python test_entity_skeleton.py

# 测试实体传递
python test_entity_propagation.py

# 测试 Agent 查询
python api_topology/example_agent_query.py
```

## Neo4j 查询示例

### 查看实体关系
```cypher
MATCH (e:Entity)-[r:REQUIRES_DATA]->(f:Entity)
RETURN e.name, f.name, r.edge_count, r.data_fields
ORDER BY r.edge_count DESC
```

### 查看 API 角色分布
```cypher
MATCH (a:API)
RETURN a.role, count(*) as count
```

### 查看能力契约
```cypher
MATCH (c:Capability)
RETURN c.name, c.required_inputs, c.recommended_sources
```

### 完整依赖路径
```cypher
MATCH (c:Capability)-[:BELONGS_TO]->(e:Entity)
MATCH (e)-[r:REQUIRES_DATA]->(f:Entity)
MATCH (a:API {entity: f.name, role: 'PRODUCER'})
RETURN c.name, e.name, f.name, r.data_fields, collect(a.operation_id)
```

## 架构优势

1. **分层推理**：从高层（实体）到低层（API）逐步细化
2. **精确制导**：明确数据来源和获取方式
3. **可复用**：实体关系可复用到所有相关 API
4. **可解释**：每个依赖都有明确原因
5. **易扩展**：可添加更多元数据

## 与 LLM 的关系

实体骨架与 LLM 推断是互补的：

- **LLM 推断**：在 API 级别提供智能依赖识别
- **实体骨架**：将 API 级依赖聚合到实体级
- **协同工作**：LLM 提供高质量的 API 依赖 → 实体骨架聚合成逻辑骨架

## 未来改进

- [ ] 实体优先级（核心 vs 辅助）
- [ ] 多跳依赖推理（A → B → C）
- [ ] 数据流分析（字段转换）
- [ ] 条件依赖（某些情况下才需要）
- [ ] 可视化实体关系图
- [ ] 性能优化（缓存、批量查询）

## 总结

实体级逻辑骨架实现了从"模糊寻址"到"精确制导"的转变，为 Agent 提供了清晰的执行路径。通过三层架构（Entity/Capability/API），Agent 可以：

1. 在 Capability 层找到任务入口
2. 在 Entity 层找到数据来源
3. 在 API 层执行具体调用

这种分层设计大大提高了 Agent 的自主性和执行成功率。
