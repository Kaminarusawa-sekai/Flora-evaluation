# 实体级逻辑骨架 - 正确方案（以 API 为实，实体为虚）

## 核心原则

**以 API 字段匹配为"实"，以实体关系为"虚"**

- **实（Physical）**：API 级依赖 - 基于字段匹配的具体连线
- **虚（Logical）**：Entity 级关系 - 从 API 依赖聚合而来的视图

## 三步构建流程

### 第一步：API 级依赖发现（事实层）

**保持现有逻辑不变**，通过 FieldMatcher 等方法找出具体的 API 连线：

```
createOrder (Consumer) --[order_id]--> getCustomer (Producer)
createOrder (Consumer) --[product_id]--> getProduct (Producer)
updateOrder (Consumer) --[order_id]--> getOrder (Producer)
```

这是**物理事实**，不可逾越。

**代码位置**：`graph_builder.py` 中的现有方法
- `_infer_field_dependencies()` - 字段匹配
- `_infer_entity_dependencies()` - 实体推断
- 结果：创建 `(API)-[:DEPENDS_ON]->(API)` 关系

### 第二步：实体级聚合（视图层）

当 API 层的连线建立后，**自动向上折叠**：

```
逻辑：
  如果 A1 ∈ Entity_A 且 B1 ∈ Entity_B
  且 A1 -> B1 存在
  则在 L1 层自动建立 Entity_A -> Entity_B

示例：
  createOrder ∈ Order
  getCustomer ∈ Customer
  createOrder -> getCustomer 存在
  ⇒ Order -> Customer
```

**关键**：Entity 边是**聚合视图**，不是独立的推断。

### 第三步：在 Entity 边上挂载"锚点"（Anchoring）

这是解决"Agent 只知道 A 依赖 B"问题的核心。

在 `Entity_A -> Entity_B` 的边上，存储一个**索引（Index）**：

```json
Edge (Order -> Customer): {
  "edge_count": 2,
  "avg_confidence": 0.85,
  "dependencies": [
    {
      "source_api": "createOrder",
      "target_api": "getCustomer",
      "field": "customer_id",
      "score": 0.8,
      "type": "SCHEMA_REFERENCE"
    },
    {
      "source_api": "updateOrder",
      "target_api": "getCustomer",
      "field": "customer_id",
      "score": 0.9,
      "type": "SCHEMA_REFERENCE"
    }
  ],
  "producer_apis": ["getCustomer", "getCustomerDetail"],
  "consumer_apis": ["createOrder", "updateOrder"],
  "data_fields": ["customer_id"]
}
```

## Neo4j 数据模型

### 节点类型

```cypher
// Entity 节点（虚 - 聚合视图）
(:Entity {
  name: "order",
  api_count: 5,
  operations: ["create", "get", "update", "delete"]
})

// API 节点（实 - 物理事实）
(:API {
  operation_id: "createOrder",
  entity: "order",
  role: "CONSUMER",
  method: "POST",
  path: "/order/create",
  response_fields: [...],
  request_fields: [...]
})
```

### 关系类型

```cypher
// API 归属关系（连接实与虚）
(createOrder:API)-[:BELONGS_TO]->(Order:Entity)

// API 依赖关系（实 - 物理事实）
(createOrder:API)-[:DEPENDS_ON {
  score: 0.8,
  type: "SCHEMA_REFERENCE",
  reason: "References customer via field 'customer_id'",
  field: "customer_id",
  source_entity: "order",
  target_entity: "customer"
}]->(getCustomer:API)

// Entity 依赖关系（虚 - 聚合视图 + 锚点索引）
(Order:Entity)-[:REQUIRES_DATA {
  edge_count: 2,
  avg_confidence: 0.85,

  // 锚点索引 - 指向底层 API 依赖
  dependencies: [
    {
      "source_api": "createOrder",
      "target_api": "getCustomer",
      "field": "customer_id",
      "score": 0.8,
      "type": "SCHEMA_REFERENCE"
    },
    {
      "source_api": "updateOrder",
      "target_api": "getCustomer",
      "field": "customer_id",
      "score": 0.9,
      "type": "SCHEMA_REFERENCE"
    }
  ],

  // 快速索引
  producer_apis: ["getCustomer", "getCustomerDetail"],
  consumer_apis: ["createOrder", "updateOrder"],
  data_fields: ["customer_id"]
}]->(Customer:Entity)
```

## 构建流程（代码层面）

### 修改 `graph_builder.py`

