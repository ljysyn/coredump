"""
日志配置模块

提供统一的日志配置，支持不同级别和格式的日志输出
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "coredump",
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    配置并返回日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则不输出到文件
        format_string: 自定义日志格式字符串
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 默认日志格式
    if format_string is None:
        format_string = "[%(asctime)s] [%(levelname)s] %(message)s"
    
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 全局日志记录器
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """
    获取全局日志记录器
    
    Returns:
        全局日志记录器实例
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def init_logging(level: str = "INFO", log_file: Optional[str] = "logs/coredump.log") -> None:
    """
    初始化全局日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
    """
    global _logger
    _logger = setup_logger(level=level, log_file=log_file)