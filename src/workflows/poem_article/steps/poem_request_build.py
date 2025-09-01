#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诗词请求构建步骤模块

负责构建AI请求参数
"""

import os
import logging
from typing import Dict, Any, Optional

# 简化导入逻辑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.workflow.base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class PoemRequestBuildStep(WorkflowStep):
    """
    诗词请求构建步骤
    
    负责构建AI请求参数
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行请求构建"""
        try:
            logger.info("开始构建诗词请求...")
            
            # 获取诗词名称
            poem_name = data.get("poem_name")
            if not poem_name:
                raise ValueError("诗词名称未提供")
            
            # 构建简化的提示词
            prompt = f"""请为古诗《{poem_name}》写一篇深度解析文章。

要求：
1. 文章结构完整，包含标题、引言、正文、结论
2. 深入分析诗歌的意境、情感、艺术手法
3. 结合历史背景和作者生平
4. 语言优美，富有文学性
5. 字数控制在800-1200字

请直接输出文章内容，不需要额外说明。"""
            
            # 构建请求消息
            messages = [{
                "role": "user",
                "content": prompt
            }]
            
            # 存储请求数据
            data.set("request_messages", messages)
            data.set("model", self.config.get("model", "glm-4-plus"))
            data.set("temperature", self.config.get("temperature", 0.7))
            data.set("max_tokens", self.config.get("max_tokens", 2000))
            
            logger.info(f"诗词请求构建完成: {poem_name}")
            return StepResult(success=True, data=data, message="请求构建成功")
            
        except Exception as e:
            error_msg = f"请求构建失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)