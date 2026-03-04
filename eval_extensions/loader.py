"""
扩展加载器 - 用于将评估扩展注册到 CapabilityManager
"""
import logging
import sys
import os
from typing import TYPE_CHECKING

# 确保 tasks 目录在路径中
_TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
if _TASKS_ROOT not in sys.path:
    sys.path.insert(0, _TASKS_ROOT)

if TYPE_CHECKING:
    from capabilities.capability_manager import CapabilityManager

logger = logging.getLogger(__name__)


def register_eval_extensions(manager: "CapabilityManager") -> None:
    """
    将评估专用的能力实现注册到 CapabilityManager。

    这个函数应该在 manager.auto_register_capabilities() 之后调用，
    这样评估扩展可以覆盖或补充核心实现。

    Args:
        manager: CapabilityManager 实例
    """
    from .eval_execution import EvalExecution
    from .eval_qwen_llm import EvalQwenLLM

    # 注册 EvalExecution（覆盖 tasks/capabilities/excution/）
    manager._available_classes["eval_execution"] = EvalExecution
    manager._available_classes["EvalExecution"] = EvalExecution
    manager._class_type_map["eval_execution"] = "excution"
    manager._class_type_map["EvalExecution"] = "excution"
    logger.info("Registered eval extension: EvalExecution")

    # 注册 EvalQwenLLM（覆盖 tasks/capabilities/llm/qwen_llm.py）
    manager._available_classes["eval_qwen_llm"] = EvalQwenLLM
    manager._available_classes["EvalQwenLLM"] = EvalQwenLLM
    manager._class_type_map["eval_qwen_llm"] = "llm"
    manager._class_type_map["EvalQwenLLM"] = "llm"
    logger.info("Registered eval extension: EvalQwenLLM")


def setup_eval_environment(config_path: str = None) -> "CapabilityManager":
    """
    便捷函数：创建并配置用于评估的 CapabilityManager。

    Args:
        config_path: 评估配置文件路径，默认使用 eval_config.json

    Returns:
        配置好的 CapabilityManager 实例
    """
    from capabilities.capability_manager import CapabilityManager

    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "coop_eval_actual",
            "configs",
            "eval_config.json"
        )

    manager = CapabilityManager(config_path)
    manager.auto_register_capabilities()
    register_eval_extensions(manager)
    manager.initialize_all_capabilities()

    return manager
