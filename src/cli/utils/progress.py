"""
进度显示工具

提供带有日志级别的进度显示功能
"""

from datetime import datetime
from typing import Optional


class ProgressDisplay:
    """进度显示工具类"""

    def __init__(self):
        """初始化进度显示"""
        self.start_time = datetime.now()

    def _format_message(self, level: str, message: str) -> str:
        """格式化消息
        
        Args:
            level: 日志级别
            message: 消息内容
        
        Returns:
            格式化后的消息
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 根据日志级别对齐：INFO和ERROR需要补充空格
        if level == "INFO":
            level_str = "[INFO]   "
        elif level == "WARNING":
            level_str = "[WARNING]"
        elif level == "ERROR":
            level_str = "[ERROR]  "
        else:
            level_str = f"[{level}]"
        
        return f"[{timestamp}] {level_str} {message}"

    def info(self, message: str) -> None:
        """显示INFO级别消息

        Args:
            message: 消息内容
        """
        print(self._format_message("INFO", message))

    def warning(self, message: str) -> None:
        """显示WARNING级别消息

        Args:
            message: 消息内容
        """
        print(self._format_message("WARNING", message))

    def error(self, message: str) -> None:
        """显示ERROR级别消息

        Args:
            message: 消息内容
        """
        print(self._format_message("ERROR", message))

    def success(self, message: str) -> None:
        """显示成功消息

        Args:
            message: 消息内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [INFO]    ✓ {message}")

    def failure(self, message: str) -> None:
        """显示失败消息

        Args:
            message: 消息内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [ERROR]   ✗ {message}")

    def command_result(self, command: str, passed: bool) -> None:
        """显示命令执行结果

        Args:
            command: 执行的命令
            passed: 是否通过
        """
        result = "通过" if passed else "失败"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [INFO]    执行命令[{result}]: {command}")

    def phase_start(self, phase: str) -> None:
        """显示阶段开始

        Args:
            phase: 阶段名称
        """
        self.info(f"阶段: {phase}")

    def scenario_start(self, scenario: str) -> None:
        """显示场景开始

        Args:
            scenario: 场景名称
        """
        self.info(f"场景: {scenario}")

    def device_connect(self, device_id: str, device_ip: str) -> None:
        """显示设备连接

        Args:
            device_id: 设备ID
            device_ip: 设备IP
        """
        self.info(f"正在连接设备: {device_id} ({device_ip})")

    def testcase_start(self, testcase_id: str, testcase_name: str) -> None:
        """显示测试用例开始

        Args:
            testcase_id: 测试用例ID
            testcase_name: 测试用例名称
        """
        self.info(f"执行测试用例: {testcase_id} - {testcase_name}")

    def elapsed_time(self) -> float:
        """获取已用时间

        Returns:
            已用时间（秒）
        """
        return (datetime.now() - self.start_time).total_seconds()
