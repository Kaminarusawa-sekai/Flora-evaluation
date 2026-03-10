# 管理后台


**简介**:管理后台


**HOST**:http://172.24.0.9:8080


**联系人**:


**Version**:1.0.0


**接口路径**:/admin-api/erp/v3/api-docs


[TOC]






# 管理后台 - ERP 财务管理统计


## 驾驶舱-付款收款单金额-时间段统计


**接口地址**:`/admin-api/erp/finance-statistics/bill-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinanceTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinanceTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;totalPaymentPrice|付款单金额|number||
|&emsp;&emsp;totalReceiptPrice|收款单金额|number||
|&emsp;&emsp;totalPrice|合计金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"totalPaymentPrice": 888,
			"totalReceiptPrice": 888,
			"totalPrice": 888
		}
	],
	"msg": ""
}
```


## 财务看板-应收应付汇总表-时间段统计


**接口地址**:`/admin-api/erp/finance-statistics/dashboard-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinanceTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinanceTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;totalPaymentPrice|付款单金额|number||
|&emsp;&emsp;totalReceiptPrice|收款单金额|number||
|&emsp;&emsp;totalPrice|合计金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"totalPaymentPrice": 888,
			"totalReceiptPrice": 888,
			"totalPrice": 888
		}
	],
	"msg": ""
}
```


## 资金看板-时间段统计


**接口地址**:`/admin-api/erp/finance-statistics/time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinanceTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinanceTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;totalPaymentPrice|付款单金额|number||
|&emsp;&emsp;totalReceiptPrice|收款单金额|number||
|&emsp;&emsp;totalPrice|合计金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"totalPaymentPrice": 888,
			"totalReceiptPrice": 888,
			"totalPrice": 888
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 采购订单


## 创建采购订单


**接口地址**:`/admin-api/erp/purchase-order/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|supplierId|供应商编号|query|true|string||
|orderTime|采购时间|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|depositPrice|定金金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|订单清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除采购订单


**接口地址**:`/admin-api/erp/purchase-order/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出采购订单 Excel


**接口地址**:`/admin-api/erp/purchase-order/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|orderTime|采购时间|query|false|string||
|remark|备注|query|false|string||
|status|采购状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|inStatus|入库状态|query|false|string||
|returnStatus|退货状态|query|false|string||
|inEnable|是否可入库|query|false|string||
|returnEnable|是否可退货|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得采购订单


**接口地址**:`/admin-api/erp/purchase-order/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpPurchaseOrderRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpPurchaseOrderRespVO|ErpPurchaseOrderRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|采购单编号|string||
|&emsp;&emsp;status|采购状态|integer(int32)||
|&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;orderTime|采购时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;depositPrice|定金金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|订单项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;inCount|采购入库数量|number||
|&emsp;&emsp;returnCount|采购退货数量|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"supplierId": 1724,
		"supplierName": "芋道",
		"accountId": 0,
		"orderTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"depositPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": "",
		"inCount": 100,
		"returnCount": 100
	},
	"msg": ""
}
```


## 获得采购订单分页


**接口地址**:`/admin-api/erp/purchase-order/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|orderTime|采购时间|query|false|string||
|remark|备注|query|false|string||
|status|采购状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|inStatus|入库状态|query|false|string||
|returnStatus|退货状态|query|false|string||
|inEnable|是否可入库|query|false|string||
|returnEnable|是否可退货|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpPurchaseOrderRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpPurchaseOrderRespVO|PageResultErpPurchaseOrderRespVO|
|&emsp;&emsp;list|数据|array|ErpPurchaseOrderRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|采购单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|采购状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderTime|采购时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;depositPrice|定金金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|订单项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;&emsp;&emsp;inCount|采购入库数量|number||
|&emsp;&emsp;&emsp;&emsp;returnCount|采购退货数量|number||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"supplierId": 1724,
				"supplierName": "芋道",
				"accountId": 0,
				"orderTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"depositPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": "",
				"inCount": 100,
				"returnCount": 100
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新采购订单


**接口地址**:`/admin-api/erp/purchase-order/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|supplierId|供应商编号|query|true|string||
|orderTime|采购时间|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|depositPrice|定金金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|订单清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新采购订单的状态


**接口地址**:`/admin-api/erp/purchase-order/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 采购入库


## 创建采购入库


**接口地址**:`/admin-api/erp/purchase-in/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|inTime|入库时间|query|true|string||
|orderId|采购订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|入库清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除采购入库


**接口地址**:`/admin-api/erp/purchase-in/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出采购入库 Excel


**接口地址**:`/admin-api/erp/purchase-in/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|inTime|入库时间|query|false|string||
|remark|备注|query|false|string||
|status|入库状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|paymentStatus|付款状态|query|false|string||
|paymentEnable|是否可付款|query|false|string||
|orderNo|采购单号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得采购入库


**接口地址**:`/admin-api/erp/purchase-in/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpPurchaseInRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpPurchaseInRespVO|ErpPurchaseInRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|入库单编号|string||
|&emsp;&emsp;status|入库状态|integer(int32)||
|&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;inTime|入库时间|string(date-time)||
|&emsp;&emsp;orderId|采购订单编号|integer(int64)||
|&emsp;&emsp;orderNo|采购订单号|string||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;paymentPrice|已付款金额，单位：元|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;otherPrice|定金金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|入库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"supplierId": 1724,
		"supplierName": "芋道",
		"accountId": 0,
		"inTime": "",
		"orderId": 17386,
		"orderNo": "XS001",
		"totalCount": 15663,
		"totalPrice": 24906,
		"paymentPrice": 7127,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"otherPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得采购入库分页


**接口地址**:`/admin-api/erp/purchase-in/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|inTime|入库时间|query|false|string||
|remark|备注|query|false|string||
|status|入库状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|paymentStatus|付款状态|query|false|string||
|paymentEnable|是否可付款|query|false|string||
|orderNo|采购单号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpPurchaseInRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpPurchaseInRespVO|PageResultErpPurchaseInRespVO|
|&emsp;&emsp;list|数据|array|ErpPurchaseInRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|入库单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|入库状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;inTime|入库时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;orderId|采购订单编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderNo|采购订单号|string||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;paymentPrice|已付款金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;otherPrice|定金金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|入库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"supplierId": 1724,
				"supplierName": "芋道",
				"accountId": 0,
				"inTime": "",
				"orderId": 17386,
				"orderNo": "XS001",
				"totalCount": 15663,
				"totalPrice": 24906,
				"paymentPrice": 7127,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"otherPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新采购入库


**接口地址**:`/admin-api/erp/purchase-in/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|inTime|入库时间|query|true|string||
|orderId|采购订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|入库清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新采购入库的状态


**接口地址**:`/admin-api/erp/purchase-in/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 采购统计


## 获得采购单时间段统计


**接口地址**:`/admin-api/erp/purchase-statistics/order-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpPurchaseOrderTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpPurchaseOrderTimeSummaryRespVO|
|&emsp;&emsp;date|时间|string||
|&emsp;&emsp;orderCount|采购单数|integer(int64)||
|&emsp;&emsp;totalOrderPrice|采购金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2022-03",
			"orderCount": 1024,
			"totalOrderPrice": 102400
		}
	],
	"msg": ""
}
```


## 获得采购统计


**接口地址**:`/admin-api/erp/purchase-statistics/summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpPurchaseSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpPurchaseSummaryRespVO|ErpPurchaseSummaryRespVO|
|&emsp;&emsp;todayPrice|今日采购金额|number||
|&emsp;&emsp;yesterdayPrice|昨日采购金额|number||
|&emsp;&emsp;monthPrice|本月采购金额|number||
|&emsp;&emsp;yearPrice|今年采购金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"todayPrice": 1024,
		"yesterdayPrice": 888,
		"monthPrice": 1024,
		"yearPrice": 88888
	},
	"msg": ""
}
```


## 获得采购时间段统计


**接口地址**:`/admin-api/erp/purchase-statistics/time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|count|时间段数量|query|false|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpPurchaseTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpPurchaseTimeSummaryRespVO|
|&emsp;&emsp;time|时间|string||
|&emsp;&emsp;price|采购金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"time": "2022-03",
			"price": 1024
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 采购退货


## 创建采购退货


**接口地址**:`/admin-api/erp/purchase-return/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|returnTime|退货时间|query|true|string||
|orderId|采购订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|退货清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除采购退货


**接口地址**:`/admin-api/erp/purchase-return/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出采购退货 Excel


**接口地址**:`/admin-api/erp/purchase-return/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|returnTime|退货时间|query|false|string||
|remark|备注|query|false|string||
|status|退货状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|orderNo|采购单号|query|false|string||
|refundStatus|退款状态|query|false|string||
|refundEnable|是否可退款|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得采购退货


**接口地址**:`/admin-api/erp/purchase-return/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpPurchaseReturnRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpPurchaseReturnRespVO|ErpPurchaseReturnRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|退货单编号|string||
|&emsp;&emsp;status|退货状态|integer(int32)||
|&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;returnTime|退货时间|string(date-time)||
|&emsp;&emsp;orderId|采购订单编号|integer(int64)||
|&emsp;&emsp;orderNo|采购订单号|string||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;refundPrice|已退款金额，单位：元|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;otherPrice|定金金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|退货项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"supplierId": 1724,
		"supplierName": "芋道",
		"accountId": 0,
		"returnTime": "",
		"orderId": 17386,
		"orderNo": "XS001",
		"totalCount": 15663,
		"totalPrice": 24906,
		"refundPrice": 7127,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"otherPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得采购退货分页


**接口地址**:`/admin-api/erp/purchase-return/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|采购单编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|returnTime|退货时间|query|false|string||
|remark|备注|query|false|string||
|status|退货状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|orderNo|采购单号|query|false|string||
|refundStatus|退款状态|query|false|string||
|refundEnable|是否可退款|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpPurchaseReturnRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpPurchaseReturnRespVO|PageResultErpPurchaseReturnRespVO|
|&emsp;&emsp;list|数据|array|ErpPurchaseReturnRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|退货单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|退货状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;returnTime|退货时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;orderId|采购订单编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderNo|采购订单号|string||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;refundPrice|已退款金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;otherPrice|定金金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|退货项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"supplierId": 1724,
				"supplierName": "芋道",
				"accountId": 0,
				"returnTime": "",
				"orderId": 17386,
				"orderNo": "XS001",
				"totalCount": 15663,
				"totalPrice": 24906,
				"refundPrice": 7127,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"otherPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新采购退货


