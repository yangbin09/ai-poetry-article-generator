#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流系统基础类和接口定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowData:
    """
    工作流数据容器
    
    用于在步骤间传递数据的标准化容器
    """
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置数据"""
        self.data[key] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """批量更新数据"""
        self.data.update(data)
    
    def has(self, key: str) -> bool:
        """检查是否包含指定键"""
        return key in self.data
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return list(self.data.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowData':
        """从字典创建实例"""
        instance = cls()
        instance.data = data.get("data", {})
        instance.metadata = data.get("metadata", {})
        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])
        return instance


@dataclass
class StepResult:
    """
    步骤执行结果
    """
    success: bool
    data: WorkflowData
    message: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    step_name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data.to_dict(),
            "message": self.message,
            "error": self.error,
            "execution_time": self.execution_time,
            "step_name": self.step_name
        }


class WorkflowStep(ABC):
    """
    工作流步骤抽象基类
    
    所有工作流步骤都必须继承此类并实现execute方法
    """
    
    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        """
        初始化步骤
        
        Args:
            name: 步骤名称
            description: 步骤描述
            config: 步骤配置参数
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def execute(self, data: WorkflowData) -> StepResult:
        """
        执行步骤逻辑
        
        Args:
            data: 输入数据
            
        Returns:
            StepResult: 执行结果
        """
        pass
    
    def validate_input(self, data: WorkflowData) -> bool:
        """
        验证输入数据
        
        Args:
            data: 输入数据
            
        Returns:
            bool: 验证是否通过
        """
        return True
    
    def get_required_inputs(self) -> List[str]:
        """
        获取必需的输入参数列表
        
        Returns:
            List[str]: 必需参数列表
        """
        return []
    
    def get_output_keys(self) -> List[str]:
        """
        获取输出参数列表
        
        Returns:
            List[str]: 输出参数列表
        """
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        获取配置参数模式
        
        Returns:
            Dict[str, Any]: 配置参数模式
        """
        return {}
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        更新配置参数
        
        Args:
            config: 新的配置参数
        """
        self.config.update(config)
    
    def __str__(self) -> str:
        return f"WorkflowStep(name='{self.name}', description='{self.description}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class WorkflowStepFactory:
    """
    工作流步骤工厂类
    
    用于注册和创建工作流步骤实例
    """
    
    _steps: Dict[str, type] = {}
    
    @classmethod
    def register(cls, step_type: str, step_class: type) -> None:
        """
        注册步骤类型
        
        Args:
            step_type: 步骤类型名称
            step_class: 步骤类
        """
        cls._steps[step_type] = step_class
        logger.info(f"注册步骤类型: {step_type} -> {step_class.__name__}")
    
    @classmethod
    def create(cls, step_type: str, name: str, description: str = "", 
               config: Optional[Dict[str, Any]] = None) -> WorkflowStep:
        """
        创建步骤实例
        
        Args:
            step_type: 步骤类型
            name: 步骤名称
            description: 步骤描述
            config: 步骤配置
            
        Returns:
            WorkflowStep: 步骤实例
            
        Raises:
            ValueError: 未知的步骤类型
        """
        if step_type not in cls._steps:
            raise ValueError(f"未知的步骤类型: {step_type}")
        
        step_class = cls._steps[step_type]
        return step_class(name=name, description=description, config=config)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """
        获取可用的步骤类型列表
        
        Returns:
            List[str]: 步骤类型列表
        """
        return list(cls._steps.keys())
    
    @classmethod
    def get_step_info(cls, step_type: str) -> Dict[str, Any]:
        """
        获取步骤类型信息
        
        Args:
            step_type: 步骤类型
            
        Returns:
            Dict[str, Any]: 步骤信息
        """
        if step_type not in cls._steps:
            raise ValueError(f"未知的步骤类型: {step_type}")
        
        step_class = cls._steps[step_type]
        # 创建临时实例获取信息
        temp_instance = step_class(name="temp", description="")
        
        return {
            "type": step_type,
            "class_name": step_class.__name__,
            "required_inputs": temp_instance.get_required_inputs(),
            "output_keys": temp_instance.get_output_keys(),
            "config_schema": temp_instance.get_config_schema()
        }


def register_step(step_type: str):
    """
    步骤注册装饰器
    
    Args:
        step_type: 步骤类型名称
    """
    def decorator(cls):
        WorkflowStepFactory.register(step_type, cls)
        return cls
    return decorator