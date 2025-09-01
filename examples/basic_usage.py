#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例

演示AI古诗词项目的基本功能使用方法。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import PoemArticleGenerator, PoemImageGenerator, PromptOptimizer


def demo_article_generation():
    """演示文章生成功能"""
    print("=" * 50)
    print("📝 古诗词文章生成演示")
    print("=" * 50)
    
    try:
        # 初始化文章生成器
        generator = PoemArticleGenerator()
        
        # 生成文章
        poem_name = "静夜思"
        print(f"正在为《{poem_name}》生成文章...")
        
        article = generator.generate_article(poem_name)
        print(f"\n生成的文章内容：\n{article}")
        
        # 保存文章
        file_path = generator.save_article(poem_name, article)
        print(f"\n✅ 文章已保存到: {file_path}")
        
    except Exception as e:
        print(f"❌ 文章生成失败: {e}")


def demo_image_generation():
    """演示图像生成功能"""
    print("\n" + "=" * 50)
    print("🎨 古诗词图像生成演示")
    print("=" * 50)
    
    try:
        # 初始化图像生成器
        generator = PoemImageGenerator()
        
        # 生成图像
        poem_name = "静夜思"
        poem_content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
        
        print(f"正在为《{poem_name}》生成图像...")
        
        result = generator.generate_and_save_image(
            poem_name=poem_name,
            poem_content=poem_content,
            style="水墨画"
        )
        
        print(f"\n✅ 图像生成成功！")
        print(f"图像URL: {result['url']}")
        print(f"本地路径: {result['local_path']}")
        
    except Exception as e:
        print(f"❌ 图像生成失败: {e}")


def demo_prompt_optimization():
    """演示提示词优化功能"""
    print("\n" + "=" * 50)
    print("✨ 提示词优化演示")
    print("=" * 50)
    
    try:
        # 初始化提示词优化器
        optimizer = PromptOptimizer()
        
        # 优化单个提示词
        original_prompt = "根据《静夜思》创作一幅画"
        print(f"原始提示词: {original_prompt}")
        
        optimized = optimizer.optimize_painting_prompt(original_prompt, style="水墨画")
        print(f"\n优化后提示词: {optimized}")
        
        # 获取多种风格建议
        print("\n🎭 多种风格建议:")
        poem_content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
        suggestions = optimizer.get_style_suggestions(poem_content)
        
        for style, prompt in suggestions.items():
            print(f"\n{style}风格:")
            print(f"  {prompt[:100]}..." if len(prompt) > 100 else f"  {prompt}")
        
        print("\n✅ 提示词优化完成！")
        
    except Exception as e:
        print(f"❌ 提示词优化失败: {e}")


def demo_batch_processing():
    """演示批量处理功能"""
    print("\n" + "=" * 50)
    print("🔄 批量处理演示")
    print("=" * 50)
    
    try:
        optimizer = PromptOptimizer()
        
        # 批量优化提示词
        prompts = [
            "描绘月夜思乡的场景",
            "表现古代文人的情怀",
            "展现中秋月圆的意境"
        ]
        
        print("正在批量优化提示词...")
        results = optimizer.batch_optimize(prompts, style="水墨画")
        
        for i, (original, optimized) in enumerate(results.items(), 1):
            print(f"\n📝 提示词 {i}:")
            print(f"原始: {original}")
            print(f"优化: {optimized[:100]}..." if len(optimized) > 100 else f"优化: {optimized}")
        
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
        # 演示各个功能
        demo_article_generation()
        demo_image_generation()
        demo_prompt_optimization()
        demo_batch_processing()
        
        print("\n" + "=" * 50)
        print("🎉 所有演示完成！")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()