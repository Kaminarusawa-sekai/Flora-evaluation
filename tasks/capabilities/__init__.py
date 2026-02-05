"""能力模块统一入口"""
import os
from .capability_manager import CapabilityManager
from .registry import CapabilityRegistry
from .capability_base import CapabilityBase

# 子模块采用延迟加载，避免在 import 时触发重初始化
_LAZY_SUBMODULES = {
    "context_resolver": ".context_resolver",
    "decision": ".decision",
    "dimension": ".dimension",
    "draw_charts": ".draw_charts",
    "excution": ".excution",
    "llm": ".llm",
    "llm_memory": ".llm_memory",
    "multifeature": ".multifeature",
    "optimization": ".optimization",
    "parallel": ".parallel",
    "result_aggregation": ".result_aggregation",
    "task_planning": ".task_planning",
    "text_to_sql": ".text_to_sql",
}


def __getattr__(name: str):
    if name in _LAZY_SUBMODULES:
        import importlib
        module = importlib.import_module(_LAZY_SUBMODULES[name], __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# 导出常用接口
__all__ = [
    "CapabilityManager",
    "CapabilityRegistry",
    "CapabilityBase",
] + list(_LAZY_SUBMODULES.keys())

# 创建全局能力管理器实例
_global_manager = None
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

def get_capability_manager(config_path: str = CONFIG_PATH) -> CapabilityManager:
    """
    获取全局能力管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        能力管理器实例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = CapabilityManager(config_path)
    return _global_manager


def init_capabilities(config_path: str = CONFIG_PATH, load_extensions: bool = True) -> CapabilityManager:
    """
    初始化所有能力

    Args:
        config_path: 配置文件路径
        load_extensions: 是否加载外部扩展（eval_extensions）

    Returns:
        能力管理器实例
    """
    manager = get_capability_manager(config_path)
    manager.auto_register_capabilities()

    # 加载外部扩展（如果存在且启用）
    if load_extensions:
        try:
            from eval_extensions import register_eval_extensions
            register_eval_extensions(manager)
        except ImportError:
            pass  # eval_extensions 不存在时静默跳过

    manager.initialize_all_capabilities()
    return manager


def get_capability_registry() -> CapabilityRegistry:
    """
    获取能力注册表实例
    
    Returns:
        能力注册表实例
    """
    return CapabilityRegistry()


def get_capability(name: str, expected_type: type) -> CapabilityBase:
    """
    获取能力实例
    
    Args:
        name: 能力名称
        expected_type: 期望的能力类型
        
    Returns:
        能力实例
    """
    manager = get_capability_manager()
    return manager.get_capability(name, expected_type)
