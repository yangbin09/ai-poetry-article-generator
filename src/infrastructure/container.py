"""依赖注入容器

提供统一的依赖管理和服务注册功能。
"""

from typing import Dict, Any, TypeVar, Type, Callable, Optional
from functools import lru_cache
import inspect

T = TypeVar('T')


class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        
    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = True) -> None:
        """注册服务
        
        Args:
            interface: 接口类型
            implementation: 实现类型
            singleton: 是否单例模式
        """
        key = self._get_key(interface)
        if singleton:
            self._services[key] = implementation
        else:
            self._factories[key] = implementation
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """注册实例
        
        Args:
            interface: 接口类型
            instance: 实例对象
        """
        key = self._get_key(interface)
        self._singletons[key] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """注册工厂函数
        
        Args:
            interface: 接口类型
            factory: 工厂函数
        """
        key = self._get_key(interface)
        self._factories[key] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """解析服务
        
        Args:
            interface: 接口类型
            
        Returns:
            服务实例
            
        Raises:
            ValueError: 服务未注册
        """
        key = self._get_key(interface)
        
        # 检查是否有已注册的实例
        if key in self._singletons:
            return self._singletons[key]
        
        # 检查是否有单例服务
        if key in self._services:
            if key not in self._singletons:
                self._singletons[key] = self._create_instance(self._services[key])
            return self._singletons[key]
        
        # 检查是否有工厂函数
        if key in self._factories:
            return self._create_instance(self._factories[key])
        
        raise ValueError(f"Service {interface.__name__} not registered")
    
    def _get_key(self, interface: Type) -> str:
        """获取服务键名"""
        return f"{interface.__module__}.{interface.__name__}"
    
    def _create_instance(self, cls_or_factory: Any) -> Any:
        """创建实例"""
        if inspect.isclass(cls_or_factory):
            # 自动注入构造函数依赖
            return self._auto_wire(cls_or_factory)
        else:
            # 工厂函数
            return cls_or_factory()
    
    def _auto_wire(self, cls: Type) -> Any:
        """自动装配依赖"""
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except ValueError:
                    # 如果依赖未注册且有默认值，使用默认值
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise
        
        return cls(**kwargs)


# 全局容器实例
_container: Optional[Container] = None


def get_container() -> Container:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = Container()
    return _container


def configure_container() -> Container:
    """配置容器"""
    from src.interfaces.base import (
        AIClientInterface, PoemServiceInterface, 
        ImageServiceInterface, PromptServiceInterface, ConfigInterface
    )
    from src.infrastructure.clients.zhipu_client import ZhipuAIClient
    from src.infrastructure.config.settings import Settings
    from src.core.services.poem_service import PoemService
    from src.core.services.image_service import ImageService
    from src.core.services.prompt_service import PromptService
    
    container = get_container()
    
    # 注册配置
    container.register_instance(ConfigInterface, Settings())
    
    # 注册AI客户端
    container.register(AIClientInterface, ZhipuAIClient)
    
    # 注册服务
    container.register(PoemServiceInterface, PoemService)
    container.register(ImageServiceInterface, ImageService)
    container.register_factory(PromptServiceInterface, lambda: PromptService())
    
    return container