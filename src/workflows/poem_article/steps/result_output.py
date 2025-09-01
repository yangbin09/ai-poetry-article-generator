#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果输出步骤模块

负责输出和保存生成的文章
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# 简化导入逻辑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.workflow.base import WorkflowStep, WorkflowData, StepResult

logger = logging.getLogger(__name__)


class ResultOutputStep(WorkflowStep):
    """
    结果输出步骤
    
    负责输出和保存生成的文章
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行结果输出"""
        try:
            logger.info("开始输出结果...")
            
            # 获取文章内容
            article_content = data.get("article_content")
            poem_name = data.get("poem_name")
            
            if not article_content:
                raise ValueError("文章内容为空")
            
            # 控制台输出
            self._output_to_console(article_content, poem_name)
            
            # 可选保存到文件
            file_path = None
            if self.config.get("save_to_file", False):
                file_path = self._save_to_file(article_content, poem_name, data)
                data.set("output_file", file_path)
                logger.info(f"文章已保存到: {file_path}")
            
            logger.info("结果输出完成")
            return StepResult(success=True, data=data, message="结果输出成功")
            
        except Exception as e:
            error_msg = f"结果输出失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)
    
    def _output_to_console(self, content: str, poem_name: str) -> None:
        """输出到控制台"""
        print("\n" + "="*50)
        print(f"《{poem_name}》文章生成完成")
        print("="*50)
        print(content)
        print("="*50)
    
    def _save_to_file(self, content: str, poem_name: str, data: WorkflowData) -> str:
        """保存到文件"""
        output_dir = Path(self.config.get("output_dir", "output"))
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{poem_name}_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"《{poem_name}》文章\n")
            f.write(f"生成时间: {data.get('generation_time')}\n")
            f.write("\n" + content)
        
        return str(file_path)