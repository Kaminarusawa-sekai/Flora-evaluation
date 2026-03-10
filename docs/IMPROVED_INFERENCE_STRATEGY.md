# 改进的推断策略实现

## 问题分析

### 原有问题

1. **实体关系推断（`_infer_entity_relations`）**
   - 只基于字段名硬匹配（如 `supplier_id` → `supplier`）
   - 无法理解语义关系
   - 没有使用 LLM 能力

2. **API 依赖推断（`_infer_api_dependencies_with_filter`）**
   - 只用 FieldMatcher 硬匹配字段名
   - 字段命名不规范时会漏掉很多依赖
   - 缺少 CRUD Flow 等补充推断

## 解决方案

### 核心思想：多层推断策略 + 降级机制

```
优先级高 ────────────────────────> 优先级低
LLM 推断 → 字段引用推断 → CRUD Flow → Path Hierarchy
(最智能)   (降级方案)     (补充)      (补充)
```

## 实现细节

### 1. 实体关系推断（L1 层 - 骨架）

#### 方法：`_infer_entity_relations()`

**多层策略：**

```python
# 策略1: LLM 推断（优先级最高）
if self.llm_inferrer:
    llm_entity_relations = self._infer_entity_relations_by_llm(entity_groups)
    # LLM 理解语义：purchase-order 依赖 supplier

# 策略2: 字段引用推断（降级方案）
field_relations = self._infer_entity_relations_by_fields(api_map, entity_groups)
# 从字段名推断：supplierCode → supplier

# 策略3: Path Hierarchy（补充）
path_relations = self._infer_entity_relations_by_path(api_map, entity_groups)
# 从路径推断：/purchase-order/{id}/supplier
```

**优先级去重：**
```
LLM_INFERENCE (优先级 3) > FIELD_REFERENCE (优先级 2) > PATH_HIERARCHY (优先级 1)
```

**示例输出：**
```
purchase-order -> supplier (via LLM_INFERENCE, confidence=0.90)
purchase-order -> product (via FIELD_REFERENCE, confidence=0.80)
```

### 2. API 依赖推断（L3 层 - 肌肉）

#### 方法：`_infer_api_dependencies_with_filter()`

**多层策略：**

```python
# 策略1: FieldMatcher（精确字段匹配）
field_deps = self._infer_api_deps_by_field_match(...)
# 精确匹配：supplierCode 字段匹配

# 策略2: LLM 语义推断（补充）
llm_deps = self._infer_api_deps_by_llm_semantic(...)
# 处理命名不规范的情况

# 策略3: CRUD Flow（同实体内）
crud_deps = self._infer_api_deps_by_crud_flow(...)
# updatePurchaseOrder → getPurchaseOrder
```

**CRUD Flow 逻辑：**
```
同一实体内：
- UPDATE 操作 → 依赖 GET 操作（需要先获取数据）
- DELETE 操作 → 依赖 GET 操作（需要验证）
```

**示例输出：**
```
createPurchaseOrder -> getSupplier (FIELD_MATCH, score=0.85)
updatePurchaseOrder -> getPurchaseOrder (CRUD_FLOW, score=0.85)
createPurchaseOrder -> getProduct (LLM_SEMANTIC, score=0.60)
```

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    L1: 实体层（骨架）                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  purchase-order ──RELATES_TO──> supplier                     │
│      ↑                              ↑                         │
│      │                              │                         │
│   推断方法：                      推断方法：                    │
│   1. LLM 推断（优先）              1. LLM 推断                 │
│   2. 字段引用（降级）              2. 字段引用                 │
│   3. Path Hierarchy（补充）        3. Path Hierarchy          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ 过滤器（Filter）
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    L3: API 层（肌肉）                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  createPurchaseOrder ──DEPENDS_ON──> getSupplier             │
│      ↑                                   ↑                    │
│      │                                   │                    │
│   推断方法：                           推断方法：               │
│   1. FieldMatcher（精确）              1. FieldMatcher        │
│   2. LLM 语义（补充）                  2. LLM 语义            │
│   3. CRUD Flow（同实体）               3. CRUD Flow           │
│                                                               │
│  updatePurchaseOrder ──> getPurchaseOrder (CRUD Flow)        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 降级机制

### LLM 不可用时的自动降级

```python
class LLMEntityInferrer:
    def __init__(self, llm_client=None, enable_fallback=True):
        self.llm_failed = False  # 跟踪 LLM 是否失败
        self.enable_fallback = enable_fallback

    def infer_dependencies(self, ...):
        if self.llm_failed and self.enable_fallback:
            print("  [LLM] Skipping - previous failure, using fallback methods")
            return []

        try:
            # 调用 LLM
            ...
        except Exception as e:
            if self.enable_fallback:
                self.llm_failed = True
                print("  [LLM] Auto-fallback enabled - will use other inference methods")
            return []
```

