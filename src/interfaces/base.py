"""基础接口定义

定义项目中使用的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIClientInterface(ABC):
    """AI客户端接口"""
    
    @abstractmethod
    def chat_completion(self, messages: list, model: str = None, **kwargs) -> str:
        """聊天完成接口"""
        pass
    
    @abstractmethod
    def image_generation(self, prompt: str, model: str = None, **kwargs) -> str:
        """图像生成接口"""
        pass


class PoemServiceInterface(ABC):
    """古诗词服务接口"""
    
    @abstractmethod
    def generate_article(self, poem_name: str, **kwargs) -> str:
        """生成古诗词文章"""
        pass


class ImageServiceInterface(ABC):
    """图像服务接口"""
    
    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> str:
        """生成图像"""
        pass
    
    @abstractmethod
    def generate_poem_image(self, poem_name: str, custom_prompt: str = "", **kwargs) -> str:
        """生成古诗词图像"""
        pass


class PromptServiceInterface(ABC):
    """提示词服务接口"""
    
    @abstractmethod
    def optimize_prompt(self, original_prompt: str, style: str = "水墨画", **kwargs) -> str:
        """优化提示词"""
        pass


class ConfigInterface(ABC):
    """配置接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass