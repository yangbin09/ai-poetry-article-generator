"""简化的工作流引擎

提供基础的工作流定义和执行能力。
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StepResult:
    """步骤执行结果"""
    status: StepStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowContext:
    """工作流上下文"""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self.data[key] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """更新上下文数据"""
        self.data.update(data)


class WorkflowStep(ABC):
    """工作流步骤抽象基类"""
    
    def __init__(self, name: str, description: str = ""):
        """初始化步骤
        
        Args:
            name: 步骤名称
            description: 步骤描述
        """
        self.name = name
        self.description = description
        self.status = StepStatus.PENDING
        self.result: Optional[StepResult] = None
    
    @abstractmethod
    def execute(self, context: WorkflowContext) -> StepResult:
        """执行步骤
        
        Args:
            context: 工作流上下文
            
        Returns:
            步骤执行结果
        """
        pass
    
    def can_execute(self, context: WorkflowContext) -> bool:
        """检查是否可以执行
        
        Args:
            context: 工作流上下文
            
        Returns:
            是否可以执行
        """
        return True
    
    def on_success(self, context: WorkflowContext, result: StepResult) -> None:
        """成功回调
        
        Args:
            context: 工作流上下文
            result: 执行结果
        """
        pass
    
    def on_failure(self, context: WorkflowContext, result: StepResult) -> None:
        """失败回调
        
        Args:
            context: 工作流上下文
            result: 执行结果
        """
        pass


class FunctionStep(WorkflowStep):
    """函数步骤实现"""
    
    def __init__(self, name: str, func: Callable, description: str = "", **kwargs):
        """初始化函数步骤
        
        Args:
            name: 步骤名称
            func: 执行函数
            description: 步骤描述
            **kwargs: 函数参数
        """
        super().__init__(name, description)
        self.func = func
        self.kwargs = kwargs
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """执行函数步骤"""
        try:
            start_time = datetime.now()
            
            # 准备函数参数
            func_kwargs = self.kwargs.copy()
            func_kwargs['context'] = context
            
            # 执行函数
            result_data = self.func(**func_kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return StepResult(
                status=StepStatus.COMPLETED,
                data=result_data,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"步骤 {self.name} 执行失败: {e}")
            
            return StepResult(
                status=StepStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: WorkflowStep) -> None:
        """添加步骤"""
        self.steps.append(step)
    
    def add_function_step(self, name: str, func: Callable, description: str = "", **kwargs) -> None:
        """添加函数步骤"""
        step = FunctionStep(name, func, description, **kwargs)
        self.add_step(step)


@dataclass
class WorkflowExecution:
    """工作流执行实例"""
    workflow: WorkflowDefinition
    context: WorkflowContext
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step_index: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    @property
    def execution_time(self) -> float:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def completed_steps(self) -> int:
        """获取已完成步骤数"""
        return sum(1 for step in self.workflow.steps if step.status == StepStatus.COMPLETED)
    
    @property
    def total_steps(self) -> int:
        """获取总步骤数"""
        return len(self.workflow.steps)
    
    @property
    def progress(self) -> float:
        """获取执行进度"""
        if self.total_steps == 0:
            return 1.0
        return self.completed_steps / self.total_steps


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self):
        """初始化工作流引擎"""
        self.executions: Dict[str, WorkflowExecution] = {}
        logger.info("工作流引擎初始化完成")
    
    def execute(self, workflow: WorkflowDefinition, context: Optional[WorkflowContext] = None) -> WorkflowExecution:
        """执行工作流
        
        Args:
            workflow: 工作流定义
            context: 工作流上下文
            
        Returns:
            工作流执行实例
        """
        if context is None:
            context = WorkflowContext()
        
        execution = WorkflowExecution(
            workflow=workflow,
            context=context,
            start_time=datetime.now()
        )
        
        execution_id = f"{workflow.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.executions[execution_id] = execution
        
        logger.info(f"开始执行工作流: {workflow.name}")
        
        try:
            execution.status = WorkflowStatus.RUNNING
            
            for i, step in enumerate(workflow.steps):
                execution.current_step_index = i
                
                # 检查是否可以执行
                if not step.can_execute(context):
                    step.status = StepStatus.SKIPPED
                    logger.info(f"跳过步骤: {step.name}")
                    continue
                
                # 执行步骤
                logger.info(f"执行步骤: {step.name}")
                step.status = StepStatus.RUNNING
                
                result = step.execute(context)
                step.result = result
                step.status = result.status
                
                # 处理执行结果
                if result.status == StepStatus.COMPLETED:
                    step.on_success(context, result)
                    logger.info(f"步骤完成: {step.name}")
                elif result.status == StepStatus.FAILED:
                    step.on_failure(context, result)
                    logger.error(f"步骤失败: {step.name}, 错误: {result.error}")
                    
                    # 工作流失败
                    execution.status = WorkflowStatus.FAILED
                    execution.error = f"步骤 {step.name} 失败: {result.error}"
                    break
            
            # 检查工作流状态
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                logger.info(f"工作流执行完成: {workflow.name}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            logger.error(f"工作流执行失败: {workflow.name}, 错误: {e}")
        
        finally:
            execution.end_time = datetime.now()
        
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取工作流执行实例
        
        Args:
            execution_id: 执行ID
            
        Returns:
            工作流执行实例
        """
        return self.executions.get(execution_id)
    
    def list_executions(self) -> List[str]:
        """列出所有执行ID
        
        Returns:
            执行ID列表
        """
        return list(self.executions.keys())
    
    def cleanup_executions(self, keep_count: int = 100) -> None:
        """清理旧的执行记录
        
        Args:
            keep_count: 保留的执行记录数量
        """
        if len(self.executions) <= keep_count:
            return
        
        # 按时间排序，保留最新的记录
        sorted_executions = sorted(
            self.executions.items(),
            key=lambda x: x[1].start_time or datetime.min,
            reverse=True
        )
        
        # 保留最新的记录
        keep_executions = dict(sorted_executions[:keep_count])
        removed_count = len(self.executions) - len(keep_executions)
        
        self.executions = keep_executions
        logger.info(f"清理了 {removed_count} 个旧的执行记录")


# 全局工作流引擎实例
engine = WorkflowEngine()