#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词图像生成模块

提供古诗词图像生成的核心功能。
"""

import os
import requests
from typing import Optional
from .base import BaseGenerator
from ...infrastructure.config.config import config


class PoemImageGenerator(BaseGenerator):
    """古诗词图像生成器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """初始化生成器
        
        Args:
            api_key: API密钥，如果不提供则从配置中获取
            base_url: API基础URL，如果不提供则从配置中获取
            model: 模型名称，如果不提供则使用默认模型
        """
        super().__init__(api_key, base_url, model)
        self.size = "1024x1024"
    
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        return "cogview-3"
    
    def generate_image_from_prompt(self, prompt: str, **kwargs) -> str:
        """从提示词生成图像
        
        Args:
            prompt: 图像生成提示词
            **kwargs: 其他参数，如model、size等
            
        Returns:
            str: 生成的图像URL
            
        Raises:
            Exception: 当生成失败时抛出异常
        """
        try:
            # 获取参数
            model = kwargs.get('model', self.model)
            size = kwargs.get('size', self.size)
            
            # 调用API生成图像
            response = self.client.images.generations(
                model=model,
                prompt=prompt,
                size=size
            )
            
            return response.data[0].url
            
        except Exception as e:
            raise Exception(f"生成图像失败: {str(e)}")
    
    def generate_image_from_poem(self, poem_name: str, style: str = "水墨画", **kwargs) -> str:
        """从古诗词生成图像
        
        Args:
            poem_name: 诗词名称
            style: 图像风格，默认为水墨画
            **kwargs: 其他参数
            
        Returns:
            str: 生成的图像URL
        """
        # 构建提示词
        prompt = f"{poem_name}，{style}风格，中国古典诗词意境，唯美，高质量"
        
        return self.generate_image_from_prompt(prompt, **kwargs)
    
    def download_image(self, image_url: str, output_path: str) -> str:
        """下载图像到本地
        
        Args:
            image_url: 图像URL
            output_path: 输出路径
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            Exception: 当下载失败时抛出异常
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 下载图像
            response = requests.get(image_url)
            response.raise_for_status()
            
            # 保存文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"下载图像失败: {str(e)}")
    
    def generate_and_save_image(self, poem_name: str, output_dir: str, style: str = "水墨画", **kwargs) -> str:
        """生成并保存图像
        
        Args:
            poem_name: 诗词名称
            output_dir: 输出目录
            style: 图像风格
            **kwargs: 其他参数
            
        Returns:
            str: 保存的文件路径
        """
        # 生成图像
        image_url = self.generate_image_from_poem(poem_name, style, **kwargs)
        
        # 构建文件路径
        filename = f"{poem_name}_{style}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        # 下载并保存
        return self.download_image(image_url, output_path)