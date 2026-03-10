"""
Agent 构建模块适配器
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage4AOutput
from typing import Dict, List


class AgentBuildAdapter(ModuleAdapter):
    """Agent 构建模块适配器"""

    def __init__(self):
        self.orchestrator = None

    def process(self, input_data: Dict, config: Dict) -> Stage4AOutput:
        from auto_agents_build.orchestrator import PipelineOrchestrator

        if not self.orchestrator:
            self.orchestrator = PipelineOrchestrator()

        # 提取 API 能力
        capabilities = input_data.get('capabilities', [])
        if isinstance(input_data, dict) and 'sources' in input_data:
            # 多源输入
            capabilities = input_data['sources'][0].get('capabilities', [])

        # 转换为 API 能力列表
        api_capabilities = self._convert_to_api_capabilities(capabilities)

        # 运行构建流程
        result = self.orchestrator.run_pipeline(
            api_capabilities,
            output_dir=config.get('output_dir', './output/stage4a')
        )

        # 如果配置了输出到 Neo4j，则保存
        neo4j_location = None
        if config.get('output_to_neo4j', False):
            neo4j_location = self._save_to_neo4j(result, config)

        return Stage4AOutput(
            org_blueprint=result['org_blueprint'],
            role_manifest=result['role_manifest'],
            prompts=result['prompts'],
            manifest=result['manifest'],
            neo4j_location=neo4j_location,
            metadata={
                'stage': 'agent_build',
                'version': '1.0.0',
                'config': config
            }
        )

    def _convert_to_api_capabilities(self, capabilities: List) -> List[Dict]:
        """转换能力格式为 Agent 构建所需格式"""
        api_capabilities = []

        for cap in capabilities:
            for api in cap.get('apis', []):
                api_capabilities.append({
                    'id': api.get('operation_id'),
                    'name': api.get('summary', api.get('operation_id')),
                    'description': api.get('description', ''),
                    'method': api.get('method'),
                    'path': api.get('path'),
                    'tags': cap.get('tags', [cap.get('resource', 'unknown')])
                })

        return api_capabilities

    def _save_to_neo4j(self, result: Dict, config: Dict) -> str:
        """保存 Agent 系统到 Neo4j"""
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            config['neo4j_uri'],
            auth=(config['neo4j_user'], config['neo4j_password'])
        )

        with driver.session() as session:
            # 清空现有数据
            session.run("MATCH (n:Agent) DETACH DELETE n")

            # 创建 Agent 节点
            for agent in result['org_blueprint']['agents']:
                session.run("""
                    CREATE (a:Agent {
                        agent_id: $agent_id,
                        name: $name,
                        role: $role,
                        level: $level,
                        prompt: $prompt
                    })
                """, agent)

            # 创建层级关系
            for relation in result['org_blueprint']['hierarchy'].get('relations', []):
                session.run("""
                    MATCH (a1:Agent {agent_id: $from})
                    MATCH (a2:Agent {agent_id: $to})
                    CREATE (a1)-[:MANAGES]->(a2)
                """, relation)

        driver.close()

        return f"{config['neo4j_uri']}/flora_agents"

    def validate_input(self, input_data: Dict) -> bool:
        return 'capabilities' in input_data or 'sources' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'Agent Build',
            'version': '1.0.0',
            'description': 'Build agent system from API capabilities',
            'input_format': 'capabilities_json',
            'output_format': 'agent_system'
        }
