#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词文章生成工作流模块

这个包包含了古诗词文章生成工作流的所有组件：
- steps: 工作流步骤类
- config: 配置管理模块
- workflow: 工作流创建和管理
- main: 主入口文件
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "古诗词文章生成工作流模块"

# 导入主要组件
from .steps import (
    EnvironmentSetupStep,
    ClientInitializationStep,
    PoemRequestBuildStep,
    ArticleGenerationStep,
    ResultOutputStep
)

from .config import ConfigIntegrator
from .workflow import create_poem_article_workflow
from .main import main

__all__ = [
    'EnvironmentSetupStep',
    'ClientInitializationStep', 
    'PoemRequestBuildStep',
    'ArticleGenerationStep',
    'ResultOutputStep',
    'ConfigIntegrator',
    'create_poem_article_workflow',

    'main'
]