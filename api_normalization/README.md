# API Normalization Service

智能 API 规范化服务，从 Swagger/OpenAPI 文档中提取语义化的能力模型。

## 核心特性

### 1. 增强的 Swagger 解析 (`swagger_parser.py`)
- ✅ 支持本地文件（JSON/YAML）和网页 URL（包括 Apifox 等平台）
- ✅ 使用 `prance` 库自动解析 `$ref` 引用
- ✅ 路径参数模板化（`/user/123` → `/user/{id}`，UUID 识别）
- ✅ 动作谓词提取（从 `operationId` 中提取 `create`, `sync`, `batch` 等）
- ✅ HTML 标签清理和描述增强
- ✅ 参数类型分类（Path/Query/Body/Header）

### 2. 混合聚类策略 (`semantic_clusterer.py`)
- ✅ **Level 1 (Hard)**: 按 Swagger `tags` 强制分组
- ✅ **Level 2 (Soft)**: 小组直接成簇，大组内语义聚类（HDBSCAN/DBSCAN）
- ✅ **Level 3**: 路径相似度细化
- ✅ 动态 `eps` 计算（基于向量距离分布）
- ✅ 噪声回收机制（Noise → Atomic Capability）
- ✅ 增强文本特征（动作谓词加权、路径段、标签）

### 3. Schema 合并与实体生命周期 (`capability_extractor.py`)
- ✅ 统一 Schema 合并（跨多个 API 的请求/响应）
- ✅ 字段读写分离（`read_only` / `write_only`）
- ✅ 必填项推断（仅在所有相关 API 中都必填时标记）
- ✅ CRUD 生命周期识别（Create/Read/Update/Delete）
- ✅ 连通性评分（API 是否形成完整工作流）
- ✅ 典型工作流推断（如：`Create → Read → Update → Delete`）

### 4. 聚类质量评估 (`evaluator.py`)
- ✅ Silhouette Score（簇内相似度）
- ✅ Davies-Bouldin Index（簇间分离度）
- ✅ 噪声比率和簇分布统计
- ✅ 连通性评分（API 工作流完整性）
- ✅ 可解释性输出（为什么 API A 和 B 被分在一起）
- ✅ 自动建议（如何改进聚类质量）

## 快速开始

### 安装依赖

```bash
pip install pyyaml requests scikit-learn numpy

# 可选：更好的聚类效果
pip install hdbscan

# 可选：增强的 Swagger 解析
pip install prance
```

### 基础使用

```python
from api_normalization import NormalizationService

# 初始化服务
service = NormalizationService(
    use_hdbscan=True,        # 使用 HDBSCAN（推荐）
    use_prance=True,         # 使用 prance 解析 $ref
    enable_evaluation=True   # 启用质量评估
)

# 解析本地文件
result = service.normalize_swagger('swagger.json')

# 或解析 URL
result = service.normalize_swagger('https://api.example.com/swagger.json')

# 查看结果
print(f"发现 {result['statistics']['total_capabilities']} 个能力")
print(f"质量评分: {result['evaluation']['quality_score']}")

for cap in result['capabilities']:
    print(f"- {cap['name']}: {cap['api_count']} APIs")
    print(f"  CRUD: {cap['lifecycle']}")
    print(f"  连通性: {cap['connectivity_score']}")
```

### 导出结果

```python
# 导出为 JSON
service.normalize_and_export(
    'swagger.json',
    output_path='output/capabilities.json'
)
```

### 生成能力卡片

```python
# 方式 1: 使用 NormalizationService
card = service.get_capability_card(result['capabilities'][0])
print(card)

# 方式 2: 使用 ClusterEvaluator
from api_normalization import ClusterEvaluator

evaluator = ClusterEvaluator()
card = evaluator.generate_capability_card(result['capabilities'][0])
print(card)
```

## 输出结构