**接口地址**:`/admin-api/erp/purchase-return/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|returnTime|退货时间|query|true|string||
|orderId|采购订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|退货清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新采购退货的状态


**接口地址**:`/admin-api/erp/purchase-return/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 仓库


## 创建仓库


**接口地址**:`/admin-api/erp/warehouse/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|仓库名称|query|true|string||
|sort|排序|query|true|string||
|status|开启状态|query|true|string||
|id|仓库编号|query|false|string||
|address|仓库地址|query|false|string||
|remark|备注|query|false|string||
|principal|负责人|query|false|string||
|warehousePrice|仓储费，单位：元|query|false|string||
|truckagePrice|搬运费，单位：元|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除仓库


**接口地址**:`/admin-api/erp/warehouse/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出仓库 Excel


**接口地址**:`/admin-api/erp/warehouse/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|仓库名称|query|false|string||
|status|开启状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得仓库


**接口地址**:`/admin-api/erp/warehouse/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpWarehouseRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpWarehouseRespVO|ErpWarehouseRespVO|
|&emsp;&emsp;id|仓库编号|integer(int64)||
|&emsp;&emsp;name|仓库名称|string||
|&emsp;&emsp;address|仓库地址|string||
|&emsp;&emsp;sort|排序|integer(int64)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;principal|负责人|string||
|&emsp;&emsp;warehousePrice|仓储费，单位：元|number||
|&emsp;&emsp;truckagePrice|搬运费，单位：元|number||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 11614,
		"name": "李四",
		"address": "上海陆家嘴",
		"sort": 10,
		"remark": "随便",
		"principal": "芋头",
		"warehousePrice": 13973,
		"truckagePrice": 9903,
		"status": 1,
		"defaultStatus": false,
		"createTime": ""
	},
	"msg": ""
}
```


## 获得仓库分页


**接口地址**:`/admin-api/erp/warehouse/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|仓库名称|query|false|string||
|status|开启状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpWarehouseRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpWarehouseRespVO|PageResultErpWarehouseRespVO|
|&emsp;&emsp;list|数据|array|ErpWarehouseRespVO|
|&emsp;&emsp;&emsp;&emsp;id|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|仓库名称|string||
|&emsp;&emsp;&emsp;&emsp;address|仓库地址|string||
|&emsp;&emsp;&emsp;&emsp;sort|排序|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;principal|负责人|string||
|&emsp;&emsp;&emsp;&emsp;warehousePrice|仓储费，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;truckagePrice|搬运费，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 11614,
				"name": "李四",
				"address": "上海陆家嘴",
				"sort": 10,
				"remark": "随便",
				"principal": "芋头",
				"warehousePrice": 13973,
				"truckagePrice": 9903,
				"status": 1,
				"defaultStatus": false,
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得仓库精简列表


**接口地址**:`/admin-api/erp/warehouse/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的仓库，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpWarehouseRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpWarehouseRespVO|
|&emsp;&emsp;id|仓库编号|integer(int64)||
|&emsp;&emsp;name|仓库名称|string||
|&emsp;&emsp;address|仓库地址|string||
|&emsp;&emsp;sort|排序|integer(int64)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;principal|负责人|string||
|&emsp;&emsp;warehousePrice|仓储费，单位：元|number||
|&emsp;&emsp;truckagePrice|搬运费，单位：元|number||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 11614,
			"name": "李四",
			"address": "上海陆家嘴",
			"sort": 10,
			"remark": "随便",
			"principal": "芋头",
			"warehousePrice": 13973,
			"truckagePrice": 9903,
			"status": 1,
			"defaultStatus": false,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新仓库


**接口地址**:`/admin-api/erp/warehouse/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|仓库名称|query|true|string||
|sort|排序|query|true|string||
|status|开启状态|query|true|string||
|id|仓库编号|query|false|string||
|address|仓库地址|query|false|string||
|remark|备注|query|false|string||
|principal|负责人|query|false|string||
|warehousePrice|仓储费，单位：元|query|false|string||
|truckagePrice|搬运费，单位：元|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新仓库默认状态


**接口地址**:`/admin-api/erp/warehouse/update-default-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||
|defaultStatus||query|true|boolean||
|status|状态|query|true|||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 产品


## 创建产品


**接口地址**:`/admin-api/erp/product/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|产品名称|query|true|string||
|barCode|产品条码|query|true|string||
|categoryId|产品分类编号|query|true|string||
|unitId|单位编号|query|true|string||
|status|产品状态|query|true|string||
|purchasePrice|采购价格，单位：元|query|true|string||
|salePrice|销售价格，单位：元|query|true|string||
|id|产品编号|query|false|string||
|standard|产品规格|query|false|string||
|remark|产品备注|query|false|string||
|expiryDay|保质期天数|query|false|string||
|weight|基础重量（kg）|query|false|string||
|minPrice|最低价格，单位：元|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除产品


**接口地址**:`/admin-api/erp/product/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出产品 Excel


**接口地址**:`/admin-api/erp/product/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|产品名称|query|false|string||
|categoryId|产品分类编号|query|false|string||
|createTime|创建时间|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得产品


**接口地址**:`/admin-api/erp/product/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpProductRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpProductRespVO|ErpProductRespVO|
|&emsp;&emsp;id|产品编号|integer(int64)||
|&emsp;&emsp;name|产品名称|string||
|&emsp;&emsp;barCode|产品条码|string||
|&emsp;&emsp;categoryId|产品分类编号|integer(int64)||
|&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;unitId|单位编号|integer(int64)||
|&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;status|产品状态|integer(int32)||
|&emsp;&emsp;standard|产品规格|string||
|&emsp;&emsp;remark|产品备注|string||
|&emsp;&emsp;expiryDay|保质期天数|integer(int32)||
|&emsp;&emsp;weight|基础重量（kg）|number||
|&emsp;&emsp;purchasePrice|采购价格，单位：元|number||
|&emsp;&emsp;salePrice|销售价格，单位：元|number||
|&emsp;&emsp;minPrice|最低价格，单位：元|number||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 15672,
		"name": "李四",
		"barCode": "X110",
		"categoryId": 11161,
		"categoryName": "水果",
		"unitId": 8869,
		"unitName": "个",
		"status": 2,
		"standard": "红色",
		"remark": "你猜",
		"expiryDay": 10,
		"weight": 1,
		"purchasePrice": 10.3,
		"salePrice": 74.32,
		"minPrice": 161.87,
		"createTime": ""
	},
	"msg": ""
}
```


## 获得产品分页


**接口地址**:`/admin-api/erp/product/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|产品名称|query|false|string||
|categoryId|产品分类编号|query|false|string||
|createTime|创建时间|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpProductRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpProductRespVO|PageResultErpProductRespVO|
|&emsp;&emsp;list|数据|array|ErpProductRespVO|
|&emsp;&emsp;&emsp;&emsp;id|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;barCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;categoryId|产品分类编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;&emsp;&emsp;unitId|单位编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;&emsp;&emsp;status|产品状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;standard|产品规格|string||
|&emsp;&emsp;&emsp;&emsp;remark|产品备注|string||
|&emsp;&emsp;&emsp;&emsp;expiryDay|保质期天数|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;weight|基础重量（kg）|number||
|&emsp;&emsp;&emsp;&emsp;purchasePrice|采购价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;salePrice|销售价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;minPrice|最低价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 15672,
				"name": "李四",
				"barCode": "X110",
				"categoryId": 11161,
				"categoryName": "水果",
				"unitId": 8869,
				"unitName": "个",
				"status": 2,
				"standard": "红色",
				"remark": "你猜",
				"expiryDay": 10,
				"weight": 1,
				"purchasePrice": 10.3,
				"salePrice": 74.32,
				"minPrice": 161.87,
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得产品精简列表


**接口地址**:`/admin-api/erp/product/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的产品，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpProductRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpProductRespVO|
|&emsp;&emsp;id|产品编号|integer(int64)||
|&emsp;&emsp;name|产品名称|string||
|&emsp;&emsp;barCode|产品条码|string||
|&emsp;&emsp;categoryId|产品分类编号|integer(int64)||
|&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;unitId|单位编号|integer(int64)||
|&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;status|产品状态|integer(int32)||
|&emsp;&emsp;standard|产品规格|string||
|&emsp;&emsp;remark|产品备注|string||
|&emsp;&emsp;expiryDay|保质期天数|integer(int32)||
|&emsp;&emsp;weight|基础重量（kg）|number||
|&emsp;&emsp;purchasePrice|采购价格，单位：元|number||
|&emsp;&emsp;salePrice|销售价格，单位：元|number||
|&emsp;&emsp;minPrice|最低价格，单位：元|number||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 15672,
			"name": "李四",
			"barCode": "X110",
			"categoryId": 11161,
			"categoryName": "水果",
			"unitId": 8869,
			"unitName": "个",
			"status": 2,
			"standard": "红色",
			"remark": "你猜",
			"expiryDay": 10,
			"weight": 1,
			"purchasePrice": 10.3,
			"salePrice": 74.32,
			"minPrice": 161.87,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新产品


**接口地址**:`/admin-api/erp/product/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|产品名称|query|true|string||
|barCode|产品条码|query|true|string||
|categoryId|产品分类编号|query|true|string||
|unitId|单位编号|query|true|string||
|status|产品状态|query|true|string||
|purchasePrice|采购价格，单位：元|query|true|string||
|salePrice|销售价格，单位：元|query|true|string||
|id|产品编号|query|false|string||
|standard|产品规格|query|false|string||
|remark|产品备注|query|false|string||
|expiryDay|保质期天数|query|false|string||
|weight|基础重量（kg）|query|false|string||
|minPrice|最低价格，单位：元|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 产品单位


## 创建产品单位


**接口地址**:`/admin-api/erp/product-unit/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|单位名字|query|true|string||
|status|单位状态|query|true|string||
|id|单位编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除产品单位


