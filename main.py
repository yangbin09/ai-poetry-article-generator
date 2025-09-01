#!/usr/bin/env python3
"""古诗词AI项目主入口

提供统一的项目启动入口。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.cli import main

if __name__ == "__main__":
    main()