"""图像服务实现

实现图像生成相关的业务逻辑。
"""

from typing import Dict, Any, Optional
from ..interfaces.base import ImageServiceInterface, ConfigInterface
from ..domain.models import ImageResult
from ..poem_image import PoemImageGenerator
import os


class ImageService(ImageServiceInterface):
    """图像服务实现"""
    
    def __init__(self, config: ConfigInterface):
        self.config = config
        self._generator = None
    
    @property
    def generator(self) -> PoemImageGenerator:
        """延迟初始化生成器"""
        if self._generator is None:
            self._generator = PoemImageGenerator(
                api_key=self.config.get_api_key(),
                base_url=self.config.get_base_url()
            )
        return self._generator
    
    def generate_image(self, prompt: str, **kwargs) -> ImageResult:
        """生成图像
        
        Args:
            prompt: 图像提示词
            **kwargs: 其他参数
            
        Returns:
            ImageResult: 生成的图像结果对象
        """
        try:
            # 获取参数
            output_path = kwargs.get('output_path', 'output/image.png')
            style = kwargs.get('style')
            size = kwargs.get('size', '1024x1024')
            
            # 使用原有的生成器生成图像
            image_path = self.generator.generate_image(
                prompt=prompt,
                output_path=output_path,
                size=size
            )
            
            # 创建ImageResult对象
            result = ImageResult(
                image_path=image_path,
                prompt=prompt,
                style=style,
                size=size
            )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"生成图像失败: {str(e)}")
    
    def save_image(self, image_result: ImageResult, output_path: str) -> str:
        """保存图像到指定路径
        
        Args:
            image_result: 图像结果对象
            output_path: 输出路径
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 如果图像已经在目标路径，直接返回
            if image_result.image_path == output_path:
                return output_path
            
            # 复制图像文件到新路径
            import shutil
            shutil.copy2(image_result.image_path, output_path)
            
            # 更新图像结果对象的路径
            image_result.image_path = output_path
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"保存图像失败: {str(e)}")