**接口地址**:`/admin-api/erp/product-unit/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出产品单位 Excel


**接口地址**:`/admin-api/erp/product-unit/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|单位名字|query|false|string||
|status|单位状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得产品单位


**接口地址**:`/admin-api/erp/product-unit/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpProductUnitRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpProductUnitRespVO|ErpProductUnitRespVO|
|&emsp;&emsp;id|单位编号|integer(int64)||
|&emsp;&emsp;name|单位名字|string||
|&emsp;&emsp;status|单位状态|integer(int32)||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 31254,
		"name": "芋艿",
		"status": 1,
		"createTime": ""
	},
	"msg": ""
}
```


## 获得产品单位分页


**接口地址**:`/admin-api/erp/product-unit/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|单位名字|query|false|string||
|status|单位状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpProductUnitRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpProductUnitRespVO|PageResultErpProductUnitRespVO|
|&emsp;&emsp;list|数据|array|ErpProductUnitRespVO|
|&emsp;&emsp;&emsp;&emsp;id|单位编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|单位名字|string||
|&emsp;&emsp;&emsp;&emsp;status|单位状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 31254,
				"name": "芋艿",
				"status": 1,
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得产品单位精简列表


**接口地址**:`/admin-api/erp/product-unit/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的单位，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpProductUnitRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpProductUnitRespVO|
|&emsp;&emsp;id|单位编号|integer(int64)||
|&emsp;&emsp;name|单位名字|string||
|&emsp;&emsp;status|单位状态|integer(int32)||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 31254,
			"name": "芋艿",
			"status": 1,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新产品单位


**接口地址**:`/admin-api/erp/product-unit/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|单位名字|query|true|string||
|status|单位状态|query|true|string||
|id|单位编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 产品分类


## 创建产品分类


**接口地址**:`/admin-api/erp/product-category/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|parentId|父分类编号|query|true|string||
|name|分类名称|query|true|string||
|code|分类编码|query|true|string||
|sort|分类排序|query|true|string||
|status|开启状态|query|true|string||
|id|分类编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除产品分类


**接口地址**:`/admin-api/erp/product-category/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出产品分类 Excel


**接口地址**:`/admin-api/erp/product-category/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|分类名称|query|false|string||
|status|开启状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得产品分类


**接口地址**:`/admin-api/erp/product-category/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpProductCategoryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpProductCategoryRespVO|ErpProductCategoryRespVO|
|&emsp;&emsp;id|分类编号|integer(int64)||
|&emsp;&emsp;parentId|父分类编号|integer(int64)||
|&emsp;&emsp;name|分类名称|string||
|&emsp;&emsp;code|分类编码|string||
|&emsp;&emsp;sort|分类排序|integer(int32)||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 5860,
		"parentId": 21829,
		"name": "芋艿",
		"code": "S110",
		"sort": 10,
		"status": 1,
		"createTime": ""
	},
	"msg": ""
}
```


## 获得产品分类列表


**接口地址**:`/admin-api/erp/product-category/list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|分类名称|query|false|string||
|status|开启状态|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpProductCategoryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpProductCategoryRespVO|
|&emsp;&emsp;id|分类编号|integer(int64)||
|&emsp;&emsp;parentId|父分类编号|integer(int64)||
|&emsp;&emsp;name|分类名称|string||
|&emsp;&emsp;code|分类编码|string||
|&emsp;&emsp;sort|分类排序|integer(int32)||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 5860,
			"parentId": 21829,
			"name": "芋艿",
			"code": "S110",
			"sort": 10,
			"status": 1,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 获得产品分类精简列表


**接口地址**:`/admin-api/erp/product-category/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的分类，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpProductCategoryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpProductCategoryRespVO|
|&emsp;&emsp;id|分类编号|integer(int64)||
|&emsp;&emsp;parentId|父分类编号|integer(int64)||
|&emsp;&emsp;name|分类名称|string||
|&emsp;&emsp;code|分类编码|string||
|&emsp;&emsp;sort|分类排序|integer(int32)||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 5860,
			"parentId": 21829,
			"name": "芋艿",
			"code": "S110",
			"sort": 10,
			"status": 1,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新产品分类


**接口地址**:`/admin-api/erp/product-category/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|parentId|父分类编号|query|true|string||
|name|分类名称|query|true|string||
|code|分类编码|query|true|string||
|sort|分类排序|query|true|string||
|status|开启状态|query|true|string||
|id|分类编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 产品库存


## 导出产品库存 Excel


**接口地址**:`/admin-api/erp/stock/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得产品库存


**接口地址**:`/admin-api/erp/stock/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|false|integer(int64)||
|productId|产品编号|query|false|integer(int64)||
|warehouseId|仓库编号|query|false|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockRespVO|ErpStockRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;count|库存数量|number||
|&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;warehouseName|仓库名称|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17086,
		"productId": 19614,
		"warehouseId": 2802,
		"count": 21935,
		"productName": "苹果",
		"categoryName": "水果",
		"unitName": "个",
		"warehouseName": "李四"
	},
	"msg": ""
}
```


## 获得产品库存数量


**接口地址**:`/admin-api/erp/stock/get-count`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|productId|产品编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBigDecimal|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 获得产品库存分页


**接口地址**:`/admin-api/erp/stock/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockRespVO|PageResultErpStockRespVO|
|&emsp;&emsp;list|数据|array|ErpStockRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;count|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;&emsp;&emsp;warehouseName|仓库名称|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17086,
				"productId": 19614,
				"warehouseId": 2802,
				"count": 21935,
				"productName": "苹果",
				"categoryName": "水果",
				"unitName": "个",
				"warehouseName": "李四"
			}
		],
		"total": 0
	},
	"msg": ""
}
```


# 管理后台 - ERP 产品库存明细


## 导出产品库存明细 Excel


**接口地址**:`/admin-api/erp/stock-record/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|bizType|业务类型|query|false|string||
|bizNo|业务单号|query|false|string||
|createTime|创建时间|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得产品库存明细


**接口地址**:`/admin-api/erp/stock-record/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockRecordRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockRecordRespVO|ErpStockRecordRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;count|出入库数量|number||
|&emsp;&emsp;totalCount|总库存量|number||
|&emsp;&emsp;bizType|业务类型|integer(int32)||
|&emsp;&emsp;bizId|业务编号|integer(int64)||
|&emsp;&emsp;bizItemId|业务项编号|integer(int64)||
|&emsp;&emsp;bizNo|业务单号|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;warehouseName|仓库名称|string||
|&emsp;&emsp;creatorName|创建人|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 18909,
		"productId": 10625,
		"warehouseId": 32407,
		"count": 11084,
		"totalCount": 4307,
		"bizType": 10,
		"bizId": 27093,
		"bizItemId": 23516,
		"bizNo": "Z110",
		"createTime": "",
		"creator": "25682",
		"productName": "苹果",
		"categoryName": "水果",
		"unitName": "个",
		"warehouseName": "李四",
		"creatorName": "张三"
	},
	"msg": ""
}
```


## 获得产品库存明细分页


**接口地址**:`/admin-api/erp/stock-record/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|bizType|业务类型|query|false|string||
|bizNo|业务单号|query|false|string||
|createTime|创建时间|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockRecordRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockRecordRespVO|PageResultErpStockRecordRespVO|
|&emsp;&emsp;list|数据|array|ErpStockRecordRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;count|出入库数量|number||
|&emsp;&emsp;&emsp;&emsp;totalCount|总库存量|number||
|&emsp;&emsp;&emsp;&emsp;bizType|业务类型|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;bizId|业务编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;bizItemId|业务项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;bizNo|业务单号|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;categoryName|产品分类|string||
|&emsp;&emsp;&emsp;&emsp;unitName|单位|string||
|&emsp;&emsp;&emsp;&emsp;warehouseName|仓库名称|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 18909,
				"productId": 10625,
				"warehouseId": 32407,
				"count": 11084,
				"totalCount": 4307,
				"bizType": 10,
				"bizId": 27093,
				"bizItemId": 23516,
				"bizNo": "Z110",
				"createTime": "",
				"creator": "25682",
				"productName": "苹果",
				"categoryName": "水果",
				"unitName": "个",
				"warehouseName": "李四",
				"creatorName": "张三"
			}
		],
		"total": 0
	},
	"msg": ""
}
```


# 管理后台 - ERP 出入库明细统计


## 库存看板-出入库明细-时间段统计


**接口地址**:`/admin-api/erp/stock-record-statistics/time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpStockRecordTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpStockRecordTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;totalInStock|入库数量|number||
|&emsp;&emsp;totalOutStock|出库数量|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"totalInStock": 888,
			"totalOutStock": 888
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 付款单


## 创建付款单


**接口地址**:`/admin-api/erp/finance-payment/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|paymentTime|付款时间|query|true|string||
|supplierId|供应商编号|query|true|string||
|accountId|付款账户编号|query|true|string||
|discountPrice|优惠金额，单位：元|query|true|string||
|items|付款项列表|query|true|string||
|id|编号|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除付款单


**接口地址**:`/admin-api/erp/finance-payment/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出付款单 Excel


