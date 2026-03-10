# 实体级逻辑骨架 - 改进方案

## 问题分析

### 当前实现的问题
我之前的实现把 Entity 当作了"实体类型"的标签，但实际上：
- **Entity 应该是独立的节点**：代表一个业务实体（如 Order, Customer, Product）
- **API 是 Entity 的实现**：多个 API 属于同一个 Entity
- **需要两层关系**：
  1. Entity 之间的关系（高层逻辑）
  2. API 之间的关系（底层实现）

### 正确的架构

```
Entity Layer (实体层):
  (Order:Entity) -[REQUIRES_DATA]-> (Customer:Entity)
  (Order:Entity) -[REQUIRES_DATA]-> (Product:Entity)
  (Payment:Entity) -[REQUIRES_DATA]-> (Order:Entity)

API Layer (接口层):
  (createOrder:API) -[BELONGS_TO]-> (Order:Entity)
  (getOrder:API) -[BELONGS_TO]-> (Order:Entity)
  (updateOrder:API) -[BELONGS_TO]-> (Order:Entity)

  (createOrder:API) -[DEPENDS_ON]-> (getCustomer:API)
  (createOrder:API) -[DEPENDS_ON]-> (getProduct:API)
```

## 改进方案

### 1. 数据模型

#### 节点类型

```cypher
// Entity 节点（业务实体）
(:Entity {
  name: "order",                    // 实体名称
  api_count: 5,                     // 包含的 API 数量
  operations: ["create", "get", "update", "delete"],  // 支持的操作
  producer_count: 2,                // Producer API 数量
  consumer_count: 1                 // Consumer API 数量
})

// API 节点（具体接口）
(:API {
  operation_id: "createOrder",
  entity: "order",                  // 所属实体
  role: "CONSUMER",                 // API 角色
  method: "POST",
  path: "/order/create",
  // ... 其他字段
})

// Capability 节点（能力）
(:Capability {
  name: "订单管理",
  entity: "order",                  // 关联实体
  // ... 契约信息
})
```

#### 关系类型

```cypher
// Entity 层关系
(Order:Entity)-[:REQUIRES_DATA {
  edge_count: 3,                    // 底层有 3 个 API 依赖
  avg_confidence: 0.85,
  data_fields: ["customer_id"],
  relationship_type: "SCHEMA_REFERENCE",
  producer_apis: ["getCustomer", "getCustomerDetail"],
  consumer_apis: ["createOrder", "updateOrder"]
}]->(Customer:Entity)

// API 归属关系
(createOrder:API)-[:BELONGS_TO]->(Order:Entity)

// API 依赖关系
(createOrder:API)-[:DEPENDS_ON {
  score: 0.8,
  type: "SCHEMA_REFERENCE",
  reason: "References customer via field 'customer_id'",
  contributes_to_entity_edge: "Order->Customer"  // 贡献给哪个实体边
}]->(getCustomer:API)
```

### 2. 构建流程

```
Step 1: 创建 Entity 节点
  - 从 api_map 中提取所有唯一的 entity
  - 统计每个 entity 的 API 数量、操作类型等

Step 2: 创建 API 节点（已有）
  - 保持现有逻辑

Step 3: 创建 API -> Entity 归属关系
  - 每个 API 通过 BELONGS_TO 连接到其 Entity

Step 4: 推断 API 依赖（已有）
  - 保持现有的 4 层推断逻辑

Step 5: 聚合 Entity 依赖
  - 分析 API 依赖，聚合到 Entity 层
  - 如果 Order 的多个 API 依赖 Customer 的 API
    → 创建 Order -> Customer 的 Entity 边

Step 6: 标注 API 角色
  - 基于跨实体依赖标注 Producer/Consumer

Step 7: 构建 Capability 契约
  - 关联到 Entity
```

### 3. 查询示例

#### 查看实体关系图
```cypher
// 只看实体层
MATCH (e:Entity)-[r:REQUIRES_DATA]->(f:Entity)
RETURN e, r, f
```

#### 查看某个实体的所有 API
```cypher
MATCH (a:API)-[:BELONGS_TO]->(e:Entity {name: "order"})
RETURN a.operation_id, a.role, a.method, a.path
```

#### 查看实体依赖的底层 API 依赖
```cypher
MATCH (e1:Entity {name: "order"})-[er:REQUIRES_DATA]->(e2:Entity {name: "customer"})
MATCH (a1:API)-[:BELONGS_TO]->(e1)
MATCH (a2:API)-[:BELONGS_TO]->(e2)
MATCH (a1)-[ar:DEPENDS_ON]->(a2)
RETURN a1.operation_id, a2.operation_id, ar.score, ar.type
```

#### Agent 查询流程
```cypher
// Step 1: 找到目标实体
MATCH (e:Entity {name: "order"})
RETURN e

// Step 2: 查看实体依赖
MATCH (e:Entity {name: "order"})-[r:REQUIRES_DATA]->(f:Entity)
RETURN f.name, r.data_fields, r.producer_apis

// Step 3: 下钻到具体 API
MATCH (a:API)-[:BELONGS_TO]->(f:Entity {name: "customer"})
WHERE a.role = "PRODUCER"
RETURN a.operation_id, a.path, a.output_fields_list

// Step 4: 找到消费者 API
MATCH (a:API)-[:BELONGS_TO]->(e:Entity {name: "order"})
WHERE a.role = "CONSUMER"
RETURN a.operation_id, a.path, a.input_fields_list
```

### 4. 可视化效果

