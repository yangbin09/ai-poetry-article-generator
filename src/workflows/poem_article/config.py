#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

负责整合命令行参数、配置文件和默认配置
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 导入工作流核心模块
import sys
workflow_path = os.path.join(os.path.dirname(__file__), '..', '..', 'workflow')
if workflow_path not in sys.path:
    sys.path.append(workflow_path)

# 使用完整模块路径避免循环导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from workflow.config import WorkflowConfig, StepConfig

logger = logging.getLogger(__name__)


class ConfigIntegrator:
    """
    配置整合器
    
    负责整合命令行参数、配置文件和默认配置
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置整合器"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self.file_config = self._load_config_file() if config_file else {}
        self.final_config = self.default_config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'workflow': {
                'name': 'poem_article_generation',
                'description': '古诗词文章生成工作流',
                'execution_mode': 'sequential'
            },
            'steps': {
                'environment_setup': {'enabled': True},
                'client_initialization': {'enabled': True},
                'poem_request_build': {'enabled': True},
                'article_generation': {
                    'enabled': True,
                    'model': 'glm-4-plus',
                    'temperature': 0.7,
                    'max_tokens': 2000
                },
                'result_output': {
                    'enabled': True,
                    'save_to_file': True,
                    'output_dir': 'output'
                }
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _load_config_file(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file:
            return {}
        
        config_path = Path(self.config_file)
        if not config_path.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"已加载配置文件: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
    
    def integrate_config(self, 
                        poem_name: str,
                        save: bool = False,
                        output_dir: Optional[str] = None,
                        model: Optional[str] = None,
                        temperature: Optional[float] = None,
                        config_file: Optional[str] = None,
                        log_level: Optional[str] = None,
                        **kwargs) -> WorkflowConfig:
        """
        整合配置
        
        Args:
            poem_name: 诗词名称
            save: 是否保存到文件
            output_dir: 输出目录
            model: AI模型名称
            temperature: 温度参数
            config_file: 配置文件路径
            log_level: 日志级别
            **kwargs: 其他参数
        
        Returns:
            整合后的工作流配置
        """
        # 构建命令行参数配置
        cli_config = {
            "workflow": {
                "poem_name": poem_name
            },
            "steps": {
                "result_output": {
                    "save_to_file": save
                }
            }
        }
        
        # 添加可选参数
        if output_dir:
            cli_config["steps"]["result_output"]["output_dir"] = output_dir
        
        if model:
            cli_config["steps"]["poem_request_build"] = cli_config["steps"].get("poem_request_build", {})
            cli_config["steps"]["poem_request_build"]["model"] = model
        
        if temperature is not None:
            cli_config["steps"]["poem_request_build"] = cli_config["steps"].get("poem_request_build", {})
            cli_config["steps"]["poem_request_build"]["temperature"] = temperature
        
        if log_level:
            cli_config["logging"] = {"level": log_level}
        
        # 如果指定了新的配置文件，重新加载
        if config_file and config_file != self.config_file:
            self.config_file = config_file
            self.file_config = self._load_config_file()
        
        # 合并配置：默认配置 < 文件配置 < 命令行配置
        final_config = self._merge_configs(self.default_config, self.file_config)
        final_config = self._merge_configs(final_config, cli_config)
        
        # 创建步骤配置列表
        step_configs = []
        for step_name, step_config in final_config["steps"].items():
            if step_config.get("enabled", True):
                step_configs.append(
                    StepConfig(
                        name=step_name,
                        type=step_name,  # 使用步骤名称作为类型
                        description=f"{step_name} step",
                        config=step_config,
                        timeout=step_config.get("timeout", 60)
                    )
                )
        
        # 创建工作流配置
        workflow_config = WorkflowConfig(
            name=final_config["workflow"]["name"],
            description=final_config["workflow"]["description"],
            version="1.0.0",
            steps=step_configs
        )
        
        # 添加全局配置
        workflow_config.global_config["poem_name"] = poem_name
        
        # 配置日志
        self._configure_logging(final_config.get("logging", {}))
        
        logger.info("配置整合完成")
        logger.debug(f"最终配置: {final_config}")
        
        return workflow_config
    
    def _configure_logging(self, logging_config: Dict[str, Any]):
        """配置日志系统"""
        level = getattr(logging, logging_config.get("level", "INFO").upper())
        logging.basicConfig(level=level)
    
    def save_config(self, output_path: str):
        """保存配置到文件"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.final_config, f, ensure_ascii=False, indent=2)
    
    def print_config_summary(self):
        """打印配置摘要"""
        workflow_config = self.final_config.get('workflow', {})
        print(f"工作流: {workflow_config.get('name', 'N/A')}")
        print(f"描述: {workflow_config.get('description', 'N/A')}")
        print(f"诗词名称: {self.final_config.get('poem_name', 'N/A')}")
        print(f"启用步骤数: {len(self.final_config.get('steps', {}))}")