**接口地址**:`/admin-api/erp/finance-payment/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|付款单编号|query|false|string||
|paymentTime|付款时间|query|false|string||
|supplierId|供应商编号|query|false|string||
|creator|创建者|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|status|付款状态|query|false|string||
|remark|备注|query|false|string||
|bizNo|业务编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得付款单


**接口地址**:`/admin-api/erp/finance-payment/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpFinancePaymentRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpFinancePaymentRespVO|ErpFinancePaymentRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|付款单号|string||
|&emsp;&emsp;status|付款状态|integer(int32)||
|&emsp;&emsp;paymentTime|付款时间|string(date-time)||
|&emsp;&emsp;financeUserId|财务人员编号|integer(int64)||
|&emsp;&emsp;financeUserName|财务人员名称|string||
|&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;accountId|付款账户编号|integer(int64)||
|&emsp;&emsp;accountName|付款账户名称|string||
|&emsp;&emsp;totalPrice|合计价格，单位：元|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;paymentPrice|实际价格，单位：元|number||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|付款项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 23752,
		"no": "FKD888",
		"status": 1,
		"paymentTime": "",
		"financeUserId": 19690,
		"financeUserName": "张三",
		"supplierId": 29399,
		"supplierName": "小番茄公司",
		"accountId": 28989,
		"accountName": "张三",
		"totalPrice": 13832,
		"discountPrice": 11600,
		"paymentPrice": 10000,
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		]
	},
	"msg": ""
}
```


## 获得付款单分页


**接口地址**:`/admin-api/erp/finance-payment/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|付款单编号|query|false|string||
|paymentTime|付款时间|query|false|string||
|supplierId|供应商编号|query|false|string||
|creator|创建者|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|status|付款状态|query|false|string||
|remark|备注|query|false|string||
|bizNo|业务编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpFinancePaymentRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpFinancePaymentRespVO|PageResultErpFinancePaymentRespVO|
|&emsp;&emsp;list|数据|array|ErpFinancePaymentRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|付款单号|string||
|&emsp;&emsp;&emsp;&emsp;status|付款状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;paymentTime|付款时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;financeUserId|财务人员编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;financeUserName|财务人员名称|string||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|付款账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;accountName|付款账户名称|string||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;paymentPrice|实际价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|付款项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 23752,
				"no": "FKD888",
				"status": 1,
				"paymentTime": "",
				"financeUserId": 19690,
				"financeUserName": "张三",
				"supplierId": 29399,
				"supplierName": "小番茄公司",
				"accountId": 28989,
				"accountName": "张三",
				"totalPrice": 13832,
				"discountPrice": 11600,
				"paymentPrice": 10000,
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				]
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新付款单


**接口地址**:`/admin-api/erp/finance-payment/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|paymentTime|付款时间|query|true|string||
|supplierId|供应商编号|query|true|string||
|accountId|付款账户编号|query|true|string||
|discountPrice|优惠金额，单位：元|query|true|string||
|items|付款项列表|query|true|string||
|id|编号|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新付款单的状态


**接口地址**:`/admin-api/erp/finance-payment/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 付款单统计


## 付款单-时间段统计


**接口地址**:`/admin-api/erp/finance-payment-statistics/order-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinancePaymentTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinancePaymentTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;paymentCount|付款单笔数|number||
|&emsp;&emsp;totalPaymentPrice|付款单金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"paymentCount": 1,
			"totalPaymentPrice": 888
		}
	],
	"msg": ""
}
```


## 业绩看板-交易趋势-时间段统计


**接口地址**:`/admin-api/erp/finance-payment-statistics/time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinancePaymentTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinancePaymentTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;paymentCount|付款单笔数|number||
|&emsp;&emsp;totalPaymentPrice|付款单金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"paymentCount": 1,
			"totalPaymentPrice": 888
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 供应商


## 创建供应商


**接口地址**:`/admin-api/erp/supplier/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|供应商名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|供应商编号|query|false|string||
|contact|联系人|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||
|email|电子邮箱|query|false|string||
|fax|传真|query|false|string||
|remark|备注|query|false|string||
|taxNo|纳税人识别号|query|false|string||
|taxPercent|税率|query|false|string||
|bankName|开户行|query|false|string||
|bankAccount|开户账号|query|false|string||
|bankAddress|开户地址|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除供应商


**接口地址**:`/admin-api/erp/supplier/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出供应商 Excel


**接口地址**:`/admin-api/erp/supplier/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|供应商名称|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得供应商


**接口地址**:`/admin-api/erp/supplier/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpSupplierRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpSupplierRespVO|ErpSupplierRespVO|
|&emsp;&emsp;id|供应商编号|integer(int64)||
|&emsp;&emsp;name|供应商名称|string||
|&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17791,
		"name": "芋道源码",
		"contact": "芋艿",
		"mobile": "15601691300",
		"telephone": "18818288888",
		"email": "76853@qq.com",
		"fax": "20 7123 4567",
		"remark": "你猜",
		"status": 1,
		"sort": 10,
		"taxNo": "91130803MA098BY05W",
		"taxPercent": 10,
		"bankName": "张三",
		"bankAccount": "622908212277228617",
		"bankAddress": "兴业银行浦东支行",
		"createTime": ""
	},
	"msg": ""
}
```


## 获得供应商名称列表


**接口地址**:`/admin-api/erp/supplier/getSupplierNameList`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpSupplierSimpleRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpSupplierSimpleRespVO|
|&emsp;&emsp;id|供应商编号|integer(int64)||
|&emsp;&emsp;name|供应商名称|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 0,
			"name": ""
		}
	],
	"msg": ""
}
```


## 获得供应商分页


**接口地址**:`/admin-api/erp/supplier/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|供应商名称|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpSupplierRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpSupplierRespVO|PageResultErpSupplierRespVO|
|&emsp;&emsp;list|数据|array|ErpSupplierRespVO|
|&emsp;&emsp;&emsp;&emsp;id|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17791,
				"name": "芋道源码",
				"contact": "芋艿",
				"mobile": "15601691300",
				"telephone": "18818288888",
				"email": "76853@qq.com",
				"fax": "20 7123 4567",
				"remark": "你猜",
				"status": 1,
				"sort": 10,
				"taxNo": "91130803MA098BY05W",
				"taxPercent": 10,
				"bankName": "张三",
				"bankAccount": "622908212277228617",
				"bankAddress": "兴业银行浦东支行",
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得供应商精简列表


**接口地址**:`/admin-api/erp/supplier/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的供应商，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpSupplierRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpSupplierRespVO|
|&emsp;&emsp;id|供应商编号|integer(int64)||
|&emsp;&emsp;name|供应商名称|string||
|&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 17791,
			"name": "芋道源码",
			"contact": "芋艿",
			"mobile": "15601691300",
			"telephone": "18818288888",
			"email": "76853@qq.com",
			"fax": "20 7123 4567",
			"remark": "你猜",
			"status": 1,
			"sort": 10,
			"taxNo": "91130803MA098BY05W",
			"taxPercent": 10,
			"bankName": "张三",
			"bankAccount": "622908212277228617",
			"bankAddress": "兴业银行浦东支行",
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新供应商


**接口地址**:`/admin-api/erp/supplier/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|供应商名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|供应商编号|query|false|string||
|contact|联系人|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||
|email|电子邮箱|query|false|string||
|fax|传真|query|false|string||
|remark|备注|query|false|string||
|taxNo|纳税人识别号|query|false|string||
|taxPercent|税率|query|false|string||
|bankName|开户行|query|false|string||
|bankAccount|开户账号|query|false|string||
|bankAddress|开户地址|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 供应商统计


## 获得供应商统计


**接口地址**:`/admin-api/erp/supplier-statistics/summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpSupplierSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpSupplierSummaryRespVO|
|&emsp;&emsp;supplierId|供应商id|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;purchaseOrderCount|订单数|integer(int32)||
|&emsp;&emsp;firstCooperateTime|初次合作时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"supplierId": 21,
			"supplierName": "供应商",
			"purchaseOrderCount": 888,
			"firstCooperateTime": ""
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 记账凭证


## 创建ERP 记账凭证


**接口地址**:`/admin-api/erp/bookkeeping-voucher/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|id|query|false|string||
|payType|记录类型|query|false|string||
|supplierId|供应商ID|query|false|string||
|supplierName|供应商名称|query|false|string||
|customerId|客户ID|query|false|string||
|customerName|客户名称|query|false|string||
|tradeType|交易类型|query|false|string||
|summary|摘要|query|false|string||
|paymentTime|付款/收款时间|query|false|string||
|billNumber|单据号|query|false|string||
|subject|总账科目|query|false|string||
|billAmount|单据金额|query|false|string||
|thisPayment|本次付款|query|false|string||
|attachesUrl|纸质凭证|query|false|string||
|payAmount|付款金额|query|false|string||
|bookkeeper|记账人|query|false|string||
|advancePayment|预付款金额|query|false|string||
|payWay|支付方式|query|false|string||
|refundAmount|退款金额|query|false|string||
|refundSummary|退款摘要|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除ERP 记账凭证


**接口地址**:`/admin-api/erp/bookkeeping-voucher/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出ERP 记账凭证 Excel


**接口地址**:`/admin-api/erp/bookkeeping-voucher/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|payType|记录类型|query|true|string||
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|tradeType|交易类型|query|false|string||
|payWay|支付方式|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得ERP 记账凭证


**接口地址**:`/admin-api/erp/bookkeeping-voucher/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpBookkeepingVoucherRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpBookkeepingVoucherRespVO|ErpBookkeepingVoucherRespVO|
|&emsp;&emsp;id|id|integer(int64)||
|&emsp;&emsp;payType|记录类型|string||
|&emsp;&emsp;supplierId|供应商ID|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;customerId|客户ID|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;tradeType|交易类型|string||
|&emsp;&emsp;summary|摘要|string||
|&emsp;&emsp;paymentTime|付款/收款时间|string(date-time)||
|&emsp;&emsp;billNumber|单据号|string||
|&emsp;&emsp;subject|总账科目|string||
|&emsp;&emsp;billAmount|单据金额|number||
|&emsp;&emsp;thisPayment|本次付款|number||
|&emsp;&emsp;attachesUrl|纸质凭证地址|string||
|&emsp;&emsp;tempAttachesUrl|临时纸质凭证地址|string||
|&emsp;&emsp;payAmount|付款金额|number||
|&emsp;&emsp;bookkeeper|记账人|string||
|&emsp;&emsp;advancePayment|预付款金额|number||
|&emsp;&emsp;payWay|支付方式|string||
|&emsp;&emsp;refundAmount|退款金额|number||
|&emsp;&emsp;refundSummary|退款摘要|string||
|&emsp;&emsp;remark|备注|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 0,
		"payType": "（收款/付款）",
		"supplierId": 0,
		"supplierName": "",
		"customerId": 0,
		"customerName": "",
		"tradeType": "",
		"summary": "",
		"paymentTime": "",
		"billNumber": "",
		"subject": "",
		"billAmount": 0,
		"thisPayment": 0,
		"attachesUrl": "",
		"tempAttachesUrl": "",
		"payAmount": 0,
		"bookkeeper": "",
		"advancePayment": 0,
		"payWay": "",
		"refundAmount": 0,
		"refundSummary": "",
		"remark": ""
	},
	"msg": ""
}
```


