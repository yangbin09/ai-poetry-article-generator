#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词优化模块测试
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.generators.prompt_optimizer import PromptOptimizer


class TestPromptOptimizer:
    """提示词优化器测试"""
    
    @patch('src.core.generators.base.config')
    def test_init(self, mock_config):
        """测试初始化"""
        mock_client = MagicMock()
        mock_config.get_zhipu_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        
        mock_config.get_zhipu_client.assert_called_once()
        assert optimizer.client == mock_client
        assert optimizer.model == "glm-4"
    
    @patch('src.core.generators.base.config')
    def test_optimize_prompt_success(self, mock_config):
        """测试优化提示词成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "优化后的提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_prompt("静夜思")
        
        assert result == "优化后的提示词"
        mock_client.chat.completions.create.assert_called_once()
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4"
        assert call_args[1]["max_tokens"] == 500
        assert call_args[1]["temperature"] == 0.7
        
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "静夜思" in messages[1]["content"]
    
    @patch('src.core.generators.base.config')
    def test_optimize_prompt_with_style(self, mock_config):
        """测试带风格的提示词优化"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "优化后的油画风格提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_prompt("春晓", style="油画风格")
        
        assert result == "优化后的油画风格提示词"
        
        # 验证风格参数
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]
        assert "春晓" in user_message
        assert "油画风格" in user_message
    
    @patch('src.core.generators.base.config')
    def test_optimize_prompt_failure(self, mock_config):
        """测试提示词优化失败"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        mock_config.get_zhipu_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        
        with pytest.raises(RuntimeError, match="优化提示词失败: API错误"):
            optimizer.optimize_prompt("静夜思")
    
    def test_get_style_suggestions(self):
        """测试获取风格建议"""
        optimizer = PromptOptimizer()
        
        # 测试已知风格
        result = optimizer.get_style_suggestions("古典")
        assert result == "传统中国画风格，注重意境和留白，色彩淡雅"
        
        result = optimizer.get_style_suggestions("水墨")
        assert result == "中国水墨画风格，黑白灰层次丰富"
        
        # 测试未知风格
        result = optimizer.get_style_suggestions("未知风格")
        assert result == "未知风格风格的艺术表现"


class TestPromptOptimizerIntegration:
    """提示词优化器集成测试"""
    
    @patch('src.core.generators.base.config')
    def test_full_workflow(self, mock_config):
        """测试完整工作流程"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "完整优化后的提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        optimizer = PromptOptimizer(model="glm-4-plus")
        
        # 获取风格建议
        style_suggestion = optimizer.get_style_suggestions("古典")
        assert "传统中国画风格" in style_suggestion
        
        # 优化提示词
        result = optimizer.optimize_prompt("静夜思", style="古典")
        assert result == "完整优化后的提示词"
        
        # 验证模型参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4-plus"


if __name__ == '__main__':
    pytest.main([__file__])