"""
Mock 服务模块适配器
"""

from core.module_adapter import ModuleAdapter
from schemas.schemas import Stage4BOutput, MockEndpoint
from typing import Dict


class MockAdapter(ModuleAdapter):
    """Mock 服务模块适配器"""

    def __init__(self):
        self.service = None

    def process(self, input_data: Dict, config: Dict) -> Stage4BOutput:
        from stateful_mock import MockService

        if not self.service:
            self.service = MockService(
                db_path=config.get('db_path', 'output/stage4b/mock_state.db')
            )

        # 提取 capabilities
        capabilities = input_data.get('capabilities', [])

        # 启动服务
        port = config.get('port', 8000)
        self.service.start_server(capabilities, port=port)

        # 收集端点信息
        endpoints = []
        for cap in capabilities:
            for api in cap.get('apis', []):
                endpoints.append(MockEndpoint(
                    operation_id=api.get('operation_id'),
                    method=api.get('method'),
                    path=api.get('path'),
                    handler=f"mock_handler_{api.get('operation_id')}"
                ))

        return Stage4BOutput(
            service_url=f"http://localhost:{port}",
            endpoints=endpoints,
            state_db_path=config.get('db_path', 'output/stage4b/mock_state.db'),
            metadata={
                'stage': 'mock_service',
                'version': '1.0.0',
                'port': port,
                'total_endpoints': len(endpoints)
            }
        )

    def validate_input(self, input_data: Dict) -> bool:
        return 'capabilities' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'Mock Service',
            'version': '1.0.0',
            'description': 'Start stateful mock API service',
            'input_format': 'capabilities_json',
            'output_format': 'service_info'
        }
