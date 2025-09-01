#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词文章生成工作流主入口模块

提供命令行接口和主要执行逻辑：
- main: 主执行函数
- 命令行参数解析
- 工作流执行协调
"""

import argparse
import logging
import os
import sys
import importlib.util
from typing import Optional

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.workflows.poem_article.config import ConfigIntegrator
from src.workflows.poem_article.workflow import create_poem_article_workflow, execute_workflow

logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="古诗词文章生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 必需参数
    parser.add_argument(
        "poem_name",
        help="要生成文章的古诗词名称"
    )
    
    # 可选参数
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="输出目录路径"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别"
    )
    
    return parser.parse_args()


def setup_logging(level: str = "INFO"):
    """
    设置日志配置
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True
    )


def main(poem_name: Optional[str] = None,
         config_file: Optional[str] = None,
         log_level: str = "INFO") -> int:
    """
    主执行函数
    
    Args:
        poem_name: 诗词名称
        config_file: 配置文件路径
        log_level: 日志级别
    
    Returns:
        退出代码，0表示成功，非0表示失败
    """
    try:
        # 设置日志
        setup_logging(log_level)
        logger.info("古诗词文章生成工作流启动")
        
        # 检查必需参数
        if not poem_name:
            logger.error("请提供诗词名称")
            return 1
        
        # 创建配置整合器
        config_integrator = ConfigIntegrator(config_file)
        config = config_integrator.integrate_config(poem_name=poem_name)
        
        # 创建并执行工作流
        workflow = create_poem_article_workflow(config)
        result = execute_workflow(workflow, poem_name)
        
        # 处理执行结果
        if result["success"]:
            logger.info("工作流执行成功")
            return 0
        else:
            logger.error(f"工作流执行失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        return 1


def cli_main():
    """命令行入口函数"""
    args = parse_arguments()
    exit_code = main(
        poem_name=args.poem_name,
        config_file=args.config,
        log_level=args.log_level
    )
    sys.exit(exit_code)


def test_main():
    """测试函数，参数写死便于直接运行"""
    exit_code = main(
        poem_name="静夜思",
        config_file=None,
        log_level="INFO"
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    # 直接运行测试，无需命令行参数
    test_main()