```json
{
  "capabilities": [
    {
      "id": "cap_0",
      "name": "User Management",
      "type": "composite",
      "description": "Capability to create, query, update, delete User resources",
      "resource": "User",
      "primary_action": "create",
      "api_count": 5,
      "apis": [
        {
          "operation_id": "createUser",
          "method": "POST",
          "path": "/api/v1/users",
          "normalized_path": "/api/v1/users",
          "summary": "Create a new user",
          "action_verb": "create"
        }
      ],
      "unified_schema": {
        "properties": {
          "username": {"type": "string"},
          "email": {"type": "string"}
        },
        "required": ["username"],
        "read_only": [],
        "write_only": ["username", "email"]
      },
      "lifecycle": {
        "has_create": true,
        "has_read": true,
        "has_update": true,
        "has_delete": true,
        "is_complete_crud": true
      },
      "connectivity_score": 0.75,
      "typical_workflow": "Create via createUser → Read via getUser → Update via updateUser → Delete via deleteUser"
    }
  ],
  "statistics": {
    "total_apis": 7,
    "total_capabilities": 2,
    "semantic_capabilities": 2,
    "atomic_capabilities": 0
  },
  "evaluation": {
    "quality_score": 75.5,
    "metrics": {
      "silhouette_score": 0.65,
      "davies_bouldin_index": 0.45,
      "total_clusters": 2,
      "noise_ratio": 0.0
    },
    "warnings": [],
    "recommendations": []
  }
}
```

## 高级配置

### 调整聚类参数

```python
service = NormalizationService(
    min_cluster_size=3,              # HDBSCAN 最小簇大小
    min_samples=2,                   # 最小样本数
    path_similarity_threshold=0.8,   # 路径相似度阈值
    use_hdbscan=True                 # 使用 HDBSCAN（推荐）
)
```

### 仅解析不聚类

```python
from api_normalization import SwaggerParser

parser = SwaggerParser(use_prance=True)
parsed = parser.parse('swagger.json')

for api in parsed['apis']:
    print(f"{api['method']} {api['normalized_path']}")
    print(f"  Action: {api['action_verb']}")
    print(f"  Segments: {api['path_segments']}")
```

### 自定义聚类

```python
from api_normalization import SwaggerParser, SemanticClusterer, CapabilityExtractor

parser = SwaggerParser()
clusterer = SemanticClusterer(min_cluster_size=2)
extractor = CapabilityExtractor()

parsed = parser.parse('swagger.json')
clustered = clusterer.cluster(parsed['apis'])
capabilities = extractor.extract(clustered)
```

## 优化建议

### 提高聚类质量

1. **改进 Swagger 文档质量**
   - 添加详细的 `summary` 和 `description`
   - 使用有意义的 `operationId`（如 `createUser` 而非 `api1`）
   - 正确使用 `tags` 分组

2. **调整聚类参数**
   - 小数据集：降低 `min_cluster_size` 到 2
   - 大数据集：提高到 5-10
   - 路径相似度：0.7-0.9 之间调整

3. **使用 HDBSCAN**
   ```bash
   pip install hdbscan
   ```
   HDBSCAN 自动处理不同密度的簇，效果通常优于 DBSCAN。

### 处理特殊场景

**场景 1: 所有 API 都被标记为噪声**
- 原因：`min_cluster_size` 太大或 API 描述太少
- 解决：降低 `min_cluster_size` 或改进文档

**场景 2: 所有 API 聚成一个簇**
- 原因：API 描述过于相似或 `path_similarity_threshold` 太低
- 解决：提高阈值或增加描述差异性

**场景 3: 连通性评分低**
- 原因：API 缺少完整的 CRUD 操作
- 解决：检查是否缺少某些端点

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                  NormalizationService                   │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│SwaggerParser │  │SemanticClust │  │CapabilityExt │
│              │  │erer          │  │ractor        │
│- URL支持     │  │- 混合聚类    │  │- Schema合并  │
│- prance集成  │  │- HDBSCAN     │  │- CRUD识别    │
│- 路径模板化  │  │- 噪声回收    │  │- 连通性评分  │
└──────────────┘  └──────────────┘  └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │ClusterEvalua │
                  │tor           │
                  │- 质量评估    │
                  │- 可解释性    │
                  └──────────────┘
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
