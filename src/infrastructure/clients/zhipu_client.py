"""智谱AI客户端实现

提供智谱AI API的统一客户端接口。
"""

import logging
from typing import Dict, Any, Optional, List
from zhipuai import ZhipuAI

from ...interfaces.base import AIClientInterface
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ZhipuAIClient(AIClientInterface):
    """智谱AI客户端实现"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化客户端
        
        Args:
            api_key: API密钥，如果不提供则从配置中获取
        """
        self._api_key = api_key or settings.get_api_key()
        self._client = ZhipuAI(api_key=self._api_key)
        self._timeout = settings.get('api.timeout', 300)
        self._max_retries = settings.get('api.max_retries', 3)
        
        logger.info("智谱AI客户端初始化成功")
    
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        """聊天完成接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            生成的文本内容
            
        Raises:
            Exception: 当API调用失败时
        """
        if model is None:
            model = settings.get('models.chat', 'glm-4-plus')
        
        # 设置默认参数
        params = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', settings.get('generation.temperature', 0.7)),
            'max_tokens': kwargs.get('max_tokens', settings.get('generation.max_tokens', 4000)),
            'top_p': kwargs.get('top_p', settings.get('generation.top_p', 0.9))
        }
        
        # 添加工具配置（如果有）
        if 'tools' in kwargs:
            params['tools'] = kwargs['tools']
        
        try:
            logger.debug(f"发送聊天请求: model={model}, messages_count={len(messages)}")
            response = self._client.chat.completions.create(**params)
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.debug(f"聊天响应成功，内容长度: {len(content) if content else 0}")
                return content or ""
            else:
                raise Exception("API响应中没有有效内容")
                
        except Exception as e:
            logger.error(f"聊天完成API调用失败: {e}")
            raise Exception(f"聊天完成失败: {str(e)}")
    
    def image_generation(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """图像生成接口
        
        Args:
            prompt: 图像生成提示词
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            生成图像的URL
            
        Raises:
            Exception: 当API调用失败时
        """
        if model is None:
            model = settings.get('models.image', 'cogView-4-250304')
        
        params = {
            'model': model,
            'prompt': prompt
        }
        
        # 添加可选参数
        if 'size' in kwargs:
            params['size'] = kwargs['size']
        if 'quality' in kwargs:
            params['quality'] = kwargs['quality']
        
        try:
            logger.debug(f"发送图像生成请求: model={model}, prompt_length={len(prompt)}")
            response = self._client.images.generations(**params)
            
            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                logger.debug(f"图像生成成功: {image_url}")
                return image_url
            else:
                raise Exception("API响应中没有有效的图像数据")
                
        except Exception as e:
            logger.error(f"图像生成API调用失败: {e}")
            raise Exception(f"图像生成失败: {str(e)}")
    
    def get_models(self) -> Dict[str, str]:
        """获取可用模型列表"""
        return {
            'chat': settings.get('models.chat', 'glm-4-plus'),
            'image': settings.get('models.image', 'cogView-4-250304'),
            'prompt_optimization': settings.get('models.prompt_optimization', 'GLM-4.5-Flash')
        }
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 发送一个简单的测试请求
            test_messages = [
                {"role": "user", "content": "你好"}
            ]
            response = self.chat_completion(test_messages)
            return bool(response)
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False


# 全局客户端实例
client = ZhipuAIClient()