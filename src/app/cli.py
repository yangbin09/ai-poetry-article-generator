"""统一的CLI应用入口

整合所有功能模块，提供命令行接口。"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.interfaces.base import (
    PoemServiceInterface, ImageServiceInterface, 
    PromptServiceInterface, ConfigInterface
)
from src.domain.models import Poem
from src.infrastructure.container import configure_container
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class PoemCLI:
    """古诗词CLI应用"""
    
    def __init__(self):
        """初始化CLI应用"""
        # 配置依赖注入容器
        self.container = configure_container()
        
        # 获取服务实例
        self.poem_service: PoemServiceInterface = self.container.resolve(PoemServiceInterface)
        self.image_service: ImageServiceInterface = self.container.resolve(ImageServiceInterface)
        self.prompt_service: PromptServiceInterface = self.container.resolve(PromptServiceInterface)
        self.config: ConfigInterface = self.container.resolve(ConfigInterface)
        
    def generate_article(self, poem_name: str, output_file: Optional[str] = None) -> None:
        """生成古诗词文章
        
        Args:
            poem_name: 诗词名称
            output_file: 输出文件路径
        """
        try:
            logger.info(f"开始生成古诗词文章: {poem_name}")
            
            # 生成文章
            poem_article = self.poem_service.generate_article(poem_name)
            
            # 输出结果
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(poem_article.article_content)
                print(f"文章已保存到: {output_path}")
            else:
                print("\n=== 生成的古诗词文章 ===")
                print(poem_article.article_content)
                print("\n=== 文章生成完成 ===")
            
            logger.info(f"古诗词文章生成完成: {poem_name}")
            
        except Exception as e:
            logger.error(f"生成古诗词文章失败: {e}")
            print(f"错误: {e}")
            sys.exit(1)
    
    def generate_image(self, poem_name: str, prompt: str = "", output_dir: Optional[str] = None) -> None:
        """生成古诗词图像
        
        Args:
            poem_name: 诗词名称
            prompt: 自定义提示词
            output_dir: 输出目录
        """
        try:
            logger.info(f"开始生成古诗词图像: {poem_name}")
            
            # 生成图像
            generated_image = self.image_service.generate_poem_image(
                poem_name=poem_name,
                custom_prompt=prompt,
                output_dir=output_dir
            )
            
            # 输出结果
            print(f"图像生成成功!")
            print(f"本地路径: {generated_image}")
            
            logger.info(f"古诗词图像生成完成: {poem_name}")
            
        except Exception as e:
            logger.error(f"生成古诗词图像失败: {e}")
            print(f"错误: {e}")
            sys.exit(1)
    
    def optimize_prompt(self, original_prompt: str, style: str = "水墨画", output_file: Optional[str] = None) -> None:
        """优化绘画提示词
        
        Args:
            original_prompt: 原始提示词
            style: 绘画风格
            output_file: 输出文件路径
        """
        try:
            logger.info(f"开始优化提示词，风格: {style}")
            
            # 优化提示词
            optimized_prompt = self.prompt_service.optimize_prompt(
                original_prompt=original_prompt,
                style=style
            )
            
            # 输出结果
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"原始提示词:\n{optimized_prompt.original_prompt}\n\n")
                    f.write(f"优化后提示词:\n{optimized_prompt.optimized_prompt}\n\n")
                    f.write(f"绘画风格: {optimized_prompt.style}\n")
                    f.write(f"优化时间: {optimized_prompt.optimized_at}\n")
                print(f"优化结果已保存到: {output_path}")
            else:
                print("\n=== 提示词优化结果 ===")
                print(f"原始提示词: {optimized_prompt.original_prompt}")
                print(f"绘画风格: {optimized_prompt.style}")
                print(f"\n优化后提示词:\n{optimized_prompt.optimized_prompt}")
                print("\n=== 优化完成 ===")
            
            logger.info(f"提示词优化完成")
            
        except Exception as e:
            logger.error(f"优化提示词失败: {e}")
            print(f"错误: {e}")
            sys.exit(1)
    
    def list_popular_poems(self) -> None:
        """列出热门诗词"""
        try:
            poems = self.poem_service.get_popular_poems()
            print("\n=== 热门古诗词 ===")
            for i, poem in enumerate(poems, 1):
                print(f"{i:2d}. {poem}")
            print("\n=== 列表完成 ===")
            
        except Exception as e:
            logger.error(f"获取热门诗词失败: {e}")
            print(f"错误: {e}")
    
    def list_styles(self) -> None:
        """列出支持的绘画风格"""
        try:
            styles = self.prompt_service.get_supported_styles()
            print("\n=== 支持的绘画风格 ===")
            for i, style in enumerate(styles, 1):
                print(f"{i:2d}. {style}")
            print("\n=== 列表完成 ===")
            
        except Exception as e:
            logger.error(f"获取绘画风格失败: {e}")
            print(f"错误: {e}")
    
    def show_config(self) -> None:
        """显示当前配置"""
        try:
            print("\n=== 当前配置 ===")
            print(f"API密钥: {'已配置' if self.config.get_api_key() else '未配置'}")
            print(f"聊天模型: {self.config.get('models.chat', '未配置')}")
            print(f"图像模型: {self.config.get('models.image', '未配置')}")
            print(f"优化模型: {self.config.get('models.prompt_optimization', '未配置')}")
            print(f"图像输出目录: {self.config.get('image.output_dir', '未配置')}")
            print(f"日志级别: {self.config.get('logging.level', '未配置')}")
            print("\n=== 配置完成 ===")
            
        except Exception as e:
            logger.error(f"显示配置失败: {e}")
            print(f"错误: {e}")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="古诗词AI助手 - 生成文章、图像和优化提示词",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s article "静夜思" --output article.txt
  %(prog)s image "春晓" --prompt "春天的早晨" --output-dir ./images
  %(prog)s optimize "山水画" --style 水墨画 --output optimized.txt
  %(prog)s list-poems
  %(prog)s list-styles
  %(prog)s config
        """
    )
    
    # 添加全局参数
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 文章生成命令
    article_parser = subparsers.add_parser('article', help='生成古诗词文章')
    article_parser.add_argument('poem_name', help='诗词名称')
    article_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 图像生成命令
    image_parser = subparsers.add_parser('image', help='生成古诗词图像')
    image_parser.add_argument('poem_name', help='诗词名称')
    image_parser.add_argument('--prompt', '-p', default='', help='自定义提示词')
    image_parser.add_argument('--output-dir', '-d', help='输出目录')
    
    # 提示词优化命令
    optimize_parser = subparsers.add_parser('optimize', help='优化绘画提示词')
    optimize_parser.add_argument('prompt', help='原始提示词')
    optimize_parser.add_argument('--style', '-s', default='水墨画', help='绘画风格')
    optimize_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 列表命令
    subparsers.add_parser('list-poems', help='列出热门诗词')
    subparsers.add_parser('list-styles', help='列出支持的绘画风格')
    subparsers.add_parser('config', help='显示当前配置')
    
    return parser


def main() -> None:
    """主函数"""
    # 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志
    log_level = 'DEBUG' if args.verbose else 'WARNING' if args.quiet else 'INFO'
    # 日志配置由容器管理
    
    # 检查是否提供了命令
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建CLI应用
    cli = PoemCLI()
    
    try:
        # 执行对应的命令
        if args.command == 'article':
            cli.generate_article(args.poem_name, args.output)
        elif args.command == 'image':
            cli.generate_image(args.poem_name, args.prompt, args.output_dir)
        elif args.command == 'optimize':
            cli.optimize_prompt(args.prompt, args.style, args.output)
        elif args.command == 'list-poems':
            cli.list_popular_poems()
        elif args.command == 'list-styles':
            cli.list_styles()
        elif args.command == 'config':
            cli.show_config()
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()