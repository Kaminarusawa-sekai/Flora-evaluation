"""
数据模型定义 - 定义各阶段的标准输入输出格式
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============ Stage 1 输出 ============
class APIDefinition(BaseModel):
    """单个 API 定义"""
    operation_id: str
    method: str
    path: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Dict = Field(default_factory=dict)
    responses: Dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class Capability(BaseModel):
    """能力模型"""
    id: str
    name: str
    type: str
    description: Optional[str] = None
    resource: Optional[str] = None  # Only for composite capabilities
    primary_action: Optional[str] = None  # Only for composite capabilities
    action_verb: Optional[str] = None  # Only for atomic capabilities
    tags: List[str] = Field(default_factory=list)
    apis: List[Dict]
    api_count: int = 0
    unified_schema: Dict
    lifecycle: Dict
    connectivity_score: float = 0.0
    typical_workflow: Optional[str] = None


class Stage1Output(BaseModel):
    """Stage 1 标准输出"""
    capabilities: List[Capability]
    statistics: Dict
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 2 输出 ============
class APIDependency(BaseModel):
    """API 依赖关系"""
    from_api: str
    to_api: str
    score: float
    type: str  # FIELD_MATCH, LLM_SEMANTIC, CRUD_FLOW
    fields: List[str] = Field(default_factory=list)


class EntityRelation(BaseModel):
    """实体关系"""
    from_entity: str
    to_entity: str
    confidence: float
    inferred_from: str  # LLM_INFERENCE, FIELD_REFERENCE, PATH_HIERARCHY


class Stage2Output(BaseModel):
    """Stage 2 标准输出"""
    apis: List[Dict]
    dependencies: List[APIDependency]
    entities: List[Dict]
    entity_relations: List[EntityRelation]
    graph_stats: Dict
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 3A 输出 ============
class FieldMapping(BaseModel):
    """字段映射"""
    db_column: str
    api_field: str
    role: str  # business, technical, hidden_logic
    confidence: float


class TableMapping(BaseModel):
    """表映射"""
    table_name: str
    entity_name: str
    relation_type: str  # core, association, log, irrelevant
    relation_score: float
    field_mappings: List[FieldMapping]


class GoldenSQL(BaseModel):
    """Golden SQL"""
    question: str
    sql: str
    entity: str


class Stage3AOutput(BaseModel):
    """Stage 3A 标准输出"""
    entity_mappings: List[TableMapping]
    golden_sqls: List[GoldenSQL]
    vanna_training_data: Dict
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 3B 输出 ============
class ParameterBinding(BaseModel):
    """参数绑定"""
    target_field: str
    source_path: str  # e.g., "login.response.token"
    transform: Optional[str] = None


class TestStep(BaseModel):
    """测试步骤"""
    api: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    expected_status: int = 200


class TestScenario(BaseModel):
    """测试场景"""
    scenario_id: str
    title: str
    description: str
    scenario_type: str  # normal, exception
    api_path: List[str]
    steps: List[TestStep]
    expected_outcome: str
    validation_score: float = 1.0


class Stage3BOutput(BaseModel):
    """Stage 3B 标准输出"""
    scenarios: List[TestScenario]
    paths: List[Dict]
    statistics: Dict
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 4A 输出 ============
class AgentDefinition(BaseModel):
    """Agent 定义"""
    agent_id: str
    name: str
    role: str
    level: str  # specialist, manager, director
    capabilities: List[str]
    prompt: str
    tools: List[str]


class OrgBlueprint(BaseModel):
    """组织蓝图"""
    agents: List[AgentDefinition]
    hierarchy: Dict
    access_control: Dict


class Stage4AOutput(BaseModel):
    """Stage 4A 标准输出"""
    org_blueprint: Dict
    role_manifest: Dict
    prompts: Dict[str, str]
    manifest: Dict
    neo4j_location: Optional[str] = None
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 4B 输出 ============
class MockEndpoint(BaseModel):
    """Mock 端点"""
    operation_id: str
    method: str
    path: str
    handler: str


class Stage4BOutput(BaseModel):
    """Stage 4B 标准输出"""
    service_url: str
    endpoints: List[MockEndpoint]
    state_db_path: str
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 5 输出 ============
class TestResult(BaseModel):
    """单个测试结果"""
    test_id: str
    scenario_id: str
    success: bool
    execution_time: float
    api_calls: int
    errors: List[str]
    metrics: Dict


class Stage5Output(BaseModel):
    """Stage 5 标准输出"""
    test_results: List[TestResult]
    summary: Dict
    success_rate: float
    average_execution_time: float
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ Stage 6 输出 ============
class OptimizationSuggestion(BaseModel):
    """优化建议"""
    target: str  # agent_id or module_name
    issue: str
    suggestion: str
    priority: str  # high, medium, low
    estimated_impact: float


class Stage6Output(BaseModel):
    """Stage 6 标准输出"""
    suggestions: List[OptimizationSuggestion]
    optimized_prompts: Dict[str, str]
    performance_improvement: Dict
    should_rebuild: bool
    metadata: Dict
    timestamp: datetime = Field(default_factory=datetime.now)
