# Flora-Evaluation 模块化架构

基于统合方案实现的完整模块化架构，支持从 API 规范化到自动优化的端到端流程。

## 项目结构

```
Flora-evaluation/
├── core/                          # 核心框架
│   ├── __init__.py
│   ├── module_adapter.py          # 模块适配器基类
│   ├── pipeline_orchestrator.py   # 流程编排器
│   └── config_manager.py          # 配置管理器
│
├── common/                        # 通用组件
│   ├── __init__.py
│   └── schemas.py                 # 数据模型定义
│
├── adapters/                      # 模块适配器
│   ├── __init__.py
│   ├── normalization_adapter.py   # Stage 1: API 规范化
│   ├── topology_adapter.py        # Stage 2: API 拓扑
│   ├── entimap_adapter.py         # Stage 3A: 数据库映射
│   ├── scenario_adapter.py        # Stage 3B: 场景生成
│   ├── agent_build_adapter.py     # Stage 4A: Agent 构建
│   ├── mock_adapter.py            # Stage 4B: Mock 服务
│   ├── evaluation_adapter.py      # Stage 5: 评估测试
│   └── optimization_adapter.py    # Stage 6: 自动调优
│
├── config/                        # 配置文件
│   └── pipeline_config.yaml       # 流程配置
│
├── examples/                      # 示例代码
│   ├── full_pipeline.py           # 完整流程示例
│   └── partial_pipeline.py        # 部分流程示例
│
├── api_normalization/             # Stage 1: API 规范化（已有）
├── api_topology/                  # Stage 2: API 拓扑（已有）
├── ddl_entimap/                   # Stage 3A: 数据库映射（已有）
├── scenario_generation/           # Stage 3B: 场景生成（已有）
├── auto_agents_build/             # Stage 4A: Agent 构建（已有）
├── stateful_mock/                 # Stage 4B: Mock 服务（已有）
├── coop_eval_actual/              # Stage 5: 评估测试（已有）
├── automatic_prompt/              # Stage 6: 自动调优（已有）
│
├── main.py                        # 主入口
├── cli.py                         # CLI 工具
└── README.md                      # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install pyyaml pydantic click requests neo4j openai
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# LLM API 配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 数据库配置
DATABASE_URL=mysql://user:pass@host:port/database
```

### 3. 运行完整流程

```bash
# 使用主入口
python main.py

# 或使用 CLI
python cli.py run
```

## CLI 命令

### 运行流程

```bash
# 运行完整流程
python cli.py run

# 运行部分流程
python cli.py run --start normalization --end topology

# 运行单个阶段
python cli.py run-stage normalization

# 指定环境
python cli.py run --env production
```

### 管理和查询

```bash
# 列出所有阶段
python cli.py list-stages

# 查看状态
python cli.py status

# 验证输入文件
python cli.py validate input/swagger.json

# 导出结果
python cli.py export --format json --output output/export
```

## 使用示例

### 示例 1: 完整流程

```python
from core.pipeline_orchestrator import PipelineOrchestrator
from adapters import *

# 创建编排器
orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')

# 注册所有模块
orchestrator.register_module('normalization', NormalizationAdapter())
orchestrator.register_module('topology', TopologyAdapter())
# ... 注册其他模块

# 运行完整流程
results = orchestrator.run_pipeline()
```

### 示例 2: 部分流程

```python
# 只运行测试分支（3B -> 4B -> 5）
orchestrator.register_module('scenario_generation', ScenarioAdapter())
orchestrator.register_module('mock_service', MockAdapter())
orchestrator.register_module('evaluation', EvaluationAdapter())

results = orchestrator.run_pipeline(
    start_stage='scenario_generation',
    end_stage='evaluation'
)
```

### 示例 3: 单个阶段

```python
# 只运行 API 规范化
orchestrator.register_module('normalization', NormalizationAdapter())

results = orchestrator.run_pipeline(
    start_stage='normalization',
    end_stage='normalization'
)
```

## 流程说明

### Stage 1: API 规范化
- 输入: Swagger/OpenAPI 文档
- 输出: 标准化的 API 能力模型
- 模块: `api_normalization/`

### Stage 2: API 拓扑构建
- 输入: API 能力模型
- 输出: Neo4j 依赖关系图
- 模块: `api_topology/`

### Stage 3A: 数据库映射
- 输入: API 能力模型
- 输出: 实体-表映射、Golden SQL
- 模块: `ddl_entimap/`

### Stage 3B: 场景生成
- 输入: API 拓扑图
- 输出: 测试场景
- 模块: `scenario_generation/`

### Stage 4A: Agent 构建
- 输入: API 能力模型 + 数据库映射
- 输出: Agent 系统（存储到 Neo4j）
- 模块: `auto_agents_build/`

### Stage 4B: Mock 服务
- 输入: API 能力模型
- 输出: Mock API 服务
- 模块: `stateful_mock/`

### Stage 5: 评估测试
- 输入: 测试场景 + Agent 系统
- 输出: 评估结果
- 模块: `coop_eval_actual/`

### Stage 6: 自动调优
- 输入: 评估结果
- 输出: 优化建议 + 优化后的 Prompts
- 模块: `automatic_prompt/`

## 配置说明

### 基础配置 (pipeline_config.yaml)

```yaml
pipeline:
  name: "Flora-Evaluation-Pipeline"
  version: "1.0.0"

stages:
  normalization:
    module: "adapters.normalization_adapter.NormalizationAdapter"
    enabled: true
    config:
      use_hdbscan: true
    input:
      type: "file"
      path: "input/swagger.json"
    output:
      type: "file"
      path: "output/stage1/capabilities.json"
```

### 环境特定配置

- `pipeline_config.development.yaml` - 开发环境
- `pipeline_config.production.yaml` - 生产环境

## 核心特性

### 1. 模块化设计
- 每个阶段独立封装
- 统一的适配器接口
- 易于替换和扩展

### 2. 标准化数据格式
- 使用 Pydantic 定义数据模型
- 类型安全
- 自动验证

### 3. 灵活的流程控制
- 支持完整流程
- 支持部分流程
- 支持单阶段执行

### 4. 配置驱动
- YAML 配置文件
- 环境变量支持
- 多环境配置

### 5. 易于扩展
- 添加新模块只需实现 ModuleAdapter
- 注册到编排器即可使用

## 扩展开发

### 添加新模块

1. 创建适配器类：

```python
from core.module_adapter import ModuleAdapter

class CustomAdapter(ModuleAdapter):
    def process(self, input_data: Dict, config: Dict) -> Dict:
        # 实现处理逻辑
        pass

    def validate_input(self, input_data: Dict) -> bool:
        # 实现输入验证
        pass

    def get_metadata(self) -> Dict:
        # 返回模块元数据
        pass
```

2. 在配置文件中添加阶段：

```yaml
stages:
  custom_stage:
    module: "adapters.custom_adapter.CustomAdapter"
    enabled: true
    config: {}
    input:
      type: "file"
      path: "input/data.json"
    output:
      type: "file"
      path: "output/result.json"
```

3. 注册并使用：

```python
orchestrator.register_module('custom_stage', CustomAdapter())
```

## 故障排除

### 问题: 模块导入失败

```bash
# 确保项目根目录在 Python 路径中
export PYTHONPATH="${PYTHONPATH}:/path/to/Flora-evaluation"
```

### 问题: Neo4j 连接失败

```bash
# 检查 Neo4j 是否运行
docker ps | grep neo4j

# 检查环境变量
echo $NEO4J_URI
```

### 问题: 配置文件找不到

```bash
# 确保在项目根目录运行
cd /path/to/Flora-evaluation
python main.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