## 获得ERP 记账凭证分页


**接口地址**:`/admin-api/erp/bookkeeping-voucher/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|payType|记录类型|query|true|string||
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|tradeType|交易类型|query|false|string||
|payWay|支付方式|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpBookkeepingVoucherRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpBookkeepingVoucherRespVO|PageResultErpBookkeepingVoucherRespVO|
|&emsp;&emsp;list|数据|array|ErpBookkeepingVoucherRespVO|
|&emsp;&emsp;&emsp;&emsp;id|id|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;payType|记录类型|string||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商ID|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;customerId|客户ID|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;tradeType|交易类型|string||
|&emsp;&emsp;&emsp;&emsp;summary|摘要|string||
|&emsp;&emsp;&emsp;&emsp;paymentTime|付款/收款时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;billNumber|单据号|string||
|&emsp;&emsp;&emsp;&emsp;subject|总账科目|string||
|&emsp;&emsp;&emsp;&emsp;billAmount|单据金额|number||
|&emsp;&emsp;&emsp;&emsp;thisPayment|本次付款|number||
|&emsp;&emsp;&emsp;&emsp;attachesUrl|纸质凭证地址|string||
|&emsp;&emsp;&emsp;&emsp;tempAttachesUrl|临时纸质凭证地址|string||
|&emsp;&emsp;&emsp;&emsp;payAmount|付款金额|number||
|&emsp;&emsp;&emsp;&emsp;bookkeeper|记账人|string||
|&emsp;&emsp;&emsp;&emsp;advancePayment|预付款金额|number||
|&emsp;&emsp;&emsp;&emsp;payWay|支付方式|string||
|&emsp;&emsp;&emsp;&emsp;refundAmount|退款金额|number||
|&emsp;&emsp;&emsp;&emsp;refundSummary|退款摘要|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 0,
				"payType": "（收款/付款）",
				"supplierId": 0,
				"supplierName": "",
				"customerId": 0,
				"customerName": "",
				"tradeType": "",
				"summary": "",
				"paymentTime": "",
				"billNumber": "",
				"subject": "",
				"billAmount": 0,
				"thisPayment": 0,
				"attachesUrl": "",
				"tempAttachesUrl": "",
				"payAmount": 0,
				"bookkeeper": "",
				"advancePayment": 0,
				"payWay": "",
				"refundAmount": 0,
				"refundSummary": "",
				"remark": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新ERP 记账凭证


**接口地址**:`/admin-api/erp/bookkeeping-voucher/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|id|query|false|string||
|payType|记录类型|query|false|string||
|supplierId|供应商ID|query|false|string||
|supplierName|供应商名称|query|false|string||
|customerId|客户ID|query|false|string||
|customerName|客户名称|query|false|string||
|tradeType|交易类型|query|false|string||
|summary|摘要|query|false|string||
|paymentTime|付款/收款时间|query|false|string||
|billNumber|单据号|query|false|string||
|subject|总账科目|query|false|string||
|billAmount|单据金额|query|false|string||
|thisPayment|本次付款|query|false|string||
|attachesUrl|纸质凭证|query|false|string||
|payAmount|付款金额|query|false|string||
|bookkeeper|记账人|query|false|string||
|advancePayment|预付款金额|query|false|string||
|payWay|支付方式|query|false|string||
|refundAmount|退款金额|query|false|string||
|refundSummary|退款摘要|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## ERP 上传纸质单据


**接口地址**:`/admin-api/erp/bookkeeping-voucher/upload`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultString|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": "",
	"msg": ""
}
```


# 管理后台 - ERP 结算账户


## 创建结算账户


**接口地址**:`/admin-api/erp/account/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|账户名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|结算账户编号|query|false|string||
|no|账户编码|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除结算账户


**接口地址**:`/admin-api/erp/account/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出结算账户 Excel


**接口地址**:`/admin-api/erp/account/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|账户编码|query|false|string||
|name|账户名称|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得结算账户


**接口地址**:`/admin-api/erp/account/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpAccountRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpAccountRespVO|ErpAccountRespVO|
|&emsp;&emsp;id|结算账户编号|integer(int64)||
|&emsp;&emsp;name|账户名称|string||
|&emsp;&emsp;no|账户编码|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 28684,
		"name": "张三",
		"no": "A88",
		"remark": "随便",
		"status": 1,
		"sort": 1,
		"defaultStatus": false,
		"createTime": ""
	},
	"msg": ""
}
```


## 获得结算账户分页


**接口地址**:`/admin-api/erp/account/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|账户编码|query|false|string||
|name|账户名称|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpAccountRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpAccountRespVO|PageResultErpAccountRespVO|
|&emsp;&emsp;list|数据|array|ErpAccountRespVO|
|&emsp;&emsp;&emsp;&emsp;id|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|账户名称|string||
|&emsp;&emsp;&emsp;&emsp;no|账户编码|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 28684,
				"name": "张三",
				"no": "A88",
				"remark": "随便",
				"status": 1,
				"sort": 1,
				"defaultStatus": false,
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得结算账户精简列表


**接口地址**:`/admin-api/erp/account/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的结算账户，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpAccountRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpAccountRespVO|
|&emsp;&emsp;id|结算账户编号|integer(int64)||
|&emsp;&emsp;name|账户名称|string||
|&emsp;&emsp;no|账户编码|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;defaultStatus|是否默认|boolean||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 28684,
			"name": "张三",
			"no": "A88",
			"remark": "随便",
			"status": 1,
			"sort": 1,
			"defaultStatus": false,
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新结算账户


**接口地址**:`/admin-api/erp/account/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|账户名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|结算账户编号|query|false|string||
|no|账户编码|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新结算账户默认状态


**接口地址**:`/admin-api/erp/account/update-default-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||
|defaultStatus||query|true|boolean||
|status|状态|query|true|||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 客户


## 创建客户


**接口地址**:`/admin-api/erp/customer/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|客户名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|客户编号|query|false|string||
|contact|联系人|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||
|email|电子邮箱|query|false|string||
|fax|传真|query|false|string||
|remark|备注|query|false|string||
|taxNo|纳税人识别号|query|false|string||
|taxPercent|税率|query|false|string||
|bankName|开户行|query|false|string||
|bankAccount|开户账号|query|false|string||
|bankAddress|开户地址|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除客户


**接口地址**:`/admin-api/erp/customer/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出客户 Excel


**接口地址**:`/admin-api/erp/customer/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|客户名称|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得客户


**接口地址**:`/admin-api/erp/customer/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpCustomerRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpCustomerRespVO|ErpCustomerRespVO|
|&emsp;&emsp;id|客户编号|integer(int64)||
|&emsp;&emsp;name|客户名称|string||
|&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 27520,
		"name": "张三",
		"contact": "老王",
		"mobile": "15601691300",
		"telephone": "15601691300",
		"email": "7685323@qq.com",
		"fax": "20 7123 4567",
		"remark": "你猜",
		"status": 1,
		"sort": 10,
		"taxNo": "91130803MA098BY05W",
		"taxPercent": 10,
		"bankName": "芋艿",
		"bankAccount": "622908212277228617",
		"bankAddress": "兴业银行浦东支行",
		"createTime": ""
	},
	"msg": ""
}
```


## 获得客户名称列表


**接口地址**:`/admin-api/erp/customer/getCustomerNameList`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpCustomerSimpleRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpCustomerSimpleRespVO|
|&emsp;&emsp;id|客户编号|integer(int64)||
|&emsp;&emsp;name|客户名称|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 0,
			"name": ""
		}
	],
	"msg": ""
}
```


## 获得客户分页


**接口地址**:`/admin-api/erp/customer/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|name|客户名称|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpCustomerRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpCustomerRespVO|PageResultErpCustomerRespVO|
|&emsp;&emsp;list|数据|array|ErpCustomerRespVO|
|&emsp;&emsp;&emsp;&emsp;id|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;name|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 27520,
				"name": "张三",
				"contact": "老王",
				"mobile": "15601691300",
				"telephone": "15601691300",
				"email": "7685323@qq.com",
				"fax": "20 7123 4567",
				"remark": "你猜",
				"status": 1,
				"sort": 10,
				"taxNo": "91130803MA098BY05W",
				"taxPercent": 10,
				"bankName": "芋艿",
				"bankAccount": "622908212277228617",
				"bankAddress": "兴业银行浦东支行",
				"createTime": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 获得客户精简列表


**接口地址**:`/admin-api/erp/customer/simple-list`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>只包含被开启的客户，主要用于前端的下拉选项</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpCustomerRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpCustomerRespVO|
|&emsp;&emsp;id|客户编号|integer(int64)||
|&emsp;&emsp;name|客户名称|string||
|&emsp;&emsp;contact|联系人|string||
|&emsp;&emsp;mobile|手机号码|string||
|&emsp;&emsp;telephone|联系电话|string||
|&emsp;&emsp;email|电子邮箱|string||
|&emsp;&emsp;fax|传真|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;status|开启状态|integer(int32)||
|&emsp;&emsp;sort|排序|integer(int32)||
|&emsp;&emsp;taxNo|纳税人识别号|string||
|&emsp;&emsp;taxPercent|税率|number||
|&emsp;&emsp;bankName|开户行|string||
|&emsp;&emsp;bankAccount|开户账号|string||
|&emsp;&emsp;bankAddress|开户地址|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"id": 27520,
			"name": "张三",
			"contact": "老王",
			"mobile": "15601691300",
			"telephone": "15601691300",
			"email": "7685323@qq.com",
			"fax": "20 7123 4567",
			"remark": "你猜",
			"status": 1,
			"sort": 10,
			"taxNo": "91130803MA098BY05W",
			"taxPercent": 10,
			"bankName": "芋艿",
			"bankAccount": "622908212277228617",
			"bankAddress": "兴业银行浦东支行",
			"createTime": ""
		}
	],
	"msg": ""
}
```


