#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流配置管理
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class StepConfig:
    """
    步骤配置
    """
    name: str
    type: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    timeout: Optional[int] = None
    retry_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepConfig':
        """从字典创建"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        if not self.name:
            errors.append("步骤名称不能为空")
        
        if not self.type:
            errors.append("步骤类型不能为空")
        
        if self.timeout is not None and self.timeout <= 0:
            errors.append("超时时间必须大于0")
        
        if self.retry_count < 0:
            errors.append("重试次数不能为负数")
        
        return errors


@dataclass
class WorkflowConfig:
    """
    工作流配置
    """
    name: str
    description: str = ""
    version: str = "1.0.0"
    steps: List[StepConfig] = field(default_factory=list)
    global_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def add_step(self, step_config: StepConfig) -> None:
        """添加步骤配置"""
        self.steps.append(step_config)
        self.updated_at = datetime.now().isoformat()
    
    def remove_step(self, step_name: str) -> bool:
        """移除步骤配置"""
        for i, step in enumerate(self.steps):
            if step.name == step_name:
                del self.steps[i]
                self.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def get_step(self, step_name: str) -> Optional[StepConfig]:
        """获取步骤配置"""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def update_step(self, step_name: str, **kwargs) -> bool:
        """更新步骤配置"""
        step = self.get_step(step_name)
        if step:
            for key, value in kwargs.items():
                if hasattr(step, key):
                    setattr(step, key, value)
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def reorder_steps(self, step_names: List[str]) -> bool:
        """重新排序步骤"""
        if len(step_names) != len(self.steps):
            return False
        
        step_dict = {step.name: step for step in self.steps}
        if not all(name in step_dict for name in step_names):
            return False
        
        self.steps = [step_dict[name] for name in step_names]
        self.updated_at = datetime.now().isoformat()
        return True
    
    def validate(self) -> Dict[str, Any]:
        """验证配置"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 验证基本信息
        if not self.name:
            result["errors"].append("工作流名称不能为空")
            result["valid"] = False
        
        if not self.steps:
            result["errors"].append("工作流必须包含至少一个步骤")
            result["valid"] = False
        
        # 验证步骤
        step_names = []
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            if step_errors:
                result["errors"].extend([f"步骤{i+1}({step.name}): {error}" for error in step_errors])
                result["valid"] = False
            
            # 检查重复名称
            if step.name in step_names:
                result["errors"].append(f"步骤名称重复: {step.name}")
                result["valid"] = False
            step_names.append(step.name)
        
        # 检查依赖关系
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_names:
                    result["warnings"].append(f"步骤 '{step.name}' 依赖的步骤 '{dep}' 不存在")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": [step.to_dict() for step in self.steps],
            "global_config": self.global_config,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowConfig':
        """从字典创建"""
        steps_data = data.pop("steps", [])
        config = cls(**data)
        config.steps = [StepConfig.from_dict(step_data) for step_data in steps_data]
        return config
    
    def clone(self, new_name: Optional[str] = None) -> 'WorkflowConfig':
        """克隆配置"""
        data = self.to_dict()
        if new_name:
            data["name"] = new_name
        data["created_at"] = None  # 重置创建时间
        return self.from_dict(data)