```python
def build(self, capabilities, dependencies=None):
    with self.driver.session() as session:
        # 清空图
        session.run("MATCH (n) DETACH DELETE n")

        api_map = {}

        # ========== 第一步：创建 API 节点（实） ==========
        for cap in capabilities:
            for api in cap.get('apis', []):
                # 创建 API 节点
                session.run("""
                    CREATE (a:API {
                        operation_id: $operation_id,
                        entity: $entity,
                        method: $method,
                        path: $path,
                        ...
                    })
                """, ...)

                api_map[api['operation_id']] = {
                    **api,
                    'entity': api.get('entity_anchor', cap.get('resource', ''))
                }

        # ========== 第二步：推断 API 依赖（实 - 物理事实） ==========
        # 保持现有逻辑不变
        inferred_field = self._infer_field_dependencies(session, api_map)
        inferred_entity = self._infer_entity_dependencies(session, api_map)

        # ========== 第三步：创建 Entity 节点（虚） ==========
        entity_stats = self._create_entity_nodes(session, api_map)

        # ========== 第四步：创建 BELONGS_TO 关系 ==========
        self._create_belongs_to_relationships(session, api_map)

        # ========== 第五步：聚合 Entity 依赖（虚 + 锚点） ==========
        entity_edges = self._aggregate_entity_relationships(session)

        # ========== 第六步：标注 API 角色 ==========
        self._annotate_api_roles(session)

        return {
            'apis_created': len(api_map),
            'api_dependencies': inferred_field + inferred_entity,
            'entities_created': entity_stats['count'],
            'entity_relationships': entity_edges
        }
```

### 关键方法实现

#### 1. `_create_entity_nodes()` - 创建 Entity 节点

```python
def _create_entity_nodes(self, session, api_map):
    """创建 Entity 节点（从 API 聚合）"""

    # 统计每个 entity 的信息
    entity_info = defaultdict(lambda: {
        'apis': [],
        'operations': set()
    })

    for op_id, api in api_map.items():
        entity = api.get('entity')
        if entity and entity != 'unknown':
            entity_info[entity]['apis'].append(op_id)
            # 提取操作类型
            op_type = self._get_operation_type(api)
            entity_info[entity]['operations'].add(op_type)

    # 创建 Entity 节点
    count = 0
    for entity, info in entity_info.items():
        session.run("""
            CREATE (e:Entity {
                name: $name,
                api_count: $api_count,
                operations: $operations
            })
        """,
            name=entity,
            api_count=len(info['apis']),
            operations=list(info['operations'])
        )
        count += 1

    return {'count': count}
```

#### 2. `_create_belongs_to_relationships()` - 创建归属关系

```python
def _create_belongs_to_relationships(self, session, api_map):
    """创建 API -> Entity 归属关系"""

    for op_id, api in api_map.items():
        entity = api.get('entity')
        if entity and entity != 'unknown':
            session.run("""
                MATCH (a:API {operation_id: $op_id})
                MATCH (e:Entity {name: $entity})
                CREATE (a)-[:BELONGS_TO]->(e)
            """,
                op_id=op_id,
                entity=entity
            )
```

#### 3. `_aggregate_entity_relationships()` - 聚合 Entity 依赖（核心）

```python
def _aggregate_entity_relationships(self, session):
    """
    从 API 依赖聚合到 Entity 依赖，并挂载锚点索引。

    这是核心方法：以 API 为实，实体为虚。
    """

    # 查询所有跨实体的 API 依赖
    result = session.run("""
        MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
        MATCH (a1)-[:BELONGS_TO]->(e1:Entity)
        MATCH (a2)-[:BELONGS_TO]->(e2:Entity)
        WHERE e1.name <> e2.name
        RETURN e1.name as source_entity,
               e2.name as target_entity,
               a1.operation_id as source_api,
               a2.operation_id as target_api,
               r.score as score,
               r.type as type,
               r.reason as reason,
               r.field as field
    """)

    # 按 (source_entity, target_entity) 分组
    entity_edges = defaultdict(lambda: {
        'dependencies': [],
        'scores': [],
        'types': Counter(),
        'fields': set(),
        'producer_apis': set(),
        'consumer_apis': set()
    })

    for record in result:
        key = (record['source_entity'], record['target_entity'])

        # 添加锚点信息
        entity_edges[key]['dependencies'].append({
            'source_api': record['source_api'],
            'target_api': record['target_api'],
            'field': record.get('field', ''),
            'score': record['score'],
            'type': record['type']
        })

        entity_edges[key]['scores'].append(record['score'])
        entity_edges[key]['types'][record['type']] += 1
        if record.get('field'):
            entity_edges[key]['fields'].add(record['field'])
        entity_edges[key]['producer_apis'].add(record['target_api'])
        entity_edges[key]['consumer_apis'].add(record['source_api'])

    # 创建 Entity 边（带锚点索引）
    count = 0
    for (source_entity, target_entity), info in entity_edges.items():
        edge_count = len(info['dependencies'])
        avg_confidence = sum(info['scores']) / edge_count if edge_count > 0 else 0.0

        # 过滤：至少 2 个 API 依赖，平均置信度 >= 0.6
        if edge_count >= 2 and avg_confidence >= 0.6:
            session.run("""
                MATCH (e1:Entity {name: $source})
                MATCH (e2:Entity {name: $target})
                MERGE (e1)-[r:REQUIRES_DATA]->(e2)
                SET r.edge_count = $edge_count,
                    r.avg_confidence = $avg_confidence,
                    r.dependencies = $dependencies,
                    r.producer_apis = $producer_apis,
                    r.consumer_apis = $consumer_apis,
                    r.data_fields = $data_fields,
                    r.edge_types = $edge_types
            """,
                source=source_entity,
                target=target_entity,
                edge_count=edge_count,
                avg_confidence=avg_confidence,
                dependencies=json.dumps(info['dependencies']),  # 锚点索引
                producer_apis=list(info['producer_apis']),
                consumer_apis=list(info['consumer_apis']),
                data_fields=list(info['fields']),
                edge_types=json.dumps(dict(info['types']))
            )
            count += 1

    return count
```

