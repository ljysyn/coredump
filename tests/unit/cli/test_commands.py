"""
CLI命令单元测试

测试CLI命令的基本功能
"""
import pytest
from click.testing import CliRunner

from src.cli.main import cli
from src.cli.utils.progress import ProgressDisplay
from src.cli.utils.display import DisplayFormatter


class TestCLICommands:
    """CLI命令测试"""

    def test_cli_group_exists(self):
        """测试CLI命令组存在"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_cli_version(self):
        """测试版本命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "coredump" in result.output


class TestProgressDisplay:
    """进度显示测试"""

    def test_progress_info(self, capsys):
        """测试INFO级别消息"""
        progress = ProgressDisplay()
        progress.info("测试消息")
        
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "测试消息" in captured.out

    def test_progress_warning(self, capsys):
        """测试WARNING级别消息"""
        progress = ProgressDisplay()
        progress.warning("警告消息")
        
        captured = capsys.readouterr()
        assert "[WARNING]" in captured.out
        assert "警告消息" in captured.out

    def test_progress_error(self, capsys):
        """测试ERROR级别消息"""
        progress = ProgressDisplay()
        progress.error("错误消息")
        
        captured = capsys.readouterr()
        assert "[ERROR]" in captured.out
        assert "错误消息" in captured.out

    def test_progress_success(self, capsys):
        """测试成功消息"""
        progress = ProgressDisplay()
        progress.success("操作成功")
        
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "操作成功" in captured.out

    def test_progress_failure(self, capsys):
        """测试失败消息"""
        progress = ProgressDisplay()
        progress.failure("操作失败")
        
        captured = capsys.readouterr()
        assert "✗" in captured.out
        assert "操作失败" in captured.out

    def test_command_result_pass(self, capsys):
        """测试命令通过结果"""
        progress = ProgressDisplay()
        progress.command_result("ls -la", True)
        
        captured = capsys.readouterr()
        assert "ls -la" in captured.out
        assert "通过" in captured.out

    def test_command_result_fail(self, capsys):
        """测试命令失败结果"""
        progress = ProgressDisplay()
        progress.command_result("false", False)
        
        captured = capsys.readouterr()
        assert "false" in captured.out
        assert "失败" in captured.out

    def test_elapsed_time(self):
        """测试已用时间"""
        import time
        
        progress = ProgressDisplay()
        time.sleep(0.1)
        
        elapsed = progress.elapsed_time()
        assert elapsed >= 0.1


class TestDisplayFormatter:
    """显示格式化测试"""

    def test_format_table(self):
        """测试表格格式化"""
        headers = ["ID", "名称", "状态"]
        rows = [
            ["001", "测试1", "通过"],
            ["002", "测试2", "失败"],
        ]
        
        table = DisplayFormatter.format_table(headers, rows)
        
        assert "ID" in table
        assert "名称" in table
        assert "状态" in table
        assert "001" in table
        assert "测试1" in table

    def test_format_device_table(self):
        """测试设备表格格式化"""
        devices = [
            {
                "id": "device001",
                "name": "测试设备",
                "ip": "192.168.1.100",
                "port": 22,
                "username": "root"
            }
        ]
        
        table = DisplayFormatter.format_device_table(devices)
        
        assert "device001" in table
        assert "测试设备" in table
        assert "192.168.1.100" in table

    def test_format_device_table_empty(self):
        """测试空设备表格"""
        table = DisplayFormatter.format_device_table([])
        assert "无待测设备配置" in table

    def test_format_testcase_table(self):
        """测试测试用例表格格式化"""
        testcases = [
            {
                "id": "tc001",
                "name": "测试用例",
                "scenarios": 2,
                "timeout": 30,
                "on_failure": "stop"
            }
        ]
        
        table = DisplayFormatter.format_testcase_table(testcases)
        
        assert "tc001" in table
        assert "测试用例" in table

    def test_format_testcase_table_empty(self):
        """测试空测试用例表格"""
        table = DisplayFormatter.format_testcase_table([])
        assert "无测试用例配置" in table

    def test_format_task_table(self):
        """测试任务表格格式化"""
        tasks = [
            {
                "id": "task001",
                "name": "测试任务",
                "devices": 2,
                "testcases": 3,
                "report_format": "json",
                "status": "pending"
            }
        ]
        
        table = DisplayFormatter.format_task_table(tasks)
        
        assert "task001" in table
        assert "测试任务" in table

    def test_format_task_table_empty(self):
        """测试空任务表格"""
        table = DisplayFormatter.format_task_table([])
        assert "无测试任务配置" in table

    def test_format_result_summary(self):
        """测试结果摘要格式化"""
        result = {
            "task_id": "task001",
            "task_name": "测试任务",
            "start_time": "2026-04-08T10:00:00",
            "end_time": "2026-04-08T10:00:05",
            "duration": 5.0,
            "devices": {
                "device001": {
                    "status": "pass",
                    "report_path": "/reports/test.json"
                }
            }
        }
        
        summary = DisplayFormatter.format_result_summary(result)
        
        assert "任务执行结果" in summary
        assert "task001" in summary
        assert "device001" in summary

    def test_truncate_string(self):
        """测试字符串截断"""
        text = "这是一个很长的字符串用于测试截断功能"
        truncated = DisplayFormatter.truncate_string(text, max_length=20)
        
        assert len(truncated) <= 20
        assert "..." in truncated

    def test_truncate_string_short(self):
        """测试短字符串不截断"""
        text = "短字符串"
        truncated = DisplayFormatter.truncate_string(text, max_length=20)
        
        assert truncated == text

    def test_format_duration_seconds(self):
        """测试持续时间格式化（秒）"""
        duration = DisplayFormatter.format_duration(5.5)
        assert "5.50秒" == duration

    def test_format_duration_minutes(self):
        """测试持续时间格式化（分钟）"""
        duration = DisplayFormatter.format_duration(125)
        assert "2分5秒" == duration

    def test_format_duration_hours(self):
        """测试持续时间格式化（小时）"""
        duration = DisplayFormatter.format_duration(3665)
        assert "1小时1分钟" == duration