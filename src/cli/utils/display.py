"""
显示格式化工具

提供CLI输出的格式化功能
"""

from typing import Any, Dict, List, Optional


class DisplayFormatter:
    """显示格式化工具类"""

    @staticmethod
    def format_table(
        headers: List[str],
        rows: List[List[Any]],
        column_widths: Optional[List[int]] = None,
    ) -> str:
        """格式化表格

        Args:
            headers: 表头列表
            rows: 数据行列表
            column_widths: 列宽度列表（可选）

        Returns:
            格式化后的表格字符串
        """
        if not column_widths:
            column_widths = [
                max(len(str(row[i])) if i < len(row) else 0 for row in [headers] + rows)
                for i in range(len(headers))
            ]

        lines = []

        header_line = "  ".join(
            str(headers[i]).ljust(column_widths[i]) for i in range(len(headers))
        )
        lines.append("=" * len(header_line))
        lines.append(header_line)
        lines.append("=" * len(header_line))

        for row in rows:
            row_line = "  ".join(
                str(row[i]).ljust(column_widths[i]) if i < len(row) else ""
                for i in range(len(headers))
            )
            lines.append(row_line)

        lines.append("=" * len(header_line))

        return "\n".join(lines)

    @staticmethod
    def format_device_table(devices: List[Dict]) -> str:
        """格式化设备表格

        Args:
            devices: 设备列表

        Returns:
            格式化后的表格字符串
        """
        if not devices:
            return "无待测设备配置"

        headers = ["ID", "名称", "IP地址", "端口", "用户名"]
        rows = [
            [
                device["id"],
                device["name"],
                device["ip"],
                device["port"],
                device["username"],
            ]
            for device in devices
        ]
        column_widths = [15, 20, 18, 8, 15]

        table = DisplayFormatter.format_table(headers, rows, column_widths)
        return f"{table}\n总计: {len(devices)} 台设备"

    @staticmethod
    def format_testcase_table(testcases: List[Dict]) -> str:
        """格式化测试用例表格

        Args:
            testcases: 测试用例列表

        Returns:
            格式化后的表格字符串
        """
        if not testcases:
            return "无测试用例配置"

        headers = ["ID", "名称", "场景数", "超时(秒)", "失败行为"]
        rows = [
            [tc["id"], tc["name"], tc["scenarios"], tc["timeout"], tc["on_failure"]]
            for tc in testcases
        ]
        column_widths = [15, 25, 10, 12, 10]

        table = DisplayFormatter.format_table(headers, rows, column_widths)
        return f"{table}\n总计: {len(testcases)} 个测试用例"

    @staticmethod
    def format_task_table(tasks: List[Dict]) -> str:
        """格式化任务表格

        Args:
            tasks: 任务列表

        Returns:
            格式化后的表格字符串
        """
        if not tasks:
            return "无测试任务配置"

        headers = ["ID", "名称", "设备数", "用例数", "报告格式", "状态"]
        rows = [
            [
                task["id"],
                task["name"],
                task["devices"],
                task["testcases"],
                task["report_format"],
                task["status"],
            ]
            for task in tasks
        ]
        column_widths = [15, 25, 10, 10, 12, 10]

        table = DisplayFormatter.format_table(headers, rows, column_widths)
        return f"{table}\n总计: {len(tasks)} 个测试任务"

    @staticmethod
    def format_result_summary(result: Dict) -> str:
        """格式化执行结果摘要

        Args:
            result: 执行结果字典

        Returns:
            格式化后的结果摘要
        """
        lines = []
        lines.append("=" * 80)
        lines.append("任务执行结果")
        lines.append("=" * 80)
        lines.append(f"任务ID: {result['task_id']}")
        lines.append(f"任务名称: {result['task_name']}")
        lines.append(f"开始时间: {result['start_time']}")
        lines.append(f"结束时间: {result['end_time']}")
        lines.append(f"执行耗时: {result['duration']:.2f}秒")
        lines.append("")
        lines.append("设备测试结果:")

        passed_count = 0
        failed_count = 0

        for device_id, device_result in result["devices"].items():
            if device_result["status"] == "pass":
                status = "✓ 通过"
                passed_count += 1
            else:
                status = "✗ 失败"
                failed_count += 1

            lines.append(f"  {device_id}: {status}")

            if "report_path" in device_result:
                lines.append(f"    报告: {device_result['report_path']}")

            if "error" in device_result:
                lines.append(f"    错误: {device_result['error']}")

        lines.append("")
        lines.append(f"通过设备: {passed_count}")
        lines.append(f"失败设备: {failed_count}")
        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def truncate_string(text: str, max_length: int = 50) -> str:
        """截断字符串

        Args:
            text: 原始字符串
            max_length: 最大长度

        Returns:
            截断后的字符串
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间

        Args:
            seconds: 秒数

        Returns:
            格式化后的时间字符串
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
            return f"{hours}小时{minutes}分钟"
