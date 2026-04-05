"""
API 拓扑模块适配器
"""

from core.module_adapter import ModuleAdapter
from schemas.schemas import Stage2Output, APIDependency, EntityRelation
from typing import Dict


class TopologyAdapter(ModuleAdapter):
    """API 拓扑模块适配器"""

    def __init__(self):
        self.service = None

    def process(self, input_data: Dict, config: Dict) -> Stage2Output:
        from api_topology import TopologyService

        if not self.service:
            self.service = TopologyService(**config)

        # 提取 capabilities
        capabilities = input_data.get('capabilities', [])

        # 构建图
        result = self.service.build_graph(capabilities)

        # 从 Neo4j 提取数据
        topology_data = self._extract_topology_from_neo4j(config)

        return Stage2Output(
            apis=topology_data['apis'],
            dependencies=[
                APIDependency(
                    **{**dep, 'fields': dep.get('fields') or []}
                ) for dep in topology_data['dependencies']
            ],
            entities=topology_data['entities'],
            entity_relations=[EntityRelation(**rel) for rel in topology_data['entity_relations']],
            graph_stats=result,
            metadata={
                'stage': 'topology',
                'version': '1.0.0'
            }
        )

    def _extract_topology_from_neo4j(self, config: Dict) -> Dict:
        """从 Neo4j 提取拓扑数据"""
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
                RETURN a1.operation_id as from_api,
                       a2.operation_id as to_api,
                       r.score as score,
                       r.type as type,
                       r.fields as fields
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

            # 获取实体关系
            entity_rels_result = session.run("""
                MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
                RETURN e1.name as from_entity,
                       e2.name as to_entity,
                       r.confidence as confidence,
                       r.inferred_from as inferred_from
            """)
            entity_relations = [dict(record) for record in entity_rels_result]

        driver.close()

        return {
            'apis': apis,
            'dependencies': dependencies,
            'entities': entities,
            'entity_relations': entity_relations
        }

    def validate_input(self, input_data: Dict) -> bool:
        return 'capabilities' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'API Topology',
            'version': '1.0.0',
            'description': 'Build API dependency graph',
            'input_format': 'capabilities_json',
            'output_format': 'neo4j_graph'
        }
