"""
工具函数
"""
import json
import yaml
from typing import Dict, Any, Union
from pathlib import Path


def load_json(file_path: str) -> Dict[str, Any]:
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str, pretty: bool = True):
    """保存 JSON 文件"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False)


def load_yaml(file_path: str) -> Dict[str, Any]:
    """加载 YAML 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], file_path: str):
    """保存 YAML 文件"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def load_file(file_path: str) -> Union[Dict[str, Any], str]:
    """根据扩展名自动加载文件"""
    path = Path(file_path)

    if path.suffix == '.json':
        return load_json(file_path)
    elif path.suffix in ['.yaml', '.yml']:
        return load_yaml(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


def save_file(data: Union[Dict[str, Any], str], file_path: str):
    """根据扩展名自动保存文件"""
    path = Path(file_path)

    if path.suffix == '.json':
        save_json(data, file_path)
    elif path.suffix in ['.yaml', '.yml']:
        save_yaml(data, file_path)
    else:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)


def ensure_dir(dir_path: str):
    """确保目录存在"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
