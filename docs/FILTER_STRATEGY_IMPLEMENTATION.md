# 过滤器策略实现总结

## 完成的工作

### 1. 重构 `graph_builder.py`

完全重写了 API 依赖推断架构，实现"以实体关系为过滤器"的策略。

#### 新的构建流程

```python
def build():
    # Step 1: 创建 API 节点
    # Step 2: 创建 Entity 节点 + BELONGS_TO 关系
    # Step 3: 推断 Entity 关系（骨架）
    # Step 4: 使用 Entity 关系作为过滤器，推断 API 依赖（肌肉）
    # Step 5: 标注 API 角色
```

#### 核心方法

1. **`_create_entities_and_belongs_to()`**
   - 从 API 聚合创建 Entity 节点
   - 创建 API -> Entity 的 BELONGS_TO 关系

2. **`_infer_entity_relations()`**（骨架）
   - 从字段引用推断实体关系
   - 例如：`user_id` 字段 → Order -> User 关系

3. **`_infer_api_dependencies_with_filter()`**（肌肉）
   - 使用实体关系作为过滤器
   - 只在关联实体内搜索 API 依赖
   - 使用 FieldMatcher 进行字段匹配
   - 记录 `filtered_by_entity_relation` 字段

4. **`_annotate_api_roles()`**
   - 基于跨实体依赖标注角色
   - Producer / Consumer / Bridge / Internal

### 2. 删除废弃代码

删除了以下文件：
- `dynamic_entity_inferrer.py` - 基于 entity 分组的推断（已废弃）
- `entity_relationship_builder.py` - 旧的聚合逻辑（已废弃）
- `graph_builder_old.py` - 旧版本备份

### 3. 数据模型

#### Neo4j 结构

```cypher
// L1: Entity 层（骨架）
(Order:Entity)-[:RELATES_TO {
  inferred_from: "FIELD_REFERENCE",
  example_field: "user_id",
  example_api: "createOrder"
}]->(User:Entity)

// L3: API 层（归属）
(createOrder:API)-[:BELONGS_TO]->(Order:Entity)

// L3: API 层（肌肉）
(createOrder:API)-[:DEPENDS_ON {
  score: 0.85,
  type: "FIELD_MATCH",
  matched_fields: [...],
  filtered_by_entity_relation: "Order->User"  // 关键字段
}]->(getUser:API)
```

## 核心原理

### 过滤器策略

```
1. 定义实体（L1）
   Order, User, Product

2. 推断实体关系（L1 Link - 骨架）
   Order -> User (通过 user_id)
   Order -> Product (通过 product_id)

3. API 归属（L3 to L1）
   Order: [createOrder, getOrder]
   User: [getUser, listUsers]

4. 填充 API 依赖（L3 Link - 肌肉）
   createOrder 需要找依赖：
     ↓
   查看 Order 的关联实体：User, Product
     ↓
   只在 User 和 Product 的 API 中搜索
     ↓
   使用 FieldMatcher 匹配字段
     ↓
   创建依赖：
     createOrder -> getUser (filtered_by: "Order->User")
     createOrder -> getProduct (filtered_by: "Order->Product")
```

### 关键优势

1. **清晰的层次**：骨架（实体）+ 肌肉（API）
2. **高效搜索**：O(n×m) 而非 O(n²)，m << n
3. **可控依赖**：实体关系作为"白名单"
4. **易于追溯**：每个依赖都记录过滤依据

## 测试

创建了测试文件：
- `test_filter_strategy.py` - 完整的过滤器策略测试

运行测试：
```bash
conda activate flora
python test_filter_strategy.py
```

## 代码统计

- 新的 `graph_builder.py`: 693 行
- 删除的废弃代码: ~1000+ 行
- 净减少代码量，提高可维护性

## 架构对比

### 旧架构（废弃）

```
API 推断 → 基于 entity 分组
  ├─ Schema Reference（受限于 entity_groups）
  ├─ CRUD Flow（只在同一 entity 内）
  └─ Path Hierarchy（受限于 entity_groups）
```

问题：
- 依赖 entity 分组，限制了跨实体依赖发现
- 违反"以 API 为实"的原则

### 新架构（过滤器策略）

```
实体关系推断（骨架）
  ↓
API 依赖推断（肌肉）
  ├─ 使用实体关系作为过滤器
  ├─ 只在关联实体内搜索
  └─ FieldMatcher 进行字段匹配
```

优势：
- 以 API 为实，实体为虚
- 实体关系作为过滤器，而非限制
- 高效且可控

## 下一步

可选的增强功能：
1. LLM 预定义实体关系（增强骨架）
2. 添加更多推断规则（CRUD 模式、路径层级）
3. 可视化实体关系图
4. 性能优化（批量查询、缓存）

## 总结

成功实现了"过滤器策略"架构：
- ✅ 实体关系 = 骨架（Master Logic）
- ✅ API 依赖 = 肌肉（Detail Filler）
- ✅ 实体关系作为过滤器，指导 API 依赖推断
- ✅ 清晰的分层，高效的搜索，可控的依赖
