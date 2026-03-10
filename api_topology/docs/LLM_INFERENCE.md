# LLM-Based Entity Inference

## Overview

LLM 智能推断是实体关系推断的最高优先级方法，利用大语言模型的语义理解能力来识别实体间的依赖关系。

## 推断优先级

系统按以下优先级进行推断（从高到低）：

1. **LLM Inference** (最高优先级) - 智能语义推断
2. **Schema Reference** - 基于字段引用（如 `customerId`）
3. **CRUD Flow** - 基于操作流程（如 UPDATE 依赖 GET）
4. **Path Hierarchy** - 基于路径层级（如 `/order/{id}/items`）

## 工作原理

### 1. 实体信息收集

系统收集每个实体的：
- 操作类型（create, get, update, delete 等）
- 示例字段（从 request/response schema 提取）

### 2. LLM 分析

将实体信息发送给 LLM，要求分析实体间的依赖关系：

```
Entities:
  order:
    Operations: create, get, update
    Sample fields: customerId, productId, quantity

  customer:
    Operations: get, list
    Sample fields: id, name, email
```

### 3. 关系推断

LLM 返回实体依赖关系和置信度：

```json
{
  "order": [["customer", 0.9], ["product", 0.85]],
  "payment": [["order", 0.95]]
}
```

### 4. 依赖生成

系统根据 LLM 建议，在写操作和读操作之间创建依赖：
- `createOrder` → `getCustomer` (score: 0.9)
- `createOrder` → `getProduct` (score: 0.85)
- `createPayment` → `getOrder` (score: 0.95)

## 使用方法

### 基本用法

```python
from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer
from openai import OpenAI

# 创建 LLM 客户端
llm_client = OpenAI(api_key="your-key")

# 创建推断器（启用 LLM）
inferrer = DynamicEntityInferrer(llm_client=llm_client)

# 推断依赖
dependencies = inferrer.infer_dependencies(api_map)
```

### 不使用 LLM

```python
# 不传入 llm_client，系统会使用其他推断方法
inferrer = DynamicEntityInferrer(llm_client=None)
dependencies = inferrer.infer_dependencies(api_map)
```

### 在图构建中使用

```python
from api_topology.graph_builder import GraphBuilder
from openai import OpenAI

llm_client = OpenAI(api_key="your-key")

builder = GraphBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_client=llm_client,  # 启用 LLM 推断
    use_entity_inference=True
)
```

## 支持的 LLM 客户端

### OpenAI

```python
from openai import OpenAI

llm_client = OpenAI(api_key="your-key")
inferrer = DynamicEntityInferrer(llm_client=llm_client)
```

### Anthropic

```python
from anthropic import Anthropic

llm_client = Anthropic(api_key="your-key")
inferrer = DynamicEntityInferrer(llm_client=llm_client)
```

### 自定义客户端

```python
def custom_llm(prompt: str) -> str:
    # 调用你的 LLM API
    response = your_llm_api.call(prompt)
    return response

inferrer = DynamicEntityInferrer(llm_client=custom_llm)
```

## 优势

1. **语义理解**：理解业务逻辑和实体关系
2. **高准确率**：基于上下文的智能推断
3. **灵活性**：可处理复杂的业务场景
4. **可解释性**：提供推断原因

## 自动降级机制

当 LLM 不可用时，系统会自动降级到其他推断方法：

### 降级触发条件

1. **API 调用失败**：网络错误、认证失败等
2. **超时**：LLM 响应超过 30 秒
3. **空响应**：LLM 返回空结果
4. **解析错误**：LLM 返回格式不正确

### 降级行为

```python
# 默认启用自动降级
inferrer = DynamicEntityInferrer(
    llm_client=llm_client,
    enable_llm_fallback=True  # 默认值
)

# 禁用自动降级（每次都尝试 LLM）
inferrer = DynamicEntityInferrer(
    llm_client=llm_client,
    enable_llm_fallback=False
)
```

### 降级流程

```
1. 尝试 LLM 推断
   ↓ (失败)
2. 标记 LLM 不可用
   ↓
3. 输出警告信息
   ↓
4. 使用其他推断方法：
   - Schema Reference
   - CRUD Flow
   - Path Hierarchy
   ↓
5. 后续调用跳过 LLM（避免重复失败）
```

### 示例输出

```
[LLM] Using intelligent inference...
[LLM] Error: LLM API unavailable
[LLM] Auto-fallback enabled - will use other inference methods
[LLM] Skipping - previous failure, using fallback methods

SCHEMA_REFERENCE: 2 dependencies
  createOrder -> getCustomer (score: 0.80)
  createOrder -> getProduct (score: 0.80)
```

## 性能考虑

1. **缓存机制**：相同实体集合的结果会被缓存
2. **批量处理**：一次 LLM 调用分析所有实体
3. **自动降级**：LLM 失败后立即切换到其他方法
4. **超时保护**：30 秒超时避免长时间等待

## 测试

运行测试（需要先激活 conda 环境）：

```bash
conda activate flora

# 快速测试
python test_llm_quick.py

# 完整功能测试
python api_topology/test_llm_inference.py

# 自动降级测试
python test_llm_fallback.py
```

## 配置

### 置信度阈值

```python
inferrer = DynamicEntityInferrer(
    llm_client=llm_client,
    min_confidence=0.7  # 只保留置信度 >= 0.7 的依赖
)
```

### LLM 参数

在 `llm_entity_inferrer.py` 中可以调整：
- `temperature`: 控制输出随机性（默认 0.3）
- `max_tokens`: 最大输出长度（默认 2000）
- `model`: 使用的模型（默认 gpt-4 或 claude-3-sonnet）

## 示例输出

```
[LLM] Using intelligent inference...
[LLM] Inferred 6 dependencies

LLM_INFERENCE: 6 dependencies
  createOrder -> getCustomer (score: 0.90)
    Reason: LLM inferred: order depends on customer
  createOrder -> getProduct (score: 0.85)
    Reason: LLM inferred: order depends on product
  createPayment -> getOrder (score: 0.95)
    Reason: LLM inferred: payment depends on order
```

## 注意事项

1. **API 成本**：每次推断会调用 LLM API，注意成本控制
2. **响应时间**：LLM 调用需要时间，首次推断会较慢
3. **网络依赖**：需要稳定的网络连接
4. **API 密钥**：确保 LLM API 密钥配置正确

## 未来改进

- [ ] 支持更多 LLM 提供商
- [ ] 优化 prompt 提高准确率
- [ ] 增加推断结果的可视化
- [ ] 支持增量更新（只分析新增实体）
