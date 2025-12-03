"""AI客户端策略与工厂模块。

使用策略模式（Strategy Pattern）统一管理不同AI提供商的调用方式，
让上层逻辑可以在不修改业务代码的前提下切换或扩展新的AI服务。
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from ...interfaces.base import AIClientInterface
from ..config.settings import settings
from .zhipu_client import ZhipuAIClient


class AIClientFactory:
    """AI客户端工厂，负责注册与创建具体客户端实例。"""

    def __init__(self, bootstrap_default: bool = True) -> None:
        """初始化工厂。

        Args:
            bootstrap_default: 是否注册默认的智谱AI客户端，测试场景下可以关闭。
        """
        self._registry: Dict[str, Callable[[], AIClientInterface]] = {}
        if bootstrap_default:
            self.register_client("zhipu", ZhipuAIClient)

    def register_client(self, provider: str, builder: Callable[[], AIClientInterface]) -> None:
        """注册新的AI客户端。

        Args:
            provider: 提供商名称，例如 ``"zhipu"`` 或 ``"openai"``。
            builder: 用于创建客户端实例的可调用对象。
        """
        if not provider:
            raise ValueError("提供商名称不能为空")
        self._registry[provider] = builder

    def get_client(self, provider: Optional[str] = None) -> AIClientInterface:
        """获取指定提供商的客户端实例。"""
        resolved_provider = provider or settings.get("api.provider", "zhipu")
        if resolved_provider not in self._registry:
            raise ValueError(f"未注册的AI提供商: {resolved_provider}")

        client = self._registry[resolved_provider]()
        if not isinstance(client, AIClientInterface):
            raise TypeError("客户端必须实现 AIClientInterface 接口")
        return client

    def available_providers(self) -> List[str]:
        """返回已注册的提供商列表。"""
        return sorted(self._registry.keys())


class AIClientStrategy:
    """AI客户端策略上下文。

    通过策略模式将 ``chat_completion``、``image_generation`` 等调用
    委托给当前选择的 AI 客户端，实现运行时灵活切换。
    """

    def __init__(self, provider: Optional[str] = None, factory: Optional[AIClientFactory] = None) -> None:
        self._factory = factory or ai_client_factory
        self._provider = provider or settings.get("api.provider", "zhipu")

    def set_provider(self, provider: str) -> None:
        """切换当前使用的AI提供商。"""
        self._provider = provider

    def get_client(self) -> AIClientInterface:
        """获取当前策略对应的客户端。"""
        return self._factory.get_client(self._provider)

    def chat_completion(self, messages: list, model: Optional[str] = None, **kwargs) -> str:
        """执行聊天补全任务。"""
        client = self.get_client()
        return client.chat_completion(messages, model=model, **kwargs)

    def image_generation(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """执行图像生成任务。"""
        client = self.get_client()
        return client.image_generation(prompt, model=model, **kwargs)


# 全局工厂实例，默认已注册智谱AI客户端
ai_client_factory = AIClientFactory()
