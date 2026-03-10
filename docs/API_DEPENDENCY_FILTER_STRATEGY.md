# API 依赖推断架构 - 实体作为过滤器（The Filter Strategy）

## 核心思路

**把实体定义作为"过滤器"，而非限制**

- **实体关系 = 骨架（Master Logic）**：预先定义的高层逻辑
- **API 依赖 = 肌肉（Detail Filler）**：在骨架指导下填充细节

## 完整流程

### 第一步：定义实体（L1 - Entity Layer）

从聚类结果中提取实体：

```python
entities = ["order", "user", "product", "payment"]
```

### 第二步：定义实体关系（L1 Link）

**方式 1：从 API 依赖自动推断（当前实现）**

```python
# 分析所有 API 依赖，聚合到实体层
Order -> User (基于 createOrder -> getUser)
Order -> Product (基于 createOrder -> getProduct)
Payment -> Order (基于 createPayment -> getOrder)
```

**方式 2：LLM 预定义（可选增强）**

```python
# LLM 分析实体语义，预先定义关系
Order -> User (1:N)
Order -> Product (N:M)
Payment -> Order (1:1)
```

### 第三步：API 归属（L3 to L1）

```python
Order:
  - createOrder
  - getOrder
  - updateOrder
  - deleteOrder

User:
  - getUser
  - listUsers

Product:
  - getProduct
  - listProducts
```

### 第四步：自动填充 API 依赖（L3 Link - 核心）

**关键：使用实体关系作为过滤器**

```python
# 伪代码
for each API in Order:
    # 只在 Order 关联的实体（User, Product）中寻找依赖
    related_entities = get_related_entities("Order")  # [User, Product]

    for each related_entity in related_entities:
        for each target_API in related_entity:
            # 使用 FieldMatcher 检查字段匹配
            if field_matches(API, target_API):
                create_dependency(API -> target_API)
```

**示例：**

```
createOrder (Order) 需要找依赖：
  ↓
查看 Order 的关联实体：User, Product
  ↓
只在 User 和 Product 的 API 中搜索：
  - getUser (User) ✓ 匹配 user_id
  - getProduct (Product) ✓ 匹配 product_id
  ↓
创建依赖：
  createOrder -> getUser
  createOrder -> getProduct
```

## 数据结构

### Neo4j 模型

```cypher
// L1: Entity 节点
(:Entity {name: "order"})
(:Entity {name: "user"})
(:Entity {name: "product"})

// L1: Entity 关系（骨架）
(Order:Entity)-[:RELATES_TO {
  relationship_type: "1:N",
  inferred_from: "API_AGGREGATION",  // 或 "LLM_PREDEFINED"
  api_edge_count: 3
}]->(User:Entity)

// L3: API 节点
(:API {operation_id: "createOrder", entity: "order"})
(:API {operation_id: "getUser", entity: "user"})

// L3: API 归属
(createOrder:API)-[:BELONGS_TO]->(Order:Entity)

// L3: API 依赖（肌肉 - 在骨架指导下填充）
(createOrder:API)-[:DEPENDS_ON {
  score: 0.85,
  type: "FIELD_MATCH",
  field: "user_id",
  filtered_by_entity_relation: "Order->User"  // 关键：记录是通过哪个实体关系过滤的
}]->(getUser:API)
```

## 代码实现

### 1. 修改 `graph_builder.py`

```python
class GraphBuilder:
    def build(self, capabilities, dependencies=None):
        with self.driver.session() as session:
            api_map = {}

            # Step 1: 创建 API 节点
            for cap in capabilities:
                for api in cap.get('apis', []):
                    session.run("CREATE (a:API {...})")
                    api_map[api['operation_id']] = {...}

            # Step 2: 创建 Entity 节点 + BELONGS_TO 关系
            entity_map = self._create_entities_and_belongsto(session, api_map)

            # Step 3: 推断或预定义 Entity 关系（骨架）
            entity_relations = self._infer_or_predefine_entity_relations(
                session, api_map, entity_map
            )

            # Step 4: 使用 Entity 关系作为过滤器，填充 API 依赖（肌肉）
            api_deps = self._infer_api_dependencies_with_filter(
                session, api_map, entity_relations
            )

            # Step 5: 标注 API 角色
            self._annotate_api_roles(session)

            return {
                'apis_created': len(api_map),
                'entities_created': len(entity_map),
                'entity_relations': len(entity_relations),
                'api_dependencies': len(api_deps)
            }
```

### 2. 核心方法：`_infer_api_dependencies_with_filter()`