## 更新客户


**接口地址**:`/admin-api/erp/customer/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|name|客户名称|query|true|string||
|status|开启状态|query|true|string||
|sort|排序|query|true|string||
|id|客户编号|query|false|string||
|contact|联系人|query|false|string||
|mobile|手机号码|query|false|string||
|telephone|联系电话|query|false|string||
|email|电子邮箱|query|false|string||
|fax|传真|query|false|string||
|remark|备注|query|false|string||
|taxNo|纳税人识别号|query|false|string||
|taxPercent|税率|query|false|string||
|bankName|开户行|query|false|string||
|bankAccount|开户账号|query|false|string||
|bankAddress|开户地址|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 库存调拨单


## 创建库存调拨单


**接口地址**:`/admin-api/erp/stock-check/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|checkTime|出库时间|query|true|string||
|items|出库项列表|query|true|string||
|id|出库编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除库存调拨单


**接口地址**:`/admin-api/erp/stock-check/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出库存调拨单 Excel


**接口地址**:`/admin-api/erp/stock-check/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|盘点单号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|checkTime|盘点时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得库存调拨单


**接口地址**:`/admin-api/erp/stock-check/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockCheckRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockCheckRespVO|ErpStockCheckRespVO|
|&emsp;&emsp;id|盘点编号|integer(int64)||
|&emsp;&emsp;no|盘点单号|string||
|&emsp;&emsp;checkTime|盘点时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|盘点项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 11756,
		"no": "S123",
		"checkTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"status": 10,
		"remark": "随便",
		"fileUrl": "https://www.iocoder.cn/1.doc",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得库存调拨单分页


**接口地址**:`/admin-api/erp/stock-check/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|盘点单号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|checkTime|盘点时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockCheckRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockCheckRespVO|PageResultErpStockCheckRespVO|
|&emsp;&emsp;list|数据|array|ErpStockCheckRespVO|
|&emsp;&emsp;&emsp;&emsp;id|盘点编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|盘点单号|string||
|&emsp;&emsp;&emsp;&emsp;checkTime|盘点时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|盘点项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 11756,
				"no": "S123",
				"checkTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"status": 10,
				"remark": "随便",
				"fileUrl": "https://www.iocoder.cn/1.doc",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新库存调拨单


**接口地址**:`/admin-api/erp/stock-check/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|checkTime|出库时间|query|true|string||
|items|出库项列表|query|true|string||
|id|出库编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新库存调拨单的状态


**接口地址**:`/admin-api/erp/stock-check/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 创建库存调拨单


**接口地址**:`/admin-api/erp/stock-move/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|moveTime|调拨时间|query|true|string||
|items|调拨项列表|query|true|string||
|id|调拨编号|query|false|string||
|customerId|客户编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除库存调拨单


**接口地址**:`/admin-api/erp/stock-move/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出库存调拨单 Excel


**接口地址**:`/admin-api/erp/stock-move/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|调拨单号|query|false|string||
|moveTime|调拨时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|fromWarehouseId|调出仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得库存调拨单


**接口地址**:`/admin-api/erp/stock-move/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockMoveRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockMoveRespVO|ErpStockMoveRespVO|
|&emsp;&emsp;id|调拨编号|integer(int64)||
|&emsp;&emsp;no|调拨单号|string||
|&emsp;&emsp;moveTime|调拨时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|调拨项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 11756,
		"no": "S123",
		"moveTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"status": 10,
		"remark": "随便",
		"fileUrl": "https://www.iocoder.cn/1.doc",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得库存调拨单分页


**接口地址**:`/admin-api/erp/stock-move/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|调拨单号|query|false|string||
|moveTime|调拨时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|fromWarehouseId|调出仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockMoveRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockMoveRespVO|PageResultErpStockMoveRespVO|
|&emsp;&emsp;list|数据|array|ErpStockMoveRespVO|
|&emsp;&emsp;&emsp;&emsp;id|调拨编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|调拨单号|string||
|&emsp;&emsp;&emsp;&emsp;moveTime|调拨时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|调拨项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 11756,
				"no": "S123",
				"moveTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"status": 10,
				"remark": "随便",
				"fileUrl": "https://www.iocoder.cn/1.doc",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新库存调拨单


**接口地址**:`/admin-api/erp/stock-move/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|moveTime|调拨时间|query|true|string||
|items|调拨项列表|query|true|string||
|id|调拨编号|query|false|string||
|customerId|客户编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新库存调拨单的状态


**接口地址**:`/admin-api/erp/stock-move/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 库存统计


## 库存概览统计


**接口地址**:`/admin-api/erp/stock-statistics/summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpStockSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpStockSummaryRespVO|
|&emsp;&emsp;warehouseId|仓库id|integer(int64)||
|&emsp;&emsp;warehouseName|仓库名称|string||
|&emsp;&emsp;totalProductCount|库存数量|number||
|&emsp;&emsp;warehouseCreateTime|仓库创建时间|string(date-time)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"warehouseId": 1,
			"warehouseName": "888",
			"totalProductCount": 888,
			"warehouseCreateTime": ""
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 其它出库单


## 创建其它出库单


**接口地址**:`/admin-api/erp/stock-out/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|outTime|出库时间|query|true|string||
|items|出库项列表|query|true|string||
|id|出库编号|query|false|string||
|customerId|客户编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除其它出库单


**接口地址**:`/admin-api/erp/stock-out/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出其它出库单 Excel


**接口地址**:`/admin-api/erp/stock-out/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|出库单号|query|false|string||
|customerId|客户编号|query|false|string||
|outTime|出库时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得其它出库单


**接口地址**:`/admin-api/erp/stock-out/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockOutRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockOutRespVO|ErpStockOutRespVO|
|&emsp;&emsp;id|出库编号|integer(int64)||
|&emsp;&emsp;no|出库单号|string||
|&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;outTime|出库时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|出库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 11756,
		"no": "S123",
		"customerId": 3113,
		"customerName": "芋道",
		"outTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"status": 10,
		"remark": "随便",
		"fileUrl": "https://www.iocoder.cn/1.doc",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得其它出库单分页


**接口地址**:`/admin-api/erp/stock-out/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|出库单号|query|false|string||
|customerId|客户编号|query|false|string||
|outTime|出库时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockOutRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockOutRespVO|PageResultErpStockOutRespVO|
|&emsp;&emsp;list|数据|array|ErpStockOutRespVO|
|&emsp;&emsp;&emsp;&emsp;id|出库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|出库单号|string||
|&emsp;&emsp;&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;outTime|出库时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|出库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 11756,
				"no": "S123",
				"customerId": 3113,
				"customerName": "芋道",
				"outTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"status": 10,
				"remark": "随便",
				"fileUrl": "https://www.iocoder.cn/1.doc",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新其它出库单


**接口地址**:`/admin-api/erp/stock-out/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|outTime|出库时间|query|true|string||
|items|出库项列表|query|true|string||
|id|出库编号|query|false|string||
|customerId|客户编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新其它出库单的状态


**接口地址**:`/admin-api/erp/stock-out/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 其它入库单


## 创建其它入库单


**接口地址**:`/admin-api/erp/stock-in/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|inTime|入库时间|query|true|string||
|items|入库项列表|query|true|string||
|id|入库编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除其它入库单


**接口地址**:`/admin-api/erp/stock-in/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出其它入库单 Excel


**接口地址**:`/admin-api/erp/stock-in/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|入库单号|query|false|string||
|supplierId|供应商编号|query|false|string||
|inTime|入库时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得其它入库单


**接口地址**:`/admin-api/erp/stock-in/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpStockInRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpStockInRespVO|ErpStockInRespVO|
|&emsp;&emsp;id|入库编号|integer(int64)||
|&emsp;&emsp;no|入库单号|string||
|&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;inTime|入库时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|入库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 11756,
		"no": "S123",
		"supplierId": 3113,
		"supplierName": "芋道",
		"inTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"status": 10,
		"remark": "随便",
		"fileUrl": "https://www.iocoder.cn/1.doc",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得其它入库单分页


**接口地址**:`/admin-api/erp/stock-in/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|入库单号|query|false|string||
|supplierId|供应商编号|query|false|string||
|inTime|入库时间|query|false|string||
|status|状态|query|false|string||
|remark|备注|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpStockInRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpStockInRespVO|PageResultErpStockInRespVO|
|&emsp;&emsp;list|数据|array|ErpStockInRespVO|
|&emsp;&emsp;&emsp;&emsp;id|入库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|入库单号|string||
|&emsp;&emsp;&emsp;&emsp;supplierId|供应商编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;supplierName|供应商名称|string||
|&emsp;&emsp;&emsp;&emsp;inTime|入库时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;status|状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件 URL|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|入库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 11756,
				"no": "S123",
				"supplierId": 3113,
				"supplierName": "芋道",
				"inTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"status": 10,
				"remark": "随便",
				"fileUrl": "https://www.iocoder.cn/1.doc",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新其它入库单


**接口地址**:`/admin-api/erp/stock-in/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|inTime|入库时间|query|true|string||
|items|入库项列表|query|true|string||
|id|入库编号|query|false|string||
|supplierId|供应商编号|query|false|string||
|remark|备注|query|false|string||
|fileUrl|附件 URL|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新其它入库单的状态


**接口地址**:`/admin-api/erp/stock-in/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 收款单


## 创建收款单


**接口地址**:`/admin-api/erp/finance-receipt/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|receiptTime|收款时间|query|true|string||
|customerId|客户编号|query|true|string||
|accountId|收款账户编号|query|true|string||
|discountPrice|优惠金额，单位：元|query|true|string||
|items|收款项列表|query|true|string||
|id|编号|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除收款单


**接口地址**:`/admin-api/erp/finance-receipt/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出收款单 Excel


