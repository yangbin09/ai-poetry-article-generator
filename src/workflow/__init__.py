#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化工作流演示系统

这是一个基于模块化架构的工作流演示系统，支持：
- 独立的步骤模块
- 动态工作流配置
- 标准化数据传递
- 可视化配置管理
"""

from .base import WorkflowStep, WorkflowData, StepResult
from .engine import WorkflowEngine
from .config import WorkflowConfig, WorkflowTemplate
from .manager import WorkflowManager

__version__ = "1.0.0"
__author__ = "AI Assistant"

__all__ = [
    "WorkflowStep",
    "WorkflowData", 
    "StepResult",
    "WorkflowEngine",
    "WorkflowConfig",
    "WorkflowTemplate",
    "WorkflowManager"
]