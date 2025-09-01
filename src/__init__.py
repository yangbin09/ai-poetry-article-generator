"""AI古诗词项目

一个基于智谱AI的古诗词文章生成和图像创作工具包。
"""

__version__ = "1.0.0"
__author__ = "AI古诗词项目团队"
__email__ = "contact@example.com"

from .poem_article import PoemArticleGenerator
from .poem_image import PoemImageGenerator
from .prompt_optimizer import PromptOptimizer

__all__ = [
    "PoemArticleGenerator",
    "PoemImageGenerator", 
    "PromptOptimizer"
]