"""提示词服务实现

实现提示词优化相关的业务逻辑。
"""

from typing import Dict, Any, Optional, List
from ..interfaces.base import PromptServiceInterface, ConfigInterface
from ..domain.models import PromptOptimization
from ..prompt_optimizer import PromptOptimizer


class PromptService(PromptServiceInterface):
    """提示词服务实现"""
    
    def __init__(self, config: ConfigInterface):
        self.config = config
        self._optimizer = None
    
    @property
    def optimizer(self) -> PromptOptimizer:
        """延迟初始化优化器"""
        if self._optimizer is None:
            self._optimizer = PromptOptimizer(
                api_key=self.config.get_api_key(),
                base_url=self.config.get_base_url(),
                model=self.config.get_model()
            )
        return self._optimizer
    
    def optimize_prompt(self, original_prompt: str, style: Optional[str] = None, **kwargs) -> PromptOptimization:
        """优化提示词
        
        Args:
            original_prompt: 原始提示词
            style: 风格要求
            **kwargs: 其他参数
            
        Returns:
            PromptOptimization: 优化结果对象
        """
        try:
            # 使用原有的优化器优化提示词
            optimized_prompt = self.optimizer.optimize_prompt(
                prompt=original_prompt,
                style=style
            )
            
            # 获取风格建议
            style_suggestions = None
            if style:
                style_suggestions = self.optimizer.get_style_suggestions(style)
            
            # 创建PromptOptimization对象
            result = PromptOptimization(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt,
                style_suggestions=style_suggestions,
                optimization_notes=kwargs.get('notes')
            )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"优化提示词失败: {str(e)}")
    
    def get_style_suggestions(self, style: str) -> str:
        """获取风格建议
        
        Args:
            style: 风格名称
            
        Returns:
            str: 风格建议
        """
        try:
            return self.optimizer.get_style_suggestions(style)
        except Exception as e:
            raise RuntimeError(f"获取风格建议失败: {str(e)}")
    
    def get_available_styles(self) -> List[str]:
        """获取可用的风格列表
        
        Returns:
            List[str]: 可用风格列表
        """
        # 返回预定义的风格列表
        return [
            "古典",
            "现代",
            "抽象",
            "写实",
            "水墨",
            "油画",
            "素描",
            "卡通"
        ]