"""
配置管理模块 - 支持多环境配置、配置验证等
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = 'config'):
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.environment = os.getenv('FLORA_ENV', 'development')

    def load_config(self, config_name: str) -> Dict:
        """
        加载配置文件
        支持环境特定配置覆盖
        """
        # 加载基础配置
        base_config_path = self.config_dir / f"{config_name}.yaml"
        base_config = self._load_yaml(base_config_path)

        # 加载环境特定配置
        env_config_path = self.config_dir / f"{config_name}.{self.environment}.yaml"
        if env_config_path.exists():
            env_config = self._load_yaml(env_config_path)
            base_config = self._merge_configs(base_config, env_config)

        # 替换环境变量
        base_config = self._replace_env_vars(base_config)

        self.configs[config_name] = base_config
        return base_config

    def _load_yaml(self, path: Path) -> Dict:
        """加载 YAML 文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """合并配置（深度合并）"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _replace_env_vars(self, config: Any) -> Any:
        """替换环境变量"""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        else:
            return config

    def get_config(self, config_name: str) -> Dict:
        """获取配置（带缓存）"""
        if config_name not in self.configs:
            return self.load_config(config_name)
        return self.configs[config_name]
