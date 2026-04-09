"""
时间工具模块

提供时间计算和格式化功能
"""

from datetime import datetime
from typing import Optional


class TimeUtils:
    """时间工具类"""

    @staticmethod
    def calculate_duration(start_time: float, end_time: float) -> float:
        """
        计算执行时间

        Args:
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            执行时间（秒）
        """
        return round(end_time - start_time, 2)

    @staticmethod
    def format_timestamp(timestamp: Optional[float] = None) -> str:
        """
        格式化时间戳为ISO格式字符串

        Args:
            timestamp: 时间戳（秒），None表示当前时间

        Returns:
            ISO格式的时间字符串
        """
        if timestamp is None:
            dt = datetime.now()
        else:
            dt = datetime.fromtimestamp(timestamp)

        return dt.isoformat()

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        格式化执行时间为易读格式

        Args:
            seconds: 执行时间（秒）

        Returns:
            格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.2f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分"

    @staticmethod
    def get_current_timestamp() -> float:
        """
        获取当前时间戳

        Returns:
            当前时间戳（秒）
        """
        return time.time()

    @staticmethod
    def get_filename_timestamp() -> str:
        """
        获取适合文件名的时间戳

        Returns:
            格式: YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")


import time
