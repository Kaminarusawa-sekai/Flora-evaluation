# LLM Cluster Refiner - 多提供商支持

## 🎉 新功能

LLM Cluster Refiner 现已支持多种LLM提供商，用于优化API聚类中的离散API！

## ✨ 支持的提供商

| 提供商 | 配置难度 | 成本 | 速度 | 推荐场景 |
|--------|---------|------|------|----------|
| 🔧 **rule** | 无需配置 | 免费 | ⚡⚡⚡ | 默认选择，生产环境 |
| 🇨🇳 **qwen** | 简单 | 低 | ⚡⚡ | 国内用户，中文API |
| 💻 **deepseek** | 简单 | 低 | ⚡⚡ | 代码分析，性价比高 |
| 🏠 **ollama** | 中等 | 免费 | ⚡ | 隐私保护，离线使用 |
| 🤖 **zhipu** | 简单 | 中 | ⚡⚡ | 国内用户 |
| 🌐 **openai** | 简单 | 高 | ⚡ | 最佳效果 |
| 🔌 **openai-compatible** | 中等 | 自定义 | 自定义 | 自定义LLM服务 |

## 🚀 快速开始

### 1. 最简单的方式（无需配置）

```python
from api_normalization.llm_cluster_refiner import LLMClusterRefiner

refiner = LLMClusterRefiner(llm_provider="rule")
refined_apis = refiner.refine(clustered_apis)
```

### 2. 使用Qwen（推荐国内用户）

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

### 3. 使用DeepSeek（推荐代码分析）

```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key'

refiner = LLMClusterRefiner(
    llm_provider="deepseek",
    model="deepseek-coder"
)
refined_apis = refiner.refine(clustered_apis)
```

**获取API Key**: https://platform.deepseek.com/

### 4. 使用Ollama（本地免费）

```bash
# 安装并启动Ollama
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

## 📊 实际效果

在 `erp-server.json` 上的测试结果：

```
改进前:
  - 离散集群: 13个 (包含15个API)

改进后:
  - 离散集群: 7个
  - 改进: 减少了6个离散集群 (46%改进)

新创建的分组:
  ✓ Statistics Reporting (7个API)
    - stock-record-statistics/time-summary
    - finance-payment-statistics/order-time-summary
    - supplier-statistics/summary
    - ...

  ✓ Status Management (2个API)
    - warehouse/update-default-status
    - account/update-default-status
```

## 🧪 测试脚本

### 测试所有提供商

```bash
cd /e/Data/Flora-evaluation
python api_normalization/test_llm_providers.py
```

### 运行示例

```bash
python api_normalization/example_llm_refiner.py
```

## 📖 文档

| 文档 | 说明 |
|------|------|
| **QUICKSTART_LLM.md** | 快速开始指南（推荐先看） |
| **LLM_PROVIDERS_GUIDE.md** | 详细的提供商配置 |
| **MULTI_PROVIDER_SUMMARY.md** | 多提供商支持总结 |
| **LLM_REFINER_GUIDE.md** | 完整使用文档 |

## 💡 使用建议

### 场景1: 快速测试/开发
```python
refiner = LLMClusterRefiner(llm_provider="rule")
```
- ✅ 无需配置
- ✅ 响应快速
- ✅ 完全免费

### 场景2: 生产环境（国内）
```python
refiner = LLMClusterRefiner(llm_provider="qwen", model="qwen-plus")
```
- ✅ 中文友好
- ✅ 性价比高（¥0.001-0.01/次）
- ✅ 国内访问快

### 场景3: 代码分析
```python
refiner = LLMClusterRefiner(llm_provider="deepseek", model="deepseek-coder")
```
- ✅ 代码专用模型
- ✅ 性价比高
- ✅ 准确度高

### 场景4: 本地部署/隐私保护
```python
refiner = LLMClusterRefiner(llm_provider="ollama", model="qwen2.5:7b")
```
- ✅ 完全免费
- ✅ 数据不出本地
- ✅ 离线可用

### 场景5: 最佳效果
```python
refiner = LLMClusterRefiner(llm_provider="openai", model="gpt-4")
```
- ✅ 最佳准确度
- ⚠️ 成本较高（$0.03-0.15/次）

## 🔧 配置环境变量

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

## 🛡️ 自动Fallback

所有LLM调用都有自动fallback机制，确保程序稳定运行：

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

## 📦 完整示例

```python
from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner
import os

# 配置API Key（可选）
os.environ['QWEN_API_KEY'] = 'sk-your-key'

# 初始聚类
service = NormalizationService(use_entity_clustering=True)
parsed = service.parser.parse('your-swagger.json')
clustered_apis = service.clusterer.cluster(parsed['apis'])

# 应用LLM refiner
refiner = LLMClusterRefiner(
    llm_provider="qwen",  # 或 "deepseek", "ollama", "rule"
    model="qwen-plus",    # 可选
    min_cluster_size=3
)

refined_apis = refiner.refine(clustered_apis)

# 提取capabilities
capabilities = service.extractor.extract(refined_apis)

print(f"总Capabilities: {len(capabilities['capabilities'])}")
```

## 🔗 获取API Key

- **Qwen**: https://dashscope.console.aliyun.com/
- **DeepSeek**: https://platform.deepseek.com/
- **Zhipu**: https://open.bigmodel.cn/
- **OpenAI**: https://platform.openai.com/

## 💰 成本对比

| 提供商 | 每次处理成本 | 月度成本估算* |
|--------|-------------|--------------|
| rule | 免费 | 免费 |
| ollama | 免费 | 免费 |
| qwen | ¥0.001-0.01 | ¥1-10 |
| deepseek | ¥0.001-0.01 | ¥1-10 |
| zhipu | ¥0.01-0.05 | ¥10-50 |
| openai | $0.03-0.15 | $30-150 |

*假设每天处理10次

## ❓ 常见问题

**Q: 哪个提供商最好？**
A: 取决于你的需求：
- 快速测试: `rule`
- 国内用户: `qwen` 或 `deepseek`
- 隐私保护: `ollama`
- 最佳效果: `openai`

**Q: Rule-based够用吗？**
A: 对于大多数场景已经足够，它能识别常见的API模式。

**Q: 如何切换提供商？**
A: 只需修改 `llm_provider` 参数即可。

**Q: 支持自定义LLM吗？**
A: 支持！使用 `openai-compatible` 提供商。

## 🎯 核心优势

✅ **7种LLM提供商** - 灵活选择
✅ **自动配置** - 从环境变量读取
✅ **自动Fallback** - 保证稳定性
✅ **向后兼容** - 旧代码仍可用
✅ **完整文档** - 详细的使用指南
✅ **生产就绪** - 已测试验证

## 🚦 开始使用

1. 选择适合你的LLM提供商
2. 配置API Key（如需要）
3. 运行测试脚本验证
4. 集成到你的工作流程

```bash
# 测试
python api_normalization/test_llm_providers.py

# 运行示例
python api_normalization/example_llm_refiner.py
```

## 📝 更新日志

### v2.0 - 多提供商支持
- ✨ 新增6种LLM提供商支持
- 🔧 改进API设计，更灵活的配置
- 📖 完善文档和示例
- 🛡️ 增强错误处理和fallback机制
- ✅ 全面测试验证

### v1.0 - 初始版本
- ✨ 基础LLM cluster refiner
- 🔧 Rule-based fallback
- 📖 基础文档

---

**环境**: conda activate flora
**测试通过**: ✅
**生产就绪**: ✅
