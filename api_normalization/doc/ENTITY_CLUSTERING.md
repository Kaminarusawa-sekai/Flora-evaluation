# Entity-Centric API Clustering

## 概述

新的实体中心聚类算法实现了**高内聚低耦合**的 API 分组策略，专注于将操作相同业务实体的 API 聚合在一起。

## 核心策略

### 1. 业务锚点提取 (Business Anchor Extraction)

从 API 路径中提取核心业务实体：

```
/admin-api/erp/purchase-order/create  → purchase-order
/admin-api/erp/product/update         → product
/api/v1/user/order/list               → order
```

**逻辑：**
- 过滤噪声词（api, v1, service, rest 等）
- 识别并跳过动作词（create, update, delete, list 等）
- 提取最后一个有意义的名词作为实体锚点

### 2. Schema 区分：实体 vs 引用

**响应体（Response Body）决定归属：**
- 如果接口返回完整的 `User` 对象 → 属于"用户管理"
- 如果接口仅在参数中传递 `user_id`，但返回 `Order` 对象 → 属于"订单管理"

**权重分配：**
- Response Schema: 40%（决定接口交付的内容）
- Path Anchor: 50%（业务实体标识）
- HTTP Method: 10%（操作类型）

### 3. 约束性层次聚类 (Constrained Hierarchical Clustering)

使用严格的相似度阈值（默认 0.85）确保：
- 每个簇都是"纯度极高"的原子能力块
- 避免过度聚合
- 保持 CRUD 闭环完整性

### 4. 原子能力名片 (Atomic Capability Card)

聚类结果示例：

```
Capability: Purchase Order Management
├── POST   /purchase-order/create
├── GET    /purchase-order/get
├── GET    /purchase-order/page
├── PUT    /purchase-order/update
└── DELETE /purchase-order/delete
CRUD: Complete ✓

Capability: Product Management
├── POST   /product/create
├── GET    /product/get
├── PUT    /product/update
└── DELETE /product/delete
CRUD: Complete ✓
```

## 使用方法

### 基本使用

```python
from api_normalization import NormalizationService

# 初始化服务（启用实体聚类）
service = NormalizationService(
    use_entity_clustering=True,          # 使用实体中心聚类
    entity_similarity_threshold=0.85,    # 严格的相似度阈值
    use_prance=True,
    enable_evaluation=True
)

# 解析 Swagger 文档
result = service.normalize_swagger('your-api.json')

# 查看能力
for cap in result['capabilities']:
    print(f"{cap['name']}: {cap['api_count']} APIs")
    if cap['lifecycle']['is_complete_crud']:
        print("  ✓ Complete CRUD")
```

### 与旧方法对比

```python
# 旧方法：基于 DBSCAN 的语义聚类
service_old = NormalizationService(
    use_entity_clustering=False,  # 使用旧的 DBSCAN
    use_hdbscan=True
)

# 新方法：实体中心聚类
service_new = NormalizationService(
    use_entity_clustering=True,   # 使用新的实体聚类
    entity_similarity_threshold=0.85
)
```

## 优势

### 1. 高内聚
- 同一实体的所有操作聚合在一起
- 自动识别 CRUD 完整性
- 便于 Agent 组合调用

### 2. 低耦合
- 不同实体严格分离
- 避免"多重归属"污染
- 清晰的能力边界

### 3. 无需描述
- 即使 API 没有 summary/description
- 仍能通过路径和 schema 准确聚类
- 适用于自动生成的 API 文档

## 测试结果

使用 ERP 系统的 169 个 API 进行测试：

```
Total APIs: 169
Total Capabilities: 39
- Complete CRUD Capabilities: 20
- Incomplete Capabilities: 19

Examples of Complete CRUD:
✓ Purchase Order Management (7 APIs)
✓ Product Management (6 APIs)
✓ Customer Management (6 APIs)
✓ Supplier Management (6 APIs)
✓ Warehouse Management (6 APIs)
...

Clustering Quality:
- Overall Score: 68.07/100
- Silhouette Score: 0.0401
- Average Cluster Size: 4.3
```

## 配置参数

### entity_similarity_threshold (默认: 0.85)

控制聚类的严格程度：
- **0.90+**: 极严格，可能产生过多小簇
- **0.85**: 推荐值，平衡内聚和粒度
- **0.80-**: 较宽松，可能过度聚合

### response_weight / request_weight

控制 schema 权重分配：
- **response_weight (默认: 0.7)**: 响应体权重
- **request_weight (默认: 0.3)**: 请求体权重

## 适用场景

### ✓ 适合使用实体聚类

1. **RESTful API**: 遵循资源命名规范
2. **CRUD 操作**: 标准的增删改查接口
3. **缺少描述**: API 文档不完整
4. **ERP/CRM 系统**: 实体关系清晰

### ✗ 不适合使用实体聚类

1. **RPC 风格 API**: 动作导向而非资源导向
2. **复杂业务流程**: 跨多个实体的事务
3. **高度定制化**: 路径命名不规范

## 文件说明

- `entity_clusterer.py`: 实体中心聚类器实现
- `semantic_clusterer.py`: 旧的语义聚类器（保留）
- `normalization_service.py`: 服务入口，支持两种聚类方式
- `test_entity_clustering.py`: 测试脚本，查看实体分组
- `test_final_result.py`: 最终结果展示

## 未来改进

1. **动态阈值**: 根据 API 数量自动调整相似度阈值
2. **实体关系**: 识别实体间的依赖关系（如 Order → OrderItem）
3. **多语言支持**: 支持中文实体名称识别
4. **Schema 深度分析**: 更智能的 schema 相似度计算
