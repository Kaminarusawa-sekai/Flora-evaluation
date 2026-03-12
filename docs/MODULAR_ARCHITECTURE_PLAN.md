# 模块化架构设计方案

## 1. 整体流程架构

```
API规范文档
    ↓
[api_normalization] → 归一化API定义
    ↓
[api_topology] → 构建API依赖图
    ↓
    ├─────────────────────┬─────────────────────┐
    ↓                     ↓                     ↓
[ddl_entimap]      [scenario_generation]  [stateful_mock]
数据库关系映射        测试场景生成           API模拟服务
    ↓                     ↓                     ↓
[auto_agents_build]      └──────────┬──────────┘
自动构建项目                        ↓
    ↓                        [coop_eval_actual]
    └──────────────────────→  评估测试
                                    ↓
                            [automatic_prompt]
                            自动化调优
```

## 2. 核心设计原则

### 2.1 模块独立性
- 每个模块通过标准接口通信
- 使用适配器模式隔离具体实现
- 支持模块热插拔替换

### 2.2 数据流标准化
- 定义统一的数据模型（schemas）
- 每个阶段输入输出明确
- 支持中间结果持久化

### 2.3 配置驱动
- 使用 YAML 配置文件定义流程
- 支持部分流程执行
- 灵活的模块组合

## 3. 模块接口定义

### 3.1 Stage 1: API Normalization
**输入**: Swagger/OpenAPI 文档
**输出**: 
```python
{
    "capabilities": [
        {
            "resource": "finance-statistics",
            "apis": [...],
            "unified_schema": {...},
            "dependencies": [...]
        }
    ]
}
```

### 3.2 Stage 2: API Topology
**输入**: Stage 1 输出
**输出**:
```python
{
    "entities": [...],
    "relationships": [...],
    "dependency_graph": {...}
}
```

### 3.3 Stage 3A: Database Mapping (ddl_entimap)
**输入**: Stage 2 输出 + 数据库连接
**输出**:
```python
{
    "entity_mappings": [
        {
            "table_name": "erp_bookkeeping_voucher",
            "entity_name": "finance-statistics",
            "relation_type": "association",
            "relation_score": 72,
            "field_mappings": [...]
        }
    ],
    "golden_sqls": [...],
    "vanna_training_data": {...}
}
```

### 3.4 Stage 3B: Scenario Generation
**输入**: Stage 2 输出
**输出**:
```python
{
    "test_scenarios": [
        {
            "scenario_id": "...",
            "path": [...],
            "test_data": {...}
        }
    ]
}
```

### 3.5 Stage 3C: Stateful Mock
**输入**: Stage 2 输出 + Stage 3B 输出
**输出**: Mock Server 实例

### 3.6 Stage 4: Auto Agents Build
**输入**: Stage 2 + Stage 3A 输出
**输出**: 
```python
{
    "agents": [...],
    "neo4j_graph": {...},
    "build_artifacts": {...}
}
```

### 3.7 Stage 5: COOP Evaluation
**输入**: Stage 4 输出 + Stage 3B/3C 输出
**输出**:
```python
{
    "evaluation_results": {...},
    "metrics": {...}
}
```

### 3.8 Stage 6: Prompt Optimization
**输入**: Stage 5 输出
**输出**:
```python
{
    "optimized_prompts": {...},
    "performance_improvements": {...}
}
```

## 4. 适配器层设计

### 4.1 基础适配器接口
```python
class ModuleAdapter(ABC):
    @abstractmethod
    def process(self, input_data: Dict, config: Dict) -> Dict:
        """处理输入数据"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict:
        """获取模块元数据"""
        pass
```

### 4.2 适配器注册表
```python
ADAPTER_REGISTRY = {
    'api_normalization': NormalizationAdapter,
    'api_topology': TopologyAdapter,
    'ddl_entimap': EntiMapAdapter,
    'scenario_generation': ScenarioAdapter,
    'stateful_mock': MockAdapter,
    'auto_agents_build': AgentBuildAdapter,
    'coop_evaluation': EvaluationAdapter,
    'prompt_optimization': OptimizationAdapter
}
```

## 5. 配置文件结构