**接口地址**:`/admin-api/erp/finance-receipt/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|收款单编号|query|false|string||
|receiptTime|收款时间|query|false|string||
|customerId|客户编号|query|false|string||
|creator|创建者|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|accountId|收款账户编号|query|false|string||
|status|收款状态|query|false|string||
|remark|备注|query|false|string||
|bizNo|业务编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得收款单


**接口地址**:`/admin-api/erp/finance-receipt/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpFinanceReceiptRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpFinanceReceiptRespVO|ErpFinanceReceiptRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|收款单号|string||
|&emsp;&emsp;status|收款状态|integer(int32)||
|&emsp;&emsp;receiptTime|收款时间|string(date-time)||
|&emsp;&emsp;financeUserId|财务人员编号|integer(int64)||
|&emsp;&emsp;financeUserName|财务人员名称|string||
|&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;accountId|收款账户编号|integer(int64)||
|&emsp;&emsp;accountName|收款账户名称|string||
|&emsp;&emsp;totalPrice|合计价格，单位：元|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;receiptPrice|实际价格，单位：元|number||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|收款项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 23752,
		"no": "FKD888",
		"status": 1,
		"receiptTime": "",
		"financeUserId": 19690,
		"financeUserName": "张三",
		"customerId": 29399,
		"customerName": "小番茄公司",
		"accountId": 28989,
		"accountName": "张三",
		"totalPrice": 13832,
		"discountPrice": 11600,
		"receiptPrice": 10000,
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		]
	},
	"msg": ""
}
```


## 获得收款单分页


**接口地址**:`/admin-api/erp/finance-receipt/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|收款单编号|query|false|string||
|receiptTime|收款时间|query|false|string||
|customerId|客户编号|query|false|string||
|creator|创建者|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|accountId|收款账户编号|query|false|string||
|status|收款状态|query|false|string||
|remark|备注|query|false|string||
|bizNo|业务编号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpFinanceReceiptRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpFinanceReceiptRespVO|PageResultErpFinanceReceiptRespVO|
|&emsp;&emsp;list|数据|array|ErpFinanceReceiptRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|收款单号|string||
|&emsp;&emsp;&emsp;&emsp;status|收款状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;receiptTime|收款时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;financeUserId|财务人员编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;financeUserName|财务人员名称|string||
|&emsp;&emsp;&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|收款账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;accountName|收款账户名称|string||
|&emsp;&emsp;&emsp;&emsp;totalPrice|合计价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;receiptPrice|实际价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|收款项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 23752,
				"no": "FKD888",
				"status": 1,
				"receiptTime": "",
				"financeUserId": 19690,
				"financeUserName": "张三",
				"customerId": 29399,
				"customerName": "小番茄公司",
				"accountId": 28989,
				"accountName": "张三",
				"totalPrice": 13832,
				"discountPrice": 11600,
				"receiptPrice": 10000,
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				]
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新收款单


**接口地址**:`/admin-api/erp/finance-receipt/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|receiptTime|收款时间|query|true|string||
|customerId|客户编号|query|true|string||
|accountId|收款账户编号|query|true|string||
|discountPrice|优惠金额，单位：元|query|true|string||
|items|收款项列表|query|true|string||
|id|编号|query|false|string||
|financeUserId|财务人员编号|query|false|string||
|remark|备注|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新收款单的状态


**接口地址**:`/admin-api/erp/finance-receipt/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 收款单统计


## 收款单-时间段统计


**接口地址**:`/admin-api/erp/finance-receipt-statistics/order-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpFinanceReceiptTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpFinanceReceiptTimeSummaryRespVO|
|&emsp;&emsp;date|日期|string||
|&emsp;&emsp;receiptCount|收款单笔数|number||
|&emsp;&emsp;totalReceiptPrice|收款单金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2024-12-16",
			"receiptCount": 1,
			"totalReceiptPrice": 888
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 统计


## 数据总览统计


**接口地址**:`/admin-api/erp/overview-statistics/summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpOverviewStatisticsRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpOverviewStatisticsRespVO|ErpOverviewStatisticsRespVO|
|&emsp;&emsp;totalSalesAmount|累计销售订单金融|number||
|&emsp;&emsp;totalPurchaseAmount|累计采购订单金额|number||
|&emsp;&emsp;totalPaymentAmount|累计合计付款金额|number||
|&emsp;&emsp;totalReceiptAmount|累计合计收款金额|number||
|&emsp;&emsp;timeStatisticsList|每日金额统计|array|ErpOverviewTimeStatisticsRespVO|
|&emsp;&emsp;&emsp;&emsp;date|日期|string||
|&emsp;&emsp;&emsp;&emsp;salesAmount|销售金额|number||
|&emsp;&emsp;&emsp;&emsp;purchaseAmount|采购金额|number||
|&emsp;&emsp;&emsp;&emsp;paymentAmount|付款金额|number||
|&emsp;&emsp;&emsp;&emsp;receiptAmount|收款金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"totalSalesAmount": 1,
		"totalPurchaseAmount": 888,
		"totalPaymentAmount": 1,
		"totalReceiptAmount": 888,
		"timeStatisticsList": 888
	},
	"msg": ""
}
```


# 管理后台 - ERP 销售出库


## 创建销售出库


**接口地址**:`/admin-api/erp/sale-out/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|outTime|出库时间|query|true|string||
|orderId|销售订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|出库清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除销售出库


**接口地址**:`/admin-api/erp/sale-out/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出销售出库 Excel


**接口地址**:`/admin-api/erp/sale-out/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|outTime|出库时间|query|false|string||
|remark|备注|query|false|string||
|status|出库状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|receiptStatus|收款状态|query|false|string||
|receiptEnable|是否可收款|query|false|string||
|orderNo|销售单号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得销售出库


**接口地址**:`/admin-api/erp/sale-out/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpSaleOutRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpSaleOutRespVO|ErpSaleOutRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|出库单编号|string||
|&emsp;&emsp;status|出库状态|integer(int32)||
|&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;saleUserId|出库员编号|integer(int64)||
|&emsp;&emsp;outTime|出库时间|string(date-time)||
|&emsp;&emsp;orderId|销售订单编号|integer(int64)||
|&emsp;&emsp;orderNo|销售订单号|string||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;receiptPrice|已收款金额，单位：元|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;otherPrice|其它金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|出库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"customerId": 1724,
		"customerName": "芋道",
		"accountId": 0,
		"saleUserId": 1888,
		"outTime": "",
		"orderId": 17386,
		"orderNo": "XS001",
		"totalCount": 15663,
		"totalPrice": 24906,
		"receiptPrice": 7127,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"otherPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得销售出库分页


**接口地址**:`/admin-api/erp/sale-out/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|outTime|出库时间|query|false|string||
|remark|备注|query|false|string||
|status|出库状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|receiptStatus|收款状态|query|false|string||
|receiptEnable|是否可收款|query|false|string||
|orderNo|销售单号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpSaleOutRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpSaleOutRespVO|PageResultErpSaleOutRespVO|
|&emsp;&emsp;list|数据|array|ErpSaleOutRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|出库单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|出库状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;saleUserId|出库员编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;outTime|出库时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;orderId|销售订单编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderNo|销售订单号|string||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;receiptPrice|已收款金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;otherPrice|其它金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|出库项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"customerId": 1724,
				"customerName": "芋道",
				"accountId": 0,
				"saleUserId": 1888,
				"outTime": "",
				"orderId": 17386,
				"orderNo": "XS001",
				"totalCount": 15663,
				"totalPrice": 24906,
				"receiptPrice": 7127,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"otherPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新销售出库


**接口地址**:`/admin-api/erp/sale-out/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|outTime|出库时间|query|true|string||
|orderId|销售订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|出库清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新销售出库的状态


**接口地址**:`/admin-api/erp/sale-out/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 销售订单


## 创建销售订单


**接口地址**:`/admin-api/erp/sale-order/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|customerId|客户编号|query|true|string||
|orderTime|下单时间|query|true|string||
|id|编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|depositPrice|定金金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|订单清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除销售订单


**接口地址**:`/admin-api/erp/sale-order/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出销售订单 Excel


**接口地址**:`/admin-api/erp/sale-order/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|orderTime|下单时间|query|false|string||
|remark|备注|query|false|string||
|status|销售状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|outStatus|出库状态|query|false|string||
|returnStatus|退货状态|query|false|string||
|outEnable|是否可出库|query|false|string||
|returnEnable|是否可退货|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得销售订单


**接口地址**:`/admin-api/erp/sale-order/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpSaleOrderRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpSaleOrderRespVO|ErpSaleOrderRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|销售单编号|string||
|&emsp;&emsp;status|销售状态|integer(int32)||
|&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;saleUserId|销售员编号|integer(int64)||
|&emsp;&emsp;orderTime|下单时间|string(date-time)||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;depositPrice|定金金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|订单项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;outCount|销售出库数量|number||
|&emsp;&emsp;returnCount|销售退货数量|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"customerId": 1724,
		"customerName": "芋道",
		"accountId": 0,
		"saleUserId": 1888,
		"orderTime": "",
		"totalCount": 15663,
		"totalPrice": 24906,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"depositPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": "",
		"outCount": 100,
		"returnCount": 100
	},
	"msg": ""
}
```


## 获得销售订单分页


**接口地址**:`/admin-api/erp/sale-order/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|orderTime|下单时间|query|false|string||
|remark|备注|query|false|string||
|status|销售状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|outStatus|出库状态|query|false|string||
|returnStatus|退货状态|query|false|string||
|outEnable|是否可出库|query|false|string||
|returnEnable|是否可退货|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpSaleOrderRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpSaleOrderRespVO|PageResultErpSaleOrderRespVO|
|&emsp;&emsp;list|数据|array|ErpSaleOrderRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|销售单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|销售状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;saleUserId|销售员编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderTime|下单时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;depositPrice|定金金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|订单项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;&emsp;&emsp;outCount|销售出库数量|number||
|&emsp;&emsp;&emsp;&emsp;returnCount|销售退货数量|number||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"customerId": 1724,
				"customerName": "芋道",
				"accountId": 0,
				"saleUserId": 1888,
				"orderTime": "",
				"totalCount": 15663,
				"totalPrice": 24906,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"depositPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": "",
				"outCount": 100,
				"returnCount": 100
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新销售订单


