#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端初始化步骤模块

负责初始化智谱AI客户端
"""

import os
import logging
from typing import Dict, Any, Optional

try:
    from zhipuai import ZhipuAI
except ImportError as e:
    logging.error(f"缺少必要的依赖包: {e}")
    raise

# 简化导入逻辑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.workflow.base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class ClientInitializationStep(WorkflowStep):
    """
    客户端初始化步骤
    
    负责初始化智谱AI客户端
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行客户端初始化"""
        try:
            logger.info("开始初始化客户端...")
            
            # 检查环境是否已设置
            if not data.get("environment_ready"):
                raise ValueError("环境未正确设置")
            
            # 获取API密钥并初始化客户端
            api_key = data.get("api_key")
            client = ZhipuAI(api_key=api_key)
            data.set("client", client)
            
            logger.info("客户端初始化完成")
            return StepResult(success=True, data=data, message="客户端初始化成功")
            
        except Exception as e:
            error_msg = f"客户端初始化失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)