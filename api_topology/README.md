# API Topology Service

构建和查询基于智能推断的 API 依赖关系图，支持实体关系推断和多层依赖分析。

## 核心架构

### 两层拓扑结构

```
┌─────────────────────────────────────────────────────────────┐
│                    L1: 实体层（骨架）                          │
│  Entity Relationship - 实体之间的语义关系                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  purchase-order ──RELATES_TO──> supplier                     │
│  purchase-order ──RELATES_TO──> product                      │
│                                                               │
│  推断方法：                                                    │
│  1. LLM 推断（优先）- 理解业务语义                             │
│  2. 字段引用推断（降级）- 基于字段命名规则                      │
│  3. Path Hierarchy（补充）- 基于路径结构                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ 过滤器（Filter）
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    L3: API 层（肌肉）                          │
│  API Dependencies - 具体操作之间的依赖关系                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  createPurchaseOrder ──DEPENDS_ON──> getSupplier             │
│  updatePurchaseOrder ──DEPENDS_ON──> getPurchaseOrder        │
│                                                               │
│  推断方法：                                                    │
│  1. FieldMatcher（精确）- 字段名精确匹配                       │
│  2. LLM 语义推断（补充）- 处理命名不规范                       │
│  3. CRUD Flow（补充）- 同实体内操作依赖                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

### 1. 多层推断策略

#### 实体关系推断（L1 层 - 骨架）

**策略优先级：**
1. **LLM 推断**（优先级最高）
   - 理解业务语义：`purchase-order` 依赖 `supplier`
   - 不依赖字段命名规则
   - 置信度：0.9

2. **字段引用推断**（降级方案）
   - 从字段名推断：`supplier_id` → `supplier`
   - 支持多种命名变体：`supplierId`, `supplier_code`
   - 置信度：0.8

3. **Path Hierarchy**（补充）
   - 从路径推断：`/purchase-order/{id}/supplier`
   - 置信度：0.75

#### API 依赖推断（L3 层 - 肌肉）

**策略优先级：**
1. **FieldMatcher**（精确匹配）
   - 字段名精确匹配
   - 支持嵌套路径：`user.id`, `items[].productId`
   - 多因子评分（实体匹配 40% + 名称相似度 30% + 语义相似度 15% + ...）

2. **LLM 语义推断**（补充）
   - 处理字段命名不规范的情况
   - 只对未找到依赖的写操作进行推断
   - 置信度：0.6

3. **CRUD Flow**（补充）
   - 同实体内的操作依赖
   - `UPDATE` → `GET`（需要先获取数据）
   - `DELETE` → `GET`（需要验证）
   - 置信度：0.85

### 2. 自动降级机制

```python
LLM 可用 ──> LLM 推断（最智能）
    │
    ↓ (LLM 失败)
    │
LLM 不可用 ──> 规则推断（降级方案）
    │
    ├─> 字段引用推断
    ├─> CRUD Flow 推断
    └─> Path Hierarchy 推断
```

**特点：**
- ✅ LLM 失败后自动标记，后续跳过 LLM 调用
- ✅ 降级方案保证基本功能可用
- ✅ 无需手动配置，自动适应环境

### 3. 实体标准化 (Entity Canonicalization)

将不同命名的字段映射到标准实体：
- `user_id`, `uid`, `u_id`, `userId` → `user`
- `supplier_code`, `supplierId`, `supplier_id` → `supplier`
- 支持单复数、分隔符变体

### 4. 语义向量匹配

使用 SentenceTransformer 计算字段描述的语义相似度：
- 识别同义不同名的字段
- 例如：`customer_name` 和 `client_name` 语义相似

### 5. 多因子评分

```
总分 = 实体匹配(40%) + 名称相似度(30%) + 语义相似度(15%)
       + 参数位置(10%) + 聚类加成(5%)
