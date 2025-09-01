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
response = client.images.generations(
    model="cogView-4-250304",  # 请填写您要调用的模型名称
    prompt="静谧夜晚，窗前床榻，一缕清冷月光透过窗棂洒在地面",
)
print(response.data[0].url)