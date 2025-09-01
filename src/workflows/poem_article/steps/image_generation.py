#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成步骤模块

负责基于诗词内容生成相关图像
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


class ImageGenerationStep(WorkflowStep):
    """
    图像生成步骤
    
    负责基于诗词内容调用智谱AI的CogView模型生成相关图像
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, description: str = ""):
        super().__init__(name, description, config)
        self.model = self.config.get("model", "cogView-4-250304")
        self.save_results = self.config.get("save_results", False)
        self.save_path = self.config.get("save_path", "image_results.txt")
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行图像生成"""
        try:
            logger.info("开始生成诗词相关图像...")
            
            # 获取必要的数据
            client = data.get("client")
            prompt = self._build_image_prompt(data)
            
            if not client:
                raise ValueError("客户端未初始化")
            
            if not prompt:
                raise ValueError("图像提示词为空")
            
            # 调用图像生成API
            response = client.images.generations(
                model=self.model,
                prompt=prompt
            )
            
            # 验证响应
            if not response.data or len(response.data) == 0:
                raise ValueError("API返回的数据为空")
            
            image_url = response.data[0].url
            
            # 存储结果
            data.set("image_url", image_url)
            data.set("image_prompt", prompt)
            data.set("image_generation_time", datetime.now().isoformat())
            
            # 可选：保存结果到文件
            if self.save_results:
                self._save_result(prompt, image_url)
            
            logger.info(f"图像生成成功，URL: {image_url}")
            return StepResult(success=True, data=data, message="图像生成成功")
            
        except Exception as e:
            error_msg = f"图像生成失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, data=data, error=error_msg)
    
    def _build_image_prompt(self, data: WorkflowData) -> str:
        """
        构建图像生成提示词
        
        Args:
            data: 工作流数据
            
        Returns:
            图像生成提示词
        """
        # 优先使用自定义提示词
        custom_prompt = data.get("image_prompt")
        if custom_prompt:
            return custom_prompt
        
        # 基于诗词内容构建提示词
        poem_content = data.get("poem_content", "")
        article_content = data.get("article_content", "")
        
        if poem_content:
            # 从诗词内容提取意象
            return f"中国古典诗词意境图像：{poem_content[:100]}，水墨画风格，意境深远，古典美学"
        elif article_content:
            # 从文章内容提取关键信息
            return f"古诗词文章配图：{article_content[:100]}，传统中国画风格，诗意画面"
        else:
            # 默认提示词
            return "中国古典诗词意境，水墨画风格，山水花鸟，意境深远"
    
    def _save_result(self, prompt: str, image_url: str) -> None:
        """
        保存生成结果到文件
        
        Args:
            prompt: 图像提示词
            image_url: 生成的图像URL
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content = f"生成时间: {timestamp}\n提示词: {prompt}\n图像URL: {image_url}\n\n"
            
            with open(self.save_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"结果已保存到: {self.save_path}")
            
        except Exception as e:
            logger.warning(f"保存结果失败: {e}")