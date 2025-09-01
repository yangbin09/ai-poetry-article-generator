#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词文章生成工作流

使用工作流模块实现古诗词文章的自动化生成，包括：
- 环境配置和客户端初始化
- 诗词信息搜索和收集
- 文章内容生成
- 结果输出和保存
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# 添加工作流模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'workflow'))

# 导入工作流核心模块
from base import WorkflowStep, WorkflowData, StepResult
from manager import WorkflowManager
from config import WorkflowConfig, StepConfig
from engine import WorkflowEngine

# 导入第三方依赖
try:
    from dotenv import load_dotenv
    from zhipuai import ZhipuAI
except ImportError as e:
    logging.error(f"缺少必要的依赖包: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('poem_article_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnvironmentSetupStep(WorkflowStep):
    """
    环境设置步骤
    
    负责加载环境变量和初始化必要的配置
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, description: str = ""):
        super().__init__(name, config, description)
        self.env_file = self.config.get("env_file", ".env")
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行环境设置"""
        try:
            logger.info("开始环境设置...")
            
            # 加载环境变量
            load_dotenv(self.env_file)
            
            # 验证必要的环境变量
            api_key = os.getenv('ZHIPU_API_KEY')
            if not api_key:
                raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
            
            # 将配置信息存储到数据中
            data.set("api_key", api_key)
            data.set("environment_ready", True)
            
            logger.info("环境设置完成")
            return StepResult(success=True, data=data, message="环境设置成功")
            
        except Exception as e:
            error_msg = f"环境设置失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)


class ClientInitializationStep(WorkflowStep):
    """
    客户端初始化步骤
    
    负责初始化智谱AI客户端
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行客户端初始化"""
        try:
            logger.info("开始初始化客户端...")
            
            # 检查环境是否已设置
            if not data.get("environment_ready"):
                raise ValueError("环境未正确设置")
            
            # 获取API密钥
            api_key = data.get("api_key")
            if not api_key:
                raise ValueError("API密钥未找到")
            
            # 初始化客户端
            client = ZhipuAI(api_key=api_key)
            data.set("client", client)
            
            logger.info("客户端初始化完成")
            return StepResult(success=True, data=data, message="客户端初始化成功")
            
        except Exception as e:
            error_msg = f"客户端初始化失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)


class PoemRequestBuildStep(WorkflowStep):
    """
    诗词请求构建步骤
    
    负责构建AI请求的消息和工具配置
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行请求构建"""
        try:
            logger.info("开始构建诗词请求...")
            
            # 获取诗词名称
            poem_name = data.get("poem_name")
            if not poem_name:
                raise ValueError("诗词名称未提供")
            
            # 构建请求模板
            template = f"""
            文章标题：{poem_name}

            诗词背景：
            请为《{poem_name}》提供相关的诗词背景，包括诗人的生平简介、创作背景以及这首诗作的写作时代和历史背景。

            诗词内容：
            请提供《{poem_name}》的完整诗词内容。

            诗词解析：
            请详细解析《{poem_name}》的每一行诗句，分析其情感表达、修辞手法、意象及其含义。

            文化背景：
            请结合这首诗的创作背景，简要介绍唐代的文化氛围以及对诗词创作的影响。

            诗歌影响与流传：
            请介绍《{poem_name}》的历史影响，后人如何解读这首诗，并探讨其流传至今的意义。

            诗人背后的故事：
            请提供诗人的详细生平，包括重要经历、个性特征，以及创作这首诗时的心路历程。还可以加入诗人与其他文化名人的交往，以及对后代诗歌和文学的影响。
            """
            
            # 构建请求消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个古诗词研究助手，能够根据用户提供的诗词名称，按照模板生成结构化文章，内容包括诗词背景、作者简介、诗词解析、文化背景、诗歌影响及诗人背后的故事等，并通过网页搜索获取更多相关信息。"
                },
                {
                    "role": "user",
                    "content": template
                }
            ]
            
            # 网页搜索工具配置
            tools = [{
                "type": "web_search",
                "web_search": {
                    "search_query": f"《{poem_name}》 诗词背景 作者简介 诗歌解析",
                    "search_result": True
                }
            }]
            
            # 存储请求数据
            data.set("request_messages", messages)
            data.set("request_tools", tools)
            data.set("model", self.config.get("model", "glm-4.5"))
            data.set("temperature", self.config.get("temperature", 0.7))
            
            logger.info(f"诗词请求构建完成: {poem_name}")
            return StepResult(success=True, data=data, message="请求构建成功")
            
        except Exception as e:
            error_msg = f"请求构建失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)