```

- **实体匹配** (40%): 最高优先级，标准化后的实体匹配
- **名称相似度** (30%): Levenshtein 距离
- **语义相似度** (15%): 描述向量匹配
- **参数位置** (10%): Path > Query > Body
- **聚类加成** (5%): 同 capability 加分

### 6. 嵌套对象支持

自动展开 JSON Schema，支持复杂路径：
- `user.id` - 嵌套对象
- `items[].productId` - 数组元素
- `data.list[].supplier.code` - 多层嵌套

### 7. 转换检测

标记需要逻辑转换的字段：
- 签名字段（`signature`, `sign`）
- 加密字段（`encrypted_*`, `cipher_*`）
- 聚合字段（`total_*`, `count_*`, `sum_*`）

### 8. 路径评分与约束

```
Score = Σ(edge_scores) / (path_length ^ 1.2)
```

支持按 `required_fields` 过滤路径，确保路径包含必需字段。

### 9. 多格式数据兼容

自动适配多种 API 数据格式：

**格式1: parameters（实际数据格式）**
```python
{
    'parameters': {
        'query': [{'name': 'supplierId', 'type': 'string'}],
        'body': [...],
        'path': [...],
        'header': [...]
    }
}
```

**格式2: request_schema / response_schemas**
```python
{
    'request_schema': {
        'properties': {
            'supplierCode': {'type': 'string'}
        }
    },
    'response_schemas': {
        '200': {
            'properties': {
                'orderId': {'type': 'string'}
            }
        }
    }
}
```

**格式3: 直接的 request_fields / response_fields**
```python
{
    'request_fields': [
        {'name': 'orderId', 'type': 'string'}
    ],
    'response_fields': [
        {'name': 'success', 'type': 'boolean'}
    ]
}
```

## 安装

```bash
pip install python-Levenshtein neo4j sentence-transformers openai
```

## 使用示例

### 基础使用（不带 LLM）

```python
from api_topology import TopologyService

service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# 构建图（使用降级方案）
result = service.build_graph(capabilities)
print(f"实体关系数: {result['entity_relationships']}")
print(f"API 依赖数: {result['api_dependencies']}")

# 查询路径
paths = service.find_paths("createOrder", "getSupplier")
```

### 高级使用（带 LLM）

```python
from api_topology import TopologyService
from openai import OpenAI

# 初始化 LLM 客户端（支持 OpenAI、通义千问、DeepSeek 等）
llm_client = OpenAI(
    api_key="your-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 通义千问
)

service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=llm_client  # 启用 LLM 推断
)

# 构建图（使用 LLM 推断）
result = service.build_graph(capabilities)

# 查询实体关系
entity_relations = service.query_entity_relations()
for rel in entity_relations:
    print(f"{rel['source']} -> {rel['target']}")
    print(f"  方法: {rel['inferred_from']}, 置信度: {rel['confidence']}")

# 查询 API 依赖
api_deps = service.query_api_dependencies(min_score=0.7)
for dep in api_deps:
    print(f"{dep['source']} -> {dep['target']}")
    print(f"  类型: {dep['type']}, 分数: {dep['score']}")
```

### 支持嵌套 Schema

```python
capabilities = [{
    "name": "User Management",
    "resource": "user",
    "apis": [{
        "operation_id": "createUser",
        "method": "POST",
        "path": "/user/create",
        "request_schema": {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "profile": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }]
}]

result = service.build_graph(capabilities)
```

### 查询路径（带约束）

```python
# 查找包含特定字段的路径
paths = service.find_paths(
    "createOrder",
    "getSupplier",
    required_fields=["supplier_id", "supplier_code"]
)

for path in paths:
    print(f"路径: {' -> '.join(path['nodes'])}")
    print(f"分数: {path['score']}")
    print(f"匹配字段: {path['matched_fields']}")
```

## 置信度分级

### 实体关系置信度

- **LLM_INFERENCE** (0.9): LLM 推断的语义关系
- **FIELD_REFERENCE** (0.8): 字段引用推断
- **PATH_HIERARCHY** (0.75): 路径层次推断

### API 依赖置信度

- **CERTAIN** (≥0.9): 确定依赖（实体完全匹配）
- **PROBABLE** (0.7-0.9): 可能依赖（名称相似）
- **CRUD_FLOW** (0.85): CRUD 流程依赖
- **LLM_SEMANTIC** (0.6): LLM 语义推断
- **WEAK** (<0.7): 不建边

## API 角色标注

基于跨实体依赖自动标注 API 角色：

- **PRODUCER**: 被其他实体的 API 依赖（提供数据）
- **CONSUMER**: 依赖其他实体的 API（消费数据）
- **BRIDGE**: 既是 Producer 又是 Consumer（中间节点）
- **INTERNAL**: 只在实体内部使用

## 配置选项

### GraphBuilder 配置

```python
from api_topology.graph_builder import GraphBuilder

builder = GraphBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_client=llm_client,  # 可选，不传则使用降级方案
    use_entity_inference=True  # 是否启用实体推断
)
```

### FieldMatcher 配置

```python
from api_topology.field_matcher import FieldMatcher

