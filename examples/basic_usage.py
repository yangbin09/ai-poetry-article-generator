#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例

演示AI古诗词项目的基本功能使用方法。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.container import configure_container
from src.interfaces.base import (
    PoemServiceInterface, ImageServiceInterface, 
    PromptServiceInterface, ConfigInterface
)


def demo_article_generation(container):
    """演示文章生成功能"""
    print("=" * 50)
    print("📝 古诗词文章生成演示")
    print("=" * 50)
    
    try:
        # 获取诗词服务
        poem_service = container.resolve(PoemServiceInterface)
        
        # 生成文章
        poem_name = "静夜思"
        print(f"正在为《{poem_name}》生成文章...")
        
        article = poem_service.generate_article(poem_name)
        print(f"\n生成的文章内容：\n{article.content}")
        
        # 保存文章
        file_path = poem_service.save_article_to_file(article, f"{poem_name}.md")
        print(f"\n✅ 文章已保存到: {file_path}")
        
    except Exception as e:
        print(f"❌ 文章生成失败: {e}")


def demo_image_generation(container):
    """演示图像生成功能"""
    print("\n" + "=" * 50)
    print("🎨 古诗词图像生成演示")
    print("=" * 50)
    
    try:
        # 获取图像服务
        image_service = container.resolve(ImageServiceInterface)
        
        # 生成图像
        poem_name = "静夜思"
        poem_content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
        
        print(f"正在为《{poem_name}》生成图像...")
        
        result = image_service.generate_image(
            poem_name=poem_name,
            poem_content=poem_content,
            style="水墨画"
        )
        
        print(f"\n✅ 图像生成成功！")
        print(f"图像URL: {result.url}")
        print(f"本地路径: {result.local_path}")
        
    except Exception as e:
        print(f"❌ 图像生成失败: {e}")


def demo_prompt_optimization(container):
    """演示提示词优化功能"""
    print("\n" + "=" * 50)
    print("✨ 提示词优化演示")
    print("=" * 50)
    
    try:
        # 获取提示词服务
        prompt_service = container.resolve(PromptServiceInterface)
        
        # 优化单个提示词
        original_prompt = "根据《静夜思》创作一幅画"
        print(f"原始提示词: {original_prompt}")
        
        optimized = prompt_service.optimize_prompt(original_prompt, style="水墨画")
        print(f"\n优化后提示词: {optimized.optimized_prompt}")
        
        # 获取多种风格建议
        print("\n🎭 多种风格建议:")
        poem_content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
        suggestions = prompt_service.get_style_suggestions(poem_content)
        
        for suggestion in suggestions:
            print(f"\n{suggestion.style}风格:")
            prompt_text = suggestion.prompt
            print(f"  {prompt_text[:100]}..." if len(prompt_text) > 100 else f"  {prompt_text}")
        
        print("\n✅ 提示词优化完成！")
        
    except Exception as e:
        print(f"❌ 提示词优化失败: {e}")


def demo_batch_processing(container):
    """演示批量处理功能"""
    print("\n" + "=" * 50)
    print("🔄 批量处理演示")
    print("=" * 50)
    
    try:
        # 获取服务
        poem_service = container.resolve(PoemServiceInterface)
        image_service = container.resolve(ImageServiceInterface)
        
        # 批量生成文章
        poem_names = ["静夜思", "春晓", "登鹳雀楼"]
        
        print("📚 批量生成文章...")
        
        for poem_name in poem_names:
            print(f"\n正在处理: {poem_name}")
            article = poem_service.generate_article(poem_name)
            file_path = poem_service.save_article_to_file(article, f"{poem_name}.md")
            print(f"✅ 已保存: {file_path}")
        
        # 批量生成图像
        print("\n🎨 批量生成图像...")
        
        poem_contents = {
            "静夜思": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "春晓": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
            "登鹳雀楼": "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。"
        }
        
        for poem_name, content in poem_contents.items():
            print(f"\n正在为《{poem_name}》生成图像...")
            result = image_service.generate_image(
                poem_name=poem_name,
                poem_content=content,
                style="水墨画"
            )
            print(f"✅ 图像已生成: {result.local_path}")
        
        print("\n✅ 批量处理完成！")
        
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")


def main():
    """主函数"""
    print("🎭 AI古诗词项目功能演示")
    print("本演示将展示项目的主要功能模块\n")
    
    # 检查环境变量
    if not os.getenv('ZHIPU_API_KEY'):
        print("⚠️  警告: 未检测到 ZHIPU_API_KEY 环境变量")
        print("请确保已正确配置 .env 文件")
        return
    
    try:
        # 配置依赖注入容器
        container = configure_container()
        
        # 演示各个功能
        demo_article_generation(container)
        demo_image_generation(container)
        demo_prompt_optimization(container)
        demo_batch_processing(container)
        
        print("\n" + "=" * 50)
        print("🎉 所有演示完成！")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()