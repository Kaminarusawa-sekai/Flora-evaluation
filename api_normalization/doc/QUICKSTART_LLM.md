# LLM Cluster Refiner - 快速开始

## 概述

LLM Cluster Refiner 现已支持多种LLM提供商，用于优化API聚类结果。

## 支持的提供商

| 提供商 | 需要配置 | 成本 | 推荐场景 |
|--------|---------|------|----------|
| **rule** | ❌ | 免费 | 默认选择，生产环境 |
| **qwen** | ✅ API Key | 低 | 国内用户，中文API |
| **deepseek** | ✅ API Key | 低 | 代码分析，性价比高 |
| **ollama** | ✅ 本地安装 | 免费 | 隐私保护，离线使用 |
| **zhipu** | ✅ API Key | 中 | 国内用户 |
| **openai** | ✅ API Key | 高 | 最佳效果 |

## 快速开始

### 1. 使用Rule-based (推荐，无需配置)

```python
from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner

# 初始聚类
service = NormalizationService(use_entity_clustering=True)
parsed = service.parser.parse('your-swagger.json')
clustered_apis = service.clusterer.cluster(parsed['apis'])

# 应用refiner
refiner = LLMClusterRefiner(llm_provider="rule")
refined_apis = refiner.refine(clustered_apis)

# 提取capabilities
capabilities = service.extractor.extract(refined_apis)
```

### 2. 使用Qwen (推荐国内用户)

```python
import os
os.environ['QWEN_API_KEY'] = 'sk-your-key'

refiner = LLMClusterRefiner(
    llm_provider="qwen",
    model="qwen-plus"
)
refined_apis = refiner.refine(clustered_apis)
```

**获取API Key**: https://dashscope.console.aliyun.com/

### 3. 使用DeepSeek (推荐代码分析)

```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key'

refiner = LLMClusterRefiner(
    llm_provider="deepseek",
    model="deepseek-coder"  # 代码专用模型
)
refined_apis = refiner.refine(clustered_apis)
```

**获取API Key**: https://platform.deepseek.com/

### 4. 使用Ollama (本地，免费)

```bash
# 安装Ollama
# Windows: https://ollama.ai/download
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 下载模型
ollama pull qwen2.5:7b
```

```python
refiner = LLMClusterRefiner(
    llm_provider="ollama",
    model="qwen2.5:7b"
)
refined_apis = refiner.refine(clustered_apis)
```

## 运行示例

### 测试所有提供商

```bash
cd /e/Data/Flora-evaluation
python api_normalization/test_llm_providers.py
```

### 运行简单示例

```bash
python api_normalization/example_llm_refiner.py
```

修改 `example_llm_refiner.py` 中的配置来切换提供商：

```python
# 选项1: Rule-based (默认)
LLM_PROVIDER = "rule"
MODEL = None

# 选项2: Qwen
# LLM_PROVIDER = "qwen"
# MODEL = "qwen-plus"
# os.environ['QWEN_API_KEY'] = 'sk-your-key'

# 选项3: DeepSeek
# LLM_PROVIDER = "deepseek"
# MODEL = "deepseek-coder"
# os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key'

# 选项4: Ollama
# LLM_PROVIDER = "ollama"
# MODEL = "qwen2.5:7b"
```

## 实际效果

在 `erp-server.json` 上的测试结果：

```
改进前:
  - 总API数: 169
  - 总集群数: 39
  - 离散集群数: 13 (包含15个API)

改进后:
  - 总集群数: 34
  - 离散集群数: 7
  - 改进: 减少了6个离散集群 (46%改进)

新创建的分组:
  - Statistics Reporting (7个API)
  - Status Management (2个API)
```

## 配置环境变量

创建 `.env` 文件：

```bash
# Qwen (阿里云通义千问)
QWEN_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# Zhipu AI
ZHIPU_API_KEY=...

# OpenAI
OPENAI_API_KEY=sk-...
```

在代码中加载：

