# Scenario Generation

基于 API 拓扑自动生成测试场景的服务。

## 核心理念

**"对着答案编题目"** - 先从拓扑中发现可能的 API 路径，再为路径生成测试主题。

### 工作流程

1. **发现路径** - 从 API 拓扑中发现可能的调用路径（基于实体和依赖关系）
2. **生成主题** - 使用 LLM 分析路径功能，生成测试主题和描述
3. **生成场景** - 为每条路径生成具体的测试场景（正常/异常）

```
API Topology (实体 + 依赖关系)
    ↓
发现可能的 API 路径
    ↓
LLM 生成测试主题 (对着答案编题目)
    ↓
生成具体测试场景
```

## 功能特性

- **智能路径发现**: 基于实体和依赖关系自动发现测试路径
- **LLM 主题生成**: 使用 LLM 为路径生成合适的测试主题
- **场景生成**: 为每条路径生成正常和异常测试场景
- **参数推断**: 自动推断 API 之间的参数依赖关系
- **场景验证**: 验证生成场景的完整性和合理性

## 快速开始

### 1. 基础用法（不使用 LLM）

```python
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService

# 准备拓扑数据（来自 api_topology）
topology_data = {
    'apis': [...],           # API 列表
    'dependencies': [...],   # API 依赖关系
    'entities': [...]        # 实体信息
}

# 从拓扑中发现路径并生成主题
path_generator = PathGenerator(llm_client=None)
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6,
    min_path_length=2
)

# 每条路径都包含自动生成的测试主题
# {
#   "path": ["login", "list_orders", "cancel_order"],
#   "test_objective": "测试 用户登录 到 取消订单 的流程",
#   "description": "验证 用户登录 -> 查询订单列表 -> 取消订单 的业务流程",
#   "scenario_type": "normal",
#   "parameter_flow": {...}
# }

# 为每条路径生成场景
scenario_service = ScenarioGenerationService()
all_scenarios = []

for path_info in paths:
    api_details = {api['operation_id']: api for api in topology_data['apis']}
    scenarios = scenario_service.generate_scenarios(
        api_path=path_info['path'],
        api_details=api_details,
        parameter_flow=path_info.get('parameter_flow', {}),
        scenario_types=['normal', 'exception'],
        count_per_type=2
    )
    all_scenarios.extend(scenarios)
```

### 2. 使用 LLM 增强主题生成

```python
from openai import OpenAI

# 配置 LLM 客户端
llm_client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

# 或使用国内 LLM
llm_client = OpenAI(
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 通义千问
)

# 创建带 LLM 的路径生成器
path_generator = PathGenerator(llm_client=llm_client)

# LLM 会分析路径中的 API 功能，生成更准确的测试主题
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6
)

# LLM 生成的主题示例：
# 路径: [login, list_orders, get_order_detail, cancel_order]
# -> test_objective: "测试用户取消订单的完整流程"
# -> description: "验证用户登录后查询订单列表，选择订单查看详情，最后成功取消订单"
```

### 3. 完整集成示例

```python
from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService

# Step 1: 规范化 API
norm_service = NormalizationService(use_entity_clustering=True)
norm_result = norm_service.normalize_swagger('your-swagger.json')

# Step 2: 构建拓扑图
topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=llm_client,
    use_entity_inference=True
)
build_result = topology_service.build_graph(norm_result['capabilities'])

# Step 3: 从 Neo4j 提取拓扑数据
with topology_service.builder.driver.session() as session:
    # 获取 APIs
    apis_result = session.run("""
        MATCH (a:API)
        RETURN a.operation_id as operation_id,
               a.method as method,
               a.path as path,
               a.summary as summary,
               a.parameters as parameters,
               a.responses as responses
    """)
    apis = [dict(record) for record in apis_result]

    # 获取依赖关系
    deps_result = session.run("""
        MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
        RETURN a1.operation_id as from,
               a2.operation_id as to,
               r.score as score
    """)
    dependencies = [dict(record) for record in deps_result]

    # 获取实体
    entities_result = session.run("""
        MATCH (e:Entity)
        OPTIONAL MATCH (a:API)-[:BELONGS_TO]->(e)
        RETURN e.name as name,
               collect(a.operation_id) as apis
    """)
    entities = [dict(record) for record in entities_result]

topology_data = {
    'apis': apis,
    'dependencies': dependencies,
    'entities': entities
}

# Step 4: 生成测试路径
path_generator = PathGenerator(llm_client=llm_client)
paths = path_generator.generate_paths(
    topology_data=topology_data,
    test_objectives=["测试核心业务流程"],
    max_paths=10
)

# Step 5: 生成测试场景
scenario_service = ScenarioGenerationService()
all_scenarios = []

for path_info in paths:
    api_details = {api['operation_id']: api for api in topology_data['apis']}
    scenarios = scenario_service.generate_scenarios(
        api_path=path_info['path'],
        api_details=api_details,
        parameter_flow=path_info.get('parameter_flow', {}),
        scenario_types=['normal', 'exception'],
        count_per_type=2
    )
    all_scenarios.extend(scenarios)

# Step 6: 保存结果
import json
with open('test_scenarios.json', 'w', encoding='utf-8') as f:
    json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

print(f"Generated {len(all_scenarios)} test scenarios!")
```