**接口地址**:`/admin-api/erp/sale-order/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|customerId|客户编号|query|true|string||
|orderTime|下单时间|query|true|string||
|id|编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|depositPrice|定金金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|订单清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新销售订单的状态


**接口地址**:`/admin-api/erp/sale-order/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# 管理后台 - ERP 销售统计


## 获得销售单时间段统计


**接口地址**:`/admin-api/erp/sale-statistics/order-time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpSaleOrderTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpSaleOrderTimeSummaryRespVO|
|&emsp;&emsp;date|时间|string||
|&emsp;&emsp;orderCount|销售单数|integer(int64)||
|&emsp;&emsp;totalOrderPrice|销售金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"date": "2022-03",
			"orderCount": 1024,
			"totalOrderPrice": 102400
		}
	],
	"msg": ""
}
```


## 获得销售统计


**接口地址**:`/admin-api/erp/sale-statistics/summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpSaleSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpSaleSummaryRespVO|ErpSaleSummaryRespVO|
|&emsp;&emsp;todayPrice|今日销售金额|number||
|&emsp;&emsp;yesterdayPrice|昨日销售金额|number||
|&emsp;&emsp;monthPrice|本月销售金额|number||
|&emsp;&emsp;yearPrice|今年销售金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"todayPrice": 1024,
		"yesterdayPrice": 888,
		"monthPrice": 1024,
		"yearPrice": 88888
	},
	"msg": ""
}
```


## 获得销售时间段统计


**接口地址**:`/admin-api/erp/sale-statistics/time-summary`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|count|时间段数量|query|false|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultListErpSaleTimeSummaryRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||array|ErpSaleTimeSummaryRespVO|
|&emsp;&emsp;time|时间|string||
|&emsp;&emsp;price|销售金额|number||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": [
		{
			"time": "2022-03",
			"price": 1024
		}
	],
	"msg": ""
}
```


# 管理后台 - ERP 销售退货


## 创建销售退货


**接口地址**:`/admin-api/erp/sale-return/create`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|returnTime|退货时间|query|true|string||
|orderId|销售订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|退货清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultLong|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||integer(int64)|integer(int64)|
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": 0,
	"msg": ""
}
```


## 删除销售退货


**接口地址**:`/admin-api/erp/sale-return/delete`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|ids|编号数组|query|true|array|integer|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 导出销售退货 Excel


**接口地址**:`/admin-api/erp/sale-return/export-excel`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|returnTime|退货时间|query|false|string||
|remark|备注|query|false|string||
|status|退货状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|orderNo|销售单号|query|false|string||
|refundStatus|退款状态|query|false|string||
|refundEnable|是否可退款|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## 获得销售退货


**接口地址**:`/admin-api/erp/sale-return/get`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id|编号|query|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultErpSaleReturnRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||ErpSaleReturnRespVO|ErpSaleReturnRespVO|
|&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;no|退货单编号|string||
|&emsp;&emsp;status|退货状态|integer(int32)||
|&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;saleUserId|退货员编号|integer(int64)||
|&emsp;&emsp;returnTime|退货时间|string(date-time)||
|&emsp;&emsp;orderId|销售订单编号|integer(int64)||
|&emsp;&emsp;orderNo|销售订单号|string||
|&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;refundPrice|已退款金额，单位：元|number||
|&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;otherPrice|其它金额，单位：元|number||
|&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;items|退货项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;productNames|产品信息|string||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"id": 17386,
		"no": "XS001",
		"status": 2,
		"customerId": 1724,
		"customerName": "芋道",
		"accountId": 0,
		"saleUserId": 1888,
		"returnTime": "",
		"orderId": 17386,
		"orderNo": "XS001",
		"totalCount": 15663,
		"totalPrice": 24906,
		"refundPrice": 7127,
		"totalProductPrice": 7127,
		"totalTaxPrice": 7127,
		"discountPercent": 99.88,
		"discountPrice": 7127,
		"otherPrice": 7127,
		"fileUrl": "https://www.iocoder.cn",
		"remark": "你猜",
		"creator": "芋道",
		"creatorName": "芋道",
		"createTime": "",
		"items": [
			{
				"id": 11756,
				"warehouseId": 3113,
				"productId": 3113,
				"productPrice": 100,
				"count": 100,
				"remark": "随便",
				"productName": "巧克力",
				"productBarCode": "A9985",
				"productUnitName": "盒",
				"stockCount": 100
			}
		],
		"productNames": ""
	},
	"msg": ""
}
```


## 获得销售退货分页


**接口地址**:`/admin-api/erp/sale-return/page`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|pageNo|页码，从 1 开始|query|true|string||
|pageSize|每页条数，最大值为 100|query|true|string||
|no|销售单编号|query|false|string||
|customerId|客户编号|query|false|string||
|returnTime|退货时间|query|false|string||
|remark|备注|query|false|string||
|status|退货状态|query|false|string||
|creator|创建者|query|false|string||
|productId|产品编号|query|false|string||
|warehouseId|仓库编号|query|false|string||
|accountId|结算账号编号|query|false|string||
|orderNo|销售单号|query|false|string||
|refundStatus|退款状态|query|false|string||
|refundEnable|是否可退款|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultPageResultErpSaleReturnRespVO|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||PageResultErpSaleReturnRespVO|PageResultErpSaleReturnRespVO|
|&emsp;&emsp;list|数据|array|ErpSaleReturnRespVO|
|&emsp;&emsp;&emsp;&emsp;id|编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;no|退货单编号|string||
|&emsp;&emsp;&emsp;&emsp;status|退货状态|integer(int32)||
|&emsp;&emsp;&emsp;&emsp;customerId|客户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;customerName|客户名称|string||
|&emsp;&emsp;&emsp;&emsp;accountId|结算账户编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;saleUserId|退货员编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;returnTime|退货时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;orderId|销售订单编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;orderNo|销售订单号|string||
|&emsp;&emsp;&emsp;&emsp;totalCount|合计数量|number||
|&emsp;&emsp;&emsp;&emsp;totalPrice|最终合计价格|number||
|&emsp;&emsp;&emsp;&emsp;refundPrice|已退款金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalProductPrice|合计产品价格，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;totalTaxPrice|合计税额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;discountPercent|优惠率，百分比|number||
|&emsp;&emsp;&emsp;&emsp;discountPrice|优惠金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;otherPrice|其它金额，单位：元|number||
|&emsp;&emsp;&emsp;&emsp;fileUrl|附件地址|string||
|&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;creator|创建人|string||
|&emsp;&emsp;&emsp;&emsp;creatorName|创建人名称|string||
|&emsp;&emsp;&emsp;&emsp;createTime|创建时间|string(date-time)||
|&emsp;&emsp;&emsp;&emsp;items|退货项列表|array|Item|
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;id|出库项编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;warehouseId|仓库编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productId|产品编号|integer(int64)||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productPrice|产品单价|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;count|产品数量|number||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remark|备注|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productName|产品名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productBarCode|产品条码|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;productUnitName|产品单位名称|string||
|&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;stockCount|库存数量|number||
|&emsp;&emsp;&emsp;&emsp;productNames|产品信息|string||
|&emsp;&emsp;total|总量|integer(int64)||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": 17386,
				"no": "XS001",
				"status": 2,
				"customerId": 1724,
				"customerName": "芋道",
				"accountId": 0,
				"saleUserId": 1888,
				"returnTime": "",
				"orderId": 17386,
				"orderNo": "XS001",
				"totalCount": 15663,
				"totalPrice": 24906,
				"refundPrice": 7127,
				"totalProductPrice": 7127,
				"totalTaxPrice": 7127,
				"discountPercent": 99.88,
				"discountPrice": 7127,
				"otherPrice": 7127,
				"fileUrl": "https://www.iocoder.cn",
				"remark": "你猜",
				"creator": "芋道",
				"creatorName": "芋道",
				"createTime": "",
				"items": [
					{
						"id": 11756,
						"warehouseId": 3113,
						"productId": 3113,
						"productPrice": 100,
						"count": 100,
						"remark": "随便",
						"productName": "巧克力",
						"productBarCode": "A9985",
						"productUnitName": "盒",
						"stockCount": 100
					}
				],
				"productNames": ""
			}
		],
		"total": 0
	},
	"msg": ""
}
```


## 更新销售退货


**接口地址**:`/admin-api/erp/sale-return/update`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|returnTime|退货时间|query|true|string||
|orderId|销售订单编号|query|true|string||
|id|编号|query|false|string||
|accountId|结算账户编号|query|false|string||
|saleUserId|销售员编号|query|false|string||
|discountPercent|优惠率，百分比|query|false|string||
|otherPrice|其它金额，单位：元|query|false|string||
|fileUrl|附件地址|query|false|string||
|remark|备注|query|false|string||
|items|退货清单列表|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


## 更新销售退货的状态


**接口地址**:`/admin-api/erp/sale-return/update-status`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||query|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK|CommonResultBoolean|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- | 
|code||integer(int32)|integer(int32)|
|data||boolean||
|msg||string||


**响应示例**:
```javascript
{
	"code": 0,
	"data": true,
	"msg": ""
}
```


# trans-proxy-controller


## findById


**接口地址**:`/easyTrans/proxy/{targetClass}/findById/{id}`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|targetClass||path|true|string||
|id||path|true|string||
|uniqueField||query|true|string||
|targetFields||query|true|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```


## findByIds


**接口地址**:`/easyTrans/proxy/{targetClass}/findByIds`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|targetClass||path|true|string||
|ids||query|false|array|string|
|uniqueField||query|false|string||
|targetFields||query|false|array|string|


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- | 
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```