"""图像生成服务实现

提供古诗词图像生成的核心业务逻辑。"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from ...interfaces.base import ImageServiceInterface
from ..generators.poem_image import PoemImageGenerator
from ...domain.models import ImageResult

logger = logging.getLogger(__name__)


class ImageService(ImageServiceInterface):
    """图像生成服务实现"""
    
    def __init__(self):
        """初始化服务"""
        self._generator = None
        logger.info("图像生成服务初始化成功")
    
    @property
    def generator(self) -> PoemImageGenerator:
        """延迟初始化生成器"""
        if self._generator is None:
            self._generator = PoemImageGenerator()
        return self._generator
    
    def generate_image(self, prompt: str, **kwargs) -> str:
        """生成图像
        
        Args:
            prompt: 图像生成提示词
            **kwargs: 其他参数
            
        Returns:
            生成图像的本地路径
        """
        logger.info(f"开始生成图像，提示词长度: {len(prompt)}")
        
        try:
            # 使用生成器生成图像
            image_path = self.generator.generate_image(
                prompt=prompt,
                output_path=kwargs.get('output_path'),
                **kwargs
            )
            
            logger.info(f"图像生成成功: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"生成图像失败，错误: {e}")
            raise Exception(f"生成图像失败: {str(e)}")
    
    def generate_poem_image(self, poem_content: str, style: str = "中国古典水墨画", output_path: Optional[str] = None) -> ImageResult:
        """生成古诗词图像
        
        Args:
            poem_content: 诗词内容
            style: 图像风格
            output_path: 输出路径
            
        Returns:
            生成的图像结果对象
        """
        logger.info(f"开始生成古诗词图像")
        
        try:
            # 使用生成器生成图像
            image_path = self.generator.generate_image(
                poem_content=poem_content,
                style=style,
                output_path=output_path
            )
            
            # 创建图像结果对象
            result = ImageResult(
                image_path=image_path,
                poem_content=poem_content,
                style=style,
                metadata={
                    'generated_at': datetime.now().isoformat(),
                    'generator': 'PoemImageGenerator'
                }
            )
            
            logger.info(f"古诗词图像生成成功: {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"生成古诗词图像失败，错误: {e}")
            raise Exception(f"生成古诗词图像失败: {str(e)}")
    
    def get_supported_styles(self) -> list[str]:
        """获取支持的图像风格
        
        Returns:
            支持的风格列表
        """
        return [
            "中国古典水墨画",
            "工笔画",
            "写意画",
            "山水画",
            "花鸟画"
        ]