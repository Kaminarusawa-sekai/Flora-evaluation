# LLM Provider 配置指南

## 支持的LLM提供商

LLM Cluster Refiner 现在支持多种LLM提供商：

### 1. Rule-based (默认，无需LLM)
```python
refiner = LLMClusterRefiner(
    llm_provider="rule",
    min_cluster_size=3
)
```

### 2. OpenAI
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'

refiner = LLMClusterRefiner(
    llm_provider="openai",
    model="gpt-4",  # 或 "gpt-3.5-turbo"
    min_cluster_size=3
)
```

### 3. 阿里云通义千问 (Qwen)
```python
import os
os.environ['QWEN_API_KEY'] = 'sk-...'

refiner = LLMClusterRefiner(
    llm_provider="qwen",
    model="qwen-plus",  # 或 "qwen-turbo", "qwen-max"
    min_cluster_size=3
)
```

**获取API Key**: https://dashscope.console.aliyun.com/

**可用模型**:
- `qwen-turbo`: 快速响应
- `qwen-plus`: 平衡性能
- `qwen-max`: 最强性能

### 4. DeepSeek
```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-...'

refiner = LLMClusterRefiner(
    llm_provider="deepseek",
    model="deepseek-chat",  # 或 "deepseek-coder"
    min_cluster_size=3
)
```

**获取API Key**: https://platform.deepseek.com/

**可用模型**:
- `deepseek-chat`: 通用对话模型
- `deepseek-coder`: 代码专用模型（推荐用于API分析）

### 5. 智谱AI (GLM)
```python
import os
os.environ['ZHIPU_API_KEY'] = '...'

refiner = LLMClusterRefiner(
    llm_provider="zhipu",
    model="glm-4",  # 或 "glm-3-turbo"
    min_cluster_size=3
)
```

**获取API Key**: https://open.bigmodel.cn/

**可用模型**:
- `glm-4`: 最新版本
- `glm-3-turbo`: 快速版本

**注意**: 需要安装 `pip install zhipuai`

### 6. Ollama (本地部署)
```bash
# 安装Ollama
# Windows: 下载 https://ollama.ai/download
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 下载模型
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
ollama pull deepseek-coder:6.7b
```

```python
refiner = LLMClusterRefiner(
    llm_provider="ollama",
    model="qwen2.5:7b",  # 或其他已下载的模型
    min_cluster_size=3
)
```

**推荐模型**:
- `qwen2.5:7b`: 通义千问2.5，中文友好
- `llama3.1:8b`: Meta Llama 3.1
- `deepseek-coder:6.7b`: DeepSeek代码模型

### 7. OpenAI兼容API (自定义端点)
```python
refiner = LLMClusterRefiner(
    llm_provider="openai-compatible",
    api_key="your-key",
    api_base="http://your-api-endpoint/v1",
    model="your-model-name",
    min_cluster_size=3
)
```

适用于：
- LM Studio
- vLLM
- FastChat
- 其他OpenAI兼容服务

## 完整示例

### 使用Qwen（推荐国内用户）

```python
from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner
import os

# 设置API Key
os.environ['QWEN_API_KEY'] = 'sk-your-qwen-api-key'

# 初始聚类
service = NormalizationService(use_entity_clustering=True)
parsed = service.parser.parse('erp-server.json')
clustered_apis = service.clusterer.cluster(parsed['apis'])

# 使用Qwen进行优化
refiner = LLMClusterRefiner(
    llm_provider="qwen",
    model="qwen-plus",
    min_cluster_size=3
)

refined_apis = refiner.refine(clustered_apis)

# 提取capabilities
capabilities = service.extractor.extract(refined_apis)
```

### 使用DeepSeek Coder（推荐代码分析）

```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-deepseek-key'

refiner = LLMClusterRefiner(
    llm_provider="deepseek",
    model="deepseek-coder",  # 代码专用模型
    min_cluster_size=3
)

refined_apis = refiner.refine(clustered_apis)
```

### 使用本地Ollama（免费，无需API Key）

```python
# 确保Ollama正在运行
# 终端运行: ollama serve

refiner = LLMClusterRefiner(
    llm_provider="ollama",
    model="qwen2.5:7b",  # 或你已下载的模型
    min_cluster_size=3
)

refined_apis = refiner.refine(clustered_apis)
```

## 性能对比

| 提供商 | 速度 | 成本 | 中文支持 | 推荐场景 |
|--------|------|------|----------|----------|
| Rule-based | ⚡⚡⚡ | 免费 | ✅ | 快速测试，生产环境 |
| Ollama | ⚡⚡ | 免费 | ✅ | 本地部署，隐私保护 |
| Qwen | ⚡⚡ | 低 | ✅✅ | 国内用户，中文API |
| DeepSeek | ⚡⚡ | 低 | ✅ | 代码分析，性价比高 |
| Zhipu GLM | ⚡⚡ | 中 | ✅✅ | 国内用户 |
| OpenAI | ⚡ | 高 | ✅ | 最佳效果 |

## 环境变量配置

创建 `.env` 文件：

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Qwen (阿里云)
QWEN_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# Zhipu AI
ZHIPU_API_KEY=...
```

在代码中加载：

```python
from dotenv import load_dotenv
load_dotenv()

# 现在可以直接使用，无需手动设置
refiner = LLMClusterRefiner(llm_provider="qwen")
```

## 错误处理

所有LLM调用都有自动fallback机制：

```
LLM调用失败 → 自动使用规则引擎 → 保证程序正常运行
```

示例输出：
```
Error calling Qwen: Connection timeout
⚠️  LLM not available, using rule-based fallback analysis...
  Created 2 new groups
  Kept 6 APIs as atomic
```

## 成本估算

### API调用成本（每次refine）

假设处理15个离散API：

- **Qwen-plus**: ¥0.001 - ¥0.01
- **DeepSeek**: ¥0.001 - ¥0.01
- **Zhipu GLM-4**: ¥0.01 - ¥0.05
- **OpenAI GPT-4**: $0.03 - $0.15
- **Ollama**: 免费（本地运行）
- **Rule-based**: 免费

### 推荐策略

1. **开发测试**: 使用 `rule` 或 `ollama`
2. **生产环境**: 使用 `qwen` 或 `deepseek`（性价比高）
3. **最佳效果**: 使用 `openai` 的 `gpt-4`

## 故障排查

### Qwen连接失败
```bash
# 检查网络
curl https://dashscope.aliyuncs.com

# 检查API Key
echo $QWEN_API_KEY
```

### Ollama无法连接
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 启动服务
ollama serve

# 查看已下载模型
ollama list
```

### DeepSeek API限流
```python
# 添加重试逻辑
import time

for attempt in range(3):
    try:
        refined_apis = refiner.refine(clustered_apis)
        break
    except Exception as e:
        if "rate limit" in str(e).lower():
            time.sleep(2 ** attempt)  # 指数退避
        else:
            raise
```

## 下一步

1. 选择适合你的LLM提供商
2. 获取API Key或安装本地模型
3. 运行测试脚本验证配置
4. 集成到你的工作流程

## 相关链接

- **Qwen**: https://help.aliyun.com/zh/dashscope/
- **DeepSeek**: https://platform.deepseek.com/docs
- **Zhipu**: https://open.bigmodel.cn/dev/api
- **Ollama**: https://ollama.ai/
- **OpenAI**: https://platform.openai.com/docs
