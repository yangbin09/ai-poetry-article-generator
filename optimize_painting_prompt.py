import os
from dotenv import load_dotenv
from zai import ZhipuAiClient

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
api_key = os.getenv('ZHIPU_API_KEY')
if not api_key:
    raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY 环境变量")

# 初始化客户端
client = ZhipuAiClient(api_key=api_key)

# 创建聊天完成请求
response = client.chat.completions.create(
    model="GLM-4.5-Flash",
    messages=[
        {
            "role": "system",
            "content": "你是一个提示词优化助手。根据用户输入内容，优化绘画参数，主要是水墨画"
        },
        {
            "role": "user",
            "content": "你好，请优化以下提示词 《静夜思》的完整诗词内容如下：床前明月光，疑是地上霜。举头望明月，低头思故乡。根据静夜思创建一张图片。"
        }
    ],
    temperature=0.6
)

# 获取回复
print(response.choices[0].message.content)