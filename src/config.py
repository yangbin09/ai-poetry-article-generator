"""配置管理模块

统一管理项目配置和API客户端初始化。
"""

import os
from typing import Optional
from dotenv import load_dotenv
from zhipuai import ZhipuAI as ZhipuAiClient


class Config:
    """项目配置类"""
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        self._api_key = os.getenv('ZHIPU_API_KEY')
        
    @property
    def api_key(self) -> str:
        """获取API密钥"""
        if not self._api_key:
            raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
        return self._api_key
    
    def get_client(self) -> ZhipuAiClient:
        """获取智谱AI客户端实例"""
        return ZhipuAiClient(api_key=self.api_key)


# 全局配置实例
config = Config()