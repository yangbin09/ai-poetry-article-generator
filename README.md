# AI古诗词项目

🎨 基于智谱AI的古诗词文章生成和图像创作工具包

## 📖 项目简介

本项目采用现代化的分层架构设计，集成智谱AI能力的古诗词处理工具包，提供以下核心功能：

- **📝 古诗词文章生成**：根据诗词名称生成包含背景、解析、文化内涵等的综合性文章
- **🎨 古诗词图像创作**：基于诗词内容生成相应的艺术图像
- **✨ 绘画提示词优化**：优化图像生成的提示词，支持多种艺术风格

## 🏗️ 项目架构

项目采用领域驱动设计（DDD）和分层架构：

```
src/
├── app/                    # 应用层 - CLI入口
├── core/                   # 核心业务层
│   ├── models/            # 领域模型
│   └── services/          # 业务服务
├── infrastructure/         # 基础设施层
│   ├── clients/           # 外部API客户端
│   ├── config/            # 配置管理
│   ├── logging/           # 日志管理
│   └── container.py       # 依赖注入容器
├── interfaces/            # 接口层
└── workflow/              # 工作流引擎
```

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
git clone <repository-url>
cd 05AI古诗词
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
pip install -r requirements-dev.txt
```

4. **配置环境变量**

创建 `.env` 文件，并填入您的智谱AI API密钥：

```env
ZHIPU_API_KEY=your_zhipu_api_key_here
```

## 🔧 使用方法

### 命令行接口

项目提供统一的CLI入口，支持所有核心功能：

```bash
# 查看帮助
python main.py --help

# 生成古诗词文章
python main.py article "静夜思" --output "静夜思.txt"

# 生成古诗词图像
python main.py image "静夜思" --prompt "水墨画风格的静夜思" --output-dir ./images

# 获取热门诗词列表
python main.py list-poems

# 获取支持的绘画风格
python main.py list-styles

# 查看当前配置
python main.py config
```

### 编程接口

```python
from src.infrastructure.container import configure_container
from src.interfaces.base import PoemServiceInterface, ImageServiceInterface

# 配置依赖注入容器
container = configure_container()

# 获取服务实例
poem_service = container.resolve(PoemServiceInterface)
image_service = container.resolve(ImageServiceInterface)

# 生成古诗词文章
article = poem_service.generate_article("静夜思")
print(article.content)

# 生成古诗词图像
image_request = image_service.create_image_request(
    poem_name="静夜思",
    poem_content="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
    style="水墨画"
)
result = image_service.generate_image(image_request)
print(f"图像已保存到: {result.local_path}")
```

## 📁 项目结构

```
05AI古诗词/
├── src/                    # 源代码目录
│   ├── app/               # 应用层
│   │   └── cli.py         # 命令行接口
│   ├── core/              # 核心业务层
│   │   ├── models/        # 领域模型
│   │   └── services/      # 业务服务
│   ├── infrastructure/    # 基础设施层
│   │   ├── clients/       # 外部API客户端
│   │   ├── config/        # 配置管理
│   │   ├── logging/       # 日志管理
│   │   └── container.py   # 依赖注入容器
│   ├── interfaces/        # 接口层
│   └── workflow/          # 工作流引擎
├── tests/                 # 测试文件目录
├── examples/              # 示例代码目录
├── output/                # 输出文件目录
│   └── images/           # 生成的图像
├── .env                   # 环境变量配置（需要创建）
├── .gitignore            # Git忽略文件
├── requirements.txt       # 项目依赖
├── requirements-dev.txt   # 开发依赖
├── pyproject.toml        # 项目配置文件
├── pytest.ini           # 测试配置
├── main.py               # 主入口文件
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

## 📝 核心服务API

### PoemService

古诗词文章生成服务。

#### 方法
- `generate_article(poem_name: str) -> PoemArticle`: 生成文章
- `save_article(article: PoemArticle, output_path: str) -> str`: 保存文章

### ImageService

古诗词图像生成服务。

#### 方法
- `create_image_request(poem_name, poem_content, style) -> ImageGenerationRequest`: 创建图像请求
- `generate_image(request: ImageGenerationRequest) -> GeneratedImage`: 生成图像
- `cleanup_old_images(days: int = 30) -> int`: 清理旧图像

### PromptService

提示词优化服务。

#### 方法
- `optimize_prompt(prompt: str, style: str) -> PromptOptimization`: 优化提示词
- `get_style_suggestions() -> List[str]`: 获取风格建议
- `get_common_focus_areas() -> List[str]`: 获取常见关注领域

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [智谱AI](https://www.zhipuai.cn/) 提供强大的AI能力支持
- 所有为项目做出贡献的开发者

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！