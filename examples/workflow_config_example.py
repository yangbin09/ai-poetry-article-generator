#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流配置化使用示例

演示如何使用配置文件来运行古诗词文章生成工作流
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.workflows.poem_article.workflow import execute_workflow, load_poem_article_workflow


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 使用默认配置文件执行工作流
    result = execute_workflow("静夜思")
    
    if result['success']:
        print(f"工作流执行成功: {result['poem_name']}")
        print(f"生成的文章: {result['result'].get('article', '未生成')}")
        print(f"生成的图像: {result['result'].get('image_url', '未生成')}")
    else:
        print(f"工作流执行失败: {result['error']}")


def example_custom_config():
    """自定义配置文件示例"""
    print("\n=== 自定义配置文件示例 ===")
    
    # 使用自定义配置文件
    custom_config = "custom_poem_workflow.json"  # 假设存在这个配置文件
    
    try:
        result = execute_workflow("春晓", custom_config)
        
        if result['success']:
            print(f"使用自定义配置执行成功: {result['poem_name']}")
        else:
            print(f"执行失败: {result['error']}")
    except Exception as e:
        print(f"配置文件不存在或有误: {e}")


def example_load_config():
    """加载配置示例"""
    print("\n=== 加载配置示例 ===")
    
    try:
        # 加载工作流配置
        config = load_poem_article_workflow()
        
        print(f"工作流名称: {config.name}")
        print(f"工作流描述: {config.description}")
        print(f"步骤数量: {len(config.steps)}")
        
        print("\n工作流步骤:")
        for i, step in enumerate(config.steps, 1):
            print(f"  {i}. {step.name} ({step.type})")
            if step.description:
                print(f"     描述: {step.description}")
        
    except Exception as e:
        print(f"加载配置失败: {e}")


def main():
    """主函数"""
    print("古诗词工作流配置化使用示例\n")
    
    # 运行示例
    example_load_config()
    example_basic_usage()
    example_custom_config()
    
    print("\n=== 使用说明 ===")
    print("1. 工作流配置文件位于 workflow_configs/ 目录")
    print("2. 默认配置文件: poem_article_workflow.json")
    print("3. 可以通过 --config 参数指定自定义配置文件")
    print("4. 配置文件包含所有步骤的详细配置，无需在代码中硬编码")
    print("\n命令行使用示例:")
    print("python -m src.workflows.poem_article.workflow --poem 静夜思")
    print("python -m src.workflows.poem_article.workflow --poem 春晓 --config custom_config.json")


if __name__ == '__main__':
    main()