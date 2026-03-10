# 快速开始 - 实体中心聚类

## 一分钟上手

```python
from api_normalization import NormalizationService

# 1. 初始化服务
service = NormalizationService(
    use_entity_clustering=True,  # 使用新的实体聚类
    entity_similarity_threshold=0.85
)

# 2. 解析 API 文档
result = service.normalize_swagger('your-api.json')

# 3. 查看结果
print(f"发现 {result['statistics']['total_capabilities']} 个能力")

for cap in result['capabilities']:
    print(f"\n{cap['name']}")
    print(f"  - APIs: {cap['api_count']}")
    print(f"  - CRUD: {cap['lifecycle']}")
```

## 运行测试

```bash
# 测试 1: 查看实体分组
python api_normalization/test_entity_clustering.py

# 测试 2: 查看最终结果（推荐）
python api_normalization/test_final_result.py

# 测试 3: 完整示例
python api_normalization/example_usage.py
```

## 核心概念

### 什么是实体中心聚类？

将操作**相同业务实体**的 API 聚合在一起：

```
实体: purchase-order
├── POST   /purchase-order/create    (创建)
├── GET    /purchase-order/get       (查询)
├── GET    /purchase-order/page      (列表)
├── PUT    /purchase-order/update    (更新)
└── DELETE /purchase-order/delete    (删除)
```

### 为什么需要它？

**问题：** 很多 API 文档缺少 summary 和 description

**解决：** 通过路径和 Schema 自动识别实体

```python
# 即使没有描述，也能正确聚类
/admin-api/erp/purchase-order/create  → purchase-order
/admin-api/erp/product/update         → product
```

## 实际效果

使用 ERP 系统的 169 个 API 测试：

```
✓ 识别出 39 个能力
✓ 其中 20 个是完整的 CRUD 能力
✓ 平均每个能力包含 4.3 个 API
✓ 聚类质量分数: 68.07/100
```

## 配置参数

### entity_similarity_threshold

控制聚类严格程度：

```python
# 严格模式（更多小簇）
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.90
)

# 推荐模式（平衡）
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.85  # 默认
)

# 宽松模式（更少大簇）
service = NormalizationService(
    use_entity_clustering=True,
    entity_similarity_threshold=0.80
)
```

## 常见问题

### Q: 如何切换回旧的聚类方法？

```python
service = NormalizationService(
    use_entity_clustering=False,  # 使用 DBSCAN
    use_hdbscan=True
)
```

### Q: 适合什么样的 API？

✓ RESTful 风格的 API
✓ 标准 CRUD 操作
✓ 缺少完整文档的 API
✓ ERP/CRM 等业务系统

### Q: 不适合什么样的 API？

✗ RPC 风格的 API
✗ 复杂业务流程 API
✗ 路径命名不规范的 API

## 下一步

- 阅读 [ENTITY_CLUSTERING.md](ENTITY_CLUSTERING.md) 了解详细原理
- 阅读 [IMPROVEMENT_SUMMARY.md](IMPROVEMENT_SUMMARY.md) 了解改进内容
- 查看 `entity_clusterer.py` 源码了解实现细节

## 示例输出

```
Purchase Order Management
├── Resource: purchase-order
├── APIs: 7
├── CRUD: Complete ✓
└── Operations:
    ├── POST   /create
    ├── GET    /get
    ├── GET    /page
    ├── PUT    /update
    └── DELETE /delete

Product Management
├── Resource: product
├── APIs: 6
├── CRUD: Complete ✓
└── Operations:
    ├── POST   /create
    ├── GET    /get
    ├── PUT    /update
    └── DELETE /delete
```

## 技术支持

如有问题，请查看：
1. 测试脚本输出
2. 详细文档
3. 源码注释
