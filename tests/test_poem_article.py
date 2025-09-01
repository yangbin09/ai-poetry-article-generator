#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词文章生成模块测试
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.generators.poem_article import PoemArticleGenerator


class TestPoemArticleGenerator:
    """古诗词文章生成器测试"""
    
    @patch('src.core.generators.base.config')
    def test_init(self, mock_config):
        """测试初始化"""
        mock_client = MagicMock()
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemArticleGenerator()
        
        mock_config.get_zhipu_client.assert_called_once()
        assert generator.client == mock_client
    
    def test_build_request_template(self):
        """测试构建请求模板"""
        with patch('src.core.generators.poem_article.config'):
            generator = PoemArticleGenerator()
            template = generator._build_request_template("静夜思")
            
            assert "静夜思" in template
            assert "诗词背景" in template
            assert "诗词内容" in template
            assert "诗词解析" in template
            assert "文化背景" in template
    
    def test_build_web_search_tools(self):
        """测试构建网页搜索工具配置"""
        with patch('src.core.generators.poem_article.config'):
            generator = PoemArticleGenerator()
            tools = generator._build_web_search_tools("静夜思")
            
            assert len(tools) == 1
            assert tools[0]["type"] == "web_search"
            assert "静夜思" in tools[0]["web_search"]["search_query"]
    
    def test_build_messages(self):
        """测试构建消息"""
        with patch('src.core.generators.poem_article.config'):
            generator = PoemArticleGenerator()
            messages, tools = generator._build_messages("静夜思")
            
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert "静夜思" in messages[1]["content"]
            
            assert len(tools) == 1
            assert tools[0]["type"] == "web_search"
    
    @patch('src.core.generators.base.config')
    def test_generate_article_success(self, mock_config):
        """测试文章生成成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "生成的文章内容"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemArticleGenerator()
        result = generator.generate_article("静夜思")
        
        assert result == "生成的文章内容"
        mock_client.chat.completions.create.assert_called_once()
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4.5"
        assert call_args[1]["temperature"] == 0.7
        assert len(call_args[1]["messages"]) == 2
        assert len(call_args[1]["tools"]) == 1
    
    @patch('src.core.generators.base.config')
    def test_generate_article_failure(self, mock_config):
        """测试文章生成失败"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemArticleGenerator()
        
        with pytest.raises(Exception, match="生成文章失败: API错误"):
            generator.generate_article("静夜思")
    
    @patch('src.core.generators.base.config')
    def test_generate_article_custom_params(self, mock_config):
        """测试自定义参数的文章生成"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "自定义文章内容"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemArticleGenerator()
        result = generator.generate_article(
            "静夜思", 
            model="glm-4", 
            temperature=0.5
        )
        
        assert result == "自定义文章内容"
        
        # 验证自定义参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "glm-4"
        assert call_args[1]["temperature"] == 0.5
    
    def test_save_article(self):
        """测试保存文章"""
        with patch('src.core.generators.poem_article.config'):
            generator = PoemArticleGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                article_content = "这是测试文章内容"
                file_path = generator.save_article(
                    "静夜思", 
                    article_content, 
                    temp_dir
                )
                
                # 验证文件路径
                expected_path = os.path.join(temp_dir, "静夜思_文章.txt")
                assert file_path == expected_path
                
                # 验证文件内容
                assert os.path.exists(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                assert saved_content == article_content
    
    def test_save_article_creates_directory(self):
        """测试保存文章时自动创建目录"""
        with patch('src.core.generators.poem_article.config'):
            generator = PoemArticleGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = os.path.join(temp_dir, "new_directory")
                article_content = "测试内容"
                
                file_path = generator.save_article(
                    "测试诗", 
                    article_content, 
                    output_dir
                )
                
                # 验证目录被创建
                assert os.path.exists(output_dir)
                assert os.path.exists(file_path)


class TestPoemArticleGeneratorIntegration:
    """古诗词文章生成器集成测试"""
    
    @patch('src.core.generators.base.config')
    def test_full_workflow(self, mock_config):
        """测试完整工作流"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "完整的文章内容\n包含多行文本"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemArticleGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 生成文章
            article = generator.generate_article("春晓")
            
            # 保存文章
            file_path = generator.save_article("春晓", article, temp_dir)
            
            # 验证结果
            assert article == "完整的文章内容\n包含多行文本"
            assert os.path.exists(file_path)
            
            # 验证文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == article


if __name__ == '__main__':
    pytest.main([__file__])