## 运行示例

```bash
# 基础示例（使用模拟数据）
cd scenario_generation
python example_usage.py

# 拓扑集成示例（使用模拟数据）
python example_with_topology.py

# 使用真实拓扑数据（需要 Neo4j 和 erp-server.json）
python run_with_real_topology.py
```

### 使用真实拓扑数据

要使用真实的 API 拓扑数据，需要：

1. **启动 Neo4j 数据库**
   ```bash
   # 使用 Docker
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. **准备 Swagger 文件**
   - 将 `erp-server.json` 放在项目根目录

3. **运行示例**
   ```bash
   cd scenario_generation
   python run_with_real_topology.py
   ```

4. **查看结果**
   - 生成的场景保存在 `output/real_topology_scenarios.json`

### 完整工作流程示例

```python
from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService

# Step 1: 规范化 API
norm_service = NormalizationService(use_entity_clustering=True)
norm_result = norm_service.normalize_swagger('erp-server.json')

# Step 2: 构建拓扑图
topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    use_entity_inference=True
)
build_result = topology_service.build_graph(norm_result['capabilities'])

# Step 3: 提取拓扑数据
with topology_service.builder.driver.session() as session:
    # 获取 APIs
    apis_result = session.run("""
        MATCH (a:API)
        RETURN a.operation_id, a.method, a.path, a.summary,
               a.parameters, a.responses, a.entity, a.role
    """)
    apis = [dict(record) for record in apis_result]

    # 获取依赖关系
    deps_result = session.run("""
        MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
        RETURN a1.operation_id as from, a2.operation_id as to, r.score as score
    """)
    dependencies = [dict(record) for record in deps_result]

    # 获取实体
    entities_result = session.run("""
        MATCH (e:Entity)
        OPTIONAL MATCH (a:API)-[:BELONGS_TO]->(e)
        RETURN e.name as name, collect(a.operation_id) as apis
    """)
    entities = [dict(record) for record in entities_result]

topology_data = {
    'apis': apis,
    'dependencies': dependencies,
    'entities': entities
}

# Step 4: 从拓扑中发现路径并生成主题
path_generator = PathGenerator(llm_client=None)
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6,
    min_path_length=2
)

# Step 5: 生成测试场景
scenario_service = ScenarioGenerationService()
all_scenarios = []

for path_info in paths:
    api_details = {api['operation_id']: api for api in topology_data['apis']}
    scenarios = scenario_service.generate_scenarios(
        api_path=path_info['path'],
        api_details=api_details,
        parameter_flow=path_info.get('parameter_flow', {}),
        scenario_types=['normal', 'exception'],
        count_per_type=2
    )
    all_scenarios.extend(scenarios)

# Step 6: 保存结果
import json
with open('test_scenarios.json', 'w', encoding='utf-8') as f:
    json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

