#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级使用示例

演示AI古诗词项目的高级功能和组合使用方法。
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import PoemArticleGenerator, PoemImageGenerator, PromptOptimizer


class PoemWorkflow:
    """古诗词处理工作流"""
    
    def __init__(self, output_dir: str = "output"):
        """初始化工作流
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.article_generator = PoemArticleGenerator()
        self.image_generator = PoemImageGenerator()
        self.prompt_optimizer = PromptOptimizer()
        
        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "articles").mkdir(exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
    
    def process_poem_complete(self, poem_name: str, poem_content: str = None, 
                            styles: list = None) -> dict:
        """完整处理一首古诗词
        
        Args:
            poem_name: 诗词名称
            poem_content: 诗词内容
            styles: 图像风格列表
            
        Returns:
            处理结果字典
        """
        if styles is None:
            styles = ["水墨画", "工笔画", "油画"]
        
        results = {
            "poem_name": poem_name,
            "poem_content": poem_content,
            "timestamp": datetime.now().isoformat(),
            "article": None,
            "images": {},
            "optimized_prompts": {},
            "errors": []
        }
        
        print(f"🎭 开始完整处理《{poem_name}》")
        
        # 1. 生成文章
        try:
            print("📝 生成文章...")
            article = self.article_generator.generate_article(poem_name)
            article_path = self.article_generator.save_article(
                poem_name, article, str(self.output_dir / "articles")
            )
            results["article"] = {
                "content": article,
                "file_path": article_path
            }
            print(f"✅ 文章生成完成: {article_path}")
        except Exception as e:
            error_msg = f"文章生成失败: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        # 2. 为每种风格生成图像
        for style in styles:
            try:
                print(f"🎨 生成{style}风格图像...")
                
                # 优化提示词
                if poem_content:
                    optimized_prompt = self.prompt_optimizer.optimize_poem_prompt(
                        poem_name, poem_content, style
                    )
                    results["optimized_prompts"][style] = optimized_prompt
                
                # 生成图像
                image_result = self.image_generator.generate_and_save_image(
                    poem_name=poem_name,
                    poem_content=poem_content,
                    style=style,
                    output_dir=str(self.output_dir / "images")
                )
                
                results["images"][style] = image_result
                print(f"✅ {style}图像生成完成: {image_result['local_path']}")
                
            except Exception as e:
                error_msg = f"{style}图像生成失败: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        # 3. 保存处理报告
        report_path = self.save_processing_report(results)
        results["report_path"] = report_path
        
        print(f"📊 处理报告已保存: {report_path}")
        print(f"🎉 《{poem_name}》处理完成！")
        
        return results
    
    def save_processing_report(self, results: dict) -> str:
        """保存处理报告
        
        Args:
            results: 处理结果
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{results['poem_name']}_report_{timestamp}.json"
        report_path = self.output_dir / "reports" / report_filename
        
        # 创建简化的报告（移除大文本内容）
        simplified_results = results.copy()
        if simplified_results.get("article"):
            simplified_results["article"] = {
                "file_path": simplified_results["article"]["file_path"],
                "content_length": len(simplified_results["article"]["content"])
            }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_results, f, ensure_ascii=False, indent=2)
        
        return str(report_path)
    
    def batch_process_poems(self, poems: list) -> dict:
        """批量处理多首古诗词
        
        Args:
            poems: 诗词列表，每个元素为 {"name": "诗名", "content": "内容"}
            
        Returns:
            批量处理结果
        """
        batch_results = {
            "total_poems": len(poems),
            "processed_poems": [],
            "failed_poems": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        print(f"🔄 开始批量处理 {len(poems)} 首古诗词")
        
        for i, poem in enumerate(poems, 1):
            print(f"\n📖 处理第 {i}/{len(poems)} 首: 《{poem['name']}》")
            
            try:
                result = self.process_poem_complete(
                    poem["name"], 
                    poem.get("content")
                )
                batch_results["processed_poems"].append(result)
                
            except Exception as e:
                error_info = {
                    "poem_name": poem["name"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                batch_results["failed_poems"].append(error_info)
                print(f"❌ 《{poem['name']}》处理失败: {e}")
        
        batch_results["end_time"] = datetime.now().isoformat()
        
        # 保存批量处理报告
        batch_report_path = self.save_batch_report(batch_results)
        batch_results["batch_report_path"] = batch_report_path
        
        print(f"\n📊 批量处理完成！")
        print(f"成功: {len(batch_results['processed_poems'])} 首")
        print(f"失败: {len(batch_results['failed_poems'])} 首")
        print(f"报告: {batch_report_path}")
        
        return batch_results
    
    def save_batch_report(self, batch_results: dict) -> str:
        """保存批量处理报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"batch_report_{timestamp}.json"
        report_path = self.output_dir / "reports" / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        
        return str(report_path)


def demo_complete_workflow():
    """演示完整工作流"""
    print("=" * 60)
    print("🎭 完整工作流演示")
    print("=" * 60)
    
    workflow = PoemWorkflow()
    
    # 处理单首诗词
    result = workflow.process_poem_complete(
        poem_name="静夜思",
        poem_content="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
        styles=["水墨画", "工笔画"]
    )
    
    print(f"\n📊 处理结果摘要:")
    print(f"文章: {'✅' if result['article'] else '❌'}")
    print(f"图像: {len(result['images'])} 张")
    print(f"错误: {len(result['errors'])} 个")


def demo_batch_processing():
    """演示批量处理"""
    print("\n" + "=" * 60)
    print("🔄 批量处理演示")
    print("=" * 60)
    
    workflow = PoemWorkflow()
    
    # 定义要处理的诗词列表
    poems = [
        {
            "name": "静夜思",
            "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
        },
        {
            "name": "春晓",
            "content": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"
        }
    ]
    
    # 批量处理
    batch_result = workflow.batch_process_poems(poems)
    
    print(f"\n📊 批量处理摘要:")
    print(f"总数: {batch_result['total_poems']} 首")
    print(f"成功: {len(batch_result['processed_poems'])} 首")
    print(f"失败: {len(batch_result['failed_poems'])} 首")


def demo_style_comparison():
    """演示风格对比"""
    print("\n" + "=" * 60)
    print("🎨 风格对比演示")
    print("=" * 60)
    
    optimizer = PromptOptimizer()
    poem_content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
    
    # 获取多种风格建议
    suggestions = optimizer.get_style_suggestions(poem_content)
    
    print("📝 不同风格的提示词对比:")
    for style, prompt in suggestions.items():
        print(f"\n🎭 {style}:")
        print(f"   {prompt[:150]}..." if len(prompt) > 150 else f"   {prompt}")


def main():
    """主函数"""
    print("🚀 AI古诗词项目高级功能演示")
    print("本演示将展示项目的高级功能和工作流\n")
    
    # 检查环境变量
    if not os.getenv('ZHIPU_API_KEY'):
        print("⚠️  警告: 未检测到 ZHIPU_API_KEY 环境变量")
        print("请确保已正确配置 .env 文件")
        return
    
    try:
        # 演示高级功能
        demo_complete_workflow()
        demo_style_comparison()
        
        # 可选：演示批量处理（注释掉以节省API调用）
        # demo_batch_processing()
        
        print("\n" + "=" * 60)
        print("🎉 高级功能演示完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()