```
Neo4j Browser 中的显示：

实体层视图（简洁）：
  [Order] --REQUIRES_DATA--> [Customer]
  [Order] --REQUIRES_DATA--> [Product]
  [Payment] --REQUIRES_DATA--> [Order]

API 层视图（详细）：
  [Order]
    ├─ createOrder (CONSUMER)
    ├─ getOrder (PRODUCER)
    ├─ updateOrder (BRIDGE)
    └─ deleteOrder (INTERNAL)

  [Customer]
    ├─ getCustomer (PRODUCER)
    └─ listCustomers (PRODUCER)

混合视图（完整）：
  [Order]
    └─ createOrder --DEPENDS_ON--> getCustomer
                                      └─ [Customer]
```

### 5. 代码改动

#### 5.1 GraphBuilder.build() 方法

```python
def build(self, capabilities, dependencies=None):
    with self.driver.session() as session:
        # 清空图
        session.run("MATCH (n) DETACH DELETE n")

        # Step 1: 创建 Entity 节点
        entity_stats = self._create_entity_nodes(session, api_map)

        # Step 2: 创建 API 节点（已有）
        api_count = self._create_api_nodes(session, capabilities)

        # Step 3: 创建 API -> Entity 归属关系
        self._create_belongs_to_relationships(session, api_map)

        # Step 4: 推断 API 依赖（已有）
        inferred_field = self._infer_field_dependencies(session, api_map)
        inferred_entity = self._infer_entity_dependencies(session, api_map)

        # Step 5: 聚合 Entity 依赖
        entity_edges = self._aggregate_entity_relationships(session, api_map)

        # Step 6: 标注 API 角色
        self._annotate_api_roles(session, api_map)

        # Step 7: 构建 Capability 契约
        contracts = self._build_capability_contracts(session, api_map)

        return {
            'entities_created': entity_stats['count'],
            'apis_created': api_count,
            'entity_relationships': entity_edges,
            'api_dependencies': inferred_field + inferred_entity,
            'capability_contracts': contracts
        }
```

#### 5.2 新增方法

```python
def _create_entity_nodes(self, session, api_map):
    """创建 Entity 节点"""
    # 统计每个 entity 的信息
    entity_info = defaultdict(lambda: {
        'apis': [],
        'operations': set(),
        'producers': 0,
        'consumers': 0
    })

    for op_id, api in api_map.items():
        entity = api.get('entity')
        if entity:
            entity_info[entity]['apis'].append(op_id)
            # 统计操作类型等

    # 创建节点
    for entity, info in entity_info.items():
        session.run("""
            CREATE (e:Entity {
                name: $name,
                api_count: $api_count,
                operations: $operations
            })
        """, name=entity, ...)

def _create_belongs_to_relationships(self, session, api_map):
    """创建 API -> Entity 归属关系"""
    for op_id, api in api_map.items():
        entity = api.get('entity')
        if entity:
            session.run("""
                MATCH (a:API {operation_id: $op_id})
                MATCH (e:Entity {name: $entity})
                CREATE (a)-[:BELONGS_TO]->(e)
            """, op_id=op_id, entity=entity)

def _aggregate_entity_relationships(self, session, api_map):
    """聚合 API 依赖到 Entity 层"""
    # 查询所有 API 依赖
    result = session.run("""
        MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
        MATCH (a1)-[:BELONGS_TO]->(e1:Entity)
        MATCH (a2)-[:BELONGS_TO]->(e2:Entity)
        WHERE e1 <> e2
        RETURN e1.name as source, e2.name as target,
               count(*) as edge_count,
               avg(r.score) as avg_score,
               collect(r.type) as types,
               collect(a1.operation_id) as consumer_apis,
               collect(a2.operation_id) as producer_apis
    """)

    # 创建 Entity 边
    for record in result:
        if record['edge_count'] >= self.min_edge_count:
            session.run("""
                MATCH (e1:Entity {name: $source})
                MATCH (e2:Entity {name: $target})
                MERGE (e1)-[r:REQUIRES_DATA]->(e2)
                SET r.edge_count = $edge_count,
                    r.avg_confidence = $avg_score,
                    ...
            """, ...)
```

### 6. 优势

1. **清晰的层次**：Entity 层和 API 层分离
2. **易于可视化**：可以只看 Entity 层的高层逻辑
3. **灵活查询**：可以从 Entity 下钻到 API，也可以从 API 上溯到 Entity
4. **符合直觉**：Entity 代表业务概念，API 是具体实现
5. **便于 Agent**：先在 Entity 层规划，再在 API 层执行

### 7. 与现有代码的关系

- **保留**：所有 API 级推断逻辑（4 层推断）
- **保留**：API 节点的所有属性
- **新增**：Entity 节点
- **新增**：BELONGS_TO 关系
- **新增**：Entity 层的 REQUIRES_DATA 关系（聚合自 API 依赖）
- **修改**：API 角色标注逻辑（基于跨实体依赖）

## 实现步骤

1. 修改 `graph_builder.py` 的 `build()` 方法
2. 新增 `_create_entity_nodes()` 方法
3. 新增 `_create_belongs_to_relationships()` 方法
4. 修改 `_build_entity_skeleton()` 为 `_aggregate_entity_relationships()`
5. 更新 `entity_relationship_builder.py` 的聚合逻辑
6. 更新测试和示例

## 总结

这个方案实现了真正的**分层架构**：
- **Entity 层**：业务逻辑骨架（Order 依赖 Customer）
- **API 层**：具体实现（createOrder 依赖 getCustomer）
- **关联**：通过 BELONGS_TO 连接两层

这样 Agent 可以：
1. 在 Entity 层理解业务逻辑
2. 在 API 层找到具体实现
3. 通过 BELONGS_TO 在两层之间导航
