"""
配置加载器 - 加载全局配置
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器，支持环境变量覆盖"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self._apply_env_overrides()

    def _find_config(self) -> str:
        """查找配置文件"""
        possible_paths = [
            'config.yaml',
            'config.yml',
            '../config.yaml',
            os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # 返回默认配置
        return None

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path or not os.path.exists(self.config_path):
            return self._default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f) or {}

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.3,
                'max_tokens': 2000,
                'api_key': None
            },
            'vector_store': {
                'type': 'faiss',
                'dimension': 1536,
                'index_path': './data/vectors'
            },
            'templates': {
                'library_path': './templates/domains',
                'auto_generate': True
            },
            'output': {
                'format': 'json',
                'pretty_print': True,
                'save_intermediate': True
            },
            'optimization': {
                'enable_ab_test': False,
                'test_iterations': 5,
                'success_threshold': 0.85
            }
        }

    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # LLM API Key
        if 'OPENAI_API_KEY' in os.environ:
            self.config['llm']['api_key'] = os.environ['OPENAI_API_KEY']

        # LLM Provider
        if 'LLM_PROVIDER' in os.environ:
            self.config['llm']['provider'] = os.environ['LLM_PROVIDER']

        # LLM Model
        if 'LLM_MODEL' in os.environ:
            self.config['llm']['model'] = os.environ['LLM_MODEL']

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[str] = None):
        """保存配置到文件"""
        save_path = path or self.config_path
        if not save_path:
            save_path = 'config.yaml'

        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)


# 全局配置实例
_global_config = None


def get_config() -> ConfigLoader:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader()
    return _global_config