class ArticleGenerationStep(WorkflowStep):
    """
    文章生成步骤
    
    负责调用AI接口生成诗词文章
    """
    
    def execute(self, data: WorkflowData) -> StepResult:
        """执行文章生成"""
        try:
            logger.info("开始生成诗词文章...")
            
            # 获取必要的数据
            client = data.get("client")
            messages = data.get("request_messages")
            tools = data.get("request_tools")
            model = data.get("model")
            temperature = data.get("temperature")
            
            if not all([client, messages, tools, model]):
                raise ValueError("缺少必要的请求参数")
            
            # 发送请求
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            # 获取生成的文章内容
            article_content = response.choices[0].message.content
            
            # 存储结果
            data.set("article_content", article_content)
            data.set("generation_time", datetime.now().isoformat())
            
            logger.info("文章生成完成")
            return StepResult(success=True, data=data, message="文章生成成功")
            
        except Exception as e:
            error_msg = f"文章生成失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)


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
            print("\n" + "="*50)
            print(f"《{poem_name}》文章生成完成")
            print("="*50)
            print(article_content)
            print("="*50)
            
            # 可选：保存到文件
            if self.config.get("save_to_file", False):
                output_dir = Path(self.config.get("output_dir", "output"))
                output_dir.mkdir(exist_ok=True)
                
                filename = f"{poem_name}_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                file_path = output_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"《{poem_name}》文章\n")
                    f.write(f"生成时间: {data.get('generation_time')}\n")
                    f.write("\n" + article_content)
                
                data.set("output_file", str(file_path))
                logger.info(f"文章已保存到: {file_path}")
            
            logger.info("结果输出完成")
            return StepResult(success=True, data=data, message="结果输出成功")
            
        except Exception as e:
            error_msg = f"结果输出失败: {str(e)}"
            logger.error(error_msg)
            return StepResult(success=False, error=error_msg)


def create_poem_article_workflow(poem_name: str, save_to_file: bool = False, output_dir: str = "output") -> WorkflowConfig:
    """
    创建古诗词文章生成工作流
    
    Args:
        poem_name: 诗词名称
        save_to_file: 是否保存到文件
        output_dir: 输出目录
    
    Returns:
        WorkflowConfig: 工作流配置
    """
    # 定义工作流步骤
    steps = [
        StepConfig(
            name="environment_setup",
            type="EnvironmentSetupStep",
            config={"env_file": ".env"}
        ),
        StepConfig(
            name="client_initialization",
            type="ClientInitializationStep"
        ),
        StepConfig(
            name="request_build",
            type="PoemRequestBuildStep",
            config={
                "model": "glm-4.5",
                "temperature": 0.7
            }
        ),
        StepConfig(
            name="article_generation",
            type="ArticleGenerationStep"
        ),
        StepConfig(
            name="result_output",
            type="ResultOutputStep",
            config={
                "save_to_file": save_to_file,
                "output_dir": output_dir
            }
        )
    ]
    
    # 创建工作流配置
    workflow_config = WorkflowConfig(
        name=f"poem_article_generation_{poem_name}",
        description=f"生成《{poem_name}》的详细文章",
        steps=steps
    )
    
    return workflow_config


def main(poem_name: str = "静夜思", save_to_file: bool = False, output_dir: str = "output"):
    """
    主函数：执行古诗词文章生成工作流
    
    Args:
        poem_name: 诗词名称
        save_to_file: 是否保存到文件
        output_dir: 输出目录
    """
    try:
        logger.info(f"开始执行古诗词文章生成工作流: {poem_name}")
        
        # 创建工作流管理器
        manager = WorkflowManager()
        
        # 注册自定义步骤类型
        manager.register_step_type("EnvironmentSetupStep", EnvironmentSetupStep)
        manager.register_step_type("ClientInitializationStep", ClientInitializationStep)
        manager.register_step_type("PoemRequestBuildStep", PoemRequestBuildStep)
        manager.register_step_type("ArticleGenerationStep", ArticleGenerationStep)
        manager.register_step_type("ResultOutputStep", ResultOutputStep)
        
        # 创建工作流配置
        workflow_config = create_poem_article_workflow(poem_name, save_to_file, output_dir)
        
        # 准备初始数据
        initial_data = WorkflowData()
        initial_data.set("poem_name", poem_name)
        
        # 执行工作流
        result = manager.execute_workflow(workflow_config, initial_data)
        
        # 检查执行结果
        if result.status == "completed":
            logger.info(f"工作流执行成功，耗时: {result.get_execution_time():.2f}秒")
            print(f"\n✅ 《{poem_name}》文章生成工作流执行成功！")
        else:
            logger.error(f"工作流执行失败: {result.error_message}")
            print(f"\n❌ 工作流执行失败: {result.error_message}")
        
        return result
        
    except Exception as e:
        error_msg = f"工作流执行异常: {str(e)}"
        logger.error(error_msg)
        print(f"\n❌ {error_msg}")
        return None


