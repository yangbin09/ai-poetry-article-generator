#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎实现
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import time
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class WorkflowExecutionContext:
    """
    工作流执行上下文
    
    记录工作流执行过程中的状态和结果
    """
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.current_step_index = 0
        self.step_results: List[StepResult] = []
        self.status = "running"  # running, completed, failed, cancelled
        self.error_message: Optional[str] = None
        self.data_history: List[WorkflowData] = []
    
    def add_step_result(self, result: StepResult) -> None:
        """添加步骤执行结果"""
        self.step_results.append(result)
        if not result.success:
            self.status = "failed"
            self.error_message = result.error
    
    def complete(self) -> None:
        """标记工作流完成"""
        self.end_time = datetime.now()
        if self.status == "running":
            self.status = "completed"
    
    def get_execution_time(self) -> float:
        """获取总执行时间"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "current_step_index": self.current_step_index,
            "status": self.status,
            "error_message": self.error_message,
            "execution_time": self.get_execution_time(),
            "step_results": [result.to_dict() for result in self.step_results]
        }


class WorkflowEngine:
    """
    工作流执行引擎
    
    负责执行工作流步骤序列，管理数据传递和错误处理
    """
    
    def __init__(self, max_workers: int = 1, enable_parallel: bool = False):
        """
        初始化工作流引擎
        
        Args:
            max_workers: 最大并发工作线程数
            enable_parallel: 是否启用并行执行
        """
        self.max_workers = max_workers
        self.enable_parallel = enable_parallel
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.step_hooks: Dict[str, List[Callable]] = {
            "before_step": [],
            "after_step": [],
            "on_error": [],
            "on_complete": []
        }
    
    def add_hook(self, hook_type: str, callback: Callable) -> None:
        """
        添加钩子函数
        
        Args:
            hook_type: 钩子类型 (before_step, after_step, on_error, on_complete)
            callback: 回调函数
        """
        if hook_type in self.step_hooks:
            self.step_hooks[hook_type].append(callback)
        else:
            raise ValueError(f"不支持的钩子类型: {hook_type}")
    
    def execute(self, steps: List[WorkflowStep], initial_data: Optional[WorkflowData] = None,
                workflow_id: Optional[str] = None) -> WorkflowExecutionContext:
        """
        执行工作流
        
        Args:
            steps: 工作流步骤列表
            initial_data: 初始数据
            workflow_id: 工作流ID
            
        Returns:
            WorkflowExecutionContext: 执行上下文
        """
        workflow_id = workflow_id or f"workflow_{int(time.time())}"
        context = WorkflowExecutionContext(workflow_id)
        
        # 初始化数据
        current_data = initial_data or WorkflowData()
        context.data_history.append(current_data)
        
        self.logger.info(f"开始执行工作流: {workflow_id}, 步骤数: {len(steps)}")
        
        try:
            if self.enable_parallel and len(steps) > 1:
                context = self._execute_parallel(steps, current_data, context)
            else:
                context = self._execute_sequential(steps, current_data, context)
            
            # 执行完成钩子
            for hook in self.step_hooks["on_complete"]:
                try:
                    hook(context)
                except Exception as e:
                    self.logger.warning(f"完成钩子执行失败: {e}")
            
        except Exception as e:
            context.status = "failed"
            context.error_message = str(e)
            self.logger.error(f"工作流执行失败: {e}")
            self.logger.error(traceback.format_exc())
            
            # 执行错误钩子
            for hook in self.step_hooks["on_error"]:
                try:
                    hook(context, e)
                except Exception as hook_error:
                    self.logger.warning(f"错误钩子执行失败: {hook_error}")
        
        finally:
            context.complete()
            self.logger.info(f"工作流执行完成: {workflow_id}, 状态: {context.status}, "
                           f"耗时: {context.get_execution_time():.2f}秒")
        
        return context
    
    def _execute_sequential(self, steps: List[WorkflowStep], current_data: WorkflowData,
                          context: WorkflowExecutionContext) -> WorkflowExecutionContext:
        """
        顺序执行步骤
        
        Args:
            steps: 步骤列表
            current_data: 当前数据
            context: 执行上下文
            
        Returns:
            WorkflowExecutionContext: 更新后的执行上下文
        """
        for i, step in enumerate(steps):
            context.current_step_index = i
            
            # 执行前置钩子
            for hook in self.step_hooks["before_step"]:
                try:
                    hook(step, current_data, context)
                except Exception as e:
                    self.logger.warning(f"前置钩子执行失败: {e}")
            
            # 执行步骤
            result = self._execute_step(step, current_data)
            context.add_step_result(result)
            
            # 执行后置钩子
            for hook in self.step_hooks["after_step"]:
                try:
                    hook(step, result, context)
                except Exception as e:
                    self.logger.warning(f"后置钩子执行失败: {e}")
            
            # 检查执行结果
            if not result.success:
                self.logger.error(f"步骤 '{step.name}' 执行失败: {result.error}")
                break
            
            # 更新数据
            current_data = result.data
            context.data_history.append(current_data)
            
            self.logger.info(f"步骤 '{step.name}' 执行成功, 耗时: {result.execution_time:.2f}秒")
        
        return context
    
    def _execute_parallel(self, steps: List[WorkflowStep], current_data: WorkflowData,
                         context: WorkflowExecutionContext) -> WorkflowExecutionContext:
        """
        并行执行步骤（实验性功能）
        
        注意：并行执行时步骤间不能有数据依赖
        
        Args:
            steps: 步骤列表
            current_data: 当前数据
            context: 执行上下文
            
        Returns:
            WorkflowExecutionContext: 更新后的执行上下文
        """
        self.logger.info(f"并行执行 {len(steps)} 个步骤")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有步骤
            future_to_step = {
                executor.submit(self._execute_step, step, current_data): step 
                for step in steps
            }
            
            # 收集结果
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                try:
                    result = future.result()
                    context.add_step_result(result)
                    
                    if result.success:
                        self.logger.info(f"步骤 '{step.name}' 并行执行成功")
                    else:
                        self.logger.error(f"步骤 '{step.name}' 并行执行失败: {result.error}")
                        
                except Exception as e:
                    error_result = StepResult(
                        success=False,
                        data=current_data,
                        error=str(e),
                        step_name=step.name
                    )
                    context.add_step_result(error_result)
                    self.logger.error(f"步骤 '{step.name}' 并行执行异常: {e}")
        
        return context
    
    def _execute_step(self, step: WorkflowStep, data: WorkflowData) -> StepResult:
        """
        执行单个步骤
        
        Args:
            step: 工作流步骤
            data: 输入数据
            
        Returns:
            StepResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            if not step.validate_input(data):
                return StepResult(
                    success=False,
                    data=data,
                    error="输入数据验证失败",
                    step_name=step.name,
                    execution_time=time.time() - start_time
                )
            
            # 执行步骤
            self.logger.debug(f"开始执行步骤: {step.name}")
            result = step.execute(data)
            result.step_name = step.name
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            error_msg = f"步骤执行异常: {str(e)}"
            self.logger.error(f"步骤 '{step.name}' 执行异常: {e}")
            self.logger.error(traceback.format_exc())
            
            return StepResult(
                success=False,
                data=data,
                error=error_msg,
                step_name=step.name,
                execution_time=time.time() - start_time
            )
    
    def validate_workflow(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """
        验证工作流配置
        
        Args:
            steps: 工作流步骤列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "step_count": len(steps)
        }
        
        if not steps:
            validation_result["valid"] = False
            validation_result["errors"].append("工作流不能为空")
            return validation_result
        
        # 检查步骤名称唯一性
        step_names = [step.name for step in steps]
        duplicate_names = [name for name in step_names if step_names.count(name) > 1]
        if duplicate_names:
            validation_result["warnings"].append(f"发现重复的步骤名称: {set(duplicate_names)}")
        
        # 检查数据依赖
        available_outputs = set()
        for i, step in enumerate(steps):
            required_inputs = step.get_required_inputs()
            missing_inputs = [inp for inp in required_inputs if inp not in available_outputs]
            
            if missing_inputs and i > 0:  # 第一个步骤可以没有输入
                validation_result["warnings"].append(
                    f"步骤 '{step.name}' 缺少必需输入: {missing_inputs}"
                )
            
            # 添加当前步骤的输出
            available_outputs.update(step.get_output_keys())
        
        return validation_result
    
    def get_execution_plan(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """
        获取执行计划
        
        Args:
            steps: 工作流步骤列表
            
        Returns:
            Dict[str, Any]: 执行计划
        """
        plan = {
            "total_steps": len(steps),
            "execution_mode": "parallel" if self.enable_parallel else "sequential",
            "max_workers": self.max_workers if self.enable_parallel else 1,
            "steps": []
        }
        
        for i, step in enumerate(steps):
            step_info = {
                "index": i,
                "name": step.name,
                "description": step.description,
                "type": step.__class__.__name__,
                "required_inputs": step.get_required_inputs(),
                "output_keys": step.get_output_keys(),
                "config": step.config
            }
            plan["steps"].append(step_info)
        
        return plan