#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI客户端策略与工厂测试。"""

from typing import List
import os
import sys
import types

import pytest

# 为了避免在测试环境中引入真实依赖，这里提供最小化的模块桩
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *_, **__: None
sys.modules.setdefault("dotenv", dotenv_stub)

zhipu_stub = types.ModuleType("zhipuai")


class _DummyZhipuAI:
    def __init__(self, *_, **__):
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **__: None))
        self.images = types.SimpleNamespace(generations=lambda **__: None)


zhipu_stub.ZhipuAI = _DummyZhipuAI
sys.modules.setdefault("zhipuai", zhipu_stub)

requests_stub = types.ModuleType("requests")
requests_stub.post = lambda *_, **__: None
sys.modules.setdefault("requests", requests_stub)

os.environ.setdefault("ZHIPU_API_KEY", "test-key")

from src.infrastructure.clients.strategy import AIClientFactory, AIClientStrategy
from src.interfaces.base import AIClientInterface


class DummyAIClient(AIClientInterface):
    """用于测试的虚拟AI客户端。"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.chat_called_with: List[str] = []
        self.image_called_with: List[str] = []

    def chat_completion(self, messages: list, model: str = None, **kwargs) -> str:
        self.chat_called_with.append(self.name)
        return f"chat:{self.name}:{model or ''}"

    def image_generation(self, prompt: str, model: str = None, **kwargs) -> str:
        self.image_called_with.append(self.name)
        return f"image:{self.name}:{model or ''}"


class TestAIClientFactory:
    """AI客户端工厂测试用例。"""

    def test_register_and_get_client(self):
        factory = AIClientFactory(bootstrap_default=False)
        factory.register_client("dummy", lambda: DummyAIClient("dummy"))

        client = factory.get_client("dummy")

        assert isinstance(client, DummyAIClient)
        assert factory.available_providers() == ["dummy"]

    def test_unknown_provider_error(self):
        factory = AIClientFactory(bootstrap_default=False)

        with pytest.raises(ValueError, match="未注册的AI提供商"):
            factory.get_client("not-exist")


class TestAIClientStrategy:
    """策略模式委托行为测试。"""

    def test_switch_provider(self):
        factory = AIClientFactory(bootstrap_default=False)
        first_client = DummyAIClient("first")
        second_client = DummyAIClient("second")
        factory.register_client("first", lambda: first_client)
        factory.register_client("second", lambda: second_client)

        strategy = AIClientStrategy(provider="first", factory=FactoryProxy(factory))

        assert strategy.chat_completion([{"role": "user", "content": "hi"}], model="m1") == "chat:first:m1"
        assert first_client.chat_called_with == ["first"]

        strategy.set_provider("second")
        assert strategy.image_generation("prompt", model="m2") == "image:second:m2"
        assert second_client.image_called_with == ["second"]


class FactoryProxy(AIClientFactory):
    """代理工厂，用于避免在策略中初始化默认客户端。"""

    def __init__(self, delegate: AIClientFactory):
        # 不调用父类构造以避免重复注册
        self._registry = delegate._registry

