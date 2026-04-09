"""
路径管理模块

管理项目的各种路径配置
"""
from pathlib import Path
from typing import Optional


class PathManager:
    """
    路径管理器
    
    管理项目各种目录路径
    """
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        devices_dir: str = "configs/devices",
        testcases_dir: str = "configs/testcases",
        tasks_dir: str = "configs/tasks",
        reports_dir: str = "reports",
        logs_dir: str = "logs",
    ):
        """
        初始化路径管理器
        
        Args:
            project_root: 项目根目录，None表示当前工作目录
            devices_dir: 设备配置文件目录
            testcases_dir: 测试用例配置文件目录
            tasks_dir: 任务配置文件目录
            reports_dir: 测试报告输出目录
            logs_dir: 日志文件目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        self.devices_dir = self.project_root / devices_dir
        self.testcases_dir = self.project_root / testcases_dir
        self.tasks_dir = self.project_root / tasks_dir
        self.reports_dir = self.project_root / reports_dir
        self.logs_dir = self.project_root / logs_dir
    
    def ensure_directories(self) -> None:
        """确保所有必需目录存在"""
        self.devices_dir.mkdir(parents=True, exist_ok=True)
        self.testcases_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_devices_dir(self) -> Path:
        """获取设备配置目录"""
        return self.devices_dir
    
    def get_testcases_dir(self) -> Path:
        """获取测试用例配置目录"""
        return self.testcases_dir
    
    def get_tasks_dir(self) -> Path:
        """获取任务配置目录"""
        return self.tasks_dir
    
    def get_reports_dir(self) -> Path:
        """获取测试报告目录"""
        return self.reports_dir
    
    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        return self.logs_dir


# 全局路径管理器实例
_path_manager: Optional[PathManager] = None


def get_path_manager() -> PathManager:
    """
    获取全局路径管理器
    
    Returns:
        路径管理器实例
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager


def init_path_manager(project_root: Optional[str] = None, **kwargs) -> None:
    """
    初始化全局路径管理器
    
    Args:
        project_root: 项目根目录
        **kwargs: 其他路径配置
    """
    global _path_manager
    _path_manager = PathManager(project_root=project_root, **kwargs)