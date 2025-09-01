#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流配置模块

提供工作流配置管理和模板功能。
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from .base import WorkflowStep
from .engine.workflow_engine import WorkflowDefinition, FunctionStep


@dataclass
class StepConfig:
    """步骤配置"""
    name: str
    type: str = "function"  # function, conditional, custom
    description: str = ""
    function: Optional[str] = None  # 函数名或模块路径
    condition: Optional[str] = None  # 条件表达式
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    timeout: Optional[int] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepConfig':
        """从字典创建"""
        return cls(**data)


@dataclass
class WorkflowConfig:
    """工作流配置"""
    name: str
    description: str = ""
    version: str = "1.0.0"
    steps: List[StepConfig] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step_config: StepConfig) -> None:
        """添加步骤配置"""
        self.steps.append(step_config)
    
    def get_step(self, name: str) -> Optional[StepConfig]:
        """获取步骤配置"""
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def remove_step(self, name: str) -> bool:
        """移除步骤配置"""
        for i, step in enumerate(self.steps):
            if step.name == name:
                del self.steps[i]
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": [step.to_dict() for step in self.steps],
            "variables": self.variables,
            "settings": self.settings,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowConfig':
        """从字典创建"""
        steps = [StepConfig.from_dict(step_data) for step_data in data.get("steps", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            steps=steps,
            variables=data.get("variables", {}),
            settings=data.get("settings", {}),
            metadata=data.get("metadata", {})
        )
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """保存到文件"""
        file_path = Path(file_path)
        data = self.to_dict()
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'WorkflowConfig':
        """从文件加载"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return cls.from_dict(data)


class WorkflowTemplate:
    """工作流模板"""
    
    @staticmethod
    def create_poem_article_template() -> WorkflowConfig:
        """创建古诗词文章生成工作流模板"""
        config = WorkflowConfig(
            name="poem_article_workflow",
            description="古诗词文章生成工作流",
            version="1.0.0"
        )
        
        # 添加步骤配置
        steps = [
            StepConfig(
                name="initialize_client",
                type="function",
                description="初始化AI客户端",
                function="initialize_zhipu_client",
                parameters={"api_key_env": "ZHIPU_API_KEY"}
            ),
            StepConfig(
                name="generate_article",
                type="function",
                description="生成古诗词文章",
                function="generate_poem_article",
                parameters={
                    "model": "glm-4",
                    "max_tokens": 2000,
                    "temperature": 0.7
                },
                dependencies=["initialize_client"]
            ),
            StepConfig(
                name="generate_image",
                type="function",
                description="生成配图",
                function="generate_poem_image",
                parameters={
                    "model": "cogview-3",
                    "size": "1024x1024"
                },
                dependencies=["generate_article"],
                optional=True
            ),
            StepConfig(
                name="save_results",
                type="function",
                description="保存结果",
                function="save_workflow_results",
                parameters={"output_dir": "output"},
                dependencies=["generate_article"]
            )
        ]
        
        for step in steps:
            config.add_step(step)
        
        # 设置变量
        config.variables = {
            "poem_name": "",
            "output_format": "markdown",
            "include_image": True
        }
        
        # 设置配置
        config.settings = {
            "parallel_execution": False,
            "stop_on_error": True,
            "timeout": 300
        }
        
        return config
    
    @staticmethod
    def create_image_generation_template() -> WorkflowConfig:
        """创建图像生成工作流模板"""
        config = WorkflowConfig(
            name="image_generation_workflow",
            description="图像生成工作流",
            version="1.0.0"
        )
        
        steps = [
            StepConfig(
                name="optimize_prompt",
                type="function",
                description="优化绘画提示词",
                function="optimize_painting_prompt",
                parameters={"style": "chinese_painting"}
            ),
            StepConfig(
                name="generate_image",
                type="function",
                description="生成图像",
                function="generate_image_from_prompt",
                parameters={
                    "model": "cogview-3",
                    "size": "1024x1024"
                },
                dependencies=["optimize_prompt"]
            ),
            StepConfig(
                name="save_image",
                type="function",
                description="保存图像",
                function="save_generated_image",
                parameters={"output_dir": "output/images"},
                dependencies=["generate_image"]
            )
        ]
        
        for step in steps:
            config.add_step(step)
        
        config.variables = {
            "prompt": "",
            "style": "chinese_painting",
            "quality": "high"
        }
        
        return config


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Union[str, Path] = "workflow_configs"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(self, config: WorkflowConfig, filename: Optional[str] = None) -> Path:
        """保存配置
        
        Args:
            config: 工作流配置
            filename: 文件名，如果为None则使用配置名称
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"{config.name}.json"
        
        file_path = self.config_dir / filename
        config.save_to_file(file_path)
        return file_path
    
    def load_config(self, filename: str) -> WorkflowConfig:
        """加载配置
        
        Args:
            filename: 文件名
            
        Returns:
            工作流配置
        """
        file_path = self.config_dir / filename
        return WorkflowConfig.load_from_file(file_path)
    
    def list_configs(self) -> List[str]:
        """列出所有配置文件
        
        Returns:
            配置文件名列表
        """
        configs = []
        for file_path in self.config_dir.glob("*.json"):
            configs.append(file_path.name)
        for file_path in self.config_dir.glob("*.yml"):
            configs.append(file_path.name)
        for file_path in self.config_dir.glob("*.yaml"):
            configs.append(file_path.name)
        return sorted(configs)
    
    def delete_config(self, filename: str) -> bool:
        """删除配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            是否删除成功
        """
        file_path = self.config_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def create_default_configs(self) -> None:
        """创建默认配置文件"""
        # 创建古诗词文章生成工作流配置
        poem_config = WorkflowTemplate.create_poem_article_template()
        self.save_config(poem_config, "poem_article_workflow.json")
        
        # 创建图像生成工作流配置
        image_config = WorkflowTemplate.create_image_generation_template()
        self.save_config(image_config, "image_generation_workflow.json")