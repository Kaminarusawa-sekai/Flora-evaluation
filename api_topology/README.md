# API Topology Service

构建和查询基于智能字段匹配的 API 依赖关系图。

## 核心功能

### 1. 实体标准化 (Entity Canonicalization)
将不同命名的字段映射到标准实体：
- `user_id`, `uid`, `u_id` → `USER_ID`
- 支持规则匹配和 LLM 增强

### 2. 语义向量匹配
使用 SentenceTransformer 计算字段描述的语义相似度，识别同义不同名的字段。

### 3. 多因子评分
- **实体匹配** (40%): 最高优先级
- **名称相似度** (30%): Levenshtein 距离
- **语义相似度** (15%): 描述向量匹配
- **参数位置** (10%): Path > Query > Body
- **聚类加成** (5%): 同 capability 加分

### 4. 嵌套对象支持
自动展开 JSON Schema，支持 `user.id`, `items[].id` 等路径。

### 5. 转换检测
标记需要逻辑转换的字段（签名、加密、聚合等）。

### 6. 路径评分与约束
```
Score = Σ(edge_scores) / (path_length ^ 1.2)
```
支持按 `required_fields` 过滤路径。

## 安装

```bash
pip install python-Levenshtein neo4j sentence-transformers
```

## 使用示例

```python
from api_topology import TopologyService

service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    llm_client=your_llm_client  # 可选
)

# 支持嵌套 schema
capabilities = [{
    "apis": [{
        "response_schema": {
            "properties": {
                "user": {"properties": {"id": {"type": "string"}}}
            }
        }
    }]
}]

result = service.build_graph(capabilities)
paths = service.find_paths("api1", "api2", required_fields=["user_id"])
```

## 置信度分级

- **CERTAIN** (≥0.9): 确定依赖
- **PROBABLE** (0.7-0.9): 可能依赖
- **WEAK** (<0.7): 不建边

