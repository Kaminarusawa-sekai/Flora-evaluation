"""
场景生成模块适配器
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage3BOutput, TestScenario, TestStep
from typing import Dict


class ScenarioAdapter(ModuleAdapter):
    """场景生成模块适配器"""

    def __init__(self):
        self.service = None
        self.path_generator = None

    def process(self, input_data: Dict, config: Dict) -> Stage3BOutput:
        from scenario_generation import ScenarioGenerationService
        from scenario_generation.path_generator import PathGenerator

        # 初始化服务
        if not self.service:
            self.service = ScenarioGenerationService()

        # 初始化 LLM 客户端（如果配置了）
        llm_client = None
        if config.get('llm_client'):
            from openai import OpenAI
            llm_client = OpenAI(**config['llm_client'])

        if not self.path_generator:
            self.path_generator = PathGenerator(llm_client=llm_client)

        # 从 Neo4j 或输入数据提取拓扑信息
        topology_data = self._extract_topology(input_data, config)

        # 生成路径
        paths = self.path_generator.generate_paths(
            topology_data=topology_data,
            max_paths=config.get('max_paths', 10),
            max_path_length=config.get('max_path_length', 6),
            min_path_length=config.get('min_path_length', 2)
        )

        # 为每条路径生成场景
        all_scenarios = []
        api_details = {api['operation_id']: api for api in topology_data['apis']}

        for path_info in paths:
            scenarios = self.service.generate_scenarios(
                api_path=path_info['path'],
                api_details=api_details,
                parameter_flow=path_info.get('parameter_flow', {}),
                scenario_types=config.get('scenario_types', ['normal', 'exception']),
                count_per_type=config.get('count_per_type', 2)
            )
            all_scenarios.extend(scenarios)

        # 转换为标准格式
        test_scenarios = []
        for scenario in all_scenarios:
            test_scenarios.append(TestScenario(
                scenario_id=scenario.get('scenario_id', f"scenario_{len(test_scenarios)}"),
                title=scenario.get('title', ''),
                description=scenario.get('description', ''),
                scenario_type=scenario.get('scenario_type', 'normal'),
                api_path=scenario.get('api_path', []),
                steps=[TestStep(**step) for step in scenario.get('steps', [])],
                expected_outcome=scenario.get('expected_outcome', ''),
                validation_score=scenario.get('validation', {}).get('score', 1.0)
            ))

        # 构建输出
        return Stage3BOutput(
            scenarios=test_scenarios,
            paths=paths,
            statistics={
                'total_paths': len(paths),
                'total_scenarios': len(test_scenarios),
                'valid_scenarios': sum(1 for s in test_scenarios if s.validation_score > 0.5)
            },
            metadata={
                'stage': 'scenario_generation',
                'version': '1.0.0',
                'config': config
            }
        )

    def _extract_topology(self, input_data: Dict, config: Dict) -> Dict:
        """从输入数据或 Neo4j 提取拓扑信息"""
        if 'apis' in input_data and 'dependencies' in input_data:
            # 直接从输入数据获取
            return input_data

        # 从 Neo4j 提取
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            config['neo4j_uri'],
            auth=(config['neo4j_user'], config['neo4j_password'])
        )

        with driver.session() as session:
            # 获取 APIs
            apis_result = session.run("""
                MATCH (a:API)
                RETURN a.operation_id as operation_id,
                       a.method as method,
                       a.path as path,
                       a.summary as summary,
                       a.parameters as parameters,
                       a.responses as responses,
                       a.entity as entity
            """)
            apis = [dict(record) for record in apis_result]

            # 获取依赖关系
            deps_result = session.run("""
                MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
                RETURN a1.operation_id as from,
                       a2.operation_id as to,
                       r.score as score,
                       r.type as type
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

        driver.close()

        return {
            'apis': apis,
            'dependencies': dependencies,
            'entities': entities
        }

    def validate_input(self, input_data: Dict) -> bool:
        # 验证是否包含必要的拓扑信息或 Neo4j 配置
        has_topology = 'apis' in input_data and 'dependencies' in input_data
        has_neo4j_config = 'neo4j_uri' in input_data
        return has_topology or has_neo4j_config

    def get_metadata(self) -> Dict:
        return {
            'name': 'Scenario Generation',
            'version': '1.0.0',
            'description': 'Generate test scenarios from API topology',
            'input_format': 'topology_graph',
            'output_format': 'test_scenarios'
        }
