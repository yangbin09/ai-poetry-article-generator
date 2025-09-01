"""工作流创建和执行模块"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到 Python 路径
import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.workflow.config import WorkflowConfig, ConfigManager
from .steps import (
    EnvironmentSetupStep,
    ClientInitializationStep,
    PoemRequestBuildStep,
    ArticleGenerationStep,
    ImageGenerationStep,
    ResultOutputStep
)

logger = logging.getLogger(__name__)


def load_poem_article_workflow(config_file: str = "poem_article_workflow.json") -> WorkflowConfig:
    """从配置文件加载古诗词文章生成工作流"""
    try:
        # 获取配置文件路径
        config_dir = project_root / "workflow_configs"
        config_manager = ConfigManager(config_dir)
        
        # 加载工作流配置
        workflow_config = config_manager.load_config(config_file)
        logger.info(f"成功加载工作流配置: {config_file}")
        
        return workflow_config
        
    except Exception as e:
        logger.error(f"加载工作流配置失败: {e}")
        raise


def execute_workflow(poem_name: str, config_file: str = "poem_article_workflow.json") -> Dict[str, Any]:
    """执行工作流"""
    from src.workflow.manager import WorkflowManager
    from src.workflow.base import WorkflowData
    from datetime import datetime
    
    logger.info(f"开始执行工作流: {poem_name}")
    
    try:
        # 加载工作流配置
        workflow_config = load_poem_article_workflow(config_file)
        
        # 创建工作流管理器
        manager = WorkflowManager()
        
        # 注册步骤类型
        step_types = {
            'EnvironmentSetupStep': EnvironmentSetupStep,
            'ClientInitializationStep': ClientInitializationStep,
            'PoemRequestBuildStep': PoemRequestBuildStep,
            'ArticleGenerationStep': ArticleGenerationStep,
            'ImageGenerationStep': ImageGenerationStep,
            'ResultOutputStep': ResultOutputStep
        }
        
        for step_type, step_class in step_types.items():
            manager.register_step_type(step_type, step_class)
        
        # 设置初始数据
        initial_data = WorkflowData()
        initial_data.set('poem_name', poem_name)
        initial_data.set('timestamp', datetime.now().isoformat())
        
        # 执行工作流
        context = manager.execute_workflow(workflow_config, initial_data)
        
        logger.info("工作流执行完成")
        return {
            'success': True,
            'result': context.to_dict(),
            'poem_name': poem_name
        }
        
    except Exception as e:
        logger.error(f"工作流执行失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'poem_name': poem_name
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='古诗词文章生成工作流')
    parser.add_argument('--poem', type=str, required=True, help='诗词名称')
    parser.add_argument('--config', type=str, default='poem_article_workflow.json', help='工作流配置文件名')
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 执行工作流
        result = execute_workflow(args.poem, args.config)
        
        if result['success']:
            print(f"工作流执行成功: {args.poem}")
            print(f"结果: {result['result']}")
        else:
            print(f"工作流执行失败: {result['error']}")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        print(f"程序执行失败: {str(e)}")


if __name__ == '__main__':
    main()