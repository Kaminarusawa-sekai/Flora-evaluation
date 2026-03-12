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

        # 提取 API 能力和实体映射
        capabilities = []
        entity_mappings = []
        
        # 处理不同的输入格式
        if 'capabilities' in input_data:
            # 格式1: 直接包含 capabilities
            capabilities = input_data.get('capabilities', [])
        elif 'sources' in input_data:
            # 格式2: 包含 sources
            capabilities = input_data['sources'][0].get('capabilities', [])
        else:
            # 格式3: 多文件输入（字典的值包含数据）
            for key, value in input_data.items():
                if isinstance(value, dict):
                    if 'capabilities' in value:
                        capabilities = value['capabilities']
                    if 'entity_mappings' in value:
                        entity_mappings = value['entity_mappings']

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

        # 适配新的结果结构 (layer2, layer3, layer4)
        layer4 = result.get('layer4', {})
        manifest = layer4.get('manifest', {})
        
        # 提取 prompts - 从 agent_definitions 中提取 prompt 字段
        prompts = {}
        layer3 = result.get('layer3', {})
        for agent in layer3.get('agent_definitions', []):
            agent_id = agent.get('agent_id', agent.get('name', ''))
            prompt = agent.get('prompt', agent.get('description', ''))
            if agent_id:
                prompts[agent_id] = str(prompt)
        
        return Stage4AOutput(
            org_blueprint=layer3,  # layer3 包含 agent_definitions
            role_manifest=result.get('layer2', {}),  # layer2 包含 roles
            prompts=prompts,  # Dict[str, str] - agent_id -> prompt
            manifest=manifest,
            neo4j_location=neo4j_location,
            metadata={
                'stage': 'agent_build',
                'version': '1.0.0',
                'config': config,
                'result_keys': list(result.keys()),
                'prompts_count': len(prompts)
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

            # 从 layer3 获取 agent_definitions
            layer3 = result.get('layer3', {})
            agents = layer3.get('agent_definitions', [])
            
            # 创建 Agent 节点
            for agent in agents:
                session.run("""
                    CREATE (a:Agent {
                        agent_id: $agent_id,
                        name: $name,
                        role: $role,
                        capabilities: $capabilities
                    })
                """, {
                    'agent_id': agent.get('agent_id', agent.get('name', '')),
                    'name': agent.get('name', ''),
                    'role': agent.get('role', ''),
                    'capabilities': str(agent.get('capabilities', []))
                })

            # 创建拓扑关系
            topology = layer3.get('topology', {})
            for relation in topology.get('edges', []):
                session.run("""
                    MATCH (a1:Agent {agent_id: $from})
                    MATCH (a2:Agent {agent_id: $to})
                    CREATE (a1)-[:COLLABORATES {type: $type}]->(a2)
                """, {
                    'from': relation.get('from', ''),
                    'to': relation.get('to', ''),
                    'type': relation.get('type', 'unknown')
                })

        driver.close()

        return f"{config['neo4j_uri']}/flora_agents"

    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据格式
        
        支持三种格式：
        1. 直接包含 capabilities: {'capabilities': [...]}
        2. 包含 sources: {'sources': [...]}
        3. 多文件输入（字典的值包含数据）: {'path1': {'capabilities': [...]}, 'path2': {...}}
        """
        # 格式1: 直接包含 capabilities
        if 'capabilities' in input_data:
            return True
        
        # 格式2: 包含 sources
        if 'sources' in input_data:
            return True
        
        # 格式3: 多文件输入，检查字典值中是否有 capabilities 或 entity_mappings
        if isinstance(input_data, dict):
            for key, value in input_data.items():
                if isinstance(value, dict):
                    if 'capabilities' in value or 'entity_mappings' in value:
                        return True
        
        return False

    def get_metadata(self) -> Dict:
        return {
            'name': 'Agent Build',
            'version': '1.0.0',
            'description': 'Build agent system from API capabilities',
            'input_format': 'capabilities_json',
            'output_format': 'agent_system'
        }
