#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成步骤使用示例

展示如何在工作流程中使用图像生成步骤
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.workflow import (
    WorkflowManager, 
    WorkflowConfig, 
    StepConfig, 
    WorkflowTemplate,
    get_workflow_manager
)
from src.workflow.base import WorkflowData, StepResult, StepStatus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """主函数 - 演示图像生成工作流的使用"""
    try:
        # 获取工作流管理器
        manager = get_workflow_manager()
        
        # 创建图像生成工作流配置
        config = WorkflowTemplate.create_image_generation_template()
        
        # 保存配置
        config_path = manager.config_manager.save_config(config, "image_generation_example.json")
        logger.info(f"工作流配置已保存到: {config_path}")
        
        # 准备输入数据
        input_data = {
            "prompt": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "poem_content": "静夜思 - 李白",
            "style": "chinese_painting"
        }
        
        print("\n=== 开始执行图像生成工作流 ===")
        print(f"输入数据: {input_data}")
        
        # 执行工作流
        execution = await manager.execute_workflow(
            "image_generation_example.json",
            input_data=input_data
        )
        
        # 检查执行结果
        if execution.status == "completed":
            print("\n=== 图像生成工作流执行成功 ===")
            print(f"工作流ID: {execution.workflow_id}")
            print(f"执行时长: {execution.duration:.2f}秒")
            print(f"完成步骤: {len([r for r in execution.step_results.values() if r.status == StepStatus.COMPLETED])}")
            
            # 显示结果
            if execution.results:
                print(f"\n执行结果:")
                for key, value in execution.results.items():
                    print(f"  {key}: {value}")
            
            # 显示步骤详情
            print(f"\n步骤执行详情:")
            for step_name, step_result in execution.step_results.items():
                status_icon = "✓" if step_result.status == StepStatus.COMPLETED else "✗"
                print(f"  {status_icon} {step_name}: {step_result.message}")
                
        else:
            print("\n=== 图像生成工作流执行失败 ===")
            print(f"状态: {execution.status}")
            if execution.errors:
                print(f"错误信息:")
                for error in execution.errors:
                    print(f"  - {error}")
        
        # 显示可用函数
        print("\n=== 可用函数列表 ===")
        functions = manager.get_function_list()
        print(f"注册的函数: {functions}")
        
        # 显示执行历史
        print("\n=== 执行历史 ===")
        executions = manager.list_executions()
        for exec_record in executions[-3:]:  # 显示最近3次执行
            print(f"- {exec_record.workflow_id}: {exec_record.status} ({exec_record.config_name})")
            
    except Exception as e:
        logger.error(f"程序执行失败: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())