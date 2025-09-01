#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试拆分后的古诗词文章生成模块
"""

import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'src', 'workflows', 'poem_article'))

# 直接导入模块文件
import importlib.util

# 导入 config 模块
config_spec = importlib.util.spec_from_file_location(
    "config", 
    os.path.join(project_root, 'src', 'workflows', 'poem_article', 'config.py')
)
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)
ConfigIntegrator = config_module.ConfigIntegrator

# 导入 workflow 模块
workflow_spec = importlib.util.spec_from_file_location(
    "workflow", 
    os.path.join(project_root, 'src', 'workflows', 'poem_article', 'workflow.py')
)
workflow_module = importlib.util.module_from_spec(workflow_spec)
workflow_spec.loader.exec_module(workflow_module)
create_poem_article_workflow = workflow_module.create_poem_article_workflow
execute_workflow = workflow_module.execute_workflow

def main():
    """主函数"""
    import argparse
    import logging
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成古诗词文章')
    parser.add_argument('--poem', required=True, help='古诗词名称')
    parser.add_argument('--save', action='store_true', help='保存结果到文件')
    parser.add_argument('--output-dir', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    try:
        # 整合配置
        config_integrator = ConfigIntegrator()
        config = config_integrator.integrate_config()
        
        # 创建工作流
        workflow = create_poem_article_workflow(config)
        
        # 执行工作流
        result = execute_workflow(
            workflow=workflow,
            poem_name=args.poem,
            save_result=args.save,
            output_dir=args.output_dir
        )
        
        if result:
            print("\n=== 工作流执行成功 ===")
            print(f"古诗词: {args.poem}")
            if args.save:
                print(f"结果已保存到: {args.output_dir}")
        else:
            print("\n=== 工作流执行失败 ===")
            
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())