#### 4. `_annotate_api_roles()` - 标注 API 角色

```python
def _annotate_api_roles(self, session):
    """
    基于跨实体依赖标注 API 角色。

    Producer: 被其他实体的 API 依赖
    Consumer: 依赖其他实体的 API
    Bridge: 既是 Producer 又是 Consumer
    Internal: 只在实体内部使用
    """

    # 统计每个 API 的跨实体依赖
    result = session.run("""
        MATCH (a:API)-[:BELONGS_TO]->(e:Entity)
        OPTIONAL MATCH (a)-[r1:DEPENDS_ON]->(other:API)-[:BELONGS_TO]->(e2:Entity)
        WHERE e.name <> e2.name
        OPTIONAL MATCH (other2:API)-[r2:DEPENDS_ON]->(a)
        MATCH (other2)-[:BELONGS_TO]->(e3:Entity)
        WHERE e.name <> e3.name
        RETURN a.operation_id as op_id,
               count(DISTINCT r1) as outgoing,
               count(DISTINCT r2) as incoming
    """)

    for record in result:
        op_id = record['op_id']
        outgoing = record['outgoing']
        incoming = record['incoming']

        # 确定角色
        if incoming > 0 and outgoing == 0:
            role = 'PRODUCER'
        elif outgoing > 0 and incoming == 0:
            role = 'CONSUMER'
        elif incoming > 0 and outgoing > 0:
            role = 'BRIDGE'
        else:
            role = 'INTERNAL'

        # 更新 API 节点
        session.run("""
            MATCH (a:API {operation_id: $op_id})
            SET a.role = $role,
                a.incoming_cross_entity = $incoming,
                a.outgoing_cross_entity = $outgoing
        """,
            op_id=op_id,
            role=role,
            incoming=incoming,
            outgoing=outgoing
        )
```

## Agent 查询流程

### 场景：Agent 需要取消订单

```cypher
-- Step 1: 在 Entity 层查看依赖
MATCH (e:Entity {name: "order"})-[r:REQUIRES_DATA]->(f:Entity)
RETURN f.name as depends_on,
       r.data_fields as needs,
       r.dependencies as anchors

-- 结果：
-- depends_on: "order" (自身)
-- needs: ["order_id"]
-- anchors: [
--   {"source_api": "cancelOrder", "target_api": "getOrder", "field": "order_id"}
-- ]

-- Step 2: 根据锚点，直接找到具体 API
-- 从 anchors 中知道：cancelOrder 需要 getOrder

-- Step 3: 执行
-- 1. 调用 getOrder 获取 order_id
-- 2. 调用 cancelOrder(order_id)
```

### 关键优势

**锚点索引**让 Agent 可以：
1. 在 Entity 层看到高层依赖（Order -> Customer）
2. 通过 `dependencies` 字段直接定位到具体 API 对
3. 无需再次查询 API 层，直接执行

## 可视化效果

```
Neo4j Browser:

实体层视图（简洁）:
  [Order] --REQUIRES_DATA(edge_count:2)--> [Customer]

  点击边，查看属性：
    dependencies: [
      {source_api: "createOrder", target_api: "getCustomer", field: "customer_id"},
      {source_api: "updateOrder", target_api: "getCustomer", field: "customer_id"}
    ]

API 层视图（详细）:
  [createOrder] --DEPENDS_ON--> [getCustomer]
  [updateOrder] --DEPENDS_ON--> [getCustomer]

  [createOrder] --BELONGS_TO--> [Order]
  [getCustomer] --BELONGS_TO--> [Customer]

混合视图（完整）:
  [Order] --REQUIRES_DATA--> [Customer]
     ↑                          ↑
     |                          |
  [createOrder] --DEPENDS_ON--> [getCustomer]
```

## 总结

### 核心原则
- **以 API 为实**：所有依赖推断基于 API 字段匹配
- **以实体为虚**：Entity 关系是 API 依赖的聚合视图
- **锚点索引**：Entity 边存储底层 API 依赖的索引

### 关键创新
- **dependencies 字段**：在 Entity 边上挂载具体的 API 依赖列表
- **双向导航**：可以从 Entity 下钻到 API，也可以从 API 上溯到 Entity
- **精确制导**：Agent 通过锚点直接定位到具体 API，无需二次查询

### 实现顺序
1. 保持现有 API 推断逻辑不变
2. 创建 Entity 节点（聚合）
3. 创建 BELONGS_TO 关系
4. 聚合 Entity 依赖（带锚点）
5. 标注 API 角色