```python
def _infer_api_dependencies_with_filter(self, session, api_map, entity_relations):
    """
    使用实体关系作为过滤器，填充 API 依赖。

    核心逻辑：
    - 对于每个 API，只在其实体的关联实体中寻找依赖
    - 使用 FieldMatcher 进行字段匹配
    """
    dependencies = []

    # 构建实体关系索引：entity -> [related_entities]
    entity_relation_map = defaultdict(set)
    for rel in entity_relations:
        entity_relation_map[rel['source']].add(rel['target'])
        # 双向关系（可选）
        # entity_relation_map[rel['target']].add(rel['source'])

    # 按实体分组 API
    entity_api_map = defaultdict(list)
    for op_id, api in api_map.items():
        entity = api.get('entity')
        if entity:
            entity_api_map[entity].append((op_id, api))

    # 遍历每个 API
    for source_entity, source_apis in entity_api_map.items():
        # 获取关联实体
        related_entities = entity_relation_map.get(source_entity, set())

        # 添加自身（同实体内的依赖）
        related_entities.add(source_entity)

        print(f"\n  [Filter] {source_entity} -> related: {related_entities}")

        for source_op_id, source_api in source_apis:
            response_fields = source_api.get('response_fields', [])
            request_fields = source_api.get('request_fields', [])

            # 只在关联实体的 API 中寻找依赖
            for target_entity in related_entities:
                target_apis = entity_api_map.get(target_entity, [])

                for target_op_id, target_api in target_apis:
                    if source_op_id == target_op_id:
                        continue

                    # 方向 1: source 的 request 依赖 target 的 response
                    if request_fields:
                        target_response = target_api.get('response_fields', [])
                        if target_response:
                            score, matched = self._match_fields(
                                request_fields, target_response
                            )
                            if score >= self.matcher.final_threshold:
                                dependencies.append({
                                    'source': source_op_id,
                                    'target': target_op_id,
                                    'score': score,
                                    'type': 'FIELD_MATCH',
                                    'matched_fields': matched,
                                    'filtered_by': f"{source_entity}->{target_entity}"
                                })

                    # 方向 2: target 的 request 依赖 source 的 response
                    if response_fields:
                        target_request = target_api.get('request_fields', [])
                        if target_request:
                            score, matched = self._match_fields(
                                target_request, response_fields
                            )
                            if score >= self.matcher.final_threshold:
                                dependencies.append({
                                    'source': target_op_id,
                                    'target': source_op_id,
                                    'score': score,
                                    'type': 'FIELD_MATCH',
                                    'matched_fields': matched,
                                    'filtered_by': f"{target_entity}->{source_entity}"
                                })

    # 去重
    dependencies = self._deduplicate_dependencies(dependencies)

    # 创建 API 依赖边
    for dep in dependencies:
        session.run("""
            MATCH (a:API {operation_id: $source})
            MATCH (b:API {operation_id: $target})
            MERGE (a)-[r:DEPENDS_ON]->(b)
            SET r.score = $score,
                r.type = $type,
                r.matched_fields = $matched_fields,
                r.filtered_by_entity_relation = $filtered_by
        """,
            source=dep['source'],
            target=dep['target'],
            score=dep['score'],
            type=dep['type'],
            matched_fields=str(dep['matched_fields']),
            filtered_by=dep['filtered_by']
        )

    return dependencies

def _match_fields(self, request_fields, response_fields):
    """使用 FieldMatcher 匹配字段"""
    best_score = 0.0
    matched_fields = []

    for req_field in request_fields:
        for resp_field in response_fields:
            score = self.matcher.calculate_score(
                resp_field, req_field,
                same_cluster=False,  # 跨实体
                source_summary='',
                target_summary=''
            )

            if score > best_score:
                best_score = score

            if score >= self.matcher.final_threshold:
                matched_fields.append({
                    'source': resp_field.get('path', resp_field.get('name')),
                    'target': req_field.get('path', req_field.get('name')),
                    'score': score
                })

    return best_score, matched_fields
```

### 3. 推断或预定义 Entity 关系

```python
def _infer_or_predefine_entity_relations(self, session, api_map, entity_map):
    """
    推断或预定义实体关系（骨架）

    方式 1：从现有 API 依赖聚合（当前实现）
    方式 2：LLM 预定义（可选）
    """
    entity_relations = []

    # 方式 1：快速推断（基于字段名）
    # 遍历所有 API，查看 request 字段是否引用其他实体
    entity_variations = self._build_entity_variations(entity_map)

    for op_id, api in api_map.items():
        source_entity = api.get('entity')
        if not source_entity:
            continue

        # 提取 request 字段
        request_fields = self._extract_field_names(api, 'request')

        for field_name in request_fields:
            # 检查是否引用其他实体（如 user_id, product_id）
            referenced_entity = self._extract_entity_from_field(
                field_name, entity_variations
            )

            if referenced_entity and referenced_entity != source_entity:
                # 记录实体关系
                entity_relations.append({
                    'source': source_entity,
                    'target': referenced_entity,
                    'inferred_from': 'FIELD_REFERENCE',
                    'example_field': field_name
                })

    # 去重
    entity_relations = self._deduplicate_entity_relations(entity_relations)

    # 创建 Entity 关系边
    for rel in entity_relations:
        session.run("""
            MATCH (e1:Entity {name: $source})
            MATCH (e2:Entity {name: $target})
            MERGE (e1)-[r:RELATES_TO]->(e2)
            SET r.inferred_from = $inferred_from,
                r.example_field = $example_field
        """,
            source=rel['source'],
            target=rel['target'],
            inferred_from=rel['inferred_from'],
            example_field=rel.get('example_field', '')
        )

    # 方式 2：LLM 预定义（可选）
    if self.llm_client:
        llm_relations = self._llm_predefine_entity_relations(entity_map)
        # 合并到 entity_relations
        # ...

    return entity_relations

def _deduplicate_entity_relations(self, relations):
    """去重实体关系"""
    seen = set()
    unique = []

    for rel in relations:
        key = (rel['source'], rel['target'])
        if key not in seen:
            seen.add(key)
            unique.append(rel)

    return unique
```

