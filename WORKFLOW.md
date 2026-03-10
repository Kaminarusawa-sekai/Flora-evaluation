# Flora Evaluation - 完整工作流程

## 系统概述

Flora Evaluation 是一个完整的 API 测试场景自动生成系统，包含三个核心模块：

1. **API Normalization** - API 规范化与实体聚类
2. **API Topology** - API 依赖关系拓扑分析
3. **Scenario Generation** - 测试场景智能生成

## 核心理念

**"对着答案编题目"** - 先从拓扑中发现可能的 API 路径（答案），再为路径生成测试主题（题目）。

## 完整工作流程

```
Swagger/OpenAPI 文档
        ↓
[API Normalization]
  - 解析 API 定义
  - 提取能力特征
  - 实体聚类
        ↓
规范化的 API 能力列表
        ↓
[API Topology]
  - 构建依赖图 (Neo4j)
  - 实体关系推断
  - API 依赖分析
        ↓
API 拓扑数据 (实体 + 依赖关系)
        ↓
[Path Generator]
  - 从拓扑中发现可能的路径
  - 基于实体内的强关联 API
  - 跨实体的强依赖路径
        ↓
候选路径列表
        ↓
[Theme Generator (LLM)]
  - 分析路径中的 API 功能
  - 生成测试主题和描述
  - "对着答案编题目"
        ↓
路径 + 测试主题
        ↓
[Scenario Generation]
  - 正常场景生成
  - 异常场景生成
  - 场景验证
        ↓
测试场景 JSON
```

## 快速开始

### 前置要求

```bash
# Python 依赖
pip install openai neo4j

# Neo4j 数据库（用于拓扑分析）
# 可选：如果不使用拓扑分析，可以直接使用模拟数据
```

### 完整示例

```python
from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService
from openai import OpenAI
import json

# ============================================================================
# Step 1: API 规范化
# ============================================================================
print("Step 1: Normalizing APIs...")

norm_service = NormalizationService(use_entity_clustering=True)
norm_result = norm_service.normalize_swagger('erp-server.json')

print(f"  - Normalized {norm_result['statistics']['total_apis']} APIs")
print(f"  - Identified {norm_result['statistics']['total_capabilities']} capabilities")

# ============================================================================
# Step 2: 构建 API 拓扑图
# ============================================================================
print("\nStep 2: Building API topology...")

# 配置 LLM（可选）
llm_client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=llm_client,
    use_entity_inference=True
)

build_result = topology_service.build_graph(norm_result['capabilities'])

print(f"  - Created {build_result['apis_created']} API nodes")
print(f"  - Created {build_result['entities_created']} entity nodes")
print(f"  - Inferred {build_result['api_dependencies']} API dependencies")

# ============================================================================
# Step 3: 提取拓扑数据
# ============================================================================
print("\nStep 3: Extracting topology data...")

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

print(f"  - Extracted {len(apis)} APIs")
print(f"  - Extracted {len(dependencies)} dependencies")
print(f"  - Extracted {len(entities)} entities")

# ============================================================================
# Step 4: 从拓扑中发现路径并生成测试主题
# ============================================================================
print("\nStep 4: Discovering paths and generating themes...")
print("  核心理念：对着答案编题目")
print("    1. 从拓扑中发现可能的 API 路径")
print("    2. LLM 为路径生成测试主题")

path_generator = PathGenerator(llm_client=llm_client)

paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6,
    min_path_length=2
)

print(f"  - Discovered {len(paths)} paths with themes")
for i, path in enumerate(paths[:3], 1):
    print(f"    Path {i}: {' -> '.join(path['path'])}")
    print(f"      Theme: {path['test_objective']}")

# ============================================================================
# Step 5: 生成测试场景
# ============================================================================
print("\nStep 5: Generating test scenarios...")

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

print(f"  - Generated {len(all_scenarios)} test scenarios")

# ============================================================================
# Step 6: 保存结果
# ============================================================================
print("\nStep 6: Saving results...")

output_data = {
    'metadata': {
        'source_file': 'erp-server.json',
        'generated_at': '2026-03-06',
        'total_apis': len(apis),
        'total_paths': len(paths),
        'total_scenarios': len(all_scenarios)
    },
    'topology_summary': {
        'apis': len(apis),
        'dependencies': len(dependencies),
        'entities': len(entities)
    },
    'paths': paths,
    'scenarios': [
        {
            'api_path': result['api_path'],
            'scenario': result['scenario'],
            'validation': result['validation']
        }
        for result in all_scenarios
    ],
    'statistics': {
        'total_paths': len(paths),
        'total_scenarios': len(all_scenarios),
        'valid_scenarios': sum(1 for r in all_scenarios if r['validation']['is_valid']),
        'average_score': sum(r['validation']['score'] for r in all_scenarios) / len(all_scenarios) if all_scenarios else 0
    }
}

with open('test_scenarios_complete.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"  - Saved to test_scenarios_complete.json")

# ============================================================================
# 统计信息
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"APIs Analyzed:        {len(apis)}")
print(f"Dependencies Found:   {len(dependencies)}")
print(f"Entities Identified:  {len(entities)}")
print(f"Test Paths Generated: {len(paths)}")
print(f"Test Scenarios:       {len(all_scenarios)}")
print(f"Valid Scenarios:      {output_data['statistics']['valid_scenarios']}")
print(f"Average Score:        {output_data['statistics']['average_score']:.2f}")
print("=" * 80)

# 清理
topology_service.close()
```

## 简化版本（无需 Neo4j）