```python
from dotenv import load_dotenv
load_dotenv()

# 现在可以直接使用
refiner = LLMClusterRefiner(llm_provider="qwen")
```

## API参数说明

```python
LLMClusterRefiner(
    llm_provider="rule",      # 提供商: rule/qwen/deepseek/ollama/zhipu/openai
    model=None,               # 模型名称 (可选，自动选择)
    api_key=None,             # API密钥 (可选，从环境变量读取)
    api_base=None,            # API端点 (可选，使用默认值)
    min_cluster_size=3        # 小于此大小视为离散集群
)
```

## 故障排查

### 问题1: 提示"No module named 'openai'"

```bash
# 安装openai包
pip install openai
```

### 问题2: Qwen/DeepSeek连接失败

```python
# 检查API Key是否正确
import os
print(os.getenv('QWEN_API_KEY'))

# 测试网络连接
import requests
response = requests.get('https://dashscope.aliyuncs.com')
print(response.status_code)
```

### 问题3: Ollama无法连接

```bash
# 检查服务是否运行
curl http://localhost:11434/api/tags

# 启动服务
ollama serve

# 查看已下载的模型
ollama list
```

### 问题4: 所有LLM都失败

不用担心！系统会自动fallback到rule-based模式：

```
Error calling Qwen: Connection timeout
⚠️  LLM not available, using rule-based fallback analysis...
  Created 2 new groups
  Kept 6 APIs as atomic
```

## 性能对比

| 提供商 | 响应时间 | Token成本 | 准确度 |
|--------|---------|----------|--------|
| rule | < 100ms | 免费 | ⭐⭐⭐ |
| ollama | 1-5s | 免费 | ⭐⭐⭐⭐ |
| qwen | 1-3s | ¥0.001-0.01 | ⭐⭐⭐⭐ |
| deepseek | 1-3s | ¥0.001-0.01 | ⭐⭐⭐⭐ |
| zhipu | 2-4s | ¥0.01-0.05 | ⭐⭐⭐⭐ |
| openai | 2-10s | $0.03-0.15 | ⭐⭐⭐⭐⭐ |

## 推荐配置

### 开发测试
```python
refiner = LLMClusterRefiner(llm_provider="rule")
```

### 生产环境（国内）
```python
refiner = LLMClusterRefiner(
    llm_provider="qwen",
    model="qwen-plus"
)
```

### 本地部署
```python
refiner = LLMClusterRefiner(
    llm_provider="ollama",
    model="qwen2.5:7b"
)
```

### 最佳效果
```python
refiner = LLMClusterRefiner(
    llm_provider="openai",
    model="gpt-4"
)
```

## 文档索引

- **LLM_PROVIDERS_GUIDE.md** - 详细的提供商配置指南
- **LLM_REFINER_GUIDE.md** - 完整使用文档
- **LLM_REFINER_SUMMARY.md** - 实现总结
- **example_llm_refiner.py** - 简单示例
- **test_llm_providers.py** - 提供商测试脚本

## 下一步

1. 选择适合你的LLM提供商
2. 配置API Key或安装本地模型
3. 运行测试脚本验证
4. 集成到你的工作流程

## 常见问题

**Q: 哪个提供商最好？**
A:
- 快速测试/生产环境: `rule`
- 国内用户: `qwen` 或 `deepseek`
- 隐私保护: `ollama`
- 最佳效果: `openai`

**Q: Rule-based够用吗？**
A: 对于大多数场景，rule-based已经足够好，它能识别常见的API模式（statistics、status、upload等）。

**Q: 如何切换提供商？**
A: 只需修改 `llm_provider` 参数，系统会自动处理其他配置。

**Q: 成本如何？**
A:
- Rule/Ollama: 完全免费
- Qwen/DeepSeek: 每次处理约¥0.001-0.01
- OpenAI: 每次处理约$0.03-0.15

**Q: 支持自定义LLM吗？**
A: 支持！使用 `openai-compatible` 提供商，配置自定义 `api_base`。

## 联系与反馈

如有问题或建议，请查看相关文档或提交issue。
