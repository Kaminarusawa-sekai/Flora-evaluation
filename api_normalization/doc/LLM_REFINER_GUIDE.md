# LLM Cluster Refiner 使用指南

## 概述

LLM Cluster Refiner 是一个用于处理离散API的后处理模块。在初始聚类后，它会识别小型集群（少于3个API），并使用LLM或基于规则的方法将它们重新分类。

## 功能特性

1. **自动识别离散API**：找出包含1-3个API的小集群
2. **智能分组**：
   - 统计类API（statistics, summary, dashboard）
   - 状态更新API（update-status, update-default-status）
   - 文件操作API（upload, download, export）
   - 简单列表API（simple-list）
3. **多种LLM支持**：
   - OpenAI API（GPT-4等）
   - 本地LLM（Ollama, LM Studio）
   - 基于规则的fallback（无需LLM）

## 快速开始

### 基本使用（无需LLM）

```python
from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner

# 1. 初始聚类
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.85
)

parsed = service.parser.parse('your-swagger.json')
clustered_apis = service.clusterer.cluster(parsed['apis'])

# 2. 应用LLM refiner（使用规则fallback）
refiner = LLMClusterRefiner(
    min_cluster_size=3,
    use_openai=False  # 使用规则fallback
)

refined_apis = refiner.refine(clustered_apis)

# 3. 提取capabilities
capabilities = service.extractor.extract(refined_apis)
```

### 使用OpenAI API

```python
import os

# 设置API key
os.environ['OPENAI_API_KEY'] = 'your-api-key'

refiner = LLMClusterRefiner(
    min_cluster_size=3,
    use_openai=True,
    model='gpt-4'  # 或 'gpt-3.5-turbo'
)

refined_apis = refiner.refine(clustered_apis)
```

### 使用本地LLM（Ollama）

```bash
# 1. 安装并启动Ollama
ollama serve

# 2. 下载模型
ollama pull llama2
```

```python
refiner = LLMClusterRefiner(
    min_cluster_size=3,
    use_openai=False  # 会自动尝试本地LLM
)

refined_apis = refiner.refine(clustered_apis)
```

## 测试示例

运行测试脚本查看效果：

```bash
conda activate flora
python api_normalization/test_llm_refiner.py
```

## 效果展示

### 改进前
```
Scattered clusters (< 3 APIs): 13
- finance-receipt-statistics (1 API)
- stock-record-statistics (1 API)
- stock-statistics (1 API)
- supplier-statistics (1 API)
- upload (1 API)
- update-default-status (2 APIs)
...
```

### 改进后
```
Scattered clusters (< 3 APIs): 7
Improvement: 6 fewer scattered clusters

New groups created:
- Cluster 1000: Statistics Reporting (7 APIs)
  - finance-receipt-statistics/order-time-summary
  - stock-record-statistics/time-summary
  - stock-statistics/summary
  - supplier-statistics/summary
  - finance-payment-statistics/order-time-summary
  - finance-payment-statistics/time-summary
  - overview-statistics/summary

- Cluster 1001: Status Management (2 APIs)
  - warehouse/update-default-status
  - account/update-default-status
```

## 配置参数

### LLMClusterRefiner 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `min_cluster_size` | int | 3 | 小于此大小的集群被视为离散 |
| `use_openai` | bool | False | 是否使用OpenAI API |
| `api_key` | str | None | OpenAI API密钥 |
| `model` | str | "gpt-4" | 使用的模型名称 |

## 规则Fallback逻辑

当LLM不可用时，使用以下规则：

1. **统计类API**：路径包含 `statistics`, `summary`, `dashboard`
2. **简单列表API**：路径包含 `simple-list`
3. **文件操作API**：路径包含 `upload`, `download`, `export`
4. **状态更新API**：路径包含 `update-status`, `update-default-status`
5. **其他**：保持为原子API

## 集成到NormalizationService

你可以将refiner集成到normalization流程中：

```python
from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner

class EnhancedNormalizationService(NormalizationService):
    def __init__(self, use_llm_refiner=True, **kwargs):
        super().__init__(**kwargs)
        self.use_llm_refiner = use_llm_refiner
        if use_llm_refiner:
            self.refiner = LLMClusterRefiner(min_cluster_size=3)

    def normalize_swagger(self, source: str):
        # 原始流程
        parsed = self.parser.parse(source)
        clustered_apis = self.clusterer.cluster(parsed['apis'])

        # 应用LLM refiner
        if self.use_llm_refiner:
            clustered_apis = self.refiner.refine(clustered_apis)

        # 提取capabilities
        capabilities_result = self.extractor.extract(clustered_apis)

        return {
            'capabilities': capabilities_result['capabilities'],
            'statistics': capabilities_result
        }

# 使用
service = EnhancedNormalizationService(use_llm_refiner=True)
result = service.normalize_swagger('erp-server.json')
```

## 输出格式

Refiner会在API对象中添加以下字段：

```python
{
    "method": "GET",
    "path": "/api/statistics/summary",
    "cluster": 1000,  # 新的cluster ID
    "cluster_type": "llm_grouped",  # 或 "llm_merged", "llm_atomic"
    "llm_reason": "Statistics and reporting APIs grouped together",
    "entity_anchor": "statistics",
    ...
}
```

## 性能考虑

- **规则fallback**：毫秒级，适合生产环境
- **本地LLM**：1-5秒，取决于模型大小
- **OpenAI API**：2-10秒，取决于网络和API负载

## 故障排查

### LLM不可用
如果看到 `⚠️ LLM not available, using rule-based fallback analysis...`，说明：
- OpenAI API key未设置或无效
- 本地LLM服务未启动
- 自动使用规则fallback

### 改进效果不明显
- 调整 `min_cluster_size` 参数（默认3）
- 检查API路径命名是否规范
- 考虑自定义规则逻辑

## 下一步

1. 根据你的业务场景调整规则
2. 训练自定义LLM模型
3. 添加更多分组策略
4. 集成到CI/CD流程

## 相关文件

- `llm_cluster_refiner.py` - 主要实现
- `test_llm_refiner.py` - 测试脚本
- `normalization_service.py` - 集成点