matcher = FieldMatcher(
    llm_client=llm_client,  # 可选
    entity_weight=0.4,      # 实体匹配权重
    name_weight=0.3,        # 名称相似度权重
    semantic_weight=0.15,   # 语义相似度权重
    position_weight=0.1,    # 参数位置权重
    cluster_weight=0.05     # 聚类加成权重
)
```

### LLMEntityInferrer 配置

```python
from api_topology.llm_entity_inferrer import LLMEntityInferrer

inferrer = LLMEntityInferrer(
    llm_client=llm_client,
    max_entities_per_call=10,  # 每次 LLM 调用最多分析的实体数
    enable_fallback=True        # 启用自动降级
)
```

## 测试

### 测试字段提取

```bash
python test_field_extraction.py
```

### 测试推断策略

```bash
python test_improved_inference.py
```

### 测试完整流程

```bash
python api_topology/example_usage.py
```

## 性能优化

### 1. 实体关系作为过滤器

```
传统方法: O(n²) - 所有 API 两两比较
过滤器策略: O(n×m) - 只在关联实体内比较，m << n
```

### 2. LLM 结果缓存

```python
# LLM 推断结果自动缓存
inferrer.relationship_cache = {}  # 缓存实体关系
```

### 3. 批量查询

```python
# Neo4j 批量创建节点和关系
session.run("CREATE (a:API {...})")  # 批量创建
```

## 架构优势

### 1. 清晰的层次

- **L1 层（骨架）**: 实体关系，定义业务语义
- **L3 层（肌肉）**: API 依赖，填充具体实现

### 2. 高效搜索

- 实体关系作为"白名单"，大幅减少搜索空间
- 只在关联实体内搜索依赖

### 3. 可控依赖

- 每个依赖都记录过滤依据（`filtered_by_entity_relation`）
- 易于追溯和调试

### 4. 智能降级

- LLM 可用时使用智能推断
- LLM 不可用时自动降级到规则方法
- 保证基本功能始终可用

## 文档

- **[改进的推断策略](../IMPROVED_INFERENCE_STRATEGY.md)** - 多层推断策略详解
- **[字段提取修复](../FIELD_EXTRACTION_FIX.md)** - 多格式数据兼容
- **[过滤器策略实现](../FILTER_STRATEGY_IMPLEMENTATION.md)** - 过滤器架构详解

## 常见问题

### Q: LLM 调用失败怎么办？

A: 系统会自动降级到规则方法，不影响基本功能。可以通过日志查看降级信息：
```
[LLM] Failed - falling back to other inference methods
```

### Q: 如何提高推断准确率？

A:
1. 提供 LLM 客户端以启用智能推断
2. 确保 API 数据包含完整的字段信息
3. 使用规范的字段命名（如 `supplier_id` 而非 `sid`）

### Q: 如何查看推断依据？

A: 查询 Neo4j 关系属性：
```cypher
MATCH (a:API)-[r:DEPENDS_ON]->(b:API)
RETURN a.operation_id, b.operation_id,
       r.type, r.score, r.filtered_by_entity_relation
```

### Q: 支持哪些 LLM？

A: 支持所有兼容 OpenAI API 的 LLM：
- OpenAI (GPT-4, GPT-3.5)
- 通义千问 (Qwen)
- DeepSeek
- Claude (Anthropic)
- 其他兼容 OpenAI API 的模型

## 许可证

MIT License
