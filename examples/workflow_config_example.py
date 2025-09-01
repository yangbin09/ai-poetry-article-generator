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

from src.workflow import WorkflowManager, WorkflowConfig, WorkflowTemplate, get_workflow_manager


async def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 获取工作流管理器
    manager = get_workflow_manager()
    
    # 创建默认配置（如果不存在）
    manager.create_default_configs()
    
    try:
        # 使用默认配置文件执行工作流
        execution = await manager.execute_workflow(
            "poem_article_workflow.json",
            input_data={"poem_name": "静夜思"}
        )
        
        if execution.status == "completed":
            print(f"工作流执行成功: {execution.workflow_id}")
            print(f"执行时长: {execution.duration:.2f}秒")
            print(f"结果: {execution.results}")
        else:
            print(f"工作流执行失败: {execution.errors}")
    except Exception as e:
        print(f"执行出错: {e}")


async def example_custom_config():
    """自定义配置文件示例"""
    print("\n=== 自定义配置文件示例 ===")
    
    # 获取工作流管理器
    manager = get_workflow_manager()
    
    # 创建自定义配置
    custom_config = WorkflowConfig(
        name="custom_poem_workflow",
        description="自定义古诗词工作流",
        variables={"poem_name": "春晓", "style": "classical"}
    )
    
    # 保存自定义配置
    config_path = manager.config_manager.save_config(custom_config, "custom_poem_workflow.json")
    print(f"自定义配置已保存到: {config_path}")
    
    try:
        # 使用自定义配置执行工作流
        execution = await manager.execute_workflow(
            "custom_poem_workflow.json",
            input_data={"poem_name": "春晓"}
        )
        
        if execution.status == "completed":
            print(f"使用自定义配置执行成功: {execution.workflow_id}")
        else:
            print(f"执行失败: {execution.errors}")
    except Exception as e:
        print(f"配置文件不存在或有误: {e}")


def example_load_config():
    """加载配置示例"""
    print("\n=== 加载配置示例 ===")
    
    try:
        # 获取工作流管理器
        manager = get_workflow_manager()
        
        # 创建默认配置（如果不存在）
        manager.create_default_configs()
        
        # 列出所有配置文件
        configs = manager.list_configs()
        print(f"可用配置文件: {configs}")
        
        if configs:
            # 加载第一个配置文件
            config_name = configs[0]
            config = manager.config_manager.load_config(config_name)
            
            print(f"\n工作流名称: {config.name}")
            print(f"工作流描述: {config.description}")
            print(f"版本: {config.version}")
            print(f"步骤数量: {len(config.steps)}")
            
            print("\n工作流步骤:")
            for i, step in enumerate(config.steps, 1):
                print(f"  {i}. {step.name} ({step.type})")
                if step.description:
                    print(f"     描述: {step.description}")
                if step.dependencies:
                    print(f"     依赖: {', '.join(step.dependencies)}")
        
    except Exception as e:
        print(f"加载配置失败: {e}")


async def main():
    """主函数"""
    print("古诗词工作流配置化使用示例\n")
    
    # 运行示例
    example_load_config()
    await example_basic_usage()
    await example_custom_config()
    
    print("\n=== 使用说明 ===")
    print("1. 工作流配置文件位于 workflow_configs/ 目录")
    print("2. 默认配置文件: poem_article_workflow.json")
    print("3. 支持 JSON 和 YAML 格式的配置文件")
    print("4. 配置文件包含所有步骤的详细配置，支持依赖关系")
    print("5. 可以通过 WorkflowManager 管理和执行工作流")
    
    print("\n=== 可用函数列表 ===")
    manager = get_workflow_manager()
    functions = manager.get_function_list()
    print(f"注册的函数: {functions}")
    
    print("\n=== 执行历史 ===")
    executions = manager.list_executions()
    if executions:
        for execution in executions[-3:]:  # 显示最近3次执行
            print(f"- {execution.workflow_id}: {execution.status} ({execution.config_name})")
    else:
        print("暂无执行历史")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())