class ConfigIntegrator:
    """
    配置整合模块
    实现配置读取优先级：命令行参数 > 代码指定参数 > 配置文件默认参数
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置整合器
        
        Args:
            config_file_path: 配置文件路径，默认为 workflow_configs/poem_article_config.json
        """
        self.config_file_path = config_file_path or "workflow_configs/poem_article_config.json"
        self.default_config = self._load_default_config()
        self.code_config = {}
        
    def _load_default_config(self) -> Dict[str, Any]:
        """
        从配置文件加载默认配置
        
        Returns:
            默认配置字典
        """
        config_path = Path(self.config_file_path)
        
        # 如果配置文件不存在，创建默认配置文件
        if not config_path.exists():
            default_config = {
                "poem": "静夜思",
                "save": False,
                "output_dir": "output",
                "model": "glm-4-plus",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 300,
                "retry_count": 3,
                "log_level": "INFO",
                "env_file": ".env"
            }
            self._save_default_config(default_config, config_path)
            return default_config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"配置文件读取失败: {e}，使用内置默认配置")
            return {
                "poem": "静夜思",
                "save": False,
                "output_dir": "output",
                "model": "glm-4-plus",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 300,
                "retry_count": 3,
                "log_level": "INFO",
                "env_file": ".env"
            }
    
    def _save_default_config(self, config: Dict[str, Any], config_path: Path) -> None:
        """
        保存默认配置到文件
        
        Args:
            config: 配置字典
            config_path: 配置文件路径
        """
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"已创建默认配置文件: {config_path}")
        except Exception as e:
            logger.error(f"保存默认配置文件失败: {e}")
    
    def set_code_config(self, **kwargs) -> 'ConfigIntegrator':
        """
        设置代码指定的参数
        
        Args:
            **kwargs: 代码指定的参数
            
        Returns:
            配置整合器实例（支持链式调用）
        """
        self.code_config.update(kwargs)
        return self
    
    def integrate_config(self, cmd_args: Optional[argparse.Namespace] = None) -> Dict[str, Any]:
        """
        整合配置，按优先级合并参数
        
        Args:
            cmd_args: 命令行参数
            
        Returns:
            整合后的配置字典
        """
        # 从默认配置开始
        final_config = self.default_config.copy()
        
        # 应用代码指定参数（覆盖默认配置）
        final_config.update(self.code_config)
        
        # 应用命令行参数（最高优先级）
        if cmd_args:
            cmd_dict = vars(cmd_args)
            # 只更新非None的值
            for key, value in cmd_dict.items():
                if value is not None:
                    final_config[key] = value
        
        logger.info(f"配置整合完成，最终配置: {final_config}")
        return final_config
    
    def get_config_summary(self) -> str:
        """
        获取配置来源摘要
        
        Returns:
            配置来源摘要字符串
        """
        summary = []
        summary.append(f"📁 配置文件: {self.config_file_path}")
        summary.append(f"💻 代码配置: {len(self.code_config)} 项")
        summary.append("🔄 优先级: 命令行参数 > 代码指定参数 > 配置文件默认参数")
        return "\n".join(summary)


def create_enhanced_workflow(integrator: ConfigIntegrator, final_config: Dict[str, Any]) -> WorkflowConfig:
    """
    基于整合配置创建增强的工作流
    
    Args:
        integrator: 配置整合器
        final_config: 整合后的配置
        
    Returns:
        工作流配置
    """
    return create_poem_article_workflow(
        poem_name=final_config.get("poem", "静夜思"),
        save_to_file=final_config.get("save", False),
        output_dir=final_config.get("output_dir", "output")
    )


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="古诗词文章生成工作流")
    parser.add_argument("--poem", help="诗词名称")
    parser.add_argument("--save", action="store_true", help="保存到文件")
    parser.add_argument("--output-dir", help="输出目录")
    parser.add_argument("--model", help="AI模型名称")
    parser.add_argument("--temperature", type=float, help="生成温度")
    parser.add_argument("--config-file", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建配置整合器
    integrator = ConfigIntegrator(config_file_path=args.config_file)
    
    # 设置代码指定的参数（可选）
    integrator.set_code_config(
        model="glm-4-plus",  # 代码中指定使用的模型
        timeout=300  # 代码中指定的超时时间
    )
    
    # 整合配置
    final_config = integrator.integrate_config(args)
    
    # 显示配置信息
    print("\n" + "="*50)
    print("🔧 配置整合模块")
    print("="*50)
    print(integrator.get_config_summary())
    print(f"\n📋 最终配置:")
    for key, value in final_config.items():
        print(f"  {key}: {value}")
    print("="*50 + "\n")
    
    # 执行工作流
    main(
        poem_name=final_config.get("poem", "静夜思"),
        save_to_file=final_config.get("save", False),
        output_dir=final_config.get("output_dir", "output")
    )