如果不想使用 Neo4j，可以使用模拟的拓扑数据：

```python
from scenario_generation.path_generator import PathGenerator
from scenario_generation import ScenarioGenerationService
import json

# 手动构建拓扑数据（或从其他来源获取）
topology_data = {
    'apis': [
        {
            'operation_id': 'login',
            'method': 'POST',
            'path': '/api/auth/login',
            'summary': '用户登录',
            'parameters': ['username', 'password'],
            'responses': {'user_id': 'string', 'token': 'string'}
        },
        # ... 更多 API
    ],
    'dependencies': [
        {'from': 'list_orders', 'to': 'login', 'score': 0.9},
        # ... 更多依赖
    ],
    'entities': [
        {'name': 'User', 'apis': ['login']},
        # ... 更多实体
    ]
}

# 从拓扑中发现路径并生成主题
path_generator = PathGenerator(llm_client=None)  # 使用启发式方法
paths = path_generator.generate_paths(
    topology_data=topology_data,
    max_paths=10,
    max_path_length=6,
    min_path_length=2
)

# 每条路径都包含自动生成的测试主题
for path in paths:
    print(f"Path: {' -> '.join(path['path'])}")
    print(f"Theme: {path['test_objective']}")
    print(f"Description: {path['description']}")

# 生成场景
scenario_service = ScenarioGenerationService()
all_scenarios = []

for path_info in paths:
    api_details = {api['operation_id']: api for api in topology_data['apis']}
    scenarios = scenario_service.generate_scenarios(
        api_path=path_info['path'],
        api_details=api_details,
        parameter_flow=path_info.get('parameter_flow', {}),
        scenario_types=['normal', 'exception'],
        count_per_type=1
    )
    all_scenarios.extend(scenarios)

# 保存结果
with open('test_scenarios.json', 'w', encoding='utf-8') as f:
    json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

print(f"Generated {len(all_scenarios)} test scenarios!")
```

## 运行示例

```bash
# 1. API 规范化示例
cd api_normalization
python example_usage.py

# 2. API 拓扑分析示例（需要 Neo4j）
cd api_topology
python example_usage.py

# 3. 场景生成示例（基础）
cd scenario_generation
python example_usage.py

# 4. 场景生成示例（集成拓扑）
cd scenario_generation
python example_with_topology.py
```

## 模块说明

### 1. API Normalization

**功能**:
- 解析 Swagger/OpenAPI 文档
- 提取 API 能力特征
- 实体聚类（基于字段引用）
- 可选 LLM 增强聚类

**输出**:
```json
{
  "capabilities": [
    {
      "operation_id": "createOrder",
      "entity": "Order",
      "role": "PRODUCER",
      "parameters": [...],
      "responses": [...]
    }
  ]
}
```

### 2. API Topology

**功能**:
- 构建 Neo4j 图数据库
- 实体关系推断
- API 依赖分析
- 路径查找

**输出**:
- Neo4j 图数据库
- API 节点、实体节点、依赖关系

### 3. Scenario Generation

**功能**:
- 智能路径生成（LLM/启发式）
- 测试场景生成（正常/异常）
- 参数流推断
- 场景验证

**输出**:
```json
{
  "paths": [...],
  "scenarios": [
    {
      "api_path": ["login", "list_orders", "cancel_order"],
      "scenario": {
        "title": "正常场景: 取消订单",
        "steps": [...],
        "parameter_bindings": {...},
        "expected_outcome": "..."
      },
      "validation": {
        "is_valid": true,
        "score": 0.95
      }
    }
  ]
}
```

## 配置选项

### LLM 配置

支持任何 OpenAI 兼容的 API：

```python
# OpenAI
llm_client = OpenAI(api_key="sk-...")

# 通义千问
llm_client = OpenAI(
    api_key="sk-...",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# DeepSeek
llm_client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)
```

### Neo4j 配置

```python
topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
```

## 最佳实践

1. **使用实体聚类**: 启用 `use_entity_clustering=True` 可以获得更好的 API 分组
2. **使用 LLM**: 如果可能，使用 LLM 可以显著提高路径和场景质量
3. **明确测试目标**: 提供具体的测试目标可以生成更有针对性的场景
4. **验证结果**: 始终检查生成场景的验证分数和警告
5. **迭代优化**: 根据实际测试结果调整生成参数

## 故障排除

### Neo4j 连接失败

```bash
# 检查 Neo4j 是否运行
docker ps | grep neo4j

# 启动 Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### LLM API 调用失败

- 检查 API key 是否正确
- 检查网络连接
- 系统会自动降级到启发式方法

### 生成的场景不合理

- 检查拓扑数据的完整性
- 使用 LLM 模式
- 调整 `test_objectives` 使其更具体

## 项目结构

```
Flora-evaluation/
├── api_normalization/          # API 规范化模块
│   ├── normalization_service.py
│   ├── capability_extractor.py
│   ├── entity_clusterer.py
│   └── example_usage.py
├── api_topology/               # API 拓扑分析模块
│   ├── topology_service.py
│   ├── graph_builder.py
│   ├── path_finder.py
│   └── example_usage.py
├── scenario_generation/        # 场景生成模块
│   ├── scenario_generation_service.py
│   ├── path_generator.py
│   ├── scenario_generator.py
│   ├── scenario_validator.py
│   ├── example_usage.py
│   └── example_with_topology.py
└── README.md                   # 本文档
```

## 相关文档

- [API Normalization README](api_normalization/README.md)
- [API Topology README](api_topology/README.md)
- [Scenario Generation README](scenario_generation/README.md)

## License

MIT
