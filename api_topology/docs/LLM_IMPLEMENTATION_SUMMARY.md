# LLM 智能推断 - 完整实现总结

## 功能概述

为 `api_topology` 模块添加了 LLM 智能推断功能，作为实体关系推断的最高优先级方法，并实现了完善的自动降级机制。

## 核心特性

### 1. 智能推断优先级

```
优先级 1: LLM Inference (最智能) ← 新增
优先级 2: Schema Reference (字段引用)
优先级 3: CRUD Flow (操作流程)
优先级 4: Path Hierarchy (路径层级)
```

### 2. 自动降级机制

当 LLM 不可用时自动降级：

- **触发条件**：API 失败、超时（30秒）、空响应、解析错误
- **降级行为**：标记失败 → 输出警告 → 使用其他方法
- **智能跳过**：失败后的调用自动跳过 LLM，避免重复等待

### 3. 多 LLM 支持

- OpenAI (GPT-4)
- Anthropic (Claude)
- 自定义 LLM 客户端

## 文件清单

### 核心实现
- `api_topology/llm_entity_inferrer.py` - LLM 推断核心逻辑
- `api_topology/dynamic_entity_inferrer.py` - 集成 LLM 到推断流程
- `api_topology/graph_builder.py` - 图构建器支持 LLM

### 测试文件
- `test_llm_quick.py` - 快速功能测试
- `test_llm_fallback.py` - 自动降级测试
- `api_topology/test_llm_inference.py` - 完整功能测试

### 文档
- `api_topology/LLM_INFERENCE.md` - 详细使用文档

## 使用示例

### 基本用法

```python
from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer
from openai import OpenAI

# 创建 LLM 客户端
llm_client = OpenAI(api_key="your-key")

# 启用 LLM 推断（默认启用自动降级）
inferrer = DynamicEntityInferrer(
    llm_client=llm_client,
    enable_llm_fallback=True  # 默认值
)

# 推断依赖
dependencies = inferrer.infer_dependencies(api_map)
```

### 禁用自动降级

```python
# 每次都尝试 LLM，不降级
inferrer = DynamicEntityInferrer(
    llm_client=llm_client,
    enable_llm_fallback=False
)
```

### 不使用 LLM

```python
# 只使用传统推断方法
inferrer = DynamicEntityInferrer(llm_client=None)
```

## 运行测试

```bash
# 激活环境
conda activate flora

# 快速测试
python test_llm_quick.py

# 自动降级测试
python test_llm_fallback.py

# 完整测试
python api_topology/test_llm_inference.py
```

## 降级流程示例

### 正常情况
```
[LLM] Using intelligent inference...
[LLM] Inferred 6 dependencies

LLM_INFERENCE: 6 dependencies
  createOrder -> getCustomer (score: 0.90)
  createPayment -> getOrder (score: 0.95)
```

### LLM 失败时
```
[LLM] Using intelligent inference...
[LLM] Error: LLM API unavailable
[LLM] Auto-fallback enabled - will use other inference methods
[LLM] Skipping - previous failure, using fallback methods

SCHEMA_REFERENCE: 2 dependencies
  createOrder -> getCustomer (score: 0.80)
  createOrder -> getProduct (score: 0.80)
```

## 技术细节

### 1. LLM 推断流程

```
1. 收集实体信息（操作类型、字段）
2. 构建分析 prompt
3. 调用 LLM API（30秒超时）
4. 解析 JSON 响应
5. 生成依赖关系
6. 缓存结果
```

### 2. 自动降级机制

```python
class LLMEntityInferrer:
    def __init__(self, llm_client, enable_fallback=True):
        self.llm_failed = False  # 失败标记
        self.enable_fallback = enable_fallback

    def infer_dependencies(self, ...):
        # 如果之前失败过，直接跳过
        if self.llm_failed and self.enable_fallback:
            return []

        try:
            # 尝试 LLM 推断
            ...
        except Exception as e:
            # 标记失败
            if self.enable_fallback:
                self.llm_failed = True
            return []
```

### 3. 去重机制

多个推断方法可能产生相同依赖，系统会自动去重并保留最高分数：

```python
def _deduplicate_dependencies(self, dependencies):
    # 按 (source, target) 分组
    # 保留每组中分数最高的
    ...
```

## 优势

1. **智能化**：LLM 理解业务语义，准确率更高
2. **可靠性**：自动降级保证系统稳定运行
3. **灵活性**：可选启用，不影响现有功能
4. **兼容性**：支持多种 LLM 提供商
5. **性能优化**：缓存、超时保护、智能跳过

## 配置选项

```python
DynamicEntityInferrer(
    min_confidence=0.6,           # 最低置信度阈值
    llm_client=llm_client,        # LLM 客户端
    enable_llm_fallback=True      # 启用自动降级
)

LLMEntityInferrer(
    llm_client=llm_client,
    max_entities_per_call=10,     # 每次最多分析实体数
    enable_fallback=True           # 启用降级
)
```

## 注意事项

1. **API 成本**：每次推断调用 LLM API
2. **响应时间**：首次推断需要等待 LLM 响应
3. **网络依赖**：需要稳定的网络连接
4. **API 密钥**：确保 LLM API 密钥正确配置

## 未来改进

- [ ] 支持更多 LLM 提供商
- [ ] 优化 prompt 提高准确率
- [ ] 增量更新（只分析新增实体）
- [ ] 推断结果可视化
- [ ] 自适应超时时间
- [ ] 更细粒度的降级策略

## 总结

LLM 智能推断功能已完全集成到 `api_topology` 模块，作为最高优先级的推断方法。通过完善的自动降级机制，确保在 LLM 不可用时系统仍能正常工作。
