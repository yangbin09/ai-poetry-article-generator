import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

# 初始化客户端
def init_client():
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")
    return ZhipuAI(api_key=api_key)


# 构建请求消息，包含网页搜索功能
def build_request(poem_name):
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
    请提供李白的详细生平，包括他的一些重要经历，诗人的个性特征，以及他在创作这首诗时的心路历程。还可以加入李白与其他文化名人的交往，以及他如何影响了后代诗歌和文学。
    """

    # 网页搜索工具配置
    tools = [{
        "type": "web_search",
        "web_search": {
            "search_result": True
        }
    }]

    return [
        {
            "role": "system",
            "content": "你是一个古诗词研究助手，能够根据用户提供的诗词名称，按照模板生成结构化文章，内容包括诗词背景、作者简介、诗词解析、文化背景、诗歌影响及诗人背后的故事等，并通过网页搜索获取更多相关信息。"
        },
        {
            "role": "user",
            "content": template
        }
    ], tools


# 发送请求并获取回复内容
def fetch_poem_article(client, poem_name):
    request_messages, tools = build_request(poem_name)

    # 发送请求并启用网页搜索工具
    response = client.chat.completions.create(
        model="glm-4.5",  # 选择合适的模型
        messages=request_messages,
        tools=tools,  # 启用网页搜索
        temperature=0.7  # 设置温度以获取创造性的文章内容
    )

    # 获取生成的文章内容
    return response.choices[0].message.content


# 主函数，负责控制流程
def main(poem_name):
    # 初始化客户端
    client = init_client()

    # 获取并生成文章
    article = fetch_poem_article(client, poem_name)

    # 输出生成的文章
    print(article)


# 示例：生成关于《静夜思》的文章
poem_name = "静夜思"
main(poem_name)