**降级流程：**
```
1. 尝试 LLM 推断
   ↓ (失败)
2. 标记 llm_failed = True
   ↓
3. 后续自动跳过 LLM，使用降级方案
   ↓
4. 字段引用推断 + CRUD Flow + Path Hierarchy
```

## 代码改动

### 修改的文件

1. **`api_topology/graph_builder.py`**
   - 添加 `LLMEntityInferrer` 初始化
   - 重写 `_infer_entity_relations()` - 多层推断
   - 重写 `_infer_api_dependencies_with_filter()` - 多层推断
   - 新增辅助方法：
     - `_infer_entity_relations_by_llm()`
     - `_infer_entity_relations_by_fields()`
     - `_infer_entity_relations_by_path()`
     - `_infer_api_deps_by_field_match()`
     - `_infer_api_deps_by_llm_semantic()`
     - `_infer_api_deps_by_crud_flow()`
     - `_deduplicate_entity_relations_with_priority()`

### 新增的文件

1. **`test_improved_inference.py`**
   - 测试带 LLM 的推断
   - 测试不带 LLM 的降级推断
   - 验证多层策略的效果

## 测试

### 运行测试

```bash
conda activate flora
python test_improved_inference.py
```

### 预期结果

#### 测试 1: 带 LLM

```
实体关系 (L1 层):
  purchase-order -> supplier (via LLM_INFERENCE, confidence=0.90)
  purchase-order -> product (via FIELD_REFERENCE, confidence=0.80)

API 依赖 (L3 层):
  createPurchaseOrder -> getSupplier (FIELD_MATCH, score=0.85)
  updatePurchaseOrder -> getPurchaseOrder (CRUD_FLOW, score=0.85)
  createPurchaseOrder -> getProduct (LLM_SEMANTIC, score=0.60)
```

#### 测试 2: 不带 LLM（降级）

```
实体关系 (降级方案):
  purchase-order -> supplier (via FIELD_REFERENCE, confidence=0.80)
  purchase-order -> product (via FIELD_REFERENCE, confidence=0.80)

API 依赖 (降级方案):
  createPurchaseOrder -> getSupplier (FIELD_MATCH, score=0.85)
  updatePurchaseOrder -> getPurchaseOrder (CRUD_FLOW, score=0.85)
```

## 优势

### 1. 智能性提升
- ✅ LLM 理解语义关系，不依赖字段命名
- ✅ 处理命名不规范的情况（如 `supplierCode` vs `supplier_id`）

### 2. 鲁棒性提升
- ✅ LLM 不可用时自动降级
- ✅ 多层策略互补，提高覆盖率

### 3. 可追溯性
- ✅ 每个关系都标注推断方法和置信度
- ✅ 便于调试和优化

### 4. 灵活性
- ✅ 可以单独启用/禁用某个策略
- ✅ 可以调整优先级和置信度阈值

## 配置

### 启用/禁用 LLM

```python
# 启用 LLM
builder = GraphBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678",
    llm_client=OpenAI(...)  # 传入 LLM 客户端
)

# 禁用 LLM（使用降级方案）
builder = GraphBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678",
    llm_client=None  # 不传入 LLM 客户端
)
```

### 调整置信度阈值

```python
# 在 _infer_entity_relations_by_fields() 中
entity_relations.append({
    'confidence': 0.8,  # 可调整
    ...
})

# 在 _infer_api_deps_by_crud_flow() 中
dependencies.append({
    'score': 0.85,  # 可调整
    ...
})
```

## 下一步优化

### 可选增强

1. **LLM 批量推断**
   - 一次性推断多个实体关系，减少 API 调用

2. **缓存机制**
   - 缓存 LLM 推断结果，避免重复调用

3. **置信度融合**
   - 多个策略推断出同一关系时，融合置信度

4. **可视化**
   - 可视化不同策略的推断结果
   - 对比 LLM vs 降级方案的差异

## 总结

成功实现了多层推断策略：

- ✅ **实体关系推断**：LLM → 字段引用 → Path Hierarchy
- ✅ **API 依赖推断**：FieldMatcher → LLM 语义 → CRUD Flow
- ✅ **降级机制**：LLM 不可用时自动降级
- ✅ **优先级去重**：保留最高优先级的推断结果
- ✅ **可追溯性**：记录推断方法和置信度

这个方案既保证了智能性（LLM），又保证了鲁棒性（降级），是一个生产级的解决方案。
