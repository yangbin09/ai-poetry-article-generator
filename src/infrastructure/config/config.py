"""配置管理模块

提供应用程序的配置管理功能。
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from ...interfaces.base import ConfigInterface
from zhipuai import ZhipuAI


class Config(ConfigInterface):
    """配置管理类"""
    
    def __init__(self):
        """初始化配置"""
        load_dotenv()
        self._config = {
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'image_model': os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '2000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            'output_dir': os.getenv('OUTPUT_DIR', 'output'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'zhipu_api_key': os.getenv('ZHIPU_API_KEY', '')
        }
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self._config['api_key']
    
    def get_base_url(self) -> str:
        """获取API基础URL"""
        return self._config['base_url']
    
    def get_model(self) -> str:
        """获取模型名称"""
        return self._config['model']
    
    def get_image_model(self) -> str:
        """获取图像模型名称"""
        return self._config['image_model']
    
    def get_max_tokens(self) -> int:
        """获取最大token数"""
        return self._config['max_tokens']
    
    def get_temperature(self) -> float:
        """获取温度参数"""
        return self._config['temperature']
    
    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self._config['output_dir']
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self._config['log_level']
    
    @property
    def zhipu_api_key(self) -> str:
        """获取智谱AI API密钥"""
        api_key = self._config.get('zhipu_api_key', '')
        if not api_key:
            raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
        return api_key
    
    @property
    def api_key(self) -> str:
        """获取API密钥（向后兼容）"""
        return self.zhipu_api_key
    
    def get_zhipu_client(self) -> ZhipuAI:
        """获取智谱AI客户端"""
        return ZhipuAI(api_key=self.zhipu_api_key)
    
    def get_client(self) -> ZhipuAI:
        """获取客户端（向后兼容）"""
        return self.get_zhipu_client()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置
        
        Args:
            config_dict: 配置字典
        """
        self._config.update(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return self._config.copy()


# 全局配置实例
config = Config()