"""
模块适配器基类 - 所有模块都需要实现此接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ModuleAdapter(ABC):
    """
    模块适配器基类 - 所有模块都需要实现此接口
    """

    @abstractmethod
    def process(self, input_data: Dict, config: Dict) -> Dict:
        """
        处理数据
        Args:
            input_data: 输入数据
            config: 模块配置
        Returns:
            处理结果
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据"""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict:
        """获取模块元数据"""
        pass
