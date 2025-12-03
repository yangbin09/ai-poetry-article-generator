"""配置管理模块

统一管理项目配置，支持环境变量、配置文件等多种配置源。
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

from ...interfaces.base import ConfigInterface


class Settings(ConfigInterface):
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        """初始化配置
        
        Args:
            config_file: 配置文件路径
            load_env: 是否加载环境变量
        """
        self._config: Dict[str, Any] = {}
        self._defaults = self._get_default_config()
        
        if load_env:
            load_dotenv()
            
        self._load_env_config()
        
        if config_file:
            self._load_file_config(config_file)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # API配置
            'api': {
                'zhipu_api_key': '',
                'provider': 'zhipu',
                'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
                'timeout': 300,
                'max_retries': 3
            },
            
            # 模型配置
            'models': {
                'chat': 'glm-4-plus',
                'image': 'cogView-4-250304',
                'prompt_optimization': 'GLM-4.5-Flash'
            },
            
            # 生成参数
            'generation': {
                'temperature': 0.7,
                'max_tokens': 4000,
                'top_p': 0.9
            },
            
            # 输出配置
            'output': {
                'directory': 'output',
                'save_to_file': False,
                'file_format': 'json'
            },
            
            # 日志配置
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'app.log'
            },
            
            # 图像生成配置
            'image': {
                'default_style': '水墨画',
                'size': '1024x1024',
                'quality': 'standard'
            }
        }
    
    def _load_env_config(self) -> None:
        """加载环境变量配置"""
        env_mappings = {
            'ZHIPU_API_KEY': 'api.zhipu_api_key',
            'AI_PROVIDER': 'api.provider',
            'API_BASE_URL': 'api.base_url',
            'API_TIMEOUT': 'api.timeout',
            'CHAT_MODEL': 'models.chat',
            'IMAGE_MODEL': 'models.image',
            'TEMPERATURE': 'generation.temperature',
            'OUTPUT_DIR': 'output.directory',
            'LOG_LEVEL': 'logging.level'
        }
        
        for env_key, config_path in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                self._set_nested_value(config_path, env_value)
    
    def _load_file_config(self, config_file: str) -> None:
        """加载配置文件"""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                self._merge_config(file_config)
            except Exception as e:
                print(f"警告: 加载配置文件失败 {config_file}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """合并配置"""
        def merge_dict(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
            return base
        
        merge_dict(self._config, new_config)
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """设置嵌套配置值"""
        keys = path.split('.')
        current = self._config
        
        # 确保路径存在
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值，尝试类型转换
        final_key = keys[-1]
        if isinstance(value, str):
            # 尝试转换数字
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
        
        current[final_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        
        # 先从用户配置中查找
        current = self._config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                break
        else:
            return current
        
        # 再从默认配置中查找
        current = self._defaults
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._set_nested_value(key, value)
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        api_key = self.get('api.zhipu_api_key')
        if not api_key:
            raise ValueError("请设置 ZHIPU_API_KEY 环境变量或在配置文件中配置 api.zhipu_api_key")
        return api_key
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        result = self._defaults.copy()
        self._merge_config(result)
        return result
    
    def save_to_file(self, file_path: str) -> None:
        """保存配置到文件"""
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_all(), f, ensure_ascii=False, indent=2)


# 全局配置实例
settings = Settings()