```yaml
# config/pipeline_config.yaml
pipeline:
  name: "Flora Evaluation Pipeline"
  version: "1.0.0"
  
stages:
  - name: "api_normalization"
    module: "api_normalization"
    enabled: true
    config:
      input_file: "erp-server.json"
      llm_provider: "qwen"
      
  - name: "api_topology"
    module: "api_topology"
    enabled: true
    depends_on: ["api_normalization"]
    config:
      use_llm: true
      
  - name: "database_mapping"
    module: "ddl_entimap"
    enabled: true
    depends_on: ["api_topology"]
    config:
      db_url: "${DB_URL}"
      api_key: "${API_KEY}"
      
  - name: "scenario_generation"
    module: "scenario_generation"
    enabled: true
    depends_on: ["api_topology"]
    
  - name: "stateful_mock"
    module: "stateful_mock"
    enabled: true
    depends_on: ["api_topology", "scenario_generation"]
    
  - name: "auto_agents_build"
    module: "auto_agents_build"
    enabled: true
    depends_on: ["api_topology", "database_mapping"]
    config:
      neo4j_url: "${NEO4J_URL}"
      
  - name: "coop_evaluation"
    module: "coop_evaluation"
    enabled: true
    depends_on: ["auto_agents_build", "scenario_generation"]
    config:
      neo4j_url: "${NEO4J_URL}"
      
  - name: "prompt_optimization"
    module: "prompt_optimization"
    enabled: false
    depends_on: ["coop_evaluation"]
```

## 6. 模块替换策略

### 6.1 替换点识别
每个模块都可以被替换，只要新模块：
1. 实现相同的适配器接口
2. 输入输出格式兼容
3. 通过验证测试

### 6.2 替换示例
```python
# 替换 LLM 提供商
class CustomLLMAdapter(ModuleAdapter):
    def process(self, input_data, config):
        # 使用自定义 LLM
        pass

# 注册新适配器
ADAPTER_REGISTRY['api_normalization'] = CustomLLMAdapter
```

### 6.3 版本管理
```python
# 支持多版本共存
ADAPTER_REGISTRY = {
    'api_normalization:v1': NormalizationAdapterV1,
    'api_normalization:v2': NormalizationAdapterV2,
}
```

## 7. 数据持久化策略

### 7.1 中间结果存储
```
output/
├── stage1_normalization/
│   ├── capabilities.json
│   └── metadata.json
├── stage2_topology/
│   ├── entities.json
│   ├── relationships.json
│   └── graph.json
├── stage3a_database_mapping/
│   ├── entity_mappings.json
│   ├── golden_sqls.json
│   └── vanna_data.json
├── stage3b_scenarios/
│   └── test_scenarios.json
├── stage4_agents/
│   └── agent_definitions.json
└── stage5_evaluation/
    └── results.json
```

### 7.2 缓存机制
- 支持跳过已完成的阶段
- 增量更新机制
- 缓存失效策略

## 8. 错误处理与恢复

### 8.1 阶段级错误处理
```python
try:
    result = adapter.process(input_data, config)
except Exception as e:
    logger.error(f"Stage {stage_name} failed: {e}")
    # 保存错误状态
    # 支持从失败点恢复
```

### 8.2 回滚机制
- 保存每个阶段的快照
- 支持回滚到任意阶段
- 清理中间产物

## 9. 监控与日志

### 9.1 执行追踪
```python
{
    "pipeline_id": "...",
    "start_time": "...",
    "stages": [
        {
            "name": "api_normalization",
            "status": "completed",
            "duration": 12.5,
            "output_size": 1024
        }
    ]
}
```

### 9.2 性能指标
- 每个阶段的执行时间
- 内存使用情况
- API 调用次数和成本

## 10. 测试策略

### 10.1 单元测试
- 每个适配器独立测试
- Mock 外部依赖

### 10.2 集成测试
- 端到端流程测试
- 使用测试数据集

### 10.3 回归测试
- 模块替换后的兼容性测试
- 性能回归测试

## 11. 实施路线图

### Phase 1: 核心框架 (已完成)
- ✅ 基础适配器接口
- ✅ Pipeline Orchestrator
- ✅ 配置管理

### Phase 2: 模块适配 (进行中)
- ✅ NormalizationAdapter
- ✅ TopologyAdapter
- 🔧 EntiMapAdapter (修复中)
- ⏳ ScenarioAdapter
- ⏳ MockAdapter
- ⏳ AgentBuildAdapter
- ⏳ EvaluationAdapter

### Phase 3: 增强功能
- ⏳ 缓存机制
- ⏳ 错误恢复
- ⏳ 监控面板

### Phase 4: 优化与扩展
- ⏳ 性能优化
- ⏳ 分布式执行
- ⏳ 插件系统

## 12. 关键注意事项

### 12.1 Neo4j 集成
- auto_agents_build 将结果存储到 Neo4j
- coop_evaluation 从 Neo4j 读取 agent 定义
- 需要确保数据模型一致性

### 12.2 LLM 成本控制
- 缓存 LLM 调用结果
- 支持本地模型
- 批量处理优化

### 12.3 数据安全
- 敏感信息脱敏
- 数据库凭证管理
- 审计日志

## 13. 下一步行动

1. ✅ 修复 EntiMapAdapter 的数据结构问题
2. 完善 field_mappings 的提取逻辑
3. 实现 ScenarioAdapter
4. 实现 MockAdapter
5. 实现 AgentBuildAdapter
6. 实现 EvaluationAdapter
7. 端到端测试
8. 性能优化
