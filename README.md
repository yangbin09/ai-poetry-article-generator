# AI古诗词项目

🎨 基于智谱AI的古诗词文章生成和图像创作工具包

## 📖 项目简介

本项目是一个集成了智谱AI能力的古诗词处理工具包，提供以下核心功能：

- **📝 古诗词文章生成**：根据诗词名称生成包含背景、解析、文化内涵等的综合性文章
- **🎨 古诗词图像创作**：基于诗词内容生成相应的艺术图像
- **✨ 绘画提示词优化**：优化图像生成的提示词，支持多种艺术风格

## 🚀 功能特性

### 文章生成
- 自动搜索诗词相关信息
- 生成结构化文章内容
- 包含诗词背景、作者简介、详细解析等
- 支持文章保存到本地文件

### 图像生成
- 支持多种艺术风格（水墨画、工笔画、油画等）
- 基于诗词内容智能生成提示词
- 自动下载并保存生成的图像
- 支持批量处理

### 提示词优化
- 智能优化绘画提示词
- 支持多种艺术风格建议
- 批量优化功能

## 📦 安装说明

### 环境要求
- Python 3.8+
- 智谱AI API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/ai-poetry.git
cd ai-poetry
```

2. **创建虚拟环境**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt

# 或者安装开发版本（包含测试工具）
pip install -e ".[dev]"
```

4. **配置环境变量**

复制 `.env.example` 文件为 `.env`，并填入您的智谱AI API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
ZHIPU_API_KEY=your_zhipu_api_key_here
```

## 🔧 使用方法

### 基础用法

```python
from src import PoemArticleGenerator, PoemImageGenerator, PromptOptimizer

# 1. 生成古诗词文章
article_generator = PoemArticleGenerator()
article = article_generator.generate_article("静夜思")
print(article)

# 保存文章到文件
file_path = article_generator.save_article("静夜思", article)
print(f"文章已保存到: {file_path}")

# 2. 生成古诗词图像
image_generator = PoemImageGenerator()
result = image_generator.generate_and_save_image(
    poem_name="静夜思",
    poem_content="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
    style="水墨画"
)
print(f"图像URL: {result['url']}")
print(f"本地路径: {result['local_path']}")

# 3. 优化绘画提示词
optimizer = PromptOptimizer()
optimized_prompt = optimizer.optimize_poem_prompt(
    "静夜思",
    "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
    style="水墨画"
)
print(f"优化后的提示词: {optimized_prompt}")
```

### 高级用法

```python
# 获取多种风格建议
optimizer = PromptOptimizer()
style_suggestions = optimizer.get_style_suggestions(
    "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
)

for style, prompt in style_suggestions.items():
    print(f"{style}: {prompt}")

# 批量优化提示词
prompts = [
    "根据《静夜思》创作图像",
    "描绘月夜思乡的场景",
    "表现古代文人的情怀"
]

batch_results = optimizer.batch_optimize(prompts, style="水墨画")
for original, optimized in batch_results.items():
    print(f"原始: {original}")
    print(f"优化: {optimized}\n")
```

## 📁 项目结构

```
ai-poetry/
├── src/                    # 源代码目录
│   ├── __init__.py        # 包初始化文件
│   ├── config.py          # 配置管理模块
│   ├── poem_article.py    # 古诗词文章生成模块
│   ├── poem_image.py      # 古诗词图像生成模块
│   └── prompt_optimizer.py # 提示词优化模块
├── tests/                  # 测试文件目录
├── docs/                   # 文档目录
├── examples/               # 示例代码目录
├── output/                 # 输出文件目录
│   ├── articles/          # 生成的文章
│   └── images/            # 生成的图像
├── .env                   # 环境变量配置（需要创建）
├── .env.example           # 环境变量示例
├── .gitignore            # Git忽略文件
├── requirements.txt       # 项目依赖
├── pyproject.toml        # 项目配置文件
└── README.md             # 项目说明文档
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_poem_article.py
```

## 🛠️ 开发工具

项目使用以下开发工具来保证代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查
- **pytest**: 单元测试

运行代码质量检查：

```bash
# 格式化代码
black src tests

# 排序导入
isort src tests

# 代码风格检查
flake8 src tests

# 类型检查
mypy src
```

## 📝 API文档

### PoemArticleGenerator

生成古诗词相关的综合性文章。

#### 方法
- `generate_article(poem_name, model="glm-4.5", temperature=0.7)`: 生成文章
- `save_article(poem_name, article_content, output_dir="output")`: 保存文章

### PoemImageGenerator

生成基于古诗词的艺术图像。

#### 方法
- `generate_image_from_poem(poem_name, poem_content, style="水墨画")`: 根据诗词生成图像
- `download_image(image_url, save_path, poem_name)`: 下载图像
- `generate_and_save_image(poem_name, poem_content, style, output_dir)`: 生成并保存图像

### PromptOptimizer

优化绘画提示词以获得更好的图像生成效果。

#### 方法
- `optimize_painting_prompt(original_prompt, style="水墨画")`: 优化提示词
- `optimize_poem_prompt(poem_name, poem_content, style="水墨画")`: 根据诗词优化提示词
- `get_style_suggestions(poem_content)`: 获取多种风格建议
- `batch_optimize(prompts, style="水墨画")`: 批量优化

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [智谱AI](https://www.zhipuai.cn/) 提供强大的AI能力支持
- 所有为项目做出贡献的开发者

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: contact@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-poetry/issues)
- 📖 文档: [项目文档](https://ai-poetry.readthedocs.io/)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！