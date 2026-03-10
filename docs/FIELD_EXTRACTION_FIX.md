# 字段提取适配修复

## 问题

原代码假设 API 数据中有 `request_fields` 和 `response_fields` 字段，但实际数据结构是：

```python
api = {
    'operation_id': 'get_/admin-api/erp/finance-statistics/bill-time-summary',
    'method': 'GET',
    'path': 'http://172.24.0.9:8080/admin-api/erp/finance-statistics/bill-time-summary',
    'parameters': {
        'path': [],
        'query': [
            {'name': '状态码', 'type': 'string', 'required': False},
            {'name': '200', 'type': 'array', 'required': False}
        ],
        'body': [],
        'header': []
    }
}
```

导致 `KeyError: 'response_fields'` 错误。

## 解决方案

### 1. 添加统一的字段提取方法

在 `graph_builder.py` 中添加了两个新方法：

#### `_extract_request_fields(api: Dict) -> List[Dict]`

支持多种数据格式：
1. **直接的 `request_fields`**（如果存在）
2. **`request_schema`**（使用 `path_extractor.flatten_schema` 展平）
3. **`parameters`**（提取 `body`, `query`, `path`）

```python
def _extract_request_fields(self, api: Dict) -> List[Dict]:
    fields = []

    # 方式1: 直接的 request_fields
    if 'request_fields' in api:
        return api['request_fields']

    # 方式2: request_schema
    if 'request_schema' in api:
        schema = api['request_schema']
        if schema:
            fields.extend(self.path_extractor.flatten_schema(schema))

    # 方式3: parameters (body, query, path)
    if 'parameters' in api:
        params = api['parameters']
        if isinstance(params, dict):
            for param in params.get('body', []):
                fields.append({
                    'name': param.get('name', ''),
                    'type': param.get('type', 'string'),
                    'path': param.get('name', ''),
                    'required': param.get('required', False)
                })
            # ... query, path 同理

    return fields
```

#### `_extract_response_fields(api: Dict) -> List[Dict]`

支持多种数据格式：
1. **直接的 `response_fields`**（如果存在）
2. **`response_schema`**（单个 schema）
3. **`response_schemas`**（多个状态码的 schemas，优先使用 2xx）

```python
def _extract_response_fields(self, api: Dict) -> List[Dict]:
    fields = []

    # 方式1: 直接的 response_fields
    if 'response_fields' in api:
        return api['response_fields']

    # 方式2: response_schema (单个)
    if 'response_schema' in api:
        schema = api['response_schema']
        if schema:
            fields.extend(self.path_extractor.flatten_schema(schema))

    # 方式3: response_schemas (多个状态码)
    if 'response_schemas' in api:
        schemas = api['response_schemas']
        if isinstance(schemas, dict):
            # 优先使用 2xx 状态码的响应
            for status_code in ['200', '201', '204']:
                if status_code in schemas:
                    schema = schemas[status_code]
                    if schema:
                        fields.extend(self.path_extractor.flatten_schema(schema))
                    break

    return fields
```

### 2. 修改 API 节点创建逻辑

在 `build()` 方法中，使用新的提取方法：

```python
# 修改前
response_fields = api.get('response_fields', [])
if api.get('response_schema'):
    response_fields = self.path_extractor.flatten_schema(api['response_schema'])

# 修改后
response_fields = self._extract_response_fields(api)
request_fields = self._extract_request_fields(api)
```

### 3. 简化 `_extract_field_names_from_api()`

由于字段已经在 `api_map` 中统一提取，简化字段名提取逻辑：

```python
def _extract_field_names_from_api(self, api: Dict, schema_type: str = 'request') -> Set[str]:
    fields = set()

    if schema_type == 'request':
        request_fields = api.get('request_fields', [])
        for field in request_fields:
            if isinstance(field, dict):
                name = field.get('name') or field.get('path', '')
                if name:
                    # 提取最后一部分作为字段名（处理嵌套路径）
                    field_name = name.split('.')[-1] if '.' in name else name
                    fields.add(field_name.lower())
    else:
        # response 同理
        ...

    return fields
```

## 支持的数据格式

### 格式1: parameters（实际数据格式）

```python
{
    'operation_id': 'getFinanceStats',
    'method': 'GET',
    'path': '/finance-statistics/summary',
    'parameters': {
        'query': [
            {'name': 'supplierId', 'type': 'string'},
            {'name': 'status', 'type': 'string'}
        ],
        'body': [],
        'path': [],
        'header': []
    }
}
```

### 格式2: request_schema / response_schemas

```python
{
    'operation_id': 'createOrder',
    'method': 'POST',
    'path': '/order/create',
    'request_schema': {
        'type': 'object',
        'properties': {
            'supplierCode': {'type': 'string'},
            'productList': {'type': 'array'}
        }
    },
    'response_schemas': {
        '200': {
            'type': 'object',
            'properties': {
                'orderId': {'type': 'string'},
                'status': {'type': 'string'}
            }
        }
    }
}
```

### 格式3: 直接的 request_fields / response_fields

```python
{
    'operation_id': 'updateOrder',
    'method': 'PUT',
    'path': '/order/update',
    'request_fields': [
        {'name': 'orderId', 'type': 'string'},
        {'name': 'status', 'type': 'string'}
    ],
    'response_fields': [
        {'name': 'success', 'type': 'boolean'}
    ]
}
```

## 测试

运行测试验证字段提取：

```bash
conda activate flora
python test_field_extraction.py
```

预期输出：
```
测试用例1: parameters 格式
提取的请求字段: [{'name': 'supplierId', 'type': 'string', ...}, ...]

测试用例2: request_schema 格式
提取的请求字段: [{'name': 'supplierCode', 'type': 'string', ...}, ...]
提取的响应字段: [{'name': 'orderId', 'type': 'string', ...}, ...]

测试用例3: 直接的 request_fields/response_fields
提取的请求字段: [{'name': 'orderId', 'type': 'string', ...}, ...]
提取的响应字段: [{'name': 'success', 'type': 'boolean', ...}, ...]
```

## 优势

✅ **兼容多种数据格式**：自动适配不同的 API 数据结构
✅ **降级机制**：优先使用直接字段，然后尝试 schema，最后尝试 parameters
✅ **统一接口**：所有字段提取都通过统一的方法
✅ **向后兼容**：不影响已有的测试用例

## 修改的文件

- `api_topology/graph_builder.py`
  - 添加 `_extract_request_fields()`
  - 添加 `_extract_response_fields()`
  - 修改 `build()` 中的字段提取逻辑
  - 简化 `_extract_field_names_from_api()`

## 总结

成功修复了字段提取的兼容性问题，现在可以处理：
- ✅ 实际数据格式（`parameters`）
- ✅ Schema 格式（`request_schema`, `response_schemas`）
- ✅ 直接字段格式（`request_fields`, `response_fields`）

所有格式都能正确提取字段并用于后续的依赖推断。
