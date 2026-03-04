# Document Parsing and Test Synthesis System

Four independent service modules for enriching test data and providing support services to the Flora-evaluation framework.

## Modules

### 1. api_normalization - API Semantic Normalization
Generates standardized API capability models from Swagger documents.

**Components:**
- `SwaggerParser`: Parse Swagger/OpenAPI documents
- `SemanticClusterer`: Cluster APIs by semantic similarity
- `CapabilityExtractor`: Extract capability models
- `NormalizationService`: Main service interface

**Usage:**
```python
from api_normalization import NormalizationService

service = NormalizationService()
capabilities = service.normalize_swagger("swagger.json")
```

### 2. api_topology - API Topology Graph
Build and query API dependency relationship graphs.

**Components:**
- `GraphBuilder`: Build dependency graph in Neo4j
- `PathFinder`: Find paths between APIs
- `TopologyService`: Main service interface

**Usage:**
```python
from api_topology import TopologyService

service = TopologyService(neo4j_uri="bolt://localhost:7687")
service.build_graph(capabilities['capabilities'])
paths = service.find_paths("login", "delete_order")
```

### 3. scenario_generation - Test Scenario Generation
Generate business test scenarios from API paths.

**Components:**
- `ScenarioGenerator`: Generate scenarios using LLM
- `ScenarioValidator`: Validate scenario quality
- `ScenarioGenerationService`: Main service interface

**Usage:**
```python
from scenario_generation import ScenarioGenerationService

service = ScenarioGenerationService()
scenarios = service.generate_scenarios(api_path, count=3)
```

### 4. stateful_mock - Stateful Mock Service
Provide mock API environment with state management.

**Components:**
- `MockServer`: FastAPI dynamic server
- `StateManager`: SQLite state management
- `MockService`: Service management interface

**Usage:**
```python
from stateful_mock import MockService

service = MockService(db_path="mock_state.db")
service.start_server(capabilities['capabilities'], port=8000)
```

## Dependencies

```bash
pip install pyyaml scikit-learn fastapi uvicorn neo4j
```

## Example

See `example_usage.py` for a complete workflow demonstration.

## Integration with Flora-evaluation

These modules can be imported and used in the test framework:

```python
# In coop_eval_actual/
from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation import ScenarioGenerationService
from stateful_mock import MockService
```
