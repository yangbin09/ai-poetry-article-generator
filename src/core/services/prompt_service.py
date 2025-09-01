"""提示词优化服务实现

提供绘画提示词优化的核心业务逻辑。
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from ...interfaces.base import PromptServiceInterface, AIClientInterface
from ..models.poem import PromptOptimizationRequest, OptimizedPrompt
from ...infrastructure.clients.zhipu_client import client
from ...infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class PromptService(PromptServiceInterface):
    """提示词优化服务实现"""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None):
        """初始化服务
        
        Args:
            ai_client: AI客户端，如果不提供则使用默认客户端
        """
        self._client = ai_client or client
        logger.info("提示词优化服务初始化成功")
    
    def optimize_prompt(self, original_prompt: str, style: str = "水墨画", **kwargs) -> str:
        """优化绘画提示词
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            **kwargs: 其他参数
            
        Returns:
            优化后的提示词
        """
        logger.info(f"开始优化提示词，风格: {style}，原始长度: {len(original_prompt)}")
        
        try:
            # 构建优化请求消息
            messages = self._build_optimization_messages(original_prompt, style, **kwargs)
            
            # 调用AI优化提示词
            optimized_content = self._client.chat_completion(
                messages=messages,
                model=kwargs.get('model', settings.get('models.prompt_optimization')),
                temperature=kwargs.get('temperature', settings.get('optimization.temperature', 0.3)),
                max_tokens=kwargs.get('max_tokens', settings.get('optimization.max_tokens', 2000))
            )
            
            logger.info(f"提示词优化成功，优化后长度: {len(optimized_content)}")
            return optimized_content
            
        except Exception as e:
            logger.error(f"优化提示词失败，错误: {e}")
            raise Exception(f"优化提示词失败: {str(e)}")
    
    def optimize_prompt_advanced(self, request: PromptOptimizationRequest) -> OptimizedPrompt:
        """高级提示词优化
        
        Args:
            request: 提示词优化请求
            
        Returns:
            优化后的提示词对象
        """
        logger.info(f"开始高级提示词优化，风格: {request.style}")
        
        try:
            # 优化提示词
            optimized_content = self.optimize_prompt(
                original_prompt=request.original_prompt,
                style=request.style,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                focus_areas=request.focus_areas,
                constraints=request.constraints
            )
            
            # 创建优化结果对象
            optimized_prompt = OptimizedPrompt(
                original_prompt=request.original_prompt,
                optimized_prompt=optimized_content,
                style=request.style,
                model=request.model,
                optimized_at=datetime.now(),
                metadata={
                    'temperature': request.temperature,
                    'focus_areas': request.focus_areas,
                    'constraints': request.constraints,
                    'optimization_version': '1.0'
                }
            )
            
            logger.info(f"高级提示词优化成功")
            return optimized_prompt
            
        except Exception as e:
            logger.error(f"高级提示词优化失败，错误: {e}")
            raise Exception(f"高级提示词优化失败: {str(e)}")
    
    def _build_optimization_messages(self, original_prompt: str, style: str, **kwargs) -> List[Dict[str, str]]:
        """构建提示词优化的消息列表
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            **kwargs: 其他参数
            
        Returns:
            消息列表
        """
        # 获取优化参数
        focus_areas = kwargs.get('focus_areas', [])
        constraints = kwargs.get('constraints', [])
        
        # 构建系统提示
        system_prompt = self._build_system_prompt(style, focus_areas, constraints)
        
        # 构建用户请求
        user_prompt = self._build_user_prompt(original_prompt, style)
        
        return [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    
    def _build_system_prompt(self, style: str, focus_areas: List[str], constraints: List[str]) -> str:
        """构建系统提示词
        
        Args:
            style: 绘画风格
            focus_areas: 重点关注领域
            constraints: 约束条件
            
        Returns:
            系统提示词
        """
        base_prompt = f"""
你是一位专业的{style}绘画提示词优化专家，擅长将普通的描述转换为富有艺术感和技术精度的绘画提示词。

你的专长包括：
1. 深入理解{style}的艺术特点、技法和美学原则
2. 精通色彩理论、构图原理和视觉表现技巧
3. 能够准确描述画面元素、氛围营造和情感表达
4. 熟悉各种绘画工具、材料和表现手法

