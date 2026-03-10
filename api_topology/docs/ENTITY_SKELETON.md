# 实体级逻辑骨架 - 分层依赖架构

## 概述

在 API 级依赖之上构建实体级"逻辑骨架"。

## 架构设计

### 三层架构

```
L1: Entity Layer (实体层)
    ├─ Entity nodes: User, Order, Product, etc.
    └─ REQUIRES_DATA relationships

L2: Capability Layer (能力层)
    ├─ Capability contracts (能力契约)
    ├─ Required inputs (前置要求)
    └─ Recommended sources (推荐来源)

L3: API Layer (接口层)
    ├─ API nodes with roles (Producer/Consumer/Internal)
    ├─ DEPENDS_ON relationships
    └─ Field-level dependencies
```

## 核心概念

### 1. API 角色化 (API Roles)

每个 API 被标记为以下角色之一：

#### Producer (产出者)
- **定义**：对外提供核心数据的接口
- **特征**：有来自其他实体的依赖（incoming cross-entity edges）
- **示例**：`getOrderDetail` - 提供 `order_id` 给其他实体使用

#### Consumer (消费者)
- **定义**：需要其他实体数据的接口
- **特征**：依赖其他实体的接口（outgoing cross-entity edges）
- **示例**：`createPayment` - 需要 `order_id` 来创建支付

#### Bridge (桥接)
- **定义**：既产出又消费数据的接口
- **特征**：同时有 incoming 和 outgoing cross-entity edges
- **示例**：`updateOrderStatus` - 需要 `user_id`，产出 `order_id`

#### Internal (内部)
- **定义**：只在实体内部使用的接口
- **特征**：没有跨实体依赖
- **示例**：`validateOrderData` - 内部验证逻辑

### 2. 实体关系聚合

从 API 级边聚合到实体级边：

```
API Level:
  createOrder -> getCustomer
  createOrder -> getProduct
  updateOrder -> getCustomer

Entity Level:
  Order -[REQUIRES_DATA]-> Customer
    ├─ edge_count: 2
    ├─ avg_confidence: 0.85
    ├─ data_fields: [customer_id, user_id]
    ├─ producer_apis: [getCustomer, getCustomerDetail]
    └─ consumer_apis: [createOrder, updateOrder]
```

**聚合规则：**
- 最少边数：`min_edge_count = 2`（至少 2 个 API 依赖）
- 最低置信度：`min_confidence = 0.7`（平均置信度 >= 0.7）

### 3. 能力契约 (Capability Contract)

每个能力（Capability）都有一个"说明书"：

```json
{
  "capability": "订单取消",
  "entity": "order",
  "required_inputs": ["order_id", "reason"],
  "entry_points": [
    {
      "operation_id": "cancelOrder",
      "path": "/order/cancel",
      "method": "POST",
      "input_fields": ["order_id", "reason"]
    }
  ],
  "producers": [
    {
      "operation_id": "getOrderDetail",
      "output_fields": ["order_id", "status", "amount"]
    }
  ],
  "recommended_sources": [
    {
      "source_entity": "order",
      "data_fields": ["order_id"],
      "producer_apis": ["listOrders", "getOrderDetail"],
      "confidence": 0.9
    }
  ]
}
```

## Agent 执行流程



### 后续使用的查询流程

```
Agent: "我要取消订单"
  ↓
L2: 查询 Capability "订单取消"
  ├─ 需要: order_id, reason
  ├─ 入口: cancelOrder
  └─ 推荐来源: Order 实体的 listOrders
  ↓
L1: 查询 Entity 关系
  Order -[REQUIRES_DATA]-> Order (自身)
  ├─ producer_apis: [listOrders, getOrderDetail]
  └─ data_fields: [order_id]
  ↓
L3: 执行 API 调用
  1. 调用 listOrders 获取 order_id
  2. 调用 cancelOrder(order_id, reason)
  ↓
✓ 成功
```

## Neo4j 数据模型

### 节点类型

