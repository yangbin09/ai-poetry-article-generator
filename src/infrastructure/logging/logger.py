"""日志配置模块

提供统一的日志管理和配置。
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import settings


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        max_bytes: 日志文件最大大小
        backup_count: 备份文件数量
    """
    # 获取配置
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_format = settings.get(
        'logging.format',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    date_format = settings.get('logging.date_format', '%Y-%m-%d %H:%M:%S')
    
    # 创建格式化器
    formatter = logging.Formatter(log_format, date_format)
    
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 添加文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    logging.info(f"日志系统初始化完成，级别: {level}")


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return logging.getLogger(name)


class LoggerMixin:
    """日志器混入类
    
    为类提供便捷的日志记录功能。
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志器"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


class ContextFilter(logging.Filter):
    """上下文过滤器
    
    为日志记录添加上下文信息。
    """
    
    def __init__(self, context: dict):
        """初始化过滤器
        
        Args:
            context: 上下文信息
        """
        super().__init__()
        self.context = context
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            是否通过过滤
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def add_context_to_logger(logger: logging.Logger, **context) -> None:
    """为日志器添加上下文信息
    
    Args:
        logger: 日志器
        **context: 上下文信息
    """
    context_filter = ContextFilter(context)
    logger.addFilter(context_filter)


def remove_context_from_logger(logger: logging.Logger) -> None:
    """移除日志器的上下文过滤器
    
    Args:
        logger: 日志器
    """
    for filter_obj in logger.filters[:]:
        if isinstance(filter_obj, ContextFilter):
            logger.removeFilter(filter_obj)


# 默认日志配置
if not logging.getLogger().handlers:
    setup_logging(
        level=settings.get('logging.level', 'INFO'),
        log_file=settings.get('logging.file')
    )