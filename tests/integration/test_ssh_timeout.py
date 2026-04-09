"""
SSH故障处理集成测试

测试SSH连接失败和超时场景
"""
import socket
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.task_runner import TaskRunner


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

        yield config_path


@pytest.fixture
def device_config(temp_config_dir):
    """设备配置文件"""
    devices_file = temp_config_dir / "devices" / "devices.yaml"
    devices_file.write_text("""
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
""")
    return devices_file


@pytest.fixture
def testcase_config(temp_config_dir):
    """测试用例配置文件"""
    testcases_file = temp_config_dir / "testcases" / "test.yaml"
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
    return testcases_file


@pytest.fixture
def task_config(temp_config_dir):
    """任务配置文件"""
    tasks_file = temp_config_dir / "tasks" / "task.yaml"
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
    return tasks_file


class TestSSHFailureHandling:
    """SSH故障处理测试"""

    def test_connection_timeout(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试SSH连接超时"""
        mock_client = MagicMock()
        mock_client.connect.side_effect = socket.timeout("SSH连接超时")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "failed"
                    assert "连接失败" in result["devices"]["device001"]["error"]

    def test_connection_refused(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试SSH连接被拒绝"""
        mock_client = MagicMock()
        mock_client.connect.side_effect = ConnectionRefusedError("Connection refused")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "failed"

    def test_authentication_failure(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试SSH认证失败"""
        mock_client = MagicMock()
        mock_client.connect.side_effect = Exception("Authentication failed")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "failed"

    def test_command_timeout(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试命令执行超时"""
        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        mock_client.execute_command.side_effect = TimeoutError("命令执行超时")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "fail"

    def test_connection_dropped(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试SSH连接中断"""
        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        mock_client.execute_command.side_effect = Exception("Connection dropped")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "fail"

    def test_graceful_disconnect_on_error(self, temp_config_dir, device_config, testcase_config, task_config):
        """测试错误时优雅断开连接"""
        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        mock_client.execute_command.side_effect = Exception("Error")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_pm_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    runner.run_task("task001")

                    mock_client.disconnect.assert_called()