class WorkflowTemplate:
    """
    工作流模板
    
    预定义的标准工作流配置模板
    """
    
    # 硬编码的标准模板
    TEMPLATES = {
        "basic_processing": {
            "name": "基础数据处理流程",
            "description": "基本的数据输入、处理、输出流程",
            "version": "1.0.0",
            "steps": [
                {
                    "name": "data_input",
                    "type": "DataInputStep",
                    "description": "数据输入步骤",
                    "config": {
                        "source_type": "file",
                        "format": "json"
                    }
                },
                {
                    "name": "data_processing",
                    "type": "DataProcessingStep",
                    "description": "数据处理步骤",
                    "config": {
                        "processing_type": "transform",
                        "rules": []
                    },
                    "dependencies": ["data_input"]
                },
                {
                    "name": "data_output",
                    "type": "DataOutputStep",
                    "description": "数据输出步骤",
                    "config": {
                        "output_type": "file",
                        "format": "json"
                    },
                    "dependencies": ["data_processing"]
                }
            ],
            "global_config": {
                "timeout": 300,
                "retry_enabled": True,
                "log_level": "INFO"
            }
        },
        
        "ai_content_generation": {
            "name": "AI内容生成流程",
            "description": "AI驱动的内容生成和优化流程",
            "version": "1.0.0",
            "steps": [
                {
                    "name": "prompt_preparation",
                    "type": "PromptPreparationStep",
                    "description": "提示词准备",
                    "config": {
                        "template_type": "creative",
                        "language": "zh-CN"
                    }
                },
                {
                    "name": "content_generation",
                    "type": "ContentGenerationStep",
                    "description": "内容生成",
                    "config": {
                        "model": "gpt-4",
                        "max_tokens": 2000,
                        "temperature": 0.7
                    },
                    "dependencies": ["prompt_preparation"]
                },
                {
                    "name": "content_optimization",
                    "type": "ContentOptimizationStep",
                    "description": "内容优化",
                    "config": {
                        "optimization_type": "quality",
                        "criteria": ["readability", "coherence"]
                    },
                    "dependencies": ["content_generation"]
                },
                {
                    "name": "result_export",
                    "type": "ResultExportStep",
                    "description": "结果导出",
                    "config": {
                        "export_format": "markdown",
                        "include_metadata": True
                    },
                    "dependencies": ["content_optimization"]
                }
            ],
            "global_config": {
                "timeout": 600,
                "retry_enabled": True,
                "log_level": "INFO",
                "api_rate_limit": 10
            }
        },
        
        "data_analysis": {
            "name": "数据分析流程",
            "description": "数据清洗、分析和可视化流程",
            "version": "1.0.0",
            "steps": [
                {
                    "name": "data_loading",
                    "type": "DataLoadingStep",
                    "description": "数据加载",
                    "config": {
                        "source_types": ["csv", "json", "excel"],
                        "encoding": "utf-8"
                    }
                },
                {
                    "name": "data_cleaning",
                    "type": "DataCleaningStep",
                    "description": "数据清洗",
                    "config": {
                        "remove_duplicates": True,
                        "handle_missing": "drop",
                        "outlier_detection": True
                    },
                    "dependencies": ["data_loading"]
                },
                {
                    "name": "data_analysis",
                    "type": "DataAnalysisStep",
                    "description": "数据分析",
                    "config": {
                        "analysis_types": ["descriptive", "correlation"],
                        "statistical_tests": []
                    },
                    "dependencies": ["data_cleaning"]
                },
                {
                    "name": "visualization",
                    "type": "VisualizationStep",
                    "description": "数据可视化",
                    "config": {
                        "chart_types": ["histogram", "scatter", "heatmap"],
                        "output_format": "png"
                    },
                    "dependencies": ["data_analysis"]
                },
                {
                    "name": "report_generation",
                    "type": "ReportGenerationStep",
                    "description": "报告生成",
                    "config": {
                        "report_format": "html",
                        "include_charts": True,
                        "template": "standard"
                    },
                    "dependencies": ["visualization"]
                }
            ],
            "global_config": {
                "timeout": 900,
                "retry_enabled": False,
                "log_level": "DEBUG",
                "memory_limit": "2GB"
            }
        }
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> Optional[WorkflowConfig]:
        """获取模板"""
        template_data = cls.TEMPLATES.get(template_name)
        if template_data:
            return WorkflowConfig.from_dict(template_data.copy())
        return None
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """列出所有模板"""
        return [
            {
                "name": name,
                "title": template["name"],
                "description": template["description"],
                "version": template["version"]
            }
            for name, template in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def create_custom_template(cls, name: str, config: WorkflowConfig) -> None:
        """创建自定义模板"""
        cls.TEMPLATES[name] = config.to_dict()


class ConfigManager:
    """
    配置管理器
    
    负责配置的保存、加载和管理
    """
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "workflow_configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def save_config(self, config: WorkflowConfig, filename: Optional[str] = None) -> Path:
        """
        保存配置到文件
        
        Args:
            config: 工作流配置
            filename: 文件名（可选）
            
        Returns:
            Path: 保存的文件路径
        """
        if filename is None:
            filename = f"{config.name.replace(' ', '_').lower()}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = self.config_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            raise
    
    def load_config(self, filename: str) -> WorkflowConfig:
        """
        从文件加载配置
        
        Args:
            filename: 文件名
            
        Returns:
            WorkflowConfig: 工作流配置
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = WorkflowConfig.from_dict(data)
            self.logger.info(f"配置已加载: {file_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            raise
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """
        列出所有配置文件
        
        Returns:
            List[Dict[str, Any]]: 配置文件信息列表
        """
        configs = []
        
        for file_path in self.config_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                configs.append({
                    "filename": file_path.name,
                    "name": data.get("name", "未知"),
                    "description": data.get("description", ""),
                    "version": data.get("version", "1.0.0"),
                    "step_count": len(data.get("steps", [])),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "file_size": file_path.stat().st_size
                })
                
            except Exception as e:
                self.logger.warning(f"读取配置文件失败 {file_path}: {e}")
        
        return sorted(configs, key=lambda x: x["updated_at"] or "", reverse=True)
    
    def delete_config(self, filename: str) -> bool:
        """
        删除配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否删除成功
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = self.config_dir / filename
        
        if file_path.exists():
            try:
                file_path.unlink()
                self.logger.info(f"配置文件已删除: {file_path}")
                return True
            except Exception as e:
                self.logger.error(f"删除配置文件失败: {e}")
                return False
        
        return False
    
    def backup_config(self, filename: str) -> Optional[Path]:
        """
        备份配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            Optional[Path]: 备份文件路径
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_path.stem}_backup_{timestamp}.json"
        backup_path = self.config_dir / backup_filename
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"配置文件已备份: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"备份配置文件失败: {e}")
            return None