"""工作流创建和执行模块"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到 Python 路径
import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.workflow.config import WorkflowConfig
from .steps import (
    EnvironmentSetupStep,
    ClientInitializationStep,
    PoemRequestBuildStep,
    ArticleGenerationStep,
    ResultOutputStep
)

logger = logging.getLogger(__name__)


def create_poem_article_workflow(config: Dict[str, Any]) -> WorkflowConfig:
    """创建古诗词文章生成工作流"""
    from src.workflow.config import StepConfig
    
    workflow_config = WorkflowConfig(
        name="poem_article_generation",
        description="古诗词文章生成工作流",
        steps=[]
    )
    
    # 添加步骤配置
    steps = [
        StepConfig(name="environment_setup", type="EnvironmentSetupStep"),
        StepConfig(name="client_initialization", type="ClientInitializationStep"),
        StepConfig(name="poem_request_build", type="PoemRequestBuildStep"),
        StepConfig(name="article_generation", type="ArticleGenerationStep"),
        StepConfig(name="result_output", type="ResultOutputStep")
    ]
    
    workflow_config.steps = steps
    return workflow_config


def execute_workflow(workflow_config: WorkflowConfig, poem_name: str) -> Dict[str, Any]:
    """执行工作流"""
    from src.workflow.manager import WorkflowManager
    from src.workflow.base import WorkflowData
    from datetime import datetime
    
    logger.info(f"开始执行工作流: {poem_name}")
    
    try:
        # 创建工作流管理器
        manager = WorkflowManager()
        
        # 注册步骤类型
        manager.register_step_type('EnvironmentSetupStep', EnvironmentSetupStep)
        manager.register_step_type('ClientInitializationStep', ClientInitializationStep)
        manager.register_step_type('PoemRequestBuildStep', PoemRequestBuildStep)
        manager.register_step_type('ArticleGenerationStep', ArticleGenerationStep)
        manager.register_step_type('ResultOutputStep', ResultOutputStep)
        
        # 设置初始数据
        initial_data = WorkflowData()
        initial_data.set('poem_name', poem_name)
        initial_data.set('timestamp', datetime.now().isoformat())
        
        # 执行工作流
        context = manager.execute_workflow(workflow_config, initial_data)
        
        logger.info("工作流执行完成")
        return {
            'success': True,
            'result': context.to_dict(),
            'poem_name': poem_name
        }
        
    except Exception as e:
        logger.error(f"工作流执行失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'poem_name': poem_name
        }