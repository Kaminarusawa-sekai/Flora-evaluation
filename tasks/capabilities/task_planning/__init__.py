"""业务路由与调度能力模块"""

_LAZY_EXPORTS = {
    "ITaskPlanningCapability": (".interface", "ITaskPlanningCapability"),
    "CommonTaskPlanning": (".common_task_planner", "CommonTaskPlanning"),
}


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        import importlib
        module_path, attr_name = _LAZY_EXPORTS[name]
        module = importlib.import_module(module_path, __name__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = list(_LAZY_EXPORTS.keys())
