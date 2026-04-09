"""
Coredump自动化测试框架

基于SSH的设备测试框架
"""
from .config import get_settings, init_settings
from .core import DeviceManager, ReportGenerator, TaskRunner, TestExecutor
from .models import Device, ExecutionPhase, Report, ReportStep, Task, TestCase, TestScenario
from .parsers import ConfigValidator, YAMLParser
from .utils import FileUtils, SSHClient, TimeUtils, get_logger, init_logging

__all__ = [
    "Device",
    "TestCase",
    "TestScenario",
    "ExecutionPhase",
    "Task",
    "Report",
    "ReportStep",
    "DeviceManager",
    "TestExecutor",
    "TaskRunner",
    "ReportGenerator",
    "YAMLParser",
    "ConfigValidator",
    "SSHClient",
    "FileUtils",
    "TimeUtils",
    "get_logger",
    "init_logging",
    "get_settings",
    "init_settings",
]

__version__ = "0.1.0"