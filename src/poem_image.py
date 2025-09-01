"""古诗词图像生成模块

提供基于古诗词内容的图像生成功能。
"""

import os
from typing import Optional, Dict, Any
from .config import config


class PoemImageGenerator:
    """古诗词图像生成器"""
    
    def __init__(self):
        """初始化图像生成器"""
        self.client = config.get_client()
    
    def generate_image_from_prompt(self, prompt: str, model: str = "cogView-4-250304") -> str:
        """根据提示词生成图像
        
        Args:
            prompt: 图像生成提示词
            model: 使用的图像生成模型
            
        Returns:
            生成图像的URL
            
        Raises:
            Exception: 当API调用失败时
        """
        try:
            response = self.client.images.generations(
                model=model,
                prompt=prompt
            )
            return response.data[0].url
            
        except Exception as e:
            raise Exception(f"图像生成失败: {str(e)}")
    
    def generate_image_from_poem(self, poem_name: str, poem_content: str = None, 
                               style: str = "水墨画", model: str = "cogView-4-250304") -> str:
        """根据古诗词生成图像
        
        Args:
            poem_name: 诗词名称
            poem_content: 诗词内容，如果为None则使用默认描述
            style: 绘画风格
            model: 使用的图像生成模型
            
        Returns:
            生成图像的URL
        """
        # 构建基于诗词的提示词
        if poem_content:
            prompt = f"{style}风格，根据古诗《{poem_name}》：{poem_content}，创作一幅意境深远的画作"
        else:
            # 使用默认的静夜思场景
            prompt = f"{style}风格，静谧夜晚，窗前床榻，一缕清冷月光透过窗棂洒在地面，营造思乡的意境"
        
        return self.generate_image_from_prompt(prompt, model)
    
    def download_image(self, image_url: str, save_path: str = None, poem_name: str = None) -> str:
        """下载生成的图像
        
        Args:
            image_url: 图像URL
            save_path: 保存路径，如果为None则自动生成
            poem_name: 诗词名称，用于生成文件名
            
        Returns:
            保存的文件路径
        """
        import requests
        from urllib.parse import urlparse
        
        try:
            # 如果没有指定保存路径，则自动生成
            if save_path is None:
                # 确保输出目录存在
                output_dir = "output/images"
                os.makedirs(output_dir, exist_ok=True)
                
                # 生成文件名
                if poem_name:
                    filename = f"{poem_name}_图像.jpg"
                else:
                    filename = "generated_image.jpg"
                
                save_path = os.path.join(output_dir, filename)
            
            # 下载图像
            response = requests.get(image_url)
            response.raise_for_status()
            
            # 保存图像
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return save_path
            
        except Exception as e:
            raise Exception(f"图像下载失败: {str(e)}")
    
    def generate_and_save_image(self, poem_name: str, poem_content: str = None, 
                              style: str = "水墨画", output_dir: str = "output/images") -> Dict[str, str]:
        """生成并保存古诗词图像
        
        Args:
            poem_name: 诗词名称
            poem_content: 诗词内容
            style: 绘画风格
            output_dir: 输出目录
            
        Returns:
            包含图像URL和本地路径的字典
        """
        # 生成图像
        image_url = self.generate_image_from_poem(poem_name, poem_content, style)
        
        # 下载并保存图像
        save_path = self.download_image(
            image_url, 
            save_path=os.path.join(output_dir, f"{poem_name}_图像.jpg"),
            poem_name=poem_name
        )
        
        return {
            "url": image_url,
            "local_path": save_path
        }