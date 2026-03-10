# LLM 配置指南

## 支持的 LLM 提供商

系统支持所有兼容 OpenAI API 格式的 LLM 提供商。

## 配置示例

### 1. OpenAI

```python
from openai import OpenAI

llm_client = OpenAI(api_key="sk-...")
```

### 2. Qwen (通义千问)

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="sk-...",  # 阿里云 API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

推荐模型：
- `qwen-plus` - 性价比高，推荐使用
- `qwen-max` - 最强性能
- `qwen-turbo` - 速度快，成本低

### 3. DeepSeek

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)
```

推荐模型：
- `deepseek-chat` - 通用对话模型

### 4. 本地模型 (Ollama)

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="ollama",  # 任意值
    base_url="http://localhost:11434/v1"
)
```

推荐模型：
- `qwen2.5:7b`
- `llama3.1:8b`

### 5. 自定义 LLM

```python
def custom_llm(prompt: str) -> str:
    """自定义 LLM 调用函数"""
    # 调用你的 LLM API
    response = your_api.call(prompt)
    return response

# 使用自定义函数
from api_topology import TopologyService

service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=custom_llm  # 传入函数
)
```

## 模型选择

系统会自动检测模型：

1. **Qwen**: 检测到 `dashscope` URL，使用 `qwen-plus`
2. **DeepSeek**: 检测到 `deepseek` URL，使用 `deepseek-chat`
3. **其他**: 默认使用 `gpt-4`

### 手动指定模型

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="sk-...",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 设置默认模型
llm_client.default_model = "qwen-max"
```

## 完整示例

```python
from openai import OpenAI
from api_normalization import NormalizationService
from api_topology import TopologyService

# 1. 配置 Qwen
llm_client = OpenAI(
    api_key="sk-your-qwen-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 2. 规范化 API
norm_service = NormalizationService(use_entity_clustering=True)
result = norm_service.normalize_swagger('erp-server.json')

# 3. 构建拓扑图（启用 LLM）
service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=llm_client,  # 使用 Qwen
    use_entity_inference=True
)

build_result = service.build_graph(result['capabilities'])
print(f"Inferred {build_result['inferred_dependencies']} dependencies")

service.close()
```

## 性能对比

| 提供商 | 速度 | 成本 | 准确率 | 推荐场景 |
|--------|------|------|--------|----------|
| OpenAI GPT-4 | 中 | 高 | 最高 | 生产环境 |
| Qwen Plus | 快 | 低 | 高 | 推荐使用 |
| Qwen Max | 中 | 中 | 最高 | 高精度需求 |
| DeepSeek | 快 | 低 | 高 | 成本敏感 |
| Ollama (本地) | 快 | 免费 | 中 | 开发测试 |

## 故障排查

### 1. API Key 错误

```
Error: Incorrect API key provided
```

解决：检查 API Key 是否正确，是否有权限。

### 2. 网络超时

```
Error: Request timed out
```

解决：检查网络连接，或增加超时时间（默认 30 秒）。

### 3. 模型不存在

```
Error: Model not found
```

解决：手动指定正确的模型名称：

```python
llm_client.default_model = "qwen-plus"
```

### 4. 自动降级

如果 LLM 失败，系统会自动降级到传统推断方法：

```
[LLM] Error: LLM API unavailable
[LLM] Auto-fallback enabled - will use other inference methods
```

这是正常行为，系统会继续工作。

## 环境变量配置

```bash
# .env 文件
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

```python
import os
from openai import OpenAI

llm_client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL")
)
```

## 推荐配置

对于大多数场景，推荐使用 Qwen Plus：

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="sk-your-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
# 系统会自动使用 qwen-plus 模型
```

优势：
- 性价比高
- 速度快
- 准确率高
- 支持中文
