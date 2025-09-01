#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章生成步骤模块

负责调用AI接口生成诗词文章
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 简化导入逻辑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.workflow.base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class ArticleGenerationStep(WorkflowStep):
    """
    文章生成步骤
    
    负责调用AI接口生成诗词文章
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行文章生成"""
        try:
            logger.info("开始生成诗词文章...")
            
            # 获取必要的数据
            client = data.get("client")
            messages = data.get("request_messages")
            model = data.get("model")
            temperature = data.get("temperature")
            max_tokens = data.get("max_tokens")
            
            if not all([client, messages, model]):
                raise ValueError("缺少必要的请求参数")
            
            # 发送请求
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 获取生成的文章内容
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("AI返回的内容为空")
                
            article_content = response.choices[0].message.content
            
            # 存储结果
            data.set("article_content", article_content)
            data.set("generation_time", datetime.now().isoformat())
            
            logger.info("文章生成完成")
            return StepResult(success=True, data=data, message="文章生成成功")
            
        except Exception as e:
            error_msg = f"文章生成失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)