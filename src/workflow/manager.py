#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流管理器模块

提供工作流的执行、管理和监控功能。
"""

import asyncio
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field

from .base import WorkflowData, StepResult, StepStatus, WorkflowStep
from .config import WorkflowConfig, StepConfig, ConfigManager
from .engine.workflow_engine import WorkflowEngine, WorkflowDefinition, FunctionStep
from . import functions


@dataclass
class WorkflowExecution:
    """工作流执行记录"""
    workflow_id: str
    config_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "config_name": self.config_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration": self.duration,
            "results": self.results,
            "errors": self.errors,
            "step_count": len(self.step_results),
            "completed_steps": len([r for r in self.step_results.values() if r.status == StepStatus.COMPLETED])
        }


class FunctionRegistry:
    """函数注册表"""
    
    def __init__(self):
        self._functions: Dict[str, Callable] = {}
        self._modules: Dict[str, Any] = {}
    
    def register_function(self, name: str, func: Callable) -> None:
        """注册函数
        
        Args:
            name: 函数名
            func: 函数对象
        """
        self._functions[name] = func
        logging.info(f"Registered function: {name}")
    
    def register_module(self, module_name: str, module_path: str) -> None:
        """注册模块
        
        Args:
            module_name: 模块名
            module_path: 模块路径
        """
        try:
            module = importlib.import_module(module_path)
            self._modules[module_name] = module
            logging.info(f"Registered module: {module_name} from {module_path}")
        except ImportError as e:
            logging.error(f"Failed to import module {module_path}: {e}")
            raise
    
    def get_function(self, name: str) -> Optional[Callable]:
        """获取函数
        
        Args:
            name: 函数名或模块.函数名
            
        Returns:
            函数对象
        """
        # 直接查找注册的函数
        if name in self._functions:
            return self._functions[name]
        
        # 查找模块中的函数
        if '.' in name:
            module_name, func_name = name.rsplit('.', 1)
            if module_name in self._modules:
                module = self._modules[module_name]
                if hasattr(module, func_name):
                    return getattr(module, func_name)
        
        # 尝试动态导入
        try:
            if '.' in name:
                module_path, func_name = name.rsplit('.', 1)
                module = importlib.import_module(module_path)
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    self._functions[name] = func  # 缓存
                    return func
        except ImportError:
            pass
        
        return None
    
    def list_functions(self) -> List[str]:
        """列出所有注册的函数"""
        functions = list(self._functions.keys())
        
        # 添加模块中的公共函数
        for module_name, module in self._modules.items():
            for attr_name in dir(module):
                if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                    functions.append(f"{module_name}.{attr_name}")
        
        return sorted(functions)


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, config_dir: Union[str, Path] = "workflow_configs"):
        """初始化工作流管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_manager = ConfigManager(config_dir)
        self.function_registry = FunctionRegistry()
        self.engine = WorkflowEngine()
        self.executions: Dict[str, WorkflowExecution] = {}
        self.logger = logging.getLogger(__name__)
        
        # 注册默认函数
        self._register_default_functions()
        
        # 注册工作流函数
        self._register_workflow_functions()
    
    def _register_default_functions(self) -> None:
        """注册默认函数"""
        # 这里可以注册一些默认的工作流函数
        self.function_registry.register_function("print_message", self._print_message)
        self.function_registry.register_function("save_data", self._save_data)
        self.function_registry.register_function("load_data", self._load_data)
    
    def _register_workflow_functions(self) -> None:
        """注册工作流函数"""
        # 注册古诗词相关函数
        self.function_registry.register_function('initialize_zhipu_client', functions.initialize_zhipu_client)
        self.function_registry.register_function('generate_poem_article', functions.generate_poem_article)
        self.function_registry.register_function('generate_poem_image', functions.generate_poem_image)
        self.function_registry.register_function('save_workflow_results', functions.save_workflow_results)
        
        # 注册图像生成相关函数
        self.function_registry.register_function('optimize_prompt', functions.optimize_prompt)
        self.function_registry.register_function('generate_image', functions.generate_image)
        self.function_registry.register_function('save_image', functions.save_image)
    
    def _print_message(self, data: WorkflowData, message: str = "") -> StepResult:
        """打印消息的默认函数"""
        print(f"[Workflow] {message}")
        return StepResult(
            status=StepStatus.COMPLETED,
            data={"message": message},
            message=f"Printed: {message}"
        )
    
    def _save_data(self, data: WorkflowData, key: str, value: Any) -> StepResult:
        """保存数据的默认函数"""
        data.set(key, value)
        return StepResult(
            status=StepStatus.COMPLETED,
            data={key: value},
            message=f"Saved data: {key}"
        )
    
    def _load_data(self, data: WorkflowData, key: str, default: Any = None) -> StepResult:
        """加载数据的默认函数"""
        value = data.get_data(key, default)
        return StepResult(
            status=StepStatus.COMPLETED,
            data={key: value},
            message=f"Loaded data: {key}"
        )
    
    def register_function(self, name: str, func: Callable) -> None:
        """注册工作流函数
        
        Args:
            name: 函数名
            func: 函数对象
        """
        self.function_registry.register_function(name, func)
    
    def register_module(self, module_name: str, module_path: str) -> None:
        """注册工作流模块
        
        Args:
            module_name: 模块名
            module_path: 模块路径
        """
        self.function_registry.register_module(module_name, module_path)
    
    def create_workflow_from_config(self, config: WorkflowConfig) -> WorkflowDefinition:
        """从配置创建工作流定义
        
        Args:
            config: 工作流配置
            
        Returns:
            工作流定义
        """
        workflow_def = WorkflowDefinition(
            name=config.name,
            description=config.description
        )
        
        # 创建步骤
        for step_config in config.steps:
            step = self._create_step_from_config(step_config)
            if step:
                workflow_def.add_step(step)
        
        return workflow_def
    
    def _create_step_from_config(self, step_config: StepConfig) -> Optional[WorkflowStep]:
        """从配置创建工作流步骤
        
        Args:
            step_config: 步骤配置
            
        Returns:
            工作流步骤
        """
        if step_config.type == "function":
            if not step_config.function:
                self.logger.error(f"Function step {step_config.name} missing function name")
                return None
            
            func = self.function_registry.get_function(step_config.function)
            if not func:
                self.logger.error(f"Function {step_config.function} not found for step {step_config.name}")
                return None
            
            return FunctionStep(
                name=step_config.name,
                func=func,
                description=step_config.description,
                **step_config.parameters
            )
        
        # 其他类型的步骤可以在这里扩展
        self.logger.warning(f"Unsupported step type: {step_config.type}")
        return None
    
    def load_workflow(self, config_name: str) -> WorkflowDefinition:
        """加载工作流
        
        Args:
            config_name: 配置文件名
            
        Returns:
            工作流定义
        """
        config = self.config_manager.load_config(config_name)
        return self.create_workflow_from_config(config)
    
    async def execute_workflow(self, 
                             config_name: str, 
                             input_data: Optional[Dict[str, Any]] = None,
                             workflow_id: Optional[str] = None) -> WorkflowExecution:
        """执行工作流
        
        Args:
            config_name: 配置文件名
            input_data: 输入数据
            workflow_id: 工作流ID，如果为None则自动生成
            
        Returns:
            工作流执行记录
        """
        if workflow_id is None:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建执行记录
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            config_name=config_name,
            start_time=datetime.now()
        )
        self.executions[workflow_id] = execution
        
        try:
            # 加载工作流
            workflow_def = self.load_workflow(config_name)
            
            # 准备输入数据
            workflow_data = WorkflowData()
            if input_data:
                for key, value in input_data.items():
                    workflow_data.set(key, value)
            
            # 执行工作流
            self.logger.info(f"Starting workflow execution: {workflow_id}")
            engine_execution = self.engine.execute(workflow_def, workflow_data)
            
            # 更新执行记录
            execution.end_time = datetime.now()
            execution.status = "completed" if engine_execution.status.value == "completed" else "failed"
            execution.results = workflow_data.data
            if engine_execution.error:
                execution.errors.append(str(engine_execution.error))
            
            # 收集步骤结果
            for step in workflow_def.steps:
                if hasattr(step, 'result') and step.result:
                    execution.step_results[step.name] = step.result
            
            self.logger.info(f"Workflow execution completed: {workflow_id}, status: {execution.status}")
            
        except Exception as e:
            execution.end_time = datetime.now()
            execution.status = "failed"
            execution.errors.append(str(e))
            self.logger.error(f"Workflow execution failed: {workflow_id}, error: {e}")
        
        return execution
    
    def get_execution(self, workflow_id: str) -> Optional[WorkflowExecution]:
        """获取工作流执行记录
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流执行记录
        """
        return self.executions.get(workflow_id)
    
    def list_executions(self) -> List[WorkflowExecution]:
        """列出所有工作流执行记录
        
        Returns:
            工作流执行记录列表
        """
        return list(self.executions.values())
    
    def list_configs(self) -> List[str]:
        """列出所有工作流配置
        
        Returns:
            配置文件名列表
        """
        return self.config_manager.list_configs()
    
    def create_default_configs(self) -> None:
        """创建默认配置文件"""
        self.config_manager.create_default_configs()
        self.logger.info("Default workflow configs created")
    
    def get_function_list(self) -> List[str]:
        """获取可用函数列表
        
        Returns:
            函数名列表
        """
        return self.function_registry.list_functions()


# 全局工作流管理器实例
_workflow_manager: Optional[WorkflowManager] = None


def get_workflow_manager(config_dir: Union[str, Path] = "workflow_configs") -> WorkflowManager:
    """获取全局工作流管理器实例
    
    Args:
        config_dir: 配置文件目录
        
    Returns:
        工作流管理器实例
    """
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager(config_dir)
    return _workflow_manager


def reset_workflow_manager() -> None:
    """重置全局工作流管理器实例"""
    global _workflow_manager
    _workflow_manager = None