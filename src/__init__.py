"""AI古诗词项目

一个基于智谱AI的古诗词文章生成和图像创作工具包。
"""

__version__ = "1.0.0"
__author__ = "AI古诗词项目团队"
__email__ = "contact@example.com"

# 新架构的主要导入
from .infrastructure.container import Container, configure_container
from .interfaces.base import (
    PoemServiceInterface,
    ImageServiceInterface,
    PromptServiceInterface,
    ConfigInterface
)
from .domain.models import PoemArticle, ImageResult, PromptOptimization
from .services.poem_service import PoemService
from .services.image_service import ImageService
from .services.prompt_service import PromptService
from .infrastructure.config import Config

# 向后兼容的导入（已弃用）
try:
    from .services.poem_service import PoemService as PoemArticleGenerator
    from .services.image_service import ImageService as PoemImageGenerator
    from .services.prompt_service import PromptService as PromptOptimizer
except ImportError:
    # 如果新服务不可用，提供占位符
    PoemArticleGenerator = None
    PoemImageGenerator = None
    PromptOptimizer = None

__all__ = [
    # 新架构
    "Container",
    "configure_container",
    "PoemServiceInterface",
    "ImageServiceInterface",
    "PromptServiceInterface",
    "ConfigInterface",
    "PoemArticle",
    "ImageResult",
    "PromptOptimization",
    "PoemService",
    "ImageService",
    "PromptService",
    "Config",
    # 向后兼容（已弃用）
    "PoemArticleGenerator",
    "PoemImageGenerator",
    "PromptOptimizer"
]