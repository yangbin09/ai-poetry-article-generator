"""古诗词文章生成模块

提供古诗词背景、解析、文化背景等综合文章生成功能。
"""

from typing import List, Dict, Any, Tuple
from .config import config


class PoemArticleGenerator:
    """古诗词文章生成器"""
    
    def __init__(self):
        """初始化文章生成器"""
        self.client = config.get_client()
    
    def _build_request_template(self, poem_name: str) -> str:
        """构建请求模板
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            格式化的请求模板
        """
        return f"""
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
    
    def _build_web_search_tools(self, poem_name: str) -> List[Dict[str, Any]]:
        """构建网页搜索工具配置
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            网页搜索工具配置列表
        """
        return [{
            "type": "web_search",
            "web_search": {
                "enable": "True",
                "search_engine": "search_pro",
                "search_query": f"《{poem_name}》 诗词背景 作者简介 诗歌解析",
                "count": 5,
                "search_domain_filter": "",
                "search_recency_filter": "noLimit",
                "content_size": "medium"
            }
        }]
    
    def _build_messages(self, poem_name: str) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """构建请求消息和工具配置
        
        Args:
            poem_name: 诗词名称
            
        Returns:
            (消息列表, 工具配置列表)
        """
        template = self._build_request_template(poem_name)
        tools = self._build_web_search_tools(poem_name)
        
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
        
        return messages, tools
    
    def generate_article(self, poem_name: str, model: str = "glm-4.5", temperature: float = 0.7) -> str:
        """生成古诗词文章
        
        Args:
            poem_name: 诗词名称
            model: 使用的模型名称
            temperature: 生成温度，控制创造性
            
        Returns:
            生成的文章内容
            
        Raises:
            Exception: 当API调用失败时
        """
        try:
            messages, tools = self._build_messages(poem_name)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"生成文章失败: {str(e)}")
    
    def save_article(self, poem_name: str, article_content: str, output_dir: str = "output") -> str:
        """保存文章到文件
        
        Args:
            poem_name: 诗词名称
            article_content: 文章内容
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        import os
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{poem_name}_文章.txt"
        filepath = os.path.join(output_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        return filepath