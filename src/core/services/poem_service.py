"""古诗词服务实现

提供古诗词文章生成的核心业务逻辑。
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from ...interfaces.base import PoemServiceInterface
from ..generators.poem_article import PoemArticleGenerator
from ...domain.models import PoemArticle

logger = logging.getLogger(__name__)


class PoemService(PoemServiceInterface):
    """古诗词服务实现"""
    
    def __init__(self):
        """初始化服务"""
        self._generator = None
        logger.info("古诗词服务初始化成功")
    
    @property
    def generator(self) -> PoemArticleGenerator:
        """延迟初始化生成器"""
        if self._generator is None:
            self._generator = PoemArticleGenerator()
        return self._generator
    
    def generate_article(self, poem_name: str, **kwargs) -> PoemArticle:
        """生成古诗词文章
        
        Args:
            poem_name: 诗词名称
            **kwargs: 其他参数
            
        Returns:
            生成的文章对象
        """
        logger.info(f"开始生成古诗词文章: {poem_name}")
        
        try:
            # 使用生成器生成文章
            result = self.generator.generate_article(
                poem_name=poem_name,
                **kwargs
            )
            
            logger.info(f"古诗词文章生成成功: {poem_name}")
            return result
            
        except Exception as e:
            logger.error(f"生成古诗词文章失败: {poem_name}, 错误: {e}")
            raise Exception(f"生成古诗词文章失败: {str(e)}")
    

    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表
        
        Returns:
            支持的模型列表
        """
        return [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku"
        ]