"""
CLI命令契约测试

验证CLI命令符合契约规范
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.cli.main import cli


@pytest.fixture
def temp_config_dir():
    """临时配置目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)

        devices_dir = config_path / "devices"
        testcases_dir = config_path / "testcases"
        tasks_dir = config_path / "tasks"
        reports_dir = config_path / "reports"

        devices_dir.mkdir()
        testcases_dir.mkdir()
        tasks_dir.mkdir()
        reports_dir.mkdir()

        devices_file = devices_dir / "devices.yaml"
        devices_file.write_text("""
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
""")

        testcases_file = testcases_dir / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 测试用例
    timeout: 30
    on_failure: stop
    scenarios:
      - name: 测试场景
        verify:
          - command: "echo test"
            check: "output_contains"
            expected: "test"
""")

        tasks_file = tasks_dir / "task.yaml"
        tasks_file.write_text("""
tasks:
  - id: task001
    name: 测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: json
""")

        yield config_path


class TestCLIContract:
    """CLI命令契约测试"""

    def test_list_devices_command_exists(self, temp_config_dir):
        """测试list devices命令存在"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "devices"])

            assert result.exit_code == 0

    def test_list_devices_output_format(self, temp_config_dir):
        """测试list devices输出格式"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "devices"])

            assert "ID" in result.output
            assert "名称" in result.output
            assert "IP地址" in result.output
            assert "device001" in result.output

    def test_list_testcases_command_exists(self, temp_config_dir):
        """测试list testcases命令存在"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "testcases"])

            assert result.exit_code == 0

    def test_list_testcases_output_format(self, temp_config_dir):
        """测试list testcases输出格式"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "testcases"])

            assert "ID" in result.output
            assert "名称" in result.output
            assert "场景数" in result.output
            assert "tc001" in result.output

    def test_list_tasks_command_exists(self, temp_config_dir):
        """测试list tasks命令存在"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "tasks"])

            assert result.exit_code == 0

    def test_list_tasks_output_format(self, temp_config_dir):
        """测试list tasks输出格式"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            result = runner.invoke(cli, ["list", "tasks"])

            assert "ID" in result.output
            assert "名称" in result.output
            assert "设备数" in result.output
            assert "task001" in result.output

    def test_run_command_exists(self, temp_config_dir):
        """测试run命令存在"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            with patch("src.core.task_runner.TaskRunner.run_task") as mock_run:
                mock_run.return_value = {
                    "task_id": "task001",
                    "task_name": "测试任务",
                    "start_time": "2026-04-08T10:00:00",
                    "end_time": "2026-04-08T10:00:05",
                    "duration": 5.0,
                    "devices": {
                        "device001": {
                            "status": "pass",
                            "report_path": "/reports/test.json",
                        }
                    },
                }

                result = runner.invoke(cli, ["run", "task001"])

                assert result.exit_code == 0

    def test_run_command_output_format(self, temp_config_dir):
        """测试run命令输出格式"""
        runner = CliRunner()

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = mock_path_manager.return_value
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_pm_instance.get_testcases_dir.return_value = (
                temp_config_dir / "testcases"
            )
            mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
            mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"

            with patch("src.core.task_runner.TaskRunner.run_task") as mock_run:
                mock_run.return_value = {
                    "task_id": "task001",
                    "task_name": "测试任务",
                    "start_time": "2026-04-08T10:00:00",
                    "end_time": "2026-04-08T10:00:05",
                    "duration": 5.0,
                    "devices": {
                        "device001": {
                            "status": "pass",
                            "report_path": "/reports/test.json",
                        }
                    },
                }

                result = runner.invoke(cli, ["run", "task001"])

                assert "任务执行结果" in result.output
                assert "任务ID: task001" in result.output
                assert "device001" in result.output

    def test_version_command(self):
        """测试version命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "coredump, version" in result.output

    def test_help_command(self):
        """测试help命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Coredump自动化测试框架" in result.output

    def test_list_help_command(self):
        """测试list help命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--help"])

        assert result.exit_code == 0
        assert "列出资源列表" in result.output

    def test_run_help_command(self):
        """测试run help命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--help"])

        assert result.exit_code == 0
        assert "执行测试任务" in result.output
