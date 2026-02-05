"""外部系统交互模块"""

_LAZY_SUBMODULES = {
    "clients": ".clients",
    "database": ".database",
    "memory_store": ".memory_store",
    "message_queue": ".message_queue",
    "repositories": ".repositories",
}


def __getattr__(name: str):
    if name in _LAZY_SUBMODULES:
        import importlib
        module = importlib.import_module(_LAZY_SUBMODULES[name], __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = list(_LAZY_SUBMODULES.keys())
