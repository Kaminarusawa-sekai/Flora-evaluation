# 依赖安装指南

## 基础依赖

LLM Cluster Refiner 的基础功能（rule-based模式）无需额外依赖。

## LLM提供商依赖

### 1. OpenAI / Qwen / DeepSeek

这些提供商都使用OpenAI兼容的API，需要安装 `openai` 包：

```bash
# 在conda环境中安装
conda activate flora
pip install openai

# 或使用conda安装
conda install openai -c conda-forge
```

**支持的提供商**:
- OpenAI (GPT-3.5, GPT-4)
- Qwen (通义千问)
- DeepSeek
- OpenAI-compatible APIs

### 2. Zhipu AI (可选)

Zhipu AI有专用的SDK，但也可以使用OpenAI兼容模式：

```bash
# 选项1: 使用专用SDK (推荐)
pip install zhipuai

# 选项2: 使用OpenAI兼容模式 (只需安装openai)
pip install openai
```

### 3. Ollama

Ollama需要本地安装服务：

**Windows**:
1. 下载安装包: https://ollama.ai/download
2. 安装后自动启动服务
3. 下载模型:
```bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
ollama pull deepseek-coder:6.7b
```

**Linux/Mac**:
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 下载模型
ollama pull qwen2.5:7b
```

### 4. Rule-based (默认)

无需任何依赖，开箱即用。

## 完整安装步骤

### 方案1: 最小安装（推荐）

```bash
conda activate flora
# 无需额外安装，使用rule-based模式
```

### 方案2: 支持国内LLM（推荐国内用户）

```bash
conda activate flora
pip install openai

# 配置API Key
export QWEN_API_KEY="sk-your-key"
# 或
export DEEPSEEK_API_KEY="sk-your-key"
```

### 方案3: 本地部署（推荐隐私保护）

```bash
# 1. 安装Ollama
# Windows: 下载 https://ollama.ai/download
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 2. 启动服务
ollama serve

# 3. 下载模型
ollama pull qwen2.5:7b

# 4. 无需其他Python依赖
```

### 方案4: 完整安装（支持所有提供商）

```bash
conda activate flora

# 安装OpenAI SDK
pip install openai

# 安装Zhipu SDK (可选)
pip install zhipuai

# 安装Ollama (可选，需要单独下载)
# 见上面的Ollama安装步骤
```

## 验证安装

### 测试基础功能（rule-based）

```python
from api_normalization.llm_cluster_refiner import LLMClusterRefiner

refiner = LLMClusterRefiner(llm_provider="rule")
print("Rule-based mode: OK")
```

### 测试OpenAI SDK

```python
try:
    import openai
    print("OpenAI SDK: OK")
except ImportError:
    print("OpenAI SDK: Not installed")
    print("Install with: pip install openai")
```

### 测试Zhipu SDK

```python
try:
    import zhipuai
    print("Zhipu SDK: OK")
except ImportError:
    print("Zhipu SDK: Not installed (optional)")
    print("Install with: pip install zhipuai")
```

### 测试Ollama服务

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 查看已下载的模型
ollama list
```

### 运行完整测试

```bash
cd /e/Data/Flora-evaluation
python api_normalization/test_llm_providers.py
```

## 常见问题

### Q: 提示 "No module named 'openai'"

**解决方案**:
```bash
conda activate flora
pip install openai
```

### Q: Qwen/DeepSeek连接失败

**可能原因**:
1. 未安装openai包
2. API Key未设置或错误
3. 网络连接问题

**解决方案**:
```bash
# 1. 安装openai
pip install openai

# 2. 检查API Key
echo $QWEN_API_KEY

# 3. 测试网络
curl https://dashscope.aliyuncs.com
```

### Q: Ollama无法连接

**可能原因**:
1. Ollama服务未启动
2. 端口被占用
3. 未下载模型

**解决方案**:
```bash
# 1. 启动服务
ollama serve

# 2. 检查服务
curl http://localhost:11434/api/tags

# 3. 下载模型
ollama pull qwen2.5:7b
```

### Q: 所有LLM都失败了怎么办？

不用担心！系统会自动fallback到rule-based模式，保证程序正常运行：

```
Error calling Qwen: Connection timeout
⚠️  LLM not available, using rule-based fallback analysis...
  Created 2 new groups
  Kept 6 APIs as atomic
```

## 推荐配置

### 开发环境
```bash
# 最小安装，使用rule-based
conda activate flora
# 无需额外安装
```

### 生产环境（国内）
```bash
conda activate flora
pip install openai

# 配置环境变量
export QWEN_API_KEY="sk-your-key"
```

### 本地部署
```bash
# 安装Ollama
# Windows: https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

ollama serve
ollama pull qwen2.5:7b
```

## 依赖版本

推荐的包版本：

```txt
openai>=1.0.0
zhipuai>=2.0.0  # 可选
requests>=2.25.0  # 通常已安装
```

## 环境变量

创建 `.env` 文件或设置环境变量：

```bash
# Qwen
export QWEN_API_KEY="sk-..."

# DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# Zhipu
export ZHIPU_API_KEY="..."

# OpenAI
export OPENAI_API_KEY="sk-..."
```

## 下一步

1. 根据需求选择安装方案
2. 安装相应的依赖
3. 配置API Key（如需要）
4. 运行测试验证
5. 开始使用

```bash
# 测试安装
python api_normalization/test_llm_providers.py

# 运行示例
python api_normalization/example_llm_refiner.py
```
