"""
并发控制集成测试

测试设备正忙时的并发控制功能
"""
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


class TestConcurrentControl:
    """并发控制测试"""

    def test_device_busy_rejection(self, temp_config_dir):
        """测试设备正忙时拒绝任务"""
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
                
                runner.device_manager._busy_devices.add("device001")

                with pytest.raises(RuntimeError, match="设备正忙"):
                    runner.run_task("task001")

    def test_device_not_busy_acceptance(self, temp_config_dir):
        """测试设备不忙时接受任务"""
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

        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.execute_command.return_value = (0, "test", "")
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None

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
                    
                    assert result["task_id"] == "task001"

    def test_multiple_devices_partial_busy(self, temp_config_dir):
        """测试多台设备部分正忙"""
        devices_file = temp_config_dir / "devices" / "devices.yaml"
        devices_file.write_text("""
devices:
  - id: device001
    name: 测试设备1
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123

  - id: device002
    name: 测试设备2
    ip: 192.168.1.101
    port: 22
    username: root
    password: password456
""")

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

        tasks_file = temp_config_dir / "tasks" / "task.yaml"
        tasks_file.write_text("""
tasks:
  - id: task001
    name: 测试任务
    devices:
      - device001
      - device002
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: json
""")

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
                    
                    runner.device_manager._busy_devices.add("device001")

                    with pytest.raises(RuntimeError, match="设备正忙"):
                        runner.run_task("task001")