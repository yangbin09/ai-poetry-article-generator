#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础生成器模块

提供所有生成器的公共基础功能。
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from ...infrastructure.config.config import config


class BaseGenerator(ABC):
    """基础生成器类
    
    所有生成器的基类，提供公共的初始化和配置功能。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """初始化生成器
        
        Args:
            api_key: API密钥，如果不提供则从配置中获取
            base_url: API基础URL，如果不提供则从配置中获取
            model: 模型名称，如果不提供则使用默认模型
        """
        self.client = config.get_zhipu_client()
        self.model = model or self.get_default_model()
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型名称
        
        Returns:
            str: 默认模型名称
        """
        pass
    
    def get_client(self):
        """获取API客户端
        
        Returns:
            API客户端实例
        """
        return self.client
    
    def set_model(self, model: str) -> None:
        """设置模型
        
        Args:
            model: 模型名称
        """
        self.model = model
    
    def get_model(self) -> str:
        """获取当前模型
        
        Returns:
            str: 当前模型名称
        """
        return self.model