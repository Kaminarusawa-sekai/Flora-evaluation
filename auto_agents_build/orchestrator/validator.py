"""
验证器 - 验证输入和输出
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Tuple
from shared.logger import get_logger
from shared.schema_validator import SchemaValidator

logger = get_logger(__name__)


class Validator:
    """全局验证器"""

    def __init__(self):
        self.schema_validator = SchemaValidator()

    def validate_input(self, api_capabilities: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证输入的 API 能力列表

        Args:
            api_capabilities: API 能力列表

        Returns:
            (is_valid, errors)
        """
        logger.info("Validating input API capabilities")

        errors = []

        if not api_capabilities:
            errors.append("API capabilities list is empty")
            return False, errors

        if not isinstance(api_capabilities, list):
            errors.append("API capabilities must be a list")
            return False, errors

        # 验证每个 API
        for i, api in enumerate(api_capabilities):
            if not isinstance(api, dict):
                errors.append(f"API at index {i} is not a dictionary")
                continue

            # 必需字段
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in api:
                    errors.append(f"API at index {i} missing required field: {field}")

            # 推荐字段
            recommended_fields = ['method', 'path', 'tags']
            missing_recommended = [f for f in recommended_fields if f not in api]
            if missing_recommended:
                logger.warning(f"API '{api.get('name', 'unknown')}' missing recommended fields: {missing_recommended}")

        if errors:
            logger.error(f"Input validation failed with {len(errors)} errors")
            return False, errors

        logger.info(f"Input validation passed: {len(api_capabilities)} APIs")
        return True, []

    def validate_layer2_output(self, manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Layer 2 输出"""
        logger.info("Validating Layer 2 output")

        is_valid = self.schema_validator.validate_layer2(manifest)

        if not is_valid:
            errors = self.schema_validator.get_validation_errors(
                manifest,
                SchemaValidator.LAYER2_SCHEMA
            )
            return False, errors

        # 业务逻辑验证
        errors = []

        roles = manifest.get('roles', [])
        if not roles:
            errors.append("No roles generated")

        # 检查是否有角色没有分配 API
        empty_roles = [r for r in roles if not r.get('assigned_apis')]
        if empty_roles:
            logger.warning(f"Found {len(empty_roles)} roles without assigned APIs")

        if errors:
            return False, errors

        logger.info("Layer 2 output validation passed")
        return True, []

    def validate_layer3_output(self, blueprint: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Layer 3 输出"""
        logger.info("Validating Layer 3 output")

        is_valid = self.schema_validator.validate_layer3(blueprint)

        if not is_valid:
            errors = self.schema_validator.get_validation_errors(
                blueprint,
                SchemaValidator.LAYER3_SCHEMA
            )
            return False, errors

        # 业务逻辑验证
        errors = []

        agents = blueprint.get('agent_definitions', [])
        if not agents:
            errors.append("No agents generated")

        # 检查能力注册表
        registry = blueprint.get('capability_registry', {})
        if not registry.get('atomic_capabilities'):
            errors.append("No atomic capabilities registered")

        # 检查拓扑
        topology = blueprint.get('topology', {})
        if not topology.get('nodes'):
            errors.append("Topology has no nodes")

        if errors:
            return False, errors

        logger.info("Layer 3 output validation passed")
        return True, []

    def validate_layer4_output(self, result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Layer 4 输出"""
        logger.info("Validating Layer 4 output")

        errors = []

        # 检查 Prompt 生成
        if result.get('prompts_count', 0) == 0:
            errors.append("No prompts generated")

        # 检查 Manifest
        manifest = result.get('manifest')
        if not manifest:
            errors.append("Manifest not generated")
        elif not manifest.get('agents'):
            errors.append("Manifest has no agents")

        # 检查知识链接
        knowledge_links = result.get('knowledge_links')
        if not knowledge_links:
            errors.append("Knowledge links not generated")

        # 检查监控配置
        monitoring = result.get('monitoring_config')
        if not monitoring:
            errors.append("Monitoring config not generated")

        if errors:
            logger.error(f"Layer 4 validation failed with {len(errors)} errors")
            return False, errors

        logger.info("Layer 4 output validation passed")
        return True, []

    def validate_pipeline_result(self, result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证整个流水线结果"""
        logger.info("Validating pipeline result")

        errors = []

        if not result.get('success'):
            errors.append(f"Pipeline failed: {result.get('error', 'Unknown error')}")
            return False, errors

        # 验证各层输出
        if 'layer2' in result:
            is_valid, layer_errors = self.validate_layer2_output(result['layer2'])
            if not is_valid:
                errors.extend([f"Layer 2: {e}" for e in layer_errors])

        if 'layer3' in result:
            is_valid, layer_errors = self.validate_layer3_output(result['layer3'])
            if not is_valid:
                errors.extend([f"Layer 3: {e}" for e in layer_errors])

        if 'layer4' in result:
            is_valid, layer_errors = self.validate_layer4_output(result['layer4'])
            if not is_valid:
                errors.extend([f"Layer 4: {e}" for e in layer_errors])

        if errors:
            logger.error(f"Pipeline validation failed with {len(errors)} errors")
            return False, errors

        logger.info("Pipeline validation passed")
        return True, []

    def generate_validation_report(
        self,
        input_valid: Tuple[bool, List[str]],
        layer2_valid: Tuple[bool, List[str]],
        layer3_valid: Tuple[bool, List[str]],
        layer4_valid: Tuple[bool, List[str]]
    ) -> str:
        """生成验证报告"""
        report_lines = [
            "=== 验证报告 ===",
            "",
            f"输入验证: {'通过' if input_valid[0] else '失败'}",
        ]

        if not input_valid[0]:
            report_lines.append("  错误:")
            for error in input_valid[1]:
                report_lines.append(f"    - {error}")

        report_lines.append(f"\nLayer 2 验证: {'通过' if layer2_valid[0] else '失败'}")
        if not layer2_valid[0]:
            report_lines.append("  错误:")
            for error in layer2_valid[1]:
                report_lines.append(f"    - {error}")

        report_lines.append(f"\nLayer 3 验证: {'通过' if layer3_valid[0] else '失败'}")
        if not layer3_valid[0]:
            report_lines.append("  错误:")
            for error in layer3_valid[1]:
                report_lines.append(f"    - {error}")

        report_lines.append(f"\nLayer 4 验证: {'通过' if layer4_valid[0] else '失败'}")
        if not layer4_valid[0]:
            report_lines.append("  错误:")
            for error in layer4_valid[1]:
                report_lines.append(f"    - {error}")

        report_lines.append("\n=== 报告结束 ===")

        return "\n".join(report_lines)
