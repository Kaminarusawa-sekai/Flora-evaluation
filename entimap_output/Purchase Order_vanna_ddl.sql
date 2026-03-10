-- Purchase Order 相关表结构

-- erp_purchase_order (匹配度: 95)
-- 该表 erp_purchase_order 是 Purchase Order 实体的核心主表：① 完全覆盖 API 所需字段（no、supplierId、orderTime、status），其中 productId 虽在 API 列表中但未在表中出现，推测其属于采购订单明细（应存在于关联表 erp_purchase_order_item 中，非本表职责）；② 包含完整业务属性（金额、数量、税率、定金、入库/退货等）；③ 具备典型技术字段（id、create_time、update_time、tenant_id）和逻辑删除字段（deleted）；④ 主键 id 为内部自增编号，不暴露给前端，符合 technical 定义；⑤ status 为 TINYINT 类型且采样值为 20，结合 ERP 常见设计，推断为枚举状态码；⑥ deleted 字段为 BIT 类型且值为 b'\x00'，明确承担逻辑删除职责；⑦ tenant_id 强制存在，表明系统为多租户架构，属 hidden_logic。综上，该表与 Purchase Order 实体为强核心映射关系。

-- erp_purchase_in (匹配度: 72)
-- 该表名为 erp_purchase_in（采购入库表），表注释明确为'ERP 采购入库表'，属于采购订单的下游执行环节，记录采购订单的实际入库动作及财务明细，而非采购订单本身。API中要求的 Purchase Order 实体字段（no, supplierId, orderTime, status, productId）仅部分匹配：no 对应入库单号（非采购单号），supplier_id 和 status 存在但语义层级不同（此处 status 是入库状态而非采购单状态），orderTime 在 API 中指采购时间，而表中 in_time 是入库时间，order_no 字段存在但未在 API 列表中直接暴露；关键缺失字段 productId（产品编号）完全未出现在该表中，说明该表不承载采购明细（产品维度），需依赖关联明细表（如 erp_purchase_in_item）。此外，存在大量财务计算字段（total_price、payment_price 等）、逻辑删除字段 deleted、租户字段 tenant_id、审计字段 create_time/update_time 等 technical/hidden_logic 字段，进一步表明其为支撑性业务过程表，非 Purchase Order 的核心主表。因此判定为 association（关联/过程表），与 Purchase Order 实体构成 '1:N 入库动作' 关系，而非实体主表。

-- erp_purchase_order_items (匹配度: 65)
-- 该表名为 erp_purchase_order_items，注释为'ERP 采购订单项表'，且字段中仅含 order_id（非 no）、product_id（对应API的 productId），缺少 API 中明确要求的 supplierId、orderTime、status 等采购订单头级属性；采样数据中 order_id=18/19 为外键引用，表明其为从属明细表；所有金额、数量、税率等字段均属于订单行项目维度，而非订单整体维度；deleted 字段用于逻辑删除控制，tenant_id 用于多租户隔离，create_time/update_time/creator/updater 为通用审计字段，均不暴露于API；因此该表是 Purchase Order 实体的关联明细表（association），不是核心主表（core），与业务实体存在弱直接映射关系，需通过 JOIN 主订单表才能完整支撑 Purchase Order 的 CRUD 功能。

