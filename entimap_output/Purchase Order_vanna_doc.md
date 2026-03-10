# Purchase Order 实体映射文档

本文档由 EntiMap 自动生成，描述了业务实体与数据库表的映射关系。

## 摘要

- 相关表数量: 3
- 核心表: 1
- 关联表: 2
- 业务字段总数: 37
- 隐藏逻辑字段: 4

## 核心表映射

### erp_purchase_order

**匹配度**: 95/100

**推理说明**: 该表 erp_purchase_order 是 Purchase Order 实体的核心主表：① 完全覆盖 API 所需字段（no、supplierId、orderTime、status），其中 productId 虽在 API 列表中但未在表中出现，推测其属于采购订单明细（应存在于关联表 erp_purchase_order_item 中，非本表职责）；② 包含完整业务属性（金额、数量、税率、定金、入库/退货等）；③ 具备典型技术字段（id、create_time、update_time、tenant_id）和逻辑删除字段（deleted）；④ 主键 id 为内部自增编号，不暴露给前端，符合 technical 定义；⑤ status 为 TINYINT 类型且采样值为 20，结合 ERP 常见设计，推断为枚举状态码；⑥ deleted 字段为 BIT 类型且值为 b'\x00'，明确承担逻辑删除职责；⑦ tenant_id 强制存在，表明系统为多租户架构，属 hidden_logic。综上，该表与 Purchase Order 实体为强核心映射关系。

**业务字段**:
- `no` → API字段: `no`
- `supplier_id`
- `order_time`
- `status` → API字段: `status`
- `total_count`
- `total_price`
- `total_product_price`
- `total_tax_price`
- `discount_percent`
- `discount_price`
- `deposit_price`
- `in_count`
- `return_count`
- `remark`

**技术字段** (仅用于JOIN，不暴露给用户):
- `id`
- `account_id`
- `creator`
- `create_time`
- `updater`
- `update_time`
- `tenant_id`

**隐藏逻辑字段** (SQL中必须过滤):
- `deleted` - 枚举值: {"b'\\x00'": '否（未删除）', "b'\\x01'": '是（已逻辑删除）'}

**关联策略**: 通过 supplier_id 关联到供应商表（如 erp_supplier）；tenant_id 用于多租户隔离，必须在 WHERE 中过滤；deleted = 0 表示未删除，需作为逻辑删除条件

---

## 关联表

### erp_purchase_in

**关联策略**: 通过 order_id 关联到采购订单主表（如 erp_purchase_order），order_no 可用于业务查询对齐；supplier_id 关联供应商表；account_id 关联结算账户表

### erp_purchase_order_items

**关联策略**: 通过 order_id 关联到主采购订单表（如 erp_purchase_order），该表不包含 supplierId、orderTime、status 等核心订单头信息，仅为明细项表

## SQL查询注意事项

### 必须包含的过滤条件

- `deleted`: 在表 erp_purchase_order, erp_purchase_in, erp_purchase_order_items 中必须过滤
- `status`: 在表 erp_purchase_in 中必须过滤

### 枚举值说明

**erp_purchase_order**:
- `status`: {'20': '已确认（或待发货/已审核，需结合业务确认；常见状态码：10=草稿, 20=已提交/已确认, 30=已发货, 40=已完成, 50=已关闭/已取消）'}
- `deleted`: {"b'\\x00'": '否（未删除）', "b'\\x01'": '是（已逻辑删除）'}

**erp_purchase_in**:
- `status`: {'20': '已入库', '10': '待入库', '30': '部分入库', '40': '入库完成'}

**erp_purchase_order_items**:
- `deleted`: {'0': '未删除', '1': '已逻辑删除'}

