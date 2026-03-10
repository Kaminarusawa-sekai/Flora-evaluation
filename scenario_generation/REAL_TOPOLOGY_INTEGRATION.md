# 集成真实拓扑数据 - 完成总结

## 新增功能

### 1. 真实拓扑数据集成

在 `example_with_topology.py` 中新增了 `example_with_real_topology()` 函数，实现了完整的真实数据流程：

```python
def example_with_real_topology():
    """演示从真实拓扑数据生成测试场景"""
    # 1. 规范化 API (从 erp-server.json)
    # 2. 构建拓扑图 (Neo4j)
    # 3. 提取拓扑数据 (APIs, dependencies, entities)
    # 4. 发现路径并生成主题
    # 5. 生成测试场景
    # 6. 保存结果
```

### 2. 独立运行脚本

创建了 `run_with_real_topology.py`，可以独立运行真实拓扑示例：

```bash
cd scenario_generation
python run_with_real_topology.py
```

## 完整工作流程

```
erp-server.json (Swagger 文件)
    ↓
API Normalization (规范化)
    ↓
API Topology (构建 Neo4j 图)
    ↓
提取拓扑数据
  - APIs (operation_id, method, path, summary, parameters, responses)
  - Dependencies (from, to, score)
  - Entities (name, apis)
    ↓
Path Generator (发现路径)
  - 实体内路径
  - 跨实体路径
  - 随机路径
    ↓
Theme Generator (生成主题)
  - LLM 分析路径功能
  - 生成测试主题和描述
    ↓
Scenario Generator (生成场景)
  - 正常场景
  - 异常场景
    ↓
output/real_topology_scenarios.json
```

## 数据流示例

### 从 Neo4j 提取的数据

```python
# APIs
{
    'operation_id': 'createOrder',
    'method': 'POST',
    'path': '/api/orders',
    'summary': '创建订单',
    'parameters': ['user_id', 'product_id', 'quantity'],
    'responses': {'order_id': 'string', 'status': 'string'},
    'entity': 'Order',
    'role': 'PRODUCER'
}

# Dependencies
{
    'from': 'createOrder',
    'to': 'getUser',
    'score': 0.85,
    'filtered_by': 'Order->User'
}

# Entities
{
    'name': 'Order',
    'apis': ['createOrder', 'getOrder', 'updateOrder', 'cancelOrder']
}
```

### 发现的路径

```python
{
    'path': ['login', 'getUser', 'createOrder', 'getOrder'],
    'test_objective': '测试用户创建订单流程',  # 自动生成
    'description': '验证用户登录后创建订单并查询订单详情',  # 自动生成
    'scenario_type': 'normal',
    'parameter_flow': {
        'getUser': {'token': 'login.response.token'},
        'createOrder': {
            'user_id': 'getUser.response.user_id',
            'token': 'login.response.token'
        },
        'getOrder': {
            'order_id': 'createOrder.response.order_id',
            'token': 'login.response.token'
        }
    }
}
```

### 生成的场景

```python
{
    'api_path': ['login', 'getUser', 'createOrder', 'getOrder'],
    'scenario': {
        'title': '正常场景: 用户创建订单',
        'description': '测试场景覆盖 4 个API操作: 用户登录 -> 获取用户信息 -> 创建订单 -> 查询订单',
        'scenario_type': 'normal',
        'steps': ['login', 'getUser', 'createOrder', 'getOrder'],
        'parameter_bindings': {...},
        'expected_outcome': '所有API调用成功，工作流正常完成'
    },
    'validation': {
        'is_valid': true,
        'issues': [],
        'warnings': [],
        'score': 1.0
    }
}
```

## 使用方法

### 方法 1: 使用独立脚本

```bash
cd scenario_generation
python run_with_real_topology.py
```

### 方法 2: 在代码中调用

```python
from scenario_generation.example_with_topology import example_with_real_topology

example_with_real_topology()
```

### 方法 3: 自定义集成

```python
from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService

# 按照完整工作流程自定义实现
# (参考 example_with_real_topology 函数)
```

## 前置要求