### 4. 辅助方法

```python
def _build_entity_variations(self, entity_map):
    """构建实体名称变体（用于匹配）"""
    variations = {}
    for entity in entity_map.keys():
        variations[entity] = self._get_entity_variations(entity)
    return variations

def _get_entity_variations(self, entity: str) -> Set[str]:
    """生成实体名称变体"""
    variations = {entity}

    # 移除分隔符
    variations.add(entity.replace('-', '').replace('_', ''))

    # 分割
    parts = re.split(r'[-_]', entity)
    variations.update(parts)

    # 单复数
    if entity.endswith('s'):
        variations.add(entity[:-1])
    else:
        variations.add(entity + 's')

    return variations

def _extract_entity_from_field(self, field_name: str, entity_variations: Dict) -> Optional[str]:
    """从字段名提取实体引用"""
    field_lower = field_name.lower()

    # 移除常见后缀
    for suffix in ['_id', 'id', '_key', 'key', '_code', 'code']:
        if field_lower.endswith(suffix):
            field_base = field_lower[:-len(suffix)]

            # 检查是否匹配任何实体
            for entity, variations in entity_variations.items():
                if field_base in variations:
                    return entity

    return None
```

## 执行流程示例

### 场景：createOrder 寻找依赖

```
1. createOrder 属于 Order 实体

2. 查找 Order 的关联实体：
   Order -> User (通过 user_id 字段推断)
   Order -> Product (通过 product_id 字段推断)

3. 只在 User 和 Product 的 API 中搜索：
   User APIs: [getUser, listUsers]
   Product APIs: [getProduct, listProducts]

4. 使用 FieldMatcher 匹配：
   createOrder.request.user_id <-> getUser.response.id ✓ 匹配
   createOrder.request.product_id <-> getProduct.response.id ✓ 匹配

5. 创建依赖：
   createOrder -> getUser (filtered_by: "Order->User")
   createOrder -> getProduct (filtered_by: "Order->Product")
```

## 优势

### 1. 清晰的层次

```
L1 (骨架):
  Order -> User
  Order -> Product
  Payment -> Order

L3 (肌肉):
  createOrder -> getUser (挂在 Order->User 骨架上)
  createOrder -> getProduct (挂在 Order->Product 骨架上)
  createPayment -> getOrder (挂在 Payment->Order 骨架上)
```

### 2. 高效的搜索

- 不需要遍历所有 API 对（O(n²)）
- 只在关联实体内搜索（O(n×m)，m << n）

### 3. 可控的依赖

- 实体关系作为"白名单"
- 避免产生不合理的跨实体依赖

### 4. 易于调试

- 每个 API 依赖都记录了 `filtered_by_entity_relation`
- 可以追溯到是通过哪个实体关系过滤的

## 可视化

```
Neo4j Browser:

实体层（骨架）:
  [Order] --RELATES_TO--> [User]
  [Order] --RELATES_TO--> [Product]

API 层（肌肉）:
  [createOrder] --DEPENDS_ON(filtered_by:"Order->User")--> [getUser]
  [createOrder] --DEPENDS_ON(filtered_by:"Order->Product")--> [getProduct]

  [createOrder] --BELONGS_TO--> [Order]
  [getUser] --BELONGS_TO--> [User]
  [getProduct] --BELONGS_TO--> [Product]
```

## 总结

### 核心思想

**实体关系 = 过滤器（Filter）**

- 不是限制，而是指导
- 先定义骨架，再填充肌肉
- API 依赖在骨架指导下生成

### 关键实现

1. **推断实体关系**：从字段引用（user_id, product_id）快速推断
2. **过滤搜索空间**：只在关联实体内寻找 API 依赖
3. **记录过滤依据**：`filtered_by_entity_relation` 字段

### 优势

- ✅ 保持实体图清爽（骨架）
- ✅ API 依赖有序挂载（肌肉）
- ✅ 搜索效率高（过滤器）
- ✅ 依赖可追溯（记录过滤依据）
