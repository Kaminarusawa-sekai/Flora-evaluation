"""
日志系统 - 结构化日志输出
"""
import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # 添加颜色
        record.levelname = f"{log_color}{record.levelname}{reset}"
        record.name = f"\033[34m{record.name}{reset}"  # Blue

        return super().format(record)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 设置日志级别
    log_level = level or 'INFO'
    logger.setLevel(getattr(logging, log_level.upper()))

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 设置格式
    formatter = ColoredFormatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


class LoggerContext:
    """日志上下文管理器，用于追踪"""

    def __init__(self, logger: logging.Logger, trace_id: str):
        self.logger = logger
        self.trace_id = trace_id
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"[{self.trace_id}] Started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(f"[{self.trace_id}] Failed after {duration:.2f}s: {exc_val}")
        else:
            self.logger.info(f"[{self.trace_id}] Completed in {duration:.2f}s")
        return False
