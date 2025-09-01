#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流模块

提供工作流引擎和相关功能。
"""

from .engine.workflow_engine import (
    WorkflowEngine,
    WorkflowStep,
    WorkflowContext,
    StepResult,
    StepStatus,
    WorkflowStatus,
    FunctionStep,
    engine
)

from .base import (
    StepStatus,
    WorkflowData as BaseWorkflowData,
    StepResult as BaseStepResult,
    WorkflowStep as BaseWorkflowStep,
    ConditionalStep as BaseConditionalStep
)

from .config import (
    WorkflowConfig,
    StepConfig,
    WorkflowTemplate,
    ConfigManager
)

from .manager import (
    WorkflowManager,
    WorkflowExecution,
    FunctionRegistry,
    get_workflow_manager,
    reset_workflow_manager
)

__all__ = [
    # 基础模块
    'WorkflowStep',
    'StepResult', 
    'StepStatus',
    'WorkflowData',
    'ConditionalStep',
    
    # 配置模块
    'StepConfig',
    'WorkflowConfig',
    'WorkflowTemplate',
    'ConfigManager',
    
    # 管理器模块
    'WorkflowManager',
    'get_workflow_manager',
    
    # 引擎模块
    'WorkflowEngine',
    'WorkflowContext',
    'WorkflowStatus',
    'FunctionStep',
    'engine'
]