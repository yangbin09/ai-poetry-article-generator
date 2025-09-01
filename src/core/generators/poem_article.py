#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词文章生成模块

提供古诗词文章生成的核心功能。
"""

import os
from typing import List, Dict, Any, Optional
from .base import BaseGenerator
from ...infrastructure.config.config import config


class PoemArticleGenerator(BaseGenerator):
    """古诗词文章生成器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """初始化生成器
        
        Args:
            api_key: API密钥，如果不提供则从配置中获取
            base_url: API基础URL，如果不提供则从配置中获取
            model: 模型名称，如果不提供则从配置中获取
        """
        super().__init__(api_key, base_url, model)
        self.temperature = 0.7
    
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        return "glm-4.5"
    
    def generate_article(self, poem_name: str, **kwargs) -> str:
        """生成古诗词文章
        
        Args:
            poem_name: 诗词名称
            **kwargs: 其他参数，如model、temperature等
            
        Returns:
            str: 生成的文章内容
            
        Raises:
            Exception: 当生成失败时抛出异常
        """
        try:
            # 构建消息和工具
            messages, tools = self._build_messages(poem_name)
            
            # 获取参数
            model = kwargs.get('model', self.model)
            temperature = kwargs.get('temperature', self.temperature)
            
            # 调用API生成文章
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"生成文章失败: {str(e)}")
    
    def save_article(self, poem_name: str, article_content: str, output_dir: str) -> str:
        """保存文章到文件
        
        Args:
            poem_name: 诗词名称
            article_content: 文章内容
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建文件路径
        filename = f"{poem_name}_文章.txt"
        file_path = os.path.join(output_dir, filename)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        return file_path
    
    def _build_messages(self, poem_name: str) -> tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """构建消息和工具
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            tuple: (消息列表, 工具列表)
        """
        # 构建请求模板
        template = self._build_request_template(poem_name)
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": "你是一位资深的古典文学专家和诗词研究学者，擅长深入分析古诗词的文学价值、历史背景和文化内涵。请根据用户的要求，生成详细、准确、富有学术价值的古诗词分析文章。"
            },
            {
                "role": "user",
                "content": template
            }
        ]
        
        # 构建工具
        tools = self._build_web_search_tools(poem_name)
        
        return messages, tools
    
    def _build_request_template(self, poem_name: str) -> str:
        """构建请求模板
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            str: 请求模板
        """
        template = f"""
文章标题：{poem_name}

诗词背景：
请为《{poem_name}》提供相关的诗词背景，包括诗人的生平简介、创作背景以及这首诗作的写作时代和历史背景。

诗词内容：
请提供《{poem_name}》的完整诗词内容。

诗词解析：
请详细解析《{poem_name}》的每一行诗句，分析其情感表达、修辞手法、意象及其含义。

文化背景：
请结合这首诗的创作背景，简要介绍相关朝代的文化氛围以及对诗词创作的影响。

诗歌影响与流传：
请介绍《{poem_name}》的历史影响，后人如何解读这首诗，并探讨其流传至今的意义。

诗人背后的故事：
请提供诗人的详细生平，包括重要经历、个性特征，以及创作这首诗时的心路历程。还可以加入诗人与其他文化名人的交往，以及对后代诗歌和文学的影响。
"""
        return template
    
    def _build_web_search_tools(self, poem_name: str) -> List[Dict[str, Any]]:
        """构建网页搜索工具配置
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            List[Dict[str, Any]]: 工具配置列表
        """
        return [
            {
                "type": "web_search",
                "web_search": {
                    "search_query": f"{poem_name} 古诗词 背景 解析 文化",
                    "search_result": True
                }
            }
        ]