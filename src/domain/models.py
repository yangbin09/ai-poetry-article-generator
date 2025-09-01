"""领域模型定义

定义核心业务实体和值对象。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class PoemArticle:
    """诗词文章模型"""
    title: str
    content: str
    author: Optional[str] = None
    dynasty: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ImageResult:
    """图像生成结果模型"""
    image_path: str
    prompt: str
    style: Optional[str] = None
    size: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PromptOptimization:
    """提示词优化结果模型"""
    original_prompt: str
    optimized_prompt: str
    style_suggestions: Optional[str] = None
    optimization_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}