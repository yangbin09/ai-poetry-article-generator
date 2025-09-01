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

from src.prompt_optimizer import PromptOptimizer


class TestPromptOptimizer:
    """提示词优化器测试"""
    
    @patch('src.prompt_optimizer.config')
    def test_init(self, mock_config):
        """测试初始化"""
        mock_client = MagicMock()
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        
        mock_config.get_client.assert_called_once()
        assert optimizer.client == mock_client
    
    @patch('src.prompt_optimizer.config')
    def test_optimize_painting_prompt_success(self, mock_config):
        """测试优化绘画提示词成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "优化后的水墨画提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_painting_prompt("静夜思")
        
        assert result == "优化后的水墨画提示词"
        mock_client.chat.completions.create.assert_called_once()
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4"
        assert call_args[1]["temperature"] == 0.7
        assert len(call_args[1]["messages"]) == 2
        assert "静夜思" in call_args[1]["messages"][1]["content"]
        assert "水墨画" in call_args[1]["messages"][0]["content"]
    
    @patch('src.prompt_optimizer.config')
    def test_optimize_painting_prompt_custom_style(self, mock_config):
        """测试自定义风格的绘画提示词优化"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "优化后的油画提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_painting_prompt(
            "春晓", 
            style="油画风格"
        )
        
        assert result == "优化后的油画提示词"
        
        # 验证自定义风格
        call_args = mock_client.chat.completions.create.call_args
        system_message = call_args[1]["messages"][0]["content"]
        user_message = call_args[1]["messages"][1]["content"]
        assert "油画风格" in system_message
        assert "春晓" in user_message
    
    @patch('src.prompt_optimizer.config')
    def test_optimize_painting_prompt_failure(self, mock_config):
        """测试绘画提示词优化失败"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        
        with pytest.raises(Exception, match="优化绘画提示词失败: API错误"):
            optimizer.optimize_painting_prompt("静夜思")
    
    @patch('src.prompt_optimizer.config')
    def test_optimize_poem_prompt_success(self, mock_config):
        """测试优化诗词提示词成功"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "优化后的诗词创作提示词"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_poem_prompt("月夜思乡")
        
        assert result == "优化后的诗词创作提示词"
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        system_message = call_args[1]["messages"][0]["content"]
        user_message = call_args[1]["messages"][1]["content"]
        assert "诗词创作" in system_message
        assert "月夜思乡" in user_message
    
    @patch('src.prompt_optimizer.config')
    def test_optimize_poem_prompt_custom_params(self, mock_config):
        """测试自定义参数的诗词提示词优化"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "自定义优化结果"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.optimize_poem_prompt(
            "秋思",
            poem_type="七言律诗",
            model="glm-4-plus",
            temperature=0.5
        )
        
        assert result == "自定义优化结果"
        
        # 验证自定义参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4-plus"
        assert call_args[1]["temperature"] == 0.5
        
        system_message = call_args[1]["messages"][0]["content"]
        assert "七言律诗" in system_message
    
    @patch('src.prompt_optimizer.config')
    def test_get_style_suggestions_success(self, mock_config):
        """测试获取风格建议成功"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "建议的艺术风格列表"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.get_style_suggestions("静夜思")
        
        assert result == "建议的艺术风格列表"
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        system_message = call_args[1]["messages"][0]["content"]
        user_message = call_args[1]["messages"][1]["content"]
        assert "艺术风格" in system_message
        assert "静夜思" in user_message
    
    @patch('src.prompt_optimizer.config')
    def test_get_style_suggestions_custom_count(self, mock_config):
        """测试自定义数量的风格建议"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "5个风格建议"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        result = optimizer.get_style_suggestions("春晓", count=5)
        
        assert result == "5个风格建议"
        
        # 验证自定义数量
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]
        assert "5个" in user_message
    
    @patch('src.prompt_optimizer.config')
    def test_batch_optimize_prompts_success(self, mock_config):
        """测试批量优化提示词成功"""
        # 模拟多次API调用
        mock_responses = [
            MagicMock(),
            MagicMock(),
            MagicMock()
        ]
        mock_responses[0].choices[0].message.content = "优化结果1"
        mock_responses[1].choices[0].message.content = "优化结果2"
        mock_responses[2].choices[0].message.content = "优化结果3"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        poems = ["静夜思", "春晓", "登鹳雀楼"]
        results = optimizer.batch_optimize_prompts(poems)
        
        # 验证结果
        expected_results = {
            "静夜思": "优化结果1",
            "春晓": "优化结果2",
            "登鹳雀楼": "优化结果3"
        }
        assert results == expected_results
        
        # 验证API调用次数
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('src.prompt_optimizer.config')
    def test_batch_optimize_prompts_with_failure(self, mock_config):
        """测试批量优化中部分失败的情况"""
        # 模拟部分成功部分失败
        mock_responses = [
            MagicMock(),
            Exception("API错误"),
            MagicMock()
        ]
        mock_responses[0].choices[0].message.content = "优化结果1"
        mock_responses[2].choices[0].message.content = "优化结果3"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        poems = ["静夜思", "春晓", "登鹳雀楼"]
        results = optimizer.batch_optimize_prompts(poems)
        
        # 验证结果（失败的应该有错误信息）
        assert "静夜思" in results
        assert "春晓" in results
        assert "登鹳雀楼" in results
        
        assert results["静夜思"] == "优化结果1"
        assert "错误" in results["春晓"]
        assert results["登鹳雀楼"] == "优化结果3"
    
    @patch('src.prompt_optimizer.config')
    def test_batch_optimize_prompts_custom_style(self, mock_config):
        """测试自定义风格的批量优化"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "油画风格优化结果"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        poems = ["静夜思"]
        results = optimizer.batch_optimize_prompts(
            poems, 
            style="油画风格"
        )
        
        assert results["静夜思"] == "油画风格优化结果"
        
        # 验证风格参数传递
        call_args = mock_client.chat.completions.create.call_args
        system_message = call_args[1]["messages"][0]["content"]
        assert "油画风格" in system_message


class TestPromptOptimizerIntegration:
    """提示词优化器集成测试"""
    
    @patch('src.prompt_optimizer.config')
    def test_full_optimization_workflow(self, mock_config):
        """测试完整优化工作流"""
        # 模拟不同类型的优化响应
        mock_responses = [
            MagicMock(),  # 绘画提示词优化
            MagicMock(),  # 诗词提示词优化
            MagicMock()   # 风格建议
        ]
        mock_responses[0].choices[0].message.content = "优化的绘画提示词"
        mock_responses[1].choices[0].message.content = "优化的诗词提示词"
        mock_responses[2].choices[0].message.content = "风格建议列表"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_config.get_client.return_value = mock_client
        
        optimizer = PromptOptimizer()
        
        # 执行不同类型的优化
        painting_result = optimizer.optimize_painting_prompt("静夜思")
        poem_result = optimizer.optimize_poem_prompt("思乡主题")
        style_result = optimizer.get_style_suggestions("静夜思")
        
        # 验证结果
        assert painting_result == "优化的绘画提示词"
        assert poem_result == "优化的诗词提示词"
        assert style_result == "风格建议列表"
        
        # 验证API调用次数
        assert mock_client.chat.completions.create.call_count == 3


if __name__ == '__main__':
    pytest.main([__file__])