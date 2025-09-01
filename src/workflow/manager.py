#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流管理器
"""

from typing import Dict, List, Any, Optional, Type, Callable
import logging
from pathlib import Path

from .base import WorkflowStep, WorkflowData, WorkflowStepFactory
from .engine import WorkflowEngine, WorkflowExecutionContext
from .config import WorkflowConfig, ConfigManager, WorkflowTemplate, StepConfig

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    工作流管理器
    
    统一管理工作流的创建、配置、执行和监控
    """
    
    def __init__(self, config_dir: Optional[str] = None, max_workers: int = 1, 
                 enable_parallel: bool = False):
        """
        初始化工作流管理器
        
        Args:
            config_dir: 配置文件目录
            max_workers: 最大并发工作线程数
            enable_parallel: 是否启用并行执行
        """
        self.engine = WorkflowEngine(max_workers=max_workers, enable_parallel=enable_parallel)
        self.config_manager = ConfigManager(config_dir)
        self.step_factory = WorkflowStepFactory()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 执行历史
        self.execution_history: List[WorkflowExecutionContext] = []
        
        # 注册默认钩子
        self._register_default_hooks()
    
    def _register_default_hooks(self) -> None:
        """注册默认钩子函数"""
        def log_step_start(step: WorkflowStep, data: WorkflowData, context: WorkflowExecutionContext):
            self.logger.info(f"[{context.workflow_id}] 开始执行步骤: {step.name}")
        
        def log_step_complete(step: WorkflowStep, result, context: WorkflowExecutionContext):
            status = "成功" if result.success else "失败"
            self.logger.info(f"[{context.workflow_id}] 步骤 '{step.name}' 执行{status}")
        
        def log_workflow_complete(context: WorkflowExecutionContext):
            self.logger.info(f"[{context.workflow_id}] 工作流执行完成，状态: {context.status}")
        
        def save_execution_history(context: WorkflowExecutionContext):
            self.execution_history.append(context)
            # 保持历史记录数量限制
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
        
        self.engine.add_hook("before_step", log_step_start)
        self.engine.add_hook("after_step", log_step_complete)
        self.engine.add_hook("on_complete", log_workflow_complete)
        self.engine.add_hook("on_complete", save_execution_history)
    
    def register_step_type(self, step_type: str, step_class: Type[WorkflowStep]) -> None:
        """
        注册步骤类型
        
        Args:
            step_type: 步骤类型名称
            step_class: 步骤类
        """
        self.step_factory.register(step_type, step_class)
        self.logger.info(f"已注册步骤类型: {step_type}")
    
    def create_workflow_from_template(self, template_name: str, 
                                    custom_config: Optional[Dict[str, Any]] = None) -> WorkflowConfig:
        """
        从模板创建工作流
        
        Args:
            template_name: 模板名称
            custom_config: 自定义配置
            
        Returns:
            WorkflowConfig: 工作流配置
        """
        config = WorkflowTemplate.get_template(template_name)
        if not config:
            raise ValueError(f"模板不存在: {template_name}")
        
        # 应用自定义配置
        if custom_config:
            if "name" in custom_config:
                config.name = custom_config["name"]
            if "description" in custom_config:
                config.description = custom_config["description"]
            if "global_config" in custom_config:
                config.global_config.update(custom_config["global_config"])
            if "steps" in custom_config:
                self._apply_step_customizations(config, custom_config["steps"])
        
        self.logger.info(f"从模板 '{template_name}' 创建工作流: {config.name}")
        return config
    
    def _apply_step_customizations(self, config: WorkflowConfig, 
                                 step_customizations: Dict[str, Dict[str, Any]]) -> None:
        """
        应用步骤自定义配置
        
        Args:
            config: 工作流配置
            step_customizations: 步骤自定义配置
        """
        for step in config.steps:
            if step.name in step_customizations:
                customization = step_customizations[step.name]
                for key, value in customization.items():
                    if key == "config":
                        step.config.update(value)
                    elif hasattr(step, key):
                        setattr(step, key, value)
    
    def create_custom_workflow(self, name: str, description: str = "") -> WorkflowConfig:
        """
        创建自定义工作流
        
        Args:
            name: 工作流名称
            description: 工作流描述
            
        Returns:
            WorkflowConfig: 工作流配置
        """
        config = WorkflowConfig(name=name, description=description)
        self.logger.info(f"创建自定义工作流: {name}")
        return config
    
    def add_step_to_workflow(self, config: WorkflowConfig, step_name: str, 
                           step_type: str, step_config: Optional[Dict[str, Any]] = None,
                           description: str = "", dependencies: Optional[List[str]] = None) -> None:
        """
        向工作流添加步骤
        
        Args:
            config: 工作流配置
            step_name: 步骤名称
            step_type: 步骤类型
            step_config: 步骤配置
            description: 步骤描述
            dependencies: 依赖步骤
        """
        step_config_obj = StepConfig(
            name=step_name,
            type=step_type,
            description=description,
            config=step_config or {},
            dependencies=dependencies or []
        )
        
        config.add_step(step_config_obj)
        self.logger.info(f"向工作流 '{config.name}' 添加步骤: {step_name}")
    
    def execute_workflow(self, config: WorkflowConfig, 
                        initial_data: Optional[WorkflowData] = None,
                        workflow_id: Optional[str] = None) -> WorkflowExecutionContext:
        """
        执行工作流
        
        Args:
            config: 工作流配置
            initial_data: 初始数据
            workflow_id: 工作流ID
            
        Returns:
            WorkflowExecutionContext: 执行上下文
        """
        # 验证配置
        validation_result = config.validate()
        if not validation_result["valid"]:
            raise ValueError(f"工作流配置无效: {validation_result['errors']}")
        
        # 创建步骤实例
        steps = self._create_step_instances(config)
        
        # 验证工作流
        engine_validation = self.engine.validate_workflow(steps)
        if not engine_validation["valid"]:
            self.logger.warning(f"工作流验证警告: {engine_validation['warnings']}")
        
        # 执行工作流
        self.logger.info(f"开始执行工作流: {config.name}")
        context = self.engine.execute(steps, initial_data, workflow_id)
        
        return context
    
    def _create_step_instances(self, config: WorkflowConfig) -> List[WorkflowStep]:
        """
        创建步骤实例
        
        Args:
            config: 工作流配置
            
        Returns:
            List[WorkflowStep]: 步骤实例列表
        """
        steps = []
        
        for step_config in config.steps:
            if not step_config.enabled:
                self.logger.info(f"跳过禁用的步骤: {step_config.name}")
                continue
            
            try:
                step = self.step_factory.create(
                    step_config.type,
                    step_config.name,
                    step_config.description,
                    step_config.config
                )
                steps.append(step)
                
            except Exception as e:
                self.logger.error(f"创建步骤实例失败 '{step_config.name}': {e}")
                raise
        
        return steps
    
    def save_workflow(self, config: WorkflowConfig, filename: Optional[str] = None) -> Path:
        """
        保存工作流配置
        
        Args:
            config: 工作流配置
            filename: 文件名
            
        Returns:
            Path: 保存的文件路径
        """
        return self.config_manager.save_config(config, filename)
    
    def load_workflow(self, filename: str) -> WorkflowConfig:
        """
        加载工作流配置
        
        Args:
            filename: 文件名
            
        Returns:
            WorkflowConfig: 工作流配置
        """
        return self.config_manager.load_config(filename)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        列出所有工作流配置
        
        Returns:
            List[Dict[str, Any]]: 工作流配置信息列表
        """
        return self.config_manager.list_configs()
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        列出所有模板
        
        Returns:
            List[Dict[str, str]]: 模板信息列表
        """
        return WorkflowTemplate.list_templates()
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取执行历史
        
        Args:
            limit: 限制返回数量
            
        Returns:
            List[Dict[str, Any]]: 执行历史列表
        """
        history = self.execution_history
        if limit:
            history = history[-limit:]
        
        return [context.to_dict() for context in history]
    
    def get_step_types(self) -> List[str]:
        """
        获取已注册的步骤类型
        
        Returns:
            List[str]: 步骤类型列表
        """
        return list(self.step_factory.step_types.keys())
    
    def validate_workflow_config(self, config: WorkflowConfig) -> Dict[str, Any]:
        """
        验证工作流配置
        
        Args:
            config: 工作流配置
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        # 配置级别验证
        config_validation = config.validate()
        
        # 引擎级别验证
        try:
            steps = self._create_step_instances(config)
            engine_validation = self.engine.validate_workflow(steps)
        except Exception as e:
            engine_validation = {
                "valid": False,
                "errors": [f"创建步骤实例失败: {str(e)}"],
                "warnings": []
            }
        
        # 合并验证结果
        combined_result = {
            "valid": config_validation["valid"] and engine_validation["valid"],
            "errors": config_validation["errors"] + engine_validation["errors"],
            "warnings": config_validation["warnings"] + engine_validation["warnings"],
            "config_validation": config_validation,
            "engine_validation": engine_validation
        }
        
        return combined_result
    
    def get_workflow_plan(self, config: WorkflowConfig) -> Dict[str, Any]:
        """
        获取工作流执行计划
        
        Args:
            config: 工作流配置
            
        Returns:
            Dict[str, Any]: 执行计划
        """
        try:
            steps = self._create_step_instances(config)
            plan = self.engine.get_execution_plan(steps)
            plan["workflow_name"] = config.name
            plan["workflow_description"] = config.description
            plan["global_config"] = config.global_config
            return plan
        except Exception as e:
            return {
                "error": f"生成执行计划失败: {str(e)}",
                "workflow_name": config.name
            }
    
    def clone_workflow(self, config: WorkflowConfig, new_name: str) -> WorkflowConfig:
        """
        克隆工作流
        
        Args:
            config: 原工作流配置
            new_name: 新工作流名称
            
        Returns:
            WorkflowConfig: 克隆的工作流配置
        """
        cloned_config = config.clone(new_name)
        self.logger.info(f"克隆工作流: {config.name} -> {new_name}")
        return cloned_config
    
    def add_hook(self, hook_type: str, callback: Callable) -> None:
        """
        添加钩子函数
        
        Args:
            hook_type: 钩子类型
            callback: 回调函数
        """
        self.engine.add_hook(hook_type, callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for ctx in self.execution_history if ctx.status == "completed")
        failed_executions = sum(1 for ctx in self.execution_history if ctx.status == "failed")
        
        avg_execution_time = 0
        if self.execution_history:
            avg_execution_time = sum(ctx.get_execution_time() for ctx in self.execution_history) / total_executions
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "registered_step_types": len(self.step_factory.step_types),
            "available_templates": len(WorkflowTemplate.TEMPLATES)
        }
    
    def cleanup_history(self, keep_last: int = 50) -> None:
        """
        清理执行历史
        
        Args:
            keep_last: 保留最近的执行记录数量
        """
        if len(self.execution_history) > keep_last:
            removed_count = len(self.execution_history) - keep_last
            self.execution_history = self.execution_history[-keep_last:]
            self.logger.info(f"清理了 {removed_count} 条执行历史记录")