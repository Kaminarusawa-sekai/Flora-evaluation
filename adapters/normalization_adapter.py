"""
API 规范化模块适配器
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage1Output, Capability
from typing import Dict


class NormalizationAdapter(ModuleAdapter):
    """API 规范化模块适配器"""

    def __init__(self):
        from api_normalization import NormalizationService
        self.service = None

    def process(self, input_data: Dict, config: Dict) -> Stage1Output:
        from api_normalization import NormalizationService

        if not self.service:
            self.service = NormalizationService(**config)

        # 适配输入格式
        swagger_path = input_data.get('path') or input_data

        # 执行处理
        result = self.service.normalize_swagger(swagger_path)

        # 适配输出格式
        return Stage1Output(
            capabilities=[Capability(**cap) for cap in result['capabilities']],
            statistics=result.get('statistics', {}),
            metadata={
                'stage': 'normalization',
                'version': '1.0.0'
            }
        )

    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入是否为有效的 Swagger 文件路径
        return isinstance(input_data, (str, dict))

    def get_metadata(self) -> Dict:
        return {
            'name': 'API Normalization',
            'version': '1.0.0',
            'description': 'Normalize Swagger/OpenAPI documents',
            'input_format': 'swagger_json',
            'output_format': 'capabilities_json'
        }