topology_service.close()
```

## 输出格式

生成的场景包含以下信息：

```json
{
  "topology_summary": {
    "total_apis": 4,
    "total_dependencies": 3,
    "total_entities": 2
  },
  "paths": [
    {
      "path": ["login", "list_orders", "cancel_order"],
      "description": "测试订单取消流程",
      "scenario_type": "normal",
      "test_objective": "验证用户可以成功取消订单",
      "parameter_flow": {
        "list_orders": {
          "token": "login.response.token"
        },
        "cancel_order": {
          "order_id": "list_orders.response.orders[0].id",
          "token": "login.response.token"
        }
      }
    }
  ],
  "scenarios": [
    {
      "api_path": ["login", "list_orders", "cancel_order"],
      "scenario": {
        "title": "正常场景: 用户取消订单",
        "description": "用户登录后查询订单列表，选择一个订单进行取消",
        "scenario_type": "normal",
        "steps": ["login", "list_orders", "cancel_order"],
        "parameter_bindings": {...},
        "expected_outcome": "订单成功取消",
        "dependency_map": {...}
      },
      "validation": {
        "is_valid": true,
        "issues": [],
        "warnings": [],
        "score": 1.0
      }
    }
  ],
  "statistics": {
    "total_paths": 3,
    "total_scenarios": 6,
    "valid_scenarios": 6,
    "average_score": 0.95
  }
}
```

## 核心组件

### PathGenerator

负责从 API 拓扑生成测试路径。

**策略**:
- **LLM 模式**: 使用 LLM 理解业务逻辑，生成智能路径
- **启发式模式**: 基于规则生成路径（无需 LLM）
  - 识别入口点（登录/认证 API）
  - 跟随依赖关系构建路径
  - 生成随机路径以提高覆盖率

### ScenarioGenerationService

为测试路径生成具体的测试场景。

**功能**:
- 生成正常场景和异常场景
- 推断参数绑定关系
- 验证场景完整性
- 计算场景质量分数

### ScenarioValidator

验证生成场景的质量。

**检查项**:
- 必填字段完整性
- 步骤数量匹配
- 参数绑定正确性
- 异常场景注入点
- 路径覆盖率

## 配置选项

### PathGenerator 配置

```python
path_generator = PathGenerator(
    llm_client=llm_client  # None 表示使用启发式方法
)

paths = path_generator.generate_paths(
    topology_data=topology_data,
    test_objectives=["目标1", "目标2"],  # 测试目标列表
    max_paths=5,                         # 最多生成路径数
    max_path_length=5                    # 每条路径最大长度
)
```

### ScenarioGenerationService 配置

```python
scenario_service = ScenarioGenerationService(
    llm_config=None,        # LLM 配置（可选）
    api_topology=None       # API 拓扑信息（可选）
)

scenarios = scenario_service.generate_scenarios(
    api_path=["api1", "api2", "api3"],
    api_details={...},
    parameter_flow={...},
    scenario_types=['normal', 'exception'],  # 场景类型
    count_per_type=2                         # 每种类型生成数量
)
```

## 最佳实践

1. **使用 LLM**: 如果可能，使用 LLM 可以生成更智能的测试路径
2. **明确测试目标**: 提供清晰的测试目标可以帮助生成更有针对性的路径
3. **控制路径长度**: 过长的路径可能难以维护，建议 3-6 步
4. **验证场景**: 始终检查生成场景的验证结果
5. **迭代优化**: 根据实际测试结果调整生成策略

## 故障排除

### 问题: 生成的路径不合理

**解决方案**:
- 检查拓扑数据的依赖关系是否正确
- 使用 LLM 模式以获得更智能的路径
- 调整 `test_objectives` 使其更具体

### 问题: 参数推断不准确

**解决方案**:
- 确保 API 的 `parameters` 和 `responses` 字段完整
- 手动指定 `parameter_flow` 覆盖自动推断
- 检查字段命名是否一致

### 问题: 场景验证失败

**解决方案**:
- 查看 `validation.issues` 了解具体问题
- 检查 API 路径是否存在于拓扑中
- 确保必填字段都已提供

## 扩展开发

### 自定义路径生成策略

```python
class CustomPathGenerator(PathGenerator):
    def _generate_heuristic(self, topology_data, max_paths, max_path_length):
        # 实现自定义逻辑
        pass
```

### 自定义场景验证规则

```python
class CustomValidator(ScenarioValidator):
    def validate(self, scenario, api_path, api_details):
        result = super().validate(scenario, api_path, api_details)
        # 添加自定义验证
        return result
```

## 相关文档

- [API Normalization](../api_normalization/README.md)
- [API Topology](../api_topology/README.md)
- [Models](./models.py) - 数据模型定义

## License

MIT
