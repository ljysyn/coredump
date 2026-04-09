"""
全局配置模块

定义框架的全局配置项
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """
    全局配置

    Attributes:
        ssh_timeout: SSH连接超时时间（秒）
        default_timeout: 默认命令执行超时时间（秒）
        report_max_size: 报告文件最大大小（MB）
        log_level: 日志级别
        log_file: 日志文件路径
    """

    ssh_timeout: int = 10
    default_timeout: int = 30
    report_max_size: int = 100
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/coredump.log"

    def __post_init__(self):
        """验证配置有效性"""
        if self.ssh_timeout < 1:
            raise ValueError("SSH超时时间必须大于0")
        if self.default_timeout < 1:
            raise ValueError("默认超时时间必须大于0")
        if self.report_max_size < 1:
            raise ValueError("报告大小限制必须大于0")


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取全局配置

    Returns:
        全局配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def init_settings(
    ssh_timeout: int = 10,
    default_timeout: int = 30,
    report_max_size: int = 100,
    log_level: str = "INFO",
    log_file: Optional[str] = "logs/coredump.log",
) -> None:
    """
    初始化全局配置

    Args:
        ssh_timeout: SSH连接超时时间（秒）
        default_timeout: 默认命令执行超时时间（秒）
        report_max_size: 报告文件最大大小（MB）
        log_level: 日志级别
        log_file: 日志文件路径
    """
    global _settings
    _settings = Settings(
        ssh_timeout=ssh_timeout,
        default_timeout=default_timeout,
        report_max_size=report_max_size,
        log_level=log_level,
        log_file=log_file,
    )
