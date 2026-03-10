"""
Schema 验证器 - 验证各层输出的 JSON 格式
"""
import json
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError, Draft7Validator
from .logger import get_logger

logger = get_logger(__name__)


class SchemaValidator:
    """Schema 验证器"""

    # Layer 2 输出 Schema
    LAYER2_SCHEMA = {
        "type": "object",
        "required": ["roles", "domain", "timestamp"],
        "properties": {
            "roles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["role_id", "role_name", "assigned_apis"],
                    "properties": {
                        "role_id": {"type": "string"},
                        "role_name": {"type": "string"},
                        "domain": {"type": "string"},
                        "assigned_apis": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["api_id", "business_name"],
                                "properties": {
                                    "api_id": {"type": "string"},
                                    "business_name": {"type": "string"},
                                    "constraint": {"type": "string"}
                                }
                            }
                        },
                        "constraints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "api_id": {"type": "string"},
                                    "api_name": {"type": "string"},
                                    "constraint_type": {"type": "string"},
                                    "constraint_rule": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "domain": {"type": "string"},
            "orphan_apis": {"type": "array"},
            "timestamp": {"type": "string"}
        }
    }

    # Layer 3 输出 Schema
    LAYER3_SCHEMA = {
        "type": "object",
        "required": ["blueprint_version", "capability_registry", "agent_definitions"],
        "properties": {
            "blueprint_version": {"type": "string"},
            "capability_registry": {
                "type": "object",
                "required": ["atomic_capabilities", "composed_capabilities"],
                "properties": {
                    "atomic_capabilities": {"type": "array"},
                    "composed_capabilities": {"type": "array"},
                    "strategic_capabilities": {"type": "array"}
                }
            },
            "agent_definitions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["agent_id", "agent_name", "level"],
                    "properties": {
                        "agent_id": {"type": "string"},
                        "agent_name": {"type": "string"},
                        "level": {"type": "string"},
                        "capability_interface": {"type": "object"},
                        "subordinates": {"type": "array"}
                    }
                }
            },
            "topology": {"type": "object"},
            "access_control_matrix": {"type": "object"}
        }
    }

    # Layer 4 输出 Schema
    LAYER4_SCHEMA = {
        "type": "object",
        "required": ["prompts", "manifest"],
        "properties": {
            "prompts": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "manifest": {
                "type": "object",
                "required": ["agents", "version"],
                "properties": {
                    "agents": {"type": "array"},
                    "version": {"type": "string"}
                }
            }
        }
    }

    @staticmethod
    def validate_layer2(data: Dict[str, Any]) -> bool:
        """验证 Layer 2 输出"""
        try:
            validate(instance=data, schema=SchemaValidator.LAYER2_SCHEMA)
            logger.info("Layer 2 output validation passed")
            return True
        except ValidationError as e:
            logger.error(f"Layer 2 validation failed: {e.message}")
            logger.error(f"Failed path: {' -> '.join(str(p) for p in e.path)}")
            return False

    @staticmethod
    def validate_layer3(data: Dict[str, Any]) -> bool:
        """验证 Layer 3 输出"""
        try:
            validate(instance=data, schema=SchemaValidator.LAYER3_SCHEMA)
            logger.info("Layer 3 output validation passed")
            return True
        except ValidationError as e:
            logger.error(f"Layer 3 validation failed: {e.message}")
            logger.error(f"Failed path: {' -> '.join(str(p) for p in e.path)}")
            return False

    @staticmethod
    def validate_layer4(data: Dict[str, Any]) -> bool:
        """验证 Layer 4 输出"""
        try:
            validate(instance=data, schema=SchemaValidator.LAYER4_SCHEMA)
            logger.info("Layer 4 output validation passed")
            return True
        except ValidationError as e:
            logger.error(f"Layer 4 validation failed: {e.message}")
            logger.error(f"Failed path: {' -> '.join(str(p) for p in e.path)}")
            return False

    @staticmethod
    def validate_custom(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证自定义 Schema"""
        try:
            validate(instance=data, schema=schema)
            logger.info("Custom schema validation passed")
            return True
        except ValidationError as e:
            logger.error(f"Custom validation failed: {e.message}")
            return False

    @staticmethod
    def get_validation_errors(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """获取所有验证错误"""
        validator = Draft7Validator(schema)
        errors = []

        for error in validator.iter_errors(data):
            path = ' -> '.join(str(p) for p in error.path)
            errors.append(f"{path}: {error.message}")

        return errors