1. **Neo4j 数据库**
   ```bash
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. **Swagger 文件**
   - 将 `erp-server.json` 放在项目根目录

3. **Python 依赖**
   ```bash
   pip install neo4j openai
   ```

## 配置选项

### Neo4j 连接

在 `example_with_real_topology()` 中修改：

```python
topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",  # 修改为你的 Neo4j 地址
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=None,
    use_entity_inference=True
)
```

### LLM 配置（可选）

```python
from openai import OpenAI

llm_client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

path_generator = PathGenerator(llm_client=llm_client)
```

### 路径生成参数

```python
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,           # 最多生成路径数
    max_path_length=6,      # 每条路径最大长度
    min_path_length=2       # 每条路径最小长度
)
```

### 场景生成参数

```python
scenarios = scenario_service.generate_scenarios(
    api_path=path_info['path'],
    api_details=api_details,
    parameter_flow=path_info.get('parameter_flow', {}),
    scenario_types=['normal', 'exception'],  # 场景类型
    count_per_type=2                         # 每种类型生成数量
)
```

## 输出文件

### output/real_topology_scenarios.json

```json
{
  "metadata": {
    "source_file": "erp-server.json",
    "total_apis": 150,
    "total_dependencies": 320,
    "total_entities": 25
  },
  "topology_summary": {
    "total_apis": 150,
    "total_dependencies": 320,
    "total_entities": 25
  },
  "paths": [
    {
      "path": ["login", "createOrder", "getOrder"],
      "test_objective": "测试用户创建订单流程",
      "description": "验证用户登录后创建订单并查询订单详情",
      "scenario_type": "normal",
      "parameter_flow": {...}
    }
  ],
  "scenarios": [
    {
      "api_path": [...],
      "scenario": {...},
      "validation": {...}
    }
  ],
  "statistics": {
    "total_paths": 10,
    "total_scenarios": 20,
    "valid_scenarios": 20,
    "average_score": 0.95
  }
}
```

## 示例运行结果

```
================================================================================
Example: Generate Test Scenarios from Real API Topology
================================================================================

[Step 1] Normalizing APIs with entity-centric clustering
  [OK] Normalized 150 APIs
  [OK] Identified 150 capabilities

[Step 2] Building topology graph with Filter Strategy
  [OK] Build Results:
    APIs created: 150
    Entities created: 25
    Entity relationships: 45
    API dependencies: 320

[Step 3] Extracting topology data from Neo4j
  [OK] Extracted 150 APIs
  [OK] Extracted 320 dependencies
  [OK] Extracted 25 entities

[Step 4] Discovering paths from topology and generating themes
  [OK] Discovered 10 paths with generated themes:

    Path 1: login -> getUser -> createOrder -> getOrder
      Test Objective: 测试用户创建订单流程
      Description: 验证用户登录后创建订单并查询订单详情...

[Step 5] Generating test scenarios for each path
  [OK] Generated 20 scenarios

[Step 6] Test Scenario Summary
================================================================================
=== Scenario 1 ===
Path: login -> getUser -> createOrder -> getOrder
Type: normal
Title: 正常场景: 用户创建订单
Valid: True
Score: 1.00

[OK] Results saved to output/real_topology_scenarios.json

================================================================================
Statistics:
  Total APIs: 150
  Total Dependencies: 320
  Total Entities: 25
  Total Paths: 10
  Total Scenarios: 20
  Valid Scenarios: 20
  Average Score: 0.95
================================================================================
```

## 优势

1. **真实数据** - 使用实际的 API 拓扑关系
2. **自动发现** - 无需手动指定测试路径
3. **智能主题** - 根据路径功能自动生成测试主题
4. **高覆盖率** - 基于拓扑关系发现所有可能的路径
5. **可扩展** - 易于添加新的路径发现策略

## 文件清单

- `example_with_topology.py` - 包含 `example_with_real_topology()` 函数
- `run_with_real_topology.py` - 独立运行脚本
- `path_generator.py` - 路径发现和主题生成
- `scenario_generation_service.py` - 场景生成服务
- `README.md` - 使用文档
- `REFACTOR_SUMMARY.md` - 重构总结

## 下一步

1. 优化路径发现算法（更智能的路径选择）
2. 改进 LLM prompt（生成更准确的主题）
3. 添加路径质量评分（优先选择高质量路径）
4. 支持更多路径发现策略（基于业务规则等）
5. 添加场景执行器（实际运行测试场景）