优化原则：
- 保持原始意图和核心概念不变
- 增强艺术性和视觉冲击力
- 使用专业的绘画术语和技法描述
- 注重画面的层次感和空间感
- 强调{style}的独特美学特征
        """
        
        # 添加重点关注领域
        if focus_areas:
            focus_text = "\n\n特别关注以下方面：\n" + "\n".join(f"- {area}" for area in focus_areas)
            base_prompt += focus_text
        
        # 添加约束条件
        if constraints:
            constraints_text = "\n\n请遵循以下约束：\n" + "\n".join(f"- {constraint}" for constraint in constraints)
            base_prompt += constraints_text
        
        return base_prompt
    
    def _build_user_prompt(self, original_prompt: str, style: str) -> str:
        """构建用户请求提示词
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            
        Returns:
            用户请求提示词
        """
        return f"""
请将以下描述优化为专业的{style}绘画提示词：

原始描述：{original_prompt}

请提供优化后的提示词，要求：
1. 保持原始意境和核心元素
2. 增强{style}的艺术特色
3. 使用专业的绘画术语
4. 注重画面的构图和色彩描述
5. 突出情感表达和意境营造

请直接提供优化后的提示词，无需额外说明。
        """
    
    def create_optimization_request(
        self, 
        original_prompt: str, 
        style: str = "水墨画", 
        **kwargs
    ) -> PromptOptimizationRequest:
        """创建提示词优化请求
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            **kwargs: 其他参数
            
        Returns:
            提示词优化请求对象
        """
        return PromptOptimizationRequest(
            original_prompt=original_prompt,
            style=style,
            model=kwargs.get('model', settings.get('models.prompt_optimization')),
            temperature=kwargs.get('temperature', settings.get('optimization.temperature', 0.3)),
            max_tokens=kwargs.get('max_tokens', settings.get('optimization.max_tokens', 2000)),
            focus_areas=kwargs.get('focus_areas', []),
            constraints=kwargs.get('constraints', [])
        )
    
    def get_supported_styles(self) -> List[str]:
        """获取支持的绘画风格
        
        Returns:
            支持的风格列表
        """
        return [
            "水墨画",
            "油画",
            "水彩画",
            "素描",
            "国画",
            "版画",
            "插画",
            "抽象画",
            "写实画",
            "印象派"
        ]
    
    def get_common_focus_areas(self) -> List[str]:
        """获取常见的重点关注领域
        
        Returns:
            常见关注领域列表
        """
        return [
            "色彩搭配",
            "构图布局",
            "光影效果",
            "质感表现",
            "情感表达",
            "意境营造",
            "细节刻画",
            "空间层次",
            "动态表现",
            "风格统一"
        ]
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """验证提示词质量
        
        Args:
            prompt: 提示词
            
        Returns:
            验证结果
        """
        result = {
            'is_valid': True,
            'score': 0,
            'suggestions': [],
            'issues': []
        }
        
        # 长度检查
        if len(prompt) < 10:
            result['issues'].append('提示词过短，建议增加更多描述')
            result['score'] -= 20
        elif len(prompt) > 1000:
            result['issues'].append('提示词过长，建议精简表达')
            result['score'] -= 10
        else:
            result['score'] += 30
        
        # 内容检查
        if not any(keyword in prompt for keyword in ['色彩', '构图', '光影', '质感', '意境']):
            result['suggestions'].append('建议添加更多艺术技法相关的描述')
            result['score'] -= 15
        else:
            result['score'] += 25
        
        # 风格检查
        style_keywords = ['水墨', '油画', '水彩', '素描', '国画']
        if not any(keyword in prompt for keyword in style_keywords):
            result['suggestions'].append('建议明确指定绘画风格')
            result['score'] -= 10
        else:
            result['score'] += 20
        
        # 情感检查
        emotion_keywords = ['优美', '深远', '宁静', '激昂', '温馨', '神秘']
        if not any(keyword in prompt for keyword in emotion_keywords):
            result['suggestions'].append('建议添加情感色彩的描述')
            result['score'] -= 10
        else:
            result['score'] += 25
        
        # 计算最终分数
        result['score'] = max(0, min(100, result['score']))
        result['is_valid'] = result['score'] >= 60
        
        return result