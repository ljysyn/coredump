"""
多测试用例场景集成测试

测试多条测试用例的批量执行功能
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


@pytest.fixture
def multi_testcase_config(temp_config_dir):
    """多测试用例配置文件"""
    testcases_file = temp_config_dir / "testcases" / "test.yaml"
    testcases_file.write_text("""
testcases:
  - id: tc001
    name: 网络连通性测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping测试
        verify:
          - command: "ping -c 1 192.168.1.1"
            check: "output_contains"
            expected: "packets transmitted"

  - id: tc002
    name: 磁盘空间检查
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 磁盘检查
        verify:
          - command: "df -h /"
            check: "output_contains"
            expected: "Filesystem"

  - id: tc003
    name: 内存使用检查
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 内存检查
        verify:
          - command: "free -m"
            check: "output_contains"
            expected: "Mem:"
""")
    return testcases_file


@pytest.fixture
def multi_testcase_task_config(temp_config_dir):
    """多测试用例任务配置文件"""
    tasks_file = temp_config_dir / "tasks" / "task.yaml"
    tasks_file.write_text("""
tasks:
  - id: task001
    name: 系统检查任务
    devices:
      - device001
    testcases:
      - tc001
      - tc002
      - tc003
    on_testcase_failure: continue
    report_format: json
""")
    return tasks_file


@pytest.fixture
def mock_ssh_client():
    """Mock SSH客户端"""
    client = MagicMock()
    client.connect.return_value = True
    client.execute_command.return_value = (
        0,
        "test output",
        "",
    )
    client.is_connected.return_value = True
    client.disconnect.return_value = None
    return client


class TestMultiTestcaseIntegration:
    """多测试用例集成测试"""

    def test_all_testcases_success(
        self,
        temp_config_dir,
        device_config,
        multi_testcase_config,
        multi_testcase_task_config,
        mock_ssh_client,
    ):
        """测试所有测试用例成功执行"""
        call_count = {"count": 0}

        def execute_command(command, timeout=None):
            call_count["count"] += 1

            if "ping" in command:
                return (0, "PING: 1 packets transmitted", "")
            elif "df" in command:
                return (0, "Filesystem Size Used Avail", "")
            elif "free" in command:
                return (0, "Mem: 2048 1024 1024", "")
            else:
                return (0, "test", "")

        mock_ssh_client.execute_command.side_effect = execute_command

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = (
                    temp_config_dir / "devices"
                )
                mock_pm_instance.get_testcases_dir.return_value = (
                    temp_config_dir / "testcases"
                )
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = (
                    temp_config_dir / "reports"
                )
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    result = runner.run_task("task001")

                    assert result["devices"]["device001"]["status"] == "pass"
                    assert call_count["count"] >= 3

    def test_testcase_failure_continue(
        self,
        temp_config_dir,
        device_config,
        multi_testcase_config,
        multi_testcase_task_config,
        mock_ssh_client,
    ):
        """测试测试用例失败后继续执行"""
        call_count = {"count": 0}

        def execute_command(command, timeout=None):
            call_count["count"] += 1

            if "ping" in command:
                return (1, "ping: network unreachable", "")
            elif "df" in command:
                return (0, "Filesystem Size Used Avail", "")
            elif "free" in command:
                return (0, "Mem: 2048 1024 1024", "")
            else:
                return (0, "test", "")

        mock_ssh_client.execute_command.side_effect = execute_command

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = (
                    temp_config_dir / "devices"
                )
                mock_pm_instance.get_testcases_dir.return_value = (
                    temp_config_dir / "testcases"
                )
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = (
                    temp_config_dir / "reports"
                )
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
                    assert call_count["count"] >= 3

    def test_testcase_failure_stop(self, temp_config_dir, device_config):
        """测试测试用例失败后停止"""
        testcases_file = temp_config_dir / "testcases" / "test.yaml"
        testcases_file.write_text("""
testcases:
  - id: tc001
    name: 网络测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping测试
        verify:
          - command: "ping -c 1 192.168.1.1"
            check: "output_contains"
            expected: "packets transmitted"

  - id: tc002
    name: 磁盘检查
    timeout: 30
    on_failure: continue
    scenarios:
      - name: 磁盘检查
        verify:
          - command: "df -h /"
            check: "output_contains"
            expected: "Filesystem"
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

        call_count = {"count": 0}

        def execute_command(command, timeout=None):
            call_count["count"] += 1
            return (1, "error", "")

        mock_client.execute_command = execute_command

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = (
                    temp_config_dir / "devices"
                )
                mock_pm_instance.get_testcases_dir.return_value = (
                    temp_config_dir / "testcases"
                )
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = (
                    temp_config_dir / "reports"
                )
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

    def test_sequential_testcase_execution(
        self,
        temp_config_dir,
        device_config,
        multi_testcase_config,
        multi_testcase_task_config,
        mock_ssh_client,
    ):
        """测试测试用例顺序执行"""
        execution_order = []

        def execute_command(command, timeout=None):
            if "ping" in command:
                execution_order.append("tc001")
            elif "df" in command:
                execution_order.append("tc002")
            elif "free" in command:
                execution_order.append("tc003")

            return (0, "test output", "")

        mock_ssh_client.execute_command.side_effect = execute_command

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_pm_instance = MagicMock()
                mock_pm_instance.get_devices_dir.return_value = (
                    temp_config_dir / "devices"
                )
                mock_pm_instance.get_testcases_dir.return_value = (
                    temp_config_dir / "testcases"
                )
                mock_pm_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_pm_instance.get_reports_dir.return_value = (
                    temp_config_dir / "reports"
                )
                mock_path_manager.return_value = mock_pm_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_s_instance = MagicMock()
                    mock_s_instance.ssh_timeout = 10
                    mock_s_instance.default_timeout = 30
                    mock_s_instance.report_max_size = 100
                    mock_settings.return_value = mock_s_instance

                    runner = TaskRunner()
                    runner.run_task("task001")

                    assert execution_order == ["tc001", "tc002", "tc003"]
