#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流基础模块

提供工作流系统的基础抽象类和数据结构。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowData:
    """工作流数据容器"""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置数据"""
        self.data[key] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """更新数据"""
        self.data.update(data)
    
    def has(self, key: str) -> bool:
        """检查是否包含指定键"""
        return key in self.data
    
    def remove(self, key: str) -> Any:
        """移除并返回指定键的值"""
        return self.data.pop(key, None)


@dataclass
class StepResult:
    """步骤执行结果"""
    status: StepStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """是否执行成功"""
        return self.status == StepStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """是否执行失败"""
        return self.status == StepStatus.FAILED


class WorkflowStep(ABC):
    """工作流步骤抽象基类"""
    
    def __init__(self, name: str, description: str = "", **kwargs):
        """初始化步骤
        
        Args:
            name: 步骤名称
            description: 步骤描述
            **kwargs: 其他配置参数
        """
        self.name = name
        self.description = description
        self.config = kwargs
        self.status = StepStatus.PENDING
        self.result: Optional[StepResult] = None
    
    @abstractmethod
    def execute(self, data: WorkflowData) -> StepResult:
        """执行步骤
        
        Args:
            data: 工作流数据
            
        Returns:
            步骤执行结果
        """
        pass
    
    def can_execute(self, data: WorkflowData) -> bool:
        """检查是否可以执行
        
        Args:
            data: 工作流数据
            
        Returns:
            是否可以执行
        """
        return True
    
    def validate_input(self, data: WorkflowData) -> bool:
        """验证输入数据
        
        Args:
            data: 工作流数据
            
        Returns:
            输入数据是否有效
        """
        return True
    
    def on_success(self, data: WorkflowData, result: StepResult) -> None:
        """成功回调
        
        Args:
            data: 工作流数据
            result: 执行结果
        """
        pass
    
    def on_failure(self, data: WorkflowData, result: StepResult) -> None:
        """失败回调
        
        Args:
            data: 工作流数据
            result: 执行结果
        """
        pass
    
    def on_skip(self, data: WorkflowData) -> None:
        """跳过回调
        
        Args:
            data: 工作流数据
        """
        pass
    
    def __str__(self) -> str:
        return f"WorkflowStep(name='{self.name}', status='{self.status.value}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class ConditionalStep(WorkflowStep):
    """条件步骤
    
    根据条件决定是否执行的步骤
    """
    
    def __init__(self, name: str, condition_func, target_step: WorkflowStep, 
                 description: str = "", **kwargs):
        """初始化条件步骤
        
        Args:
            name: 步骤名称
            condition_func: 条件函数，接收WorkflowData，返回bool
            target_step: 目标步骤
            description: 步骤描述
            **kwargs: 其他配置参数
        """
        super().__init__(name, description, **kwargs)
        self.condition_func = condition_func
        self.target_step = target_step
    
    def can_execute(self, data: WorkflowData) -> bool:
        """检查条件是否满足"""
        try:
            return self.condition_func(data)
        except Exception:
            return False
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行目标步骤"""
        if self.can_execute(data):
            return self.target_step.execute(data)
        else:
            return StepResult(
                status=StepStatus.SKIPPED,
                metadata={"reason": "Condition not met"}
            )