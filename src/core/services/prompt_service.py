"""提示词优化服务实现

提供绘画提示词优化的核心业务逻辑。
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from ...interfaces.base import PromptServiceInterface
from ..generators.prompt_optimizer import PromptOptimizer
from ...domain.models import OptimizedPrompt

logger = logging.getLogger(__name__)


class PromptService(PromptServiceInterface):
    """提示词优化服务实现"""
    
    def __init__(self):
        """初始化服务"""
        self._optimizer = None
        logger.info("提示词优化服务初始化成功")
    
    @property
    def optimizer(self) -> PromptOptimizer:
        """延迟初始化优化器"""
        if self._optimizer is None:
            self._optimizer = PromptOptimizer()
        return self._optimizer
    
    def optimize_prompt(self, original_prompt: str, style: str = "水墨画", **kwargs) -> OptimizedPrompt:
        """优化绘画提示词
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            **kwargs: 其他参数
            
        Returns:
            优化后的提示词对象
        """
        logger.info(f"开始优化提示词，风格: {style}，原始长度: {len(original_prompt)}")
        
        try:
            # 使用生成器优化提示词
            result = self.optimizer.optimize_prompt(
                original_prompt=original_prompt,
                style=style,
                **kwargs
            )
            
            logger.info(f"提示词优化成功")
            return result
            
        except Exception as e:
            logger.error(f"优化提示词失败，错误: {e}")
            raise Exception(f"优化提示词失败: {str(e)}")
    
    def get_supported_styles(self) -> List[str]:
        """获取支持的绘画风格列表
        
        Returns:
            支持的绘画风格列表
        """
        return [
            "水墨画",
            "油画",
            "素描",
            "水彩画",
            "国画",
            "版画",
            "抽象画",
            "写实主义",
            "印象派",
            "现代艺术"
        ]