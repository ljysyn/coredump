"""
多设备场景集成测试

测试多台设备的批量测试功能
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.task_runner import TaskRunner
from src.models import Device


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
def multi_device_config(temp_config_dir):
    """多设备配置文件"""
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

  - id: device003
    name: 测试设备3
    ip: 192.168.1.102
    port: 22
    username: root
    password: password789
""")
    return devices_file


@pytest.fixture
def testcase_config(temp_config_dir):
    """测试用例配置文件"""
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
""")
    return testcases_file


@pytest.fixture
def multi_device_task_config(temp_config_dir):
    """多设备任务配置文件"""
    tasks_file = temp_config_dir / "tasks" / "task.yaml"
    tasks_file.write_text("""
tasks:
  - id: task001
    name: 多设备测试任务
    devices:
      - device001
      - device002
      - device003
    testcases:
      - tc001
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
        "PING 192.168.1.1: 1 packets transmitted, 1 received",
        "",
    )
    client.is_connected.return_value = True
    client.disconnect.return_value = None
    return client


class TestMultiDeviceIntegration:
    """多设备集成测试"""

    def test_all_devices_success(
        self,
        temp_config_dir,
        multi_device_config,
        testcase_config,
        multi_device_task_config,
        mock_ssh_client,
    ):
        """测试所有设备成功执行"""
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

                    assert result["task_id"] == "task001"
                    assert len(result["devices"]) == 3

                    for device_id in ["device001", "device002", "device003"]:
                        assert device_id in result["devices"]
                        assert result["devices"][device_id]["status"] == "pass"

    def test_partial_device_failure(
        self,
        temp_config_dir,
        multi_device_config,
        testcase_config,
        multi_device_task_config,
    ):
        """测试部分设备失败"""
        with patch("src.utils.ssh_client.SSHClient") as mock_ssh_class:
            clients = {}

            def create_client(*args, **kwargs):
                client = MagicMock()
                client.is_connected.return_value = True
                client.disconnect.return_value = None
                return client

            mock_ssh_class.side_effect = create_client

            connect_results = {
                "device001": True,
                "device002": ConnectionError("SSH连接超时"),
                "device003": True,
            }

            connect_call_count = {"count": 0}

            def mock_connect(device):
                connect_call_count["count"] += 1
                result = connect_results.get(device.id, True)
                if isinstance(result, Exception):
                    raise result
                return result

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

                    with patch("src.core.device_manager.SSHClient") as mock_dm_ssh:

                        def create_device_client(*args, **kwargs):
                            client = MagicMock()
                            client.is_connected.return_value = True
                            client.disconnect.return_value = None
                            client.execute_command.return_value = (0, "test output", "")
                            client.connect.side_effect = mock_connect
                            return client

                        mock_dm_ssh.side_effect = create_device_client

                        runner = TaskRunner()
                        result = runner.run_task("task001")

                        assert result["devices"]["device001"]["status"] == "pass"
                        assert result["devices"]["device002"]["status"] == "failed"
                        assert result["devices"]["device003"]["status"] == "pass"

    def test_sequential_execution_order(
        self,
        temp_config_dir,
        multi_device_config,
        testcase_config,
        multi_device_task_config,
    ):
        """测试设备顺序执行"""
        execution_log = []

        with patch("src.utils.ssh_client.SSHClient") as mock_ssh_class:

            def create_client(*args, **kwargs):
                client = MagicMock()
                client.is_connected.return_value = True
                client.disconnect.return_value = None
                client.execute_command.return_value = (0, "test", "")

                original_connect = client.connect

                def track_connect(device):
                    execution_log.append(f"connect:{device.id}")
                    return True

                client.connect = track_connect

                def track_disconnect():
                    device_id = (
                        execution_log[-1].split(":")[1] if execution_log else "unknown"
                    )
                    execution_log.append(f"disconnect:{device_id}")

                client.disconnect = track_disconnect

                return client

            mock_ssh_class.side_effect = create_client

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

                    connect_order = [
                        log for log in execution_log if log.startswith("connect:")
                    ]
                    assert len(connect_order) == 3

    def test_multiple_reports_generated(
        self,
        temp_config_dir,
        multi_device_config,
        testcase_config,
        multi_device_task_config,
        mock_ssh_client,
    ):
        """测试生成多份报告"""
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

                    report_paths = [
                        result["devices"][device_id].get("report_path")
                        for device_id in ["device001", "device002", "device003"]
                    ]

                    assert len(report_paths) == 3
                    assert all(path is not None for path in report_paths)
