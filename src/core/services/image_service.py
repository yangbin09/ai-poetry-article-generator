"""图像生成服务实现

提供古诗词图像生成的核心业务逻辑。
"""

import logging
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from ...interfaces.base import ImageServiceInterface, AIClientInterface
from ..models.poem import ImageGenerationRequest, GeneratedImage, Poem
from ...infrastructure.clients.zhipu_client import client
from ...infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class ImageService(ImageServiceInterface):
    """图像生成服务实现"""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None):
        """初始化服务
        
        Args:
            ai_client: AI客户端，如果不提供则使用默认客户端
        """
        self._client = ai_client or client
        self._output_dir = Path(settings.get('image.output_dir', 'output/images'))
        self._output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("图像生成服务初始化成功")
    
    def generate_image(self, prompt: str, **kwargs) -> str:
        """生成图像
        
        Args:
            prompt: 图像生成提示词
            **kwargs: 其他参数
            
        Returns:
            生成图像的URL
        """
        logger.info(f"开始生成图像，提示词长度: {len(prompt)}")
        
        try:
            # 调用AI生成图像
            image_url = self._client.image_generation(
                prompt=prompt,
                model=kwargs.get('model', settings.get('models.image')),
                size=kwargs.get('size', settings.get('image.size', '1024x1024')),
                quality=kwargs.get('quality', settings.get('image.quality', 'standard'))
            )
            
            logger.info(f"图像生成成功: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"生成图像失败，错误: {e}")
            raise Exception(f"生成图像失败: {str(e)}")
    
    def generate_poem_image(self, request: ImageGenerationRequest) -> GeneratedImage:
        """生成古诗词图像
        
        Args:
            request: 图像生成请求
            
        Returns:
            生成的图像对象
        """
        logger.info(f"开始生成古诗词图像: {request.poem.name if request.poem else '未知'}")
        
        try:
            # 构建完整的提示词
            full_prompt = self._build_poem_prompt(request)
            
            # 生成图像
            image_url = self.generate_image(
                prompt=full_prompt,
                model=request.model,
                size=request.size,
                quality=request.quality
            )
            
            # 下载并保存图像（如果需要）
            local_path = None
            if request.save_local:
                local_path = self._download_and_save_image(
                    image_url, 
                    request.poem.name if request.poem else 'unknown'
                )
            
            # 创建生成图像对象
            generated_image = GeneratedImage(
                url=image_url,
                prompt=full_prompt,
                style=request.style,
                model=request.model,
                generated_at=datetime.now(),
                local_path=local_path,
                poem=request.poem,
                metadata={
                    'size': request.size,
                    'quality': request.quality,
                    'original_prompt': request.prompt
                }
            )
            
            logger.info(f"古诗词图像生成成功: {request.poem.name if request.poem else '未知'}")
            return generated_image
            
        except Exception as e:
            logger.error(f"生成古诗词图像失败，错误: {e}")
            raise Exception(f"生成古诗词图像失败: {str(e)}")
    
    def _build_poem_prompt(self, request: ImageGenerationRequest) -> str:
        """构建古诗词图像生成的完整提示词
        
        Args:
            request: 图像生成请求
            
        Returns:
            完整的提示词
        """
        base_style = settings.get('image.default_style', '中国水墨画风格')
        
        # 基础提示词模板
        if request.poem and request.poem.content:
            poem_context = f"根据古诗《{request.poem.name}》的意境：{request.poem.content}"
        elif request.poem:
            poem_context = f"根据古诗《{request.poem.name}》的意境"
        else:
            poem_context = "根据古诗词的意境"
        
        # 构建完整提示词
        full_prompt_parts = [
            poem_context,
            request.prompt if request.prompt else "创作一幅意境深远的画作",
            f"采用{base_style}，注重意境表达和情感传递",
            "画面要有诗意美感，色彩和谐，构图优美"
        ]
        
        return "，".join(full_prompt_parts)
    
    def _download_and_save_image(self, image_url: str, poem_name: str) -> str:
        """下载并保存图像到本地
        
        Args:
            image_url: 图像URL
            poem_name: 诗词名称
            
        Returns:
            本地文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_poem_name = "".join(c for c in poem_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_poem_name}_{timestamp}.png"
            file_path = self._output_dir / filename
            
            # 下载图像
            logger.debug(f"开始下载图像: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 保存到本地
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图像保存成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"下载保存图像失败: {e}")
            raise Exception(f"下载保存图像失败: {str(e)}")
    
    def create_image_request(self, poem: Optional[Poem] = None, prompt: str = "", **kwargs) -> ImageGenerationRequest:
        """创建图像生成请求
        
        Args:
            poem: 诗词对象
            prompt: 自定义提示词
            **kwargs: 其他参数
            
        Returns:
            图像生成请求对象
        """
        return ImageGenerationRequest(
            poem=poem,
            prompt=prompt,
            model=kwargs.get('model', settings.get('models.image')),
            size=kwargs.get('size', settings.get('image.size', '1024x1024')),
            quality=kwargs.get('quality', settings.get('image.quality', 'standard')),
            save_local=kwargs.get('save_local', True)
        )
    
    def get_supported_sizes(self) -> list[str]:
        """获取支持的图像尺寸
        
        Returns:
            支持的尺寸列表
        """
        return ['1024x1024', '1024x1792', '1792x1024']
    
    def get_supported_qualities(self) -> list[str]:
        """获取支持的图像质量
        
        Returns:
            支持的质量列表
        """
        return ['standard', 'hd']
    
    def cleanup_old_images(self, days: int = 30) -> int:
        """清理旧的图像文件
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            deleted_count = 0
            for file_path in self._output_dir.glob('*.png'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"删除旧图像文件: {file_path}")
            
            logger.info(f"清理完成，删除了 {deleted_count} 个旧图像文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧图像文件失败: {e}")
            return 0