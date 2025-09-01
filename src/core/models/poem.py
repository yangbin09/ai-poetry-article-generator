"""古诗词领域模型

定义古诗词相关的数据结构和业务实体。
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Poem:
    """古诗词实体"""
    name: str
    content: Optional[str] = None
    author: Optional[str] = None
    dynasty: Optional[str] = None
    background: Optional[str] = None
    analysis: Optional[str] = None
    cultural_context: Optional[str] = None
    influence: Optional[str] = None
    author_story: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'content': self.content,
            'author': self.author,
            'dynasty': self.dynasty,
            'background': self.background,
            'analysis': self.analysis,
            'cultural_context': self.cultural_context,
            'influence': self.influence,
            'author_story': self.author_story
        }


@dataclass
class PoemArticle:
    """古诗词文章实体"""
    poem: Poem
    article_content: str
    generated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'poem': self.poem.to_dict(),
            'article_content': self.article_content,
            'generated_at': self.generated_at.isoformat(),
            'metadata': self.metadata or {}
        }


@dataclass
class ImageGenerationRequest:
    """图像生成请求实体"""
    prompt: str
    poem: Optional[str] = None
    style: str = "水墨画"
    model: str = "cogView-4-250304"
    size: Optional[str] = None
    quality: Optional[str] = None
    save_local: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GeneratedImage:
    """生成的图像实体"""
    url: str
    prompt: str
    style: str
    model: str
    generated_at: datetime
    local_path: Optional[str] = None
    poem: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'url': self.url,
            'prompt': self.prompt,
            'style': self.style,
            'model': self.model,
            'generated_at': self.generated_at.isoformat(),
            'metadata': self.metadata or {}
        }


@dataclass
class PromptOptimizationRequest:
    """提示词优化请求实体"""
    original_prompt: str
    style: str = "水墨画"
    model: str = "GLM-4.5-Flash"
    temperature: float = 0.6
    max_tokens: int = 2000
    focus_areas: List[str] = None
    constraints: List[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.focus_areas is None:
            self.focus_areas = []
        if self.constraints is None:
            self.constraints = []


@dataclass
class OptimizedPrompt:
    """优化后的提示词实体"""
    original_prompt: str
    optimized_prompt: str
    style: str
    model: str
    optimized_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'original_prompt': self.original_prompt,
            'optimized_prompt': self.optimized_prompt,
            'style': self.style,
            'model': self.model,
            'optimized_at': self.optimized_at.isoformat(),
            'metadata': self.metadata or {}
        }