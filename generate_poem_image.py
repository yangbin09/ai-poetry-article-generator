#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词图像生成器
基于智谱AI的CogView模型生成古诗词相关图像
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from zhipuai import ZhipuAI as ZhipuAiClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('poem_image_generator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class PoemImageGenerator:
    """古诗词图像生成器类"""
    
    def __init__(self, api_key: str, model: str = "cogView-4-250304"):
        """
        初始化图像生成器
        
        Args:
            api_key: 智谱AI API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """初始化智谱AI客户端"""
        try:
            self.client = ZhipuAiClient(api_key=self.api_key)
            logger.info(f"智谱AI客户端初始化成功，使用模型: {self.model}")
        except Exception as e:
            logger.error(f"客户端初始化失败: {e}")
            raise
    
    def generate_image(self, prompt: str, save_path: Optional[str] = None) -> str:
        """
        生成图像
        
        Args:
            prompt: 图像描述提示词
            save_path: 可选的保存路径
            
        Returns:
            生成的图像URL
        """
        try:
            logger.info(f"开始生成图像，提示词: {prompt}")
            
            response = self.client.images.generations(
                model=self.model,
                prompt=prompt
            )
            
            if not response.data or len(response.data) == 0:
                raise ValueError("API返回的数据为空")
            
            image_url = response.data[0].url
            logger.info(f"图像生成成功，URL: {image_url}")
            
            # 如果指定了保存路径，记录到文件
            if save_path:
                self._save_result(prompt, image_url, save_path)
            
            return image_url
            
        except Exception as e:
            logger.error(f"图像生成失败: {e}")
            raise
    
    def _save_result(self, prompt: str, image_url: str, save_path: str) -> None:
        """保存生成结果到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content = f"生成时间: {timestamp}\n提示词: {prompt}\n图像URL: {image_url}\n\n"
            
            with open(save_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"结果已保存到: {save_path}")
            
        except Exception as e:
            logger.warning(f"保存结果失败: {e}")

def load_environment() -> str:
    """加载环境变量并获取API密钥"""
    load_dotenv()
    
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
    
    return api_key

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='古诗词图像生成器 - 基于智谱AI的CogView模型',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例用法:
  python generate_poem_image.py "静谧夜晚，窗前床榻，一缕清冷月光透过窗棂洒在地面"
  python generate_poem_image.py "春江花月夜" --model cogView-4-250304 --save-path results.txt
        """
    )
    
    parser.add_argument(
        'prompt',
        help='图像描述提示词'
    )
    
    parser.add_argument(
        '--model',
        default='cogView-4-250304',
        help='使用的模型名称 (默认: cogView-4-250304)'
    )
    
    parser.add_argument(
        '--save-path',
        help='保存结果的文件路径'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    
    return parser

def main():
    """主函数"""
    try:
        # 解析命令行参数
        parser = create_parser()
        args = parser.parse_args()
        
        # 设置日志级别
        logging.getLogger().setLevel(getattr(logging, args.log_level))
        
        # 加载环境变量
        api_key = load_environment()
        
        # 创建图像生成器
        generator = PoemImageGenerator(api_key=api_key, model=args.model)
        
        # 生成图像
        image_url = generator.generate_image(
            prompt=args.prompt,
            save_path=args.save_path
        )
        
        # 输出结果
        print(f"\n生成成功！")
        print(f"图像URL: {image_url}")
        
        if args.save_path:
            print(f"结果已保存到: {args.save_path}")
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()