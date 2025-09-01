"""工作流函数库

提供工作流中使用的基础函数。
"""

import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

from .base import WorkflowData, StepResult, StepStatus

logger = logging.getLogger(__name__)


def initialize_zhipu_client(context: WorkflowData, **kwargs) -> Any:
    """初始化智谱AI客户端"""
    try:
        # 模拟客户端初始化
        logger.info("正在初始化智谱AI客户端...")
        
        # 检查环境变量
        api_key = os.getenv('ZHIPU_API_KEY')
        if not api_key:
            logger.warning("未找到ZHIPU_API_KEY环境变量，使用模拟模式")
            context.set('client_mode', 'mock')
        else:
            context.set('client_mode', 'real')
            
        context.set('client_initialized', True)
        context.set('initialization_time', datetime.now().isoformat())
        
        logger.info("智谱AI客户端初始化完成")
        return "客户端初始化成功"
        
    except Exception as e:
        logger.error(f"客户端初始化失败: {e}")
        raise


def generate_poem_article(context: WorkflowData, **kwargs) -> Any:
    """生成古诗词文章"""
    try:
        logger.info("正在生成古诗词文章...")
        
        # 获取输入参数
        topic = context.get('topic', '春天')
        style = context.get('style', '古典')
        
        # 模拟文章生成
        article = f"""# {topic}诗词赏析

春天是诗人们最喜爱的主题之一。在{style}诗词中，我们可以看到对{topic}的深情描绘。

## 经典诗句

"春眠不觉晓，处处闻啼鸟。
夜来风雨声，花落知多少。"

这首诗以简洁的语言，描绘了{topic}的美好景象。

## 诗词解析

诗人通过细腻的观察，将{topic}的特色展现得淋漓尽致。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        context.set('article_content', article)
        context.set('article_length', len(article))
        context.set('generation_time', datetime.now().isoformat())
        
        logger.info(f"古诗词文章生成完成，长度: {len(article)}字符")
        return article
        
    except Exception as e:
        logger.error(f"文章生成失败: {e}")
        raise


def generate_poem_image(context: WorkflowData, **kwargs) -> Any:
    """生成古诗词相关图像"""
    try:
        logger.info("正在生成古诗词图像...")
        
        # 获取输入参数
        poem_content = context.get('poem_content', '春眠不觉晓，处处闻啼鸟')
        style = context.get('image_style', 'chinese_painting')
        
        # 模拟图像生成
        image_prompt = f"中国古典绘画风格，{poem_content}，{style}，水墨画，意境深远"
        image_url = f"https://example.com/generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        context.set('image_prompt', image_prompt)
        context.set('image_url', image_url)
        context.set('image_style', style)
        context.set('image_generation_time', datetime.now().isoformat())
        
        logger.info(f"图像生成完成: {image_url}")
        return {
            'image_url': image_url,
            'prompt': image_prompt,
            'style': style
        }
        
    except Exception as e:
        logger.error(f"图像生成失败: {e}")
        raise


def save_workflow_results(context: WorkflowData, **kwargs) -> Any:
    """保存工作流结果"""
    try:
        logger.info("正在保存工作流结果...")
        
        # 获取保存路径
        save_path = kwargs.get('save_path', 'workflow_results')
        if not save_path.endswith('.json'):
            save_path += '.json'
            
        # 准备保存的数据
        results = {
            'workflow_id': context.get('workflow_id', 'unknown'),
            'execution_time': datetime.now().isoformat(),
            'data': dict(context.data),
            'metadata': dict(context.metadata)
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        
        # 保存到文件
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        context.set('save_path', save_path)
        context.set('save_time', datetime.now().isoformat())
        
        logger.info(f"工作流结果已保存到: {save_path}")
        return save_path
        
    except Exception as e:
        logger.error(f"保存结果失败: {e}")
        raise


def optimize_prompt(context: WorkflowData, **kwargs) -> Any:
    """优化绘画提示词"""
    try:
        logger.info("正在优化绘画提示词...")
        
        # 获取原始提示词
        original_prompt = context.get('prompt', kwargs.get('prompt', '美丽的风景'))
        style = context.get('style', kwargs.get('style', 'chinese_painting'))
        
        # 优化提示词
        optimized_prompt = f"{original_prompt}, {style}, 高质量, 艺术作品, 细节丰富, 色彩和谐"
        
        context.set('optimized_prompt', optimized_prompt)
        context.set('original_prompt', original_prompt)
        
        logger.info(f"提示词优化完成: {optimized_prompt}")
        return optimized_prompt
        
    except Exception as e:
        logger.error(f"提示词优化失败: {e}")
        raise


def generate_image(context: WorkflowData, **kwargs) -> Any:
    """生成图像"""
    try:
        logger.info("正在生成图像...")
        
        # 获取优化后的提示词
        prompt = context.get('optimized_prompt', context.get('prompt', '美丽的风景'))
        
        # 模拟图像生成
        image_url = f"https://example.com/image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        context.set('generated_image_url', image_url)
        context.set('generation_prompt', prompt)
        
        logger.info(f"图像生成完成: {image_url}")
        return image_url
        
    except Exception as e:
        logger.error(f"图像生成失败: {e}")
        raise


def save_image(context: WorkflowData, **kwargs) -> Any:
    """保存图像"""
    try:
        logger.info("正在保存图像...")
        
        # 获取图像URL
        image_url = context.get('generated_image_url')
        if not image_url:
            raise ValueError("未找到要保存的图像URL")
            
        # 模拟保存过程
        save_path = f"images/generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # 确保目录存在
        os.makedirs('images', exist_ok=True)
        
        context.set('saved_image_path', save_path)
        context.set('save_time', datetime.now().isoformat())
        
        logger.info(f"图像已保存到: {save_path}")
        return save_path
        
    except Exception as e:
        logger.error(f"图像保存失败: {e}")
        raise