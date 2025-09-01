"""诗词服务实现

实现诗词相关的业务逻辑。
"""

from typing import Dict, Any, Optional
from ..interfaces.base import PoemServiceInterface, ConfigInterface
from ..domain.models import PoemArticle
from ..poem_article import PoemArticleGenerator
import os


class PoemService(PoemServiceInterface):
    """诗词服务实现"""
    
    def __init__(self, config: ConfigInterface):
        self.config = config
        self._generator = None
    
    @property
    def generator(self) -> PoemArticleGenerator:
        """延迟初始化生成器"""
        if self._generator is None:
            self._generator = PoemArticleGenerator(
                api_key=self.config.get_api_key(),
                base_url=self.config.get_base_url(),
                model=self.config.get_model()
            )
        return self._generator
    
    def generate_article(self, poem_text: str, **kwargs) -> PoemArticle:
        """生成诗词文章
        
        Args:
            poem_text: 诗词文本
            **kwargs: 其他参数
            
        Returns:
            PoemArticle: 生成的文章对象
        """
        try:
            # 使用原有的生成器生成文章
            article_content = self.generator.generate_article(poem_text)
            
            # 创建PoemArticle对象
            article = PoemArticle(
                title=kwargs.get('title', '诗词赏析'),
                content=article_content,
                author=kwargs.get('author'),
                dynasty=kwargs.get('dynasty')
            )
            
            return article
            
        except Exception as e:
            raise RuntimeError(f"生成文章失败: {str(e)}")
    
    def save_article(self, article: PoemArticle, output_path: str) -> str:
        """保存文章到文件
        
        Args:
            article: 文章对象
            output_path: 输出路径
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存文章内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {article.title}\n\n")
                if article.author:
                    f.write(f"**作者**: {article.author}\n")
                if article.dynasty:
                    f.write(f"**朝代**: {article.dynasty}\n")
                f.write(f"**创建时间**: {article.created_at}\n\n")
                f.write(article.content)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"保存文章失败: {str(e)}")