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

from src.workflow.base import WorkflowData
from src.workflows.poem_article.steps import (
    EnvironmentSetupStep,
    ClientInitializationStep,
    ImageGenerationStep
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数 - 演示图像生成步骤的使用"""
    try:
        # 初始化工作流数据
        data = WorkflowData()
        
        # 步骤1: 环境设置
        env_step = EnvironmentSetupStep(
            name="environment_setup",
            description="设置环境变量"
        )
        result = env_step.execute(data)
        if not result.success:
            logger.error(f"环境设置失败: {result.error}")
            return
        
        # 步骤2: 客户端初始化
        client_step = ClientInitializationStep(
            name="client_initialization",
            description="初始化智谱AI客户端"
        )
        result = client_step.execute(data)
        if not result.success:
            logger.error(f"客户端初始化失败: {result.error}")
            return
        
        # 步骤3: 图像生成
        # 设置图像生成的输入数据
        data.set("poem_content", "床前明月光，疑是地上霜。举头望明月，低头思故乡。")
        
        image_step = ImageGenerationStep(
            name="image_generation",
            description="生成诗词相关图像",
            config={
                "model": "cogView-4-250304",
                "save_results": True,
                "save_path": "image_generation_results.txt"
            }
        )
        
        result = image_step.execute(data)
        if result.success:
            image_url = data.get("image_url")
            image_prompt = data.get("image_prompt")
            
            print("\n=== 图像生成成功 ===")
            print(f"提示词: {image_prompt}")
            print(f"图像URL: {image_url}")
            print(f"生成时间: {data.get('image_generation_time')}")
        else:
            logger.error(f"图像生成失败: {result.error}")
            
    except Exception as e:
        logger.error(f"程序执行失败: {e}")


if __name__ == "__main__":
    main()