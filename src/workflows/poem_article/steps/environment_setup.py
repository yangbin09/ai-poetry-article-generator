#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境设置步骤模块

负责加载环境变量和初始化必要的配置
"""

import os
import logging
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
except ImportError as e:
    logging.error(f"缺少必要的依赖包: {e}")
    raise

# 简化导入逻辑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.workflow.base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class EnvironmentSetupStep(WorkflowStep):
    """
    环境设置步骤
    
    负责加载环境变量和初始化必要的配置
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, description: str = ""):
        super().__init__(name, description, config)
        self.env_file = self.config.get("env_file", ".env")
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行环境设置"""
        try:
            logger.info("开始环境设置...")
            
            # 加载环境变量
            load_dotenv(self.env_file)
            
            # 验证API密钥
            api_key = os.getenv('ZHIPU_API_KEY')
            if not api_key:
                raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
            
            # 存储配置信息
            data.set("api_key", api_key)
            data.set("environment_ready", True)
            
            logger.info("环境设置完成")
            return StepResult(success=True, data=data, message="环境设置成功")
            
        except Exception as e:
            error_msg = f"环境设置失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)