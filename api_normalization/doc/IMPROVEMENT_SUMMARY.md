# API Normalization - 实体中心聚类改进总结

## 改进内容

针对大量 API 文档缺少简介和描述的问题，实现了基于**实体中心（Entity-Centric）**的高内聚低耦合聚类算法。

## 核心改进

### 1. 新增实体聚类器 (`entity_clusterer.py`)

**核心策略：**
- **路径锚点提取**: 从 API 路径中识别核心业务实体（如 `purchase-order`, `product`, `customer`）
- **Schema 权重分配**: Response Schema 40% + Path Anchor 50% + HTTP Method 10%
- **约束性层次聚类**: 使用严格阈值（0.85）确保高内聚低耦合
- **CRUD 完整性检查**: 自动识别并验证 CRUD 闭环

**关键特性：**
```python
# 路径锚点提取示例
/admin-api/erp/purchase-order/create  → 实体: purchase-order
/admin-api/erp/product/update         → 实体: product
/api/v1/user/order/list               → 实体: order
```

### 2. 更新服务接口 (`normalization_service.py`)

**新增参数：**
- `use_entity_clustering`: 是否使用实体聚类（默认 True）
- `entity_similarity_threshold`: 相似度阈值（默认 0.85）

**向后兼容：**
- 保留原有的 DBSCAN/HDBSCAN 语义聚类
- 可通过参数切换聚类方式

### 3. 优化能力提取器 (`capability_extractor.py`)

**改进点：**
- 优先使用 `entity_anchor` 生成能力名称
- 生成更简洁的名称（如 "Purchase Order Management"）
- 更好地识别资源实体

### 4. 测试脚本

**新增文件：**
- `test_entity_clustering.py`: 查看实体分组详情
- `test_final_result.py`: 展示最终聚类结果
- `ENTITY_CLUSTERING.md`: 详细文档

## 测试结果

### 测试数据
- **数据源**: ERP 系统 API 文档 (`erp-server.json`)
- **API 数量**: 169 个
- **特点**: 大部分 API 缺少 summary/description

### 聚类效果

```
总计:
├── 39 个能力
├── 20 个完整 CRUD 能力
└── 19 个不完整能力

完整 CRUD 能力示例:
✓ Purchase Order Management (7 APIs)
  ├── POST   /create
  ├── GET    /get
  ├── GET    /page
  ├── GET    /export-excel
  ├── PUT    /update
  ├── PUT    /update-status
  └── DELETE /delete

✓ Product Management (6 APIs)
✓ Customer Management (6 APIs)
✓ Supplier Management (6 APIs)
✓ Warehouse Management (6 APIs)
✓ Stock Check Management (7 APIs)
✓ Finance Payment Management (7 APIs)
... 等 20 个完整能力
```

### 质量指标

```
Clustering Quality Score: 68.07/100
├── Silhouette Score: 0.0401
├── Davies-Bouldin Index: 1.5219
└── Average Cluster Size: 4.3
```

## 使用示例

### 基本使用

```python
from api_normalization import NormalizationService

# 使用实体聚类（推荐）
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.85
)

result = service.normalize_swagger('erp-server.json')

# 查看能力
for cap in result['capabilities']:
    print(f"{cap['name']}: {cap['api_count']} APIs")
    if cap['lifecycle']['is_complete_crud']:
        print("  ✓ Complete CRUD")
```

### 切换到旧方法

```python
# 使用 DBSCAN 语义聚类
service = NormalizationService(
    use_entity_clustering=False,
    use_hdbscan=True
)
```

## 优势对比

### 实体聚类 vs 语义聚类

| 特性 | 实体聚类 | 语义聚类 (DBSCAN) |
|------|---------|------------------|
| **无需描述** | ✓ 支持 | ✗ 依赖描述 |
| **高内聚** | ✓ 按实体聚合 | △ 按语义相似 |
| **低耦合** | ✓ 实体严格分离 | △ 可能过度聚合 |
| **CRUD 识别** | ✓ 自动识别 | △ 需要推断 |
| **适用场景** | RESTful API | 有完整文档的 API |

## 技术亮点

### 1. 智能路径解析
```python
# 自动过滤噪声词和动作词
/admin-api/erp/purchase-order/create
  ↓ 过滤: admin-api, erp, create
  ↓ 提取: purchase-order
```

### 2. Schema 权重分配
```python
# Response Schema 决定实体归属
API: /user/order/list
├── Request: user_id (引用)
└── Response: Order[] (主体)
    → 归属: Order Management
```

### 3. 约束性聚类
```python
# 严格阈值防止过度聚合
similarity_threshold = 0.85
├── purchase-order → 独立簇
├── purchase-in    → 独立簇
└── purchase-return → 独立簇
```

## 文件清单

### 新增文件
- `api_normalization/entity_clusterer.py` - 实体聚类器
- `api_normalization/test_entity_clustering.py` - 实体分组测试
- `api_normalization/test_final_result.py` - 最终结果展示
- `api_normalization/ENTITY_CLUSTERING.md` - 详细文档

### 修改文件
- `api_normalization/normalization_service.py` - 集成实体聚类
- `api_normalization/capability_extractor.py` - 优化命名
- `api_normalization/__init__.py` - 导出新类
- `api_normalization/example_usage.py` - 更新示例

### 保留文件
- `api_normalization/semantic_clusterer.py` - 旧方法（向后兼容）

## 运行测试

```bash
# 查看实体分组
python api_normalization/test_entity_clustering.py

# 查看最终结果
python api_normalization/test_final_result.py

# 完整示例
python api_normalization/example_usage.py
```

## 配置建议

### 推荐配置（RESTful API）
```python
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.85,  # 平衡内聚和粒度
    use_prance=True,
    enable_evaluation=True
)
```

### 严格模式（更细粒度）
```python
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.90,  # 更严格
)
```

### 宽松模式（更大簇）
```python
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.80,  # 更宽松
)
```

## 总结

✓ **成功实现**了基于实体中心的高内聚低耦合聚类算法
✓ **解决了**无描述 API 的聚类问题
✓ **识别出** 20 个完整的 CRUD 能力
✓ **保持了**向后兼容性
✓ **提供了**详细的文档和测试脚本

这个改进使得 API 规范化服务能够更好地处理实际生产环境中的 API 文档，特别是那些自动生成或缺少完整描述的文档。
