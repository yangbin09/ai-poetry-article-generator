#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词优化模块

提供提示词优化功能，用于改进和优化用户输入的提示词。
"""

from typing import Optional
from .base import BaseGenerator
from ...infrastructure.config.config import config


class PromptOptimizer(BaseGenerator):
    """提示词优化器
    
    用于优化和改进用户输入的提示词，使其更适合AI模型生成高质量内容。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """初始化提示词优化器
        
        Args:
            api_key: API密钥，如果不提供则从配置中获取
            base_url: API基础URL，如果不提供则从配置中获取
            model: 使用的模型名称，如果不提供则使用默认模型
        """
        super().__init__(api_key, base_url, model)
        
        # 风格建议映射
        self.style_suggestions = {
            "古典": "传统中国画风格，注重意境和留白，色彩淡雅",
            "水墨": "中国水墨画风格，黑白灰层次丰富",
            "油画": "西方油画风格，色彩浓郁，笔触明显",
            "素描": "铅笔素描风格，线条清晰，明暗对比强烈",
            "现代": "现代艺术风格，抽象表现，色彩大胆",
            "写实": "写实主义风格，细节丰富，真实感强"
        }
    
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        return "glm-4"
    
    def optimize_prompt(self, original_prompt: str, style: Optional[str] = None) -> str:
        """优化提示词
        
        Args:
            original_prompt: 原始提示词
            style: 风格要求（可选）
            
        Returns:
            优化后的提示词
            
        Raises:
            RuntimeError: 当优化失败时抛出
        """
        try:
            # 构建系统提示词
            system_prompt = (
                "你是一个专业的提示词优化专家。你的任务是优化用户提供的提示词，"
                "使其更加清晰、具体、富有表现力，能够生成高质量的内容。"
                "请保持原意的同时，增强描述的生动性和准确性。"
            )
            
            # 构建用户提示词
            user_prompt = f"请优化以下提示词：{original_prompt}"
            if style:
                user_prompt += f"\n\n要求风格：{style}"
                # 如果有风格建议，添加到提示词中
                style_suggestion = self.get_style_suggestions(style)
                user_prompt += f"\n风格说明：{style_suggestion}"
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise RuntimeError(f"优化提示词失败: {str(e)}")
    
    def get_style_suggestions(self, style: str) -> str:
        """获取风格建议
        
        Args:
            style: 风格名称
            
        Returns:
            风格建议描述
        """
        return self.style_suggestions.get(style, f"{style}风格的艺术表现")
    
    def add_style_suggestion(self, style: str, description: str) -> None:
        """添加新的风格建议
        
        Args:
            style: 风格名称
            description: 风格描述
        """
        self.style_suggestions[style] = description
    
    def get_available_styles(self) -> list:
        """获取可用的风格列表
        
        Returns:
            风格名称列表
        """
        return list(self.style_suggestions.keys())