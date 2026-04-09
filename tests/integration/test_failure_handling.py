"""
失败处理集成测试

测试测试用例失败后的不同处理策略
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


class TestFailureHandling:
    """失败处理测试"""

    def test_testcase_failure_stop(self, temp_config_dir, device_config):
        """测试测试用例失败后停止执行"""
        testcases_file = temp_config_dir / "testcases" / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 测试用例1
    timeout: 30
    on_failure: stop
    scenarios:
      - name: 场景1
        verify:
          - command: "test1"
            check: "output_contains"
            expected: "success"

  - id: tc002
    name: 测试用例2
    timeout: 30
    on_failure: stop
    scenarios:
      - name: 场景2
        verify:
          - command: "test2"
            check: "output_contains"
            expected: "success"
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
      - tc002
    on_testcase_failure: stop
    report_format: json
""")

        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        
        command_count = {"count": 0}
        
        def execute_command(cmd, timeout=None):
            command_count["count"] += 1
            return (1, "error", "")

        mock_client.execute_command = execute_command

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
                    assert result["devices"]["device001"]["stopped_at"] == "tc001"
                    assert command_count["count"] == 1

    def test_testcase_failure_continue(self, temp_config_dir, device_config):
        """测试测试用例失败后继续执行"""
        testcases_file = temp_config_dir / "testcases" / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 测试用例1
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 场景1
        verify:
          - command: "test1"
            check: "output_contains"
            expected: "success"

  - id: tc002
    name: 测试用例2
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 场景2
        verify:
          - command: "test2"
            check: "output_contains"
            expected: "success"
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
      - tc002
    on_testcase_failure: continue
    report_format: json
""")

        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        
        command_count = {"count": 0}
        
        def execute_command(cmd, timeout=None):
            command_count["count"] += 1
            return (1, "error", "")

        mock_client.execute_command = execute_command

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
                    assert command_count["count"] == 2

    def test_mixed_success_and_failure(self, temp_config_dir, device_config):
        """测试部分成功部分失败的场景"""
        testcases_file = temp_config_dir / "testcases" / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 测试用例1
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 场景1
        verify:
          - command: "test1"
            check: "output_contains"
            expected: "success"

  - id: tc002
    name: 测试用例2
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 场景2
        verify:
          - command: "test2"
            check: "output_contains"
            expected: "success"

  - id: tc003
    name: 测试用例3
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 场景3
        verify:
          - command: "test3"
            check: "output_contains"
            expected: "success"
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
      - tc002
      - tc003
    on_testcase_failure: continue
    report_format: json
""")

        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        
        call_count = {"count": 0}
        
        def execute_command(cmd, timeout=None):
            call_count["count"] += 1
            
            if "test1" in cmd:
                return (0, "success", "")
            elif "test2" in cmd:
                return (1, "error", "")
            elif "test3" in cmd:
                return (0, "success", "")
            
            return (0, "", "")

        mock_client.execute_command = execute_command

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
                    assert call_count["count"] == 3

    def test_scenario_failure_in_testcase(self, temp_config_dir, device_config):
        """测试场景失败时的处理"""
        testcases_file = temp_config_dir / "testcases" / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 测试用例
    timeout: 30
    on_failure: stop
    scenarios:
      - name: 场景1
        verify:
          - command: "test1"
            check: "output_contains"
            expected: "success"

      - name: 场景2
        verify:
          - command: "test2"
            check: "output_contains"
            expected: "success"
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
        mock_client.is_connected.return_value = True
        mock_client.disconnect.return_value = None
        
        call_count = {"count": 0}
        
        def execute_command(cmd, timeout=None):
            call_count["count"] += 1
            
            if "test1" in cmd:
                return (1, "error", "")
            
            return (0, "success", "")

        mock_client.execute_command = execute_command

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
                    assert call_count["count"] == 1