```cypher
// Entity nodes (L1)
(:Entity {
  name: "order"
})

// Capability nodes (L2)
(:Capability {
  name: "订单取消",
  entity: "order",
  required_inputs: ["order_id", "reason"],
  entry_points: "...",
  producers: "...",
  recommended_sources: "..."
})

// API nodes (L3)
(:API {
  operation_id: "cancelOrder",
  role: "CONSUMER",
  entity: "order",
  incoming_cross_entity: 0,
  outgoing_cross_entity: 1,
  input_fields_list: ["order_id", "reason"],
  output_fields_list: []
})
```

### 关系类型

```cypher
// Entity-level (L1)
(e:Entity)-[:REQUIRES_DATA {
  edge_count: 2,
  avg_confidence: 0.85,
  edge_types: "{'SCHEMA_REFERENCE': 2}",
  data_fields: ["customer_id"],
  producer_apis: ["getCustomer"],
  consumer_apis: ["createOrder", "updateOrder"]
}]->(f:Entity)

// API-level (L3)
(a:API)-[:DEPENDS_ON {
  score: 0.8,
  type: "SCHEMA_REFERENCE",
  reason: "References customer via field 'customer_id'"
}]->(b:API)
```

## 查询示例

### 1. 查找能力的前置要求

```cypher
MATCH (c:Capability {name: "订单取消"})
RETURN c.required_inputs as inputs,
       c.recommended_sources as sources
```

### 2. 查找数据来源

```cypher
MATCH (e:Entity {name: "order"})-[r:REQUIRES_DATA]->(f:Entity)
RETURN f.name as source_entity,
       r.data_fields as fields,
       r.producer_apis as apis
```

### 3. 查找 Producer APIs

```cypher
MATCH (a:API {entity: "customer"})
WHERE a.role = "PRODUCER"
RETURN a.operation_id, a.output_fields_list
```

### 4. 完整的依赖路径

```cypher
// 找到能力 -> 实体 -> API 的完整路径
MATCH (c:Capability {name: "订单取消"})
MATCH (e:Entity {name: c.entity})-[r:REQUIRES_DATA]->(f:Entity)
MATCH (a:API {entity: f.name})
WHERE a.role = "PRODUCER"
RETURN c.name as capability,
       c.required_inputs as needs,
       f.name as source_entity,
       r.data_fields as fields,
       collect(a.operation_id) as producer_apis
```

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

print(f"Entity relationships: {build_result['entity_relationships']}")
print(f"Capability contracts: {build_result['capability_contracts']}")
```

### Agent 查询示例

```python
# Agent 想要执行某个任务
task = "取消订单"

# Step 1: 查找相关能力
with driver.session() as session:
    result = session.run("""
        MATCH (c:Capability)
        WHERE c.name CONTAINS $task
        RETURN c.name, c.required_inputs, c.recommended_sources
    """, task=task)

    for record in result:
        print(f"Capability: {record['c.name']}")
        print(f"Needs: {record['c.required_inputs']}")
        print(f"Sources: {record['c.recommended_sources']}")

# Step 2: 获取数据来源
# Step 3: 执行 API 调用
```

## 配置选项

```python
from api_topology.entity_relationship_builder import EntityRelationshipBuilder

# 自定义聚合阈值
builder = EntityRelationshipBuilder(
    min_edge_count=3,      # 至少 3 个 API 依赖才创建实体边
    min_confidence=0.8     # 平均置信度 >= 0.8
)
```

## 优势

1. **分层推理**：Agent 可以从高层（实体）到低层（API）逐步细化
2. **精确制导**：明确告诉 Agent 需要什么数据、从哪里获取
3. **可复用**：实体关系可以复用到所有相关 API
4. **可解释**：每个依赖都有明确的原因和数据字段
5. **易扩展**：可以添加更多元数据（如优先级、成本等）

## 测试

```bash
# 测试实体骨架构建
python test_entity_skeleton.py

# 测试实体传递
python test_entity_propagation.py
```

## 未来改进

- [ ] 添加实体优先级（核心实体 vs 辅助实体）
- [ ] 支持多跳依赖推理（A -> B -> C）
- [ ] 添加数据流分析（哪些字段被转换）
- [ ] 支持条件依赖（某些情况下才需要）
- [ ] 可视化实体关系图
