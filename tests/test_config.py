#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config, config


class TestConfig:
    """配置类测试"""
    
    def test_config_init(self):
        """测试配置初始化"""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            with patch.dict(os.environ, {'ZHIPU_API_KEY': 'test_key'}):
                test_config = Config()
                mock_load_dotenv.assert_called_once()
                assert test_config._api_key == 'test_key'
    
    def test_api_key_property_success(self):
        """测试API密钥属性获取成功"""
        with patch.dict(os.environ, {'ZHIPU_API_KEY': 'test_key'}):
            test_config = Config()
            assert test_config.api_key == 'test_key'
    
    def test_api_key_property_missing(self):
        """测试API密钥缺失时的异常"""
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()
            with pytest.raises(ValueError, match="请在 .env 文件中设置 ZHIPU_API_KEY 环境变量"):
                _ = test_config.api_key
    
    @patch('src.config.ZhipuAiClient')
    def test_get_client(self, mock_client_class):
        """测试获取客户端"""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        with patch.dict(os.environ, {'ZHIPU_API_KEY': 'test_key'}):
            test_config = Config()
            client = test_config.get_client()
            
            mock_client_class.assert_called_once_with(api_key='test_key')
            assert client == mock_client_instance
    
    def test_global_config_instance(self):
        """测试全局配置实例"""
        assert isinstance(config, Config)


class TestConfigIntegration:
    """配置集成测试"""
    
    @patch('src.config.ZhipuAiClient')
    def test_config_workflow(self, mock_client_class):
        """测试配置工作流"""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        with patch.dict(os.environ, {'ZHIPU_API_KEY': 'workflow_test_key'}):
            # 创建配置实例
            test_config = Config()
            
            # 验证API密钥
            assert test_config.api_key == 'workflow_test_key'
            
            # 获取客户端
            client1 = test_config.get_client()
            client2 = test_config.get_client()
            
            # 验证每次调用都创建新的客户端实例
            assert mock_client_class.call_count == 2
            mock_client_class.assert_called_with(api_key='workflow_test_key')


if __name__ == '__main__':
    pytest.main([__file__])