#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词图像生成模块测试
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, mock_open

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.poem_image import PoemImageGenerator


class TestPoemImageGenerator:
    """古诗词图像生成器测试"""
    
    @patch('src.poem_image.config')
    def test_init(self, mock_config):
        """测试初始化"""
        mock_client = MagicMock()
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        
        mock_config.get_zhipu_client.assert_called_once()
        assert generator.client == mock_client
    
    @patch('src.poem_image.config')
    def test_generate_image_from_prompt_success(self, mock_config):
        """测试从提示词生成图像成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.data[0].url = "https://example.com/image.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        result = generator.generate_image_from_prompt("美丽的山水画")
        
        assert result == "https://example.com/image.jpg"
        mock_client.images.generations.assert_called_once()
        
        # 验证调用参数
        call_args = mock_client.images.generations.call_args
        assert call_args[1]["model"] == "cogview-3"
        assert call_args[1]["prompt"] == "美丽的山水画"
        assert call_args[1]["size"] == "1024x1024"
    
    @patch('src.poem_image.config')
    def test_generate_image_from_prompt_custom_params(self, mock_config):
        """测试自定义参数的图像生成"""
        mock_response = MagicMock()
        mock_response.data[0].url = "https://example.com/custom.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        result = generator.generate_image_from_prompt(
            "自定义提示词",
            model="cogview-3-plus",
            size="512x512"
        )
        
        assert result == "https://example.com/custom.jpg"
        
        # 验证自定义参数
        call_args = mock_client.images.generations.call_args
        assert call_args[1]["model"] == "cogview-3-plus"
        assert call_args[1]["size"] == "512x512"
    
    @patch('src.poem_image.config')
    def test_generate_image_from_prompt_failure(self, mock_config):
        """测试图像生成失败"""
        mock_client = MagicMock()
        mock_client.images.generations.side_effect = Exception("API错误")
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        
        with pytest.raises(Exception, match="生成图像失败: API错误"):
            generator.generate_image_from_prompt("测试提示词")
    
    @patch('src.poem_image.config')
    def test_generate_image_from_poem(self, mock_config):
        """测试从古诗词生成图像"""
        mock_response = MagicMock()
        mock_response.data[0].url = "https://example.com/poem_image.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        result = generator.generate_image_from_poem("静夜思")
        
        assert result == "https://example.com/poem_image.jpg"
        
        # 验证调用参数包含诗词名称和水墨画风格
        call_args = mock_client.images.generations.call_args
        prompt = call_args[1]["prompt"]
        assert "静夜思" in prompt
        assert "水墨画" in prompt
        assert "中国古典" in prompt
    
    @patch('src.poem_image.config')
    def test_generate_image_from_poem_custom_style(self, mock_config):
        """测试自定义风格的古诗词图像生成"""
        mock_response = MagicMock()
        mock_response.data[0].url = "https://example.com/custom_style.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        generator = PoemImageGenerator()
        result = generator.generate_image_from_poem(
            "春晓", 
            style="油画风格"
        )
        
        assert result == "https://example.com/custom_style.jpg"
        
        # 验证自定义风格
        call_args = mock_client.images.generations.call_args
        prompt = call_args[1]["prompt"]
        assert "春晓" in prompt
        assert "油画风格" in prompt
    
    @patch('requests.get')
    def test_download_image_success(self, mock_get):
        """测试下载图像成功"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('src.poem_image.config'):
            generator = PoemImageGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = generator.download_image(
                    "https://example.com/image.jpg",
                    "静夜思",
                    temp_dir
                )
                
                # 验证文件路径
                expected_path = os.path.join(temp_dir, "静夜思_图像.jpg")
                assert file_path == expected_path
                
                # 验证HTTP请求
                mock_get.assert_called_once_with(
                    "https://example.com/image.jpg", 
                    timeout=30
                )
                
                # 验证文件内容
                assert os.path.exists(file_path)
                with open(file_path, 'rb') as f:
                    saved_content = f.read()
                assert saved_content == b"fake_image_data"
    
    @patch('requests.get')
    def test_download_image_creates_directory(self, mock_get):
        """测试下载图像时自动创建目录"""
        mock_response = MagicMock()
        mock_response.content = b"test_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('src.poem_image.config'):
            generator = PoemImageGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = os.path.join(temp_dir, "new_directory")
                
                file_path = generator.download_image(
                    "https://example.com/test.jpg",
                    "测试诗",
                    output_dir
                )
                
                # 验证目录被创建
                assert os.path.exists(output_dir)
                assert os.path.exists(file_path)
    
    @patch('requests.get')
    def test_download_image_failure(self, mock_get):
        """测试下载图像失败"""
        mock_get.side_effect = Exception("网络错误")
        
        with patch('src.poem_image.config'):
            generator = PoemImageGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                with pytest.raises(Exception, match="下载图像失败: 网络错误"):
                    generator.download_image(
                        "https://example.com/image.jpg",
                        "静夜思",
                        temp_dir
                    )
    
    @patch('src.poem_image.config')
    @patch('requests.get')
    def test_generate_and_save_image_success(self, mock_get, mock_config):
        """测试生成并保存图像成功"""
        # 模拟图像生成API响应
        mock_gen_response = MagicMock()
        mock_gen_response.data[0].url = "https://example.com/generated.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_gen_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        # 模拟图像下载响应
        mock_download_response = MagicMock()
        mock_download_response.content = b"generated_image_data"
        mock_download_response.raise_for_status.return_value = None
        mock_get.return_value = mock_download_response
        
        generator = PoemImageGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_url, file_path = generator.generate_and_save_image(
                "春晓",
                temp_dir
            )
            
            # 验证返回值
            assert image_url == "https://example.com/generated.jpg"
            expected_path = os.path.join(temp_dir, "春晓_图像.jpg")
            assert file_path == expected_path
            
            # 验证文件存在
            assert os.path.exists(file_path)


class TestPoemImageGeneratorIntegration:
    """古诗词图像生成器集成测试"""
    
    @patch('src.poem_image.config')
    @patch('requests.get')
    def test_full_workflow(self, mock_get, mock_config):
        """测试完整工作流"""
        # 模拟图像生成
        mock_gen_response = MagicMock()
        mock_gen_response.data[0].url = "https://example.com/workflow.jpg"
        
        mock_client = MagicMock()
        mock_client.images.generations.return_value = mock_gen_response
        mock_config.get_zhipu_client.return_value = mock_client
        
        # 模拟图像下载
        mock_download_response = MagicMock()
        mock_download_response.content = b"workflow_image_data"
        mock_download_response.raise_for_status.return_value = None
        mock_get.return_value = mock_download_response
        
        generator = PoemImageGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 生成图像
            image_url = generator.generate_image_from_poem("登鹳雀楼")
            
            # 下载图像
            file_path = generator.download_image(
                image_url, 
                "登鹳雀楼", 
                temp_dir
            )
            
            # 验证结果
            assert image_url == "https://example.com/workflow.jpg"
            assert os.path.exists(file_path)
            
            # 验证文件内容
            with open(file_path, 'rb') as f:
                saved_content = f.read()
            assert saved_content == b"workflow_image_data"


if __name__ == '__main__':
    pytest.main([__file__])