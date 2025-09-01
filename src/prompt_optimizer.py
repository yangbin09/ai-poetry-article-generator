"""提示词优化模块

提供绘画提示词优化功能，特别针对水墨画风格。
"""

from typing import Optional, Dict, Any
from .config import config


class PromptOptimizer:
    """提示词优化器"""
    
    def __init__(self):
        """初始化提示词优化器"""
        self.client = config.get_client()
    
    def optimize_painting_prompt(self, original_prompt: str, style: str = "水墨画", 
                               model: str = "GLM-4.5-Flash", temperature: float = 0.6) -> str:
        """优化绘画提示词
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            model: 使用的模型
            temperature: 生成温度
            
        Returns:
            优化后的提示词
            
        Raises:
            Exception: 当API调用失败时
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"你是一个提示词优化助手。根据用户输入内容，优化绘画参数，主要是{style}风格。请提供详细、具体、富有艺术感的描述，包括构图、色彩、意境等元素。"
                },
                {
                    "role": "user",
                    "content": f"请优化以下提示词，使其更适合{style}创作：{original_prompt}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"提示词优化失败: {str(e)}")
    
    def optimize_poem_prompt(self, poem_name: str, poem_content: str, 
                           style: str = "水墨画", model: str = "GLM-4.5-Flash") -> str:
        """根据古诗词优化绘画提示词
        
        Args:
            poem_name: 诗词名称
            poem_content: 诗词内容
            style: 绘画风格
            model: 使用的模型
            
        Returns:
            优化后的绘画提示词
        """
        original_prompt = f"根据古诗《{poem_name}》创建一张图片。诗词内容：{poem_content}"
        return self.optimize_painting_prompt(original_prompt, style, model)
    
    def get_style_suggestions(self, poem_content: str, model: str = "GLM-4.5-Flash") -> Dict[str, str]:
        """根据诗词内容获取多种风格建议
        
        Args:
            poem_content: 诗词内容
            model: 使用的模型
            
        Returns:
            不同风格的提示词建议字典
        """
        styles = ["水墨画", "工笔画", "油画", "素描", "版画"]
        suggestions = {}
        
        for style in styles:
            try:
                optimized = self.optimize_painting_prompt(
                    f"根据诗词内容创作：{poem_content}", 
                    style=style, 
                    model=model
                )
                suggestions[style] = optimized
            except Exception as e:
                suggestions[style] = f"优化失败: {str(e)}"
        
        return suggestions
    
    def batch_optimize(self, prompts: list, style: str = "水墨画", 
                      model: str = "GLM-4.5-Flash") -> Dict[str, str]:
        """批量优化提示词
        
        Args:
            prompts: 提示词列表
            style: 绘画风格
            model: 使用的模型
            
        Returns:
            原始提示词到优化提示词的映射字典
        """
        results = {}
        
        for prompt in prompts:
            try:
                optimized = self.optimize_painting_prompt(prompt, style, model)
                results[prompt] = optimized
            except Exception as e:
                results[prompt] = f"优化失败: {str(e)}"
        
        return results