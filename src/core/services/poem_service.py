"""古诗词服务实现

提供古诗词文章生成的核心业务逻辑。
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from ...interfaces.base import PoemServiceInterface, AIClientInterface
from ..models.poem import Poem, PoemArticle
from ...infrastructure.clients.zhipu_client import client
from ...infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class PoemService(PoemServiceInterface):
    """古诗词服务实现"""
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None):
        """初始化服务
        
        Args:
            ai_client: AI客户端，如果不提供则使用默认客户端
        """
        self._client = ai_client or client
        logger.info("古诗词服务初始化成功")
    
    def generate_article(self, poem_name: str, **kwargs) -> str:
        """生成古诗词文章
        
        Args:
            poem_name: 诗词名称
            **kwargs: 其他参数
            
        Returns:
            生成的文章内容
        """
        logger.info(f"开始生成古诗词文章: {poem_name}")
        
        try:
            # 构建请求消息
            messages = self._build_article_messages(poem_name)
            
            # 配置工具（网页搜索）
            tools = self._build_search_tools()
            
            # 调用AI生成文章
            article_content = self._client.chat_completion(
                messages=messages,
                tools=tools,
                model=kwargs.get('model', settings.get('models.chat')),
                temperature=kwargs.get('temperature', settings.get('generation.temperature')),
                max_tokens=kwargs.get('max_tokens', settings.get('generation.max_tokens'))
            )
            
            logger.info(f"古诗词文章生成成功: {poem_name}")
            return article_content
            
        except Exception as e:
            logger.error(f"生成古诗词文章失败: {poem_name}, 错误: {e}")
            raise Exception(f"生成古诗词文章失败: {str(e)}")
    
    def generate_poem_article(self, poem_name: str, **kwargs) -> PoemArticle:
        """生成完整的古诗词文章对象
        
        Args:
            poem_name: 诗词名称
            **kwargs: 其他参数
            
        Returns:
            古诗词文章对象
        """
        # 生成文章内容
        article_content = self.generate_article(poem_name, **kwargs)
        
        # 创建诗词对象
        poem = Poem(name=poem_name)
        
        # 创建文章对象
        poem_article = PoemArticle(
            poem=poem,
            article_content=article_content,
            generated_at=datetime.now(),
            metadata=kwargs.get('metadata', {})
        )
        
        return poem_article
    
    def _build_article_messages(self, poem_name: str) -> List[Dict[str, str]]:
        """构建文章生成的消息列表
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            消息列表
        """
        template = f"""
        文章标题：{poem_name}

        诗词背景：
        请为《{poem_name}》提供相关的诗词背景，包括诗人的生平简介、创作背景以及这首诗作的写作时代和历史背景。

        诗词内容：
        请提供《{poem_name}》的完整诗词内容。

        诗词解析：
        请详细解析《{poem_name}》的每一行诗句，分析其情感表达、修辞手法、意象及其含义。

        文化背景：
        请结合这首诗的创作背景，简要介绍相关朝代的文化氛围以及对诗词创作的影响。

        诗歌影响与流传：
        请介绍《{poem_name}》的历史影响，后人如何解读这首诗，并探讨其流传至今的意义。

        诗人背后的故事：
        请提供诗人的详细生平，包括重要经历、个性特征，以及创作这首诗时的心路历程。还可以加入诗人与其他文化名人的交往，以及对后代诗歌和文学的影响。
        """
        
        return [
            {
                "role": "system",
                "content": "你是一位资深的古典文学专家和诗词研究学者，擅长深入分析古诗词的文学价值、历史背景和文化内涵。请根据用户的要求，生成详细、准确、富有学术价值的古诗词分析文章。"
            },
            {
                "role": "user",
                "content": template
            }
        ]
    
    def _build_search_tools(self) -> List[Dict[str, Any]]:
        """构建网页搜索工具配置
        
        Returns:
            工具配置列表
        """
        return [
            {
                "type": "web_search",
                "web_search": {
                    "search_result": True
                }
            }
        ]
    
    def extract_poem_info(self, article_content: str) -> Poem:
        """从文章内容中提取诗词信息
        
        Args:
            article_content: 文章内容
            
        Returns:
            诗词对象
        """
        # 这里可以实现更复杂的信息提取逻辑
        # 目前返回基本的诗词对象
        return Poem(name="未知")
    
    def validate_poem_name(self, poem_name: str) -> bool:
        """验证诗词名称
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            是否有效
        """
        if not poem_name or not poem_name.strip():
            return False
        
        # 可以添加更多验证逻辑
        return True
    
    def get_popular_poems(self) -> List[str]:
        """获取热门诗词列表
        
        Returns:
            热门诗词名称列表
        """
        return [
            "静夜思",
            "春晓",
            "登鹳雀楼",
            "相思",
            "春夜喜雨",
            "黄鹤楼",
            "将进酒",
            "水调歌头·明月几时有",
            "念奴娇·赤壁怀古",
            "虞美人·春花秋月何时了"
        ]