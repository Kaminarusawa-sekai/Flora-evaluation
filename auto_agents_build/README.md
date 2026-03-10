# Agent 自动化构建系统

基于四层架构的 Agent 自动化构建系统，从 API 到 Agent 的端到端自动化生成。

## 架构概览

```
auto_agents_build/
├── role_alignment/          # Layer 2: 职能对齐层
├── org_fusion/              # Layer 3: 组织融合层
├── artifact_generation/     # Layer 4: 代码生成层
├── shared/                  # 共享组件
├── orchestrator/            # 总控编排器
├── config.yaml              # 配置文件
└── example_usage.py         # 示例用法
```

## 四层架构

### Layer 2: 职能对齐层
将技术性 API 能力映射到业务性职能角色

**模块:**
- `functional_meta_library.py` - 全领域职能元库
- `domain_detector.py` - 领域探测器
- `semantic_alignment_engine.py` - 语义对齐引擎
- `template_loader.py` - 模板加载器
- `capability_slotter.py` - 能力填装器
- `gap_analyzer.py` - 差异分析器
- `constraint_injector.py` - 约束注入器
- `role_manifest_generator.py` - 清单生成器

**输出:** `role_manifest.json`

### Layer 3: 组织融合层
基于组合模式，将职能角色组织成层级化的 Agent 体系

**模块:**
- `capability_unit_registry.py` - 能力单元注册中心
- `agent_encapsulator.py` - Agent 标准封装器
- `capability_composer.py` - 能力组合器
- `capability_promoter.py` - 能力晋升器
- `topology_builder.py` - 拓扑结构构建器
- `supervisor_synthesizer.py` - 主管合成器
- `capability_access_controller.py` - 能力访问控制器
- `org_blueprint_generator.py` - 组织蓝图生成器

**输出:** `org_blueprint.json`

### Layer 4: 代码生成层
将逻辑设计转化为可执行的 Prompt、配置和测试用例

**模块:**
- `prompt_factory.py` - Prompt 工厂
- `manifest_generator.py` - 配置清单生成器
- `rag_knowledge_linker.py` - RAG 知识链接器
- `monitoring_config_generator.py` - 监控配置生成器

**输出:**
- `prompts/` - Agent Prompt 文件
- `manifest.json` - 运行时配置
- `knowledge_links.json` - 知识库链接
- `monitoring/` - 监控配置

## 快速开始

### 1. 安装依赖

```bash
pip install openai anthropic faiss-cpu numpy pyyaml jsonschema
```

### 2. 配置

编辑 `config.yaml`，设置 LLM API Key:

```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: your-api-key-here
```

或通过环境变量:

```bash
export OPENAI_API_KEY=your-api-key-here
```

### 3. 运行示例

```bash
python example_usage.py
```

### 4. 查看输出

```
output/
├── layer2/
│   └── role_manifest.json
├── layer3/
│   └── org_blueprint.json
├── layer4/
│   ├── prompts/
│   ├── manifest.json
│   ├── knowledge_links.json
│   └── monitoring/
├── build_report.txt
└── build_report.html
```

## 使用方法

### 基本用法

```python
from orchestrator import PipelineOrchestrator

# 准备 API 能力列表
api_capabilities = [
    {
        "id": "api_001",
        "name": "创建订单",
        "description": "创建新的销售订单",
        "method": "POST",
        "path": "/api/order/create",
        "tags": ["订单", "销售"]
    },
    # ... 更多 API
]

# 运行流水线
orchestrator = PipelineOrchestrator()
result = orchestrator.run_pipeline(api_capabilities, output_dir="./output")

# 检查结果
if result['success']:
    print("构建成功！")
else:
    print(f"构建失败: {result['error']}")
```

### 分步执行

```python
from orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

# 只执行 Layer 2
layer2_result = orchestrator._execute_layer2(api_capabilities, "./output")

# 只执行 Layer 3
layer3_result = orchestrator._execute_layer3(layer2_result, "./output")

# 只执行 Layer 4
layer4_result = orchestrator._execute_layer4(layer3_result, layer2_result, "./output")
```

## 核心特性

### 1. 智能领域识别
- 关键词匹配 + LLM 语义分析
- 支持多领域混合场景
- 自动识别主导领域和次要领域

### 2. 语义对齐
- 向量粗筛（Embedding + 余弦相似度）
- LLM 终审（基于业务逻辑推理）
- 处理一对多、多对一映射

### 3. 组合模式
- **横向复用**: 同级 Agent 共享能力
- **纵向晋升**: 上级能力抽象
- **跨域组合**: 战略级能力协调

### 4. 约束注入
- 自动识别敏感 API
- 基于规则的约束生成
- LLM 生成业务契约

### 5. 自动化生成
- Agent Prompt 自动生成
- 运行时配置自动生成
- 监控配置自动生成
- RAG 知识库自动链接

## 配置说明

### LLM 配置

支持多种 LLM 提供商:

```yaml
llm:
  provider: openai  # openai/claude/qwen
  model: gpt-4
  temperature: 0.3
  max_tokens: 2000
```

### 向量存储配置

支持多种向量存储:

```yaml
vector_store:
  type: faiss  # faiss/milvus/chroma
  dimension: 1536
  index_path: ./data/vectors
```

## 扩展

### 添加新领域模板

```python
from role_alignment import FunctionalMetaLibrary

library = FunctionalMetaLibrary()

library.add_domain("CustomDomain", {
    "domain_name": "自定义领域",
    "keywords": ["关键词1", "关键词2"],
    "roles": [
        {
            "role_name": "自定义角色",
            "level": "specialist",
            "responsibilities": ["职责1", "职责2"],
            "required_capabilities": ["能力1", "能力2"]
        }
    ]
})

library.save()
```

### 自定义验证规则

```python
from orchestrator import Validator

validator = Validator()

# 添加自定义验证
def custom_validation(data):
    # 自定义验证逻辑
    return True, []

# 使用自定义验证
is_valid, errors = custom_validation(data)
```

## 输出说明

### role_manifest.json
包含职能角色定义、API 分配、约束规则等

### org_blueprint.json
包含 Agent 定义、能力注册表、拓扑结构、访问控制矩阵等

### prompts/
每个 Agent 的 Prompt 文件，包含角色定义、工具说明、执行规范等

### manifest.json
运行时配置，包含 Agent 配置、API 端点、认证信息等

## 故障排除

### 1. LLM API 调用失败
- 检查 API Key 是否正确
- 检查网络连接
- 检查 API 配额

### 2. 向量存储错误
- 确保已安装 faiss-cpu
- 检查索引路径是否可写

### 3. 验证失败
- 检查输入 API 格式是否正确
- 查看详细错误信息

## 性能优化

### 1. 批量处理
系统自动批量处理 API 和 Agent，减少 LLM 调用次数

### 2. 缓存机制
向量 embedding 自动缓存，避免重复计算

### 3. 并发控制
能力访问控制器提供并发锁机制

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
