"""
完整工作流集成测试

测试从设备配置到测试执行到报告生成的完整流程
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.device_manager import DeviceManager
from src.core.report_generator import ReportGenerator
from src.core.task_runner import TaskRunner
from src.core.test_executor import TestExecutor
from src.models import Device, ExecutionPhase, TestCase, TestScenario, Task


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
def sample_device_config(temp_config_dir):
    """示例设备配置文件"""
    devices_file = temp_config_dir / "devices" / "devices.yaml"
    devices_file.write_text("""
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/bin:/usr/bin:/bin
""")
    return devices_file


@pytest.fixture
def sample_testcase_config(temp_config_dir):
    """示例测试用例配置文件"""
    testcases_file = temp_config_dir / "testcases" / "test.yaml"
    testcases_file.write_text("""
testcases:
  - id: tc001
    name: 网络连通性测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping测试
        setup:
          commands:
            - "mkdir -p /tmp/test"
        verify:
          - command: "ping -c 1 192.168.1.1"
            check: "output_contains"
            expected: "1 packets transmitted"
        cleanup:
          commands:
            - "rm -rf /tmp/test"
""")
    return testcases_file


@pytest.fixture
def sample_task_config(temp_config_dir):
    """示例任务配置文件"""
    tasks_file = temp_config_dir / "tasks" / "task.yaml"
    tasks_file.write_text("""
tasks:
  - id: task001
    name: 网络测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
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


class TestFullWorkflow:
    """测试完整工作流"""

    def test_complete_workflow_success(
        self,
        temp_config_dir,
        sample_device_config,
        sample_testcase_config,
        sample_task_config,
        mock_ssh_client,
    ):
        """测试完整工作流成功场景"""
        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.paths.PathManager") as mock_path_manager:
                mock_path_manager_instance = MagicMock()
                mock_path_manager_instance.get_devices_dir.return_value = temp_config_dir / "devices"
                mock_path_manager_instance.get_testcases_dir.return_value = temp_config_dir / "testcases"
                mock_path_manager_instance.get_tasks_dir.return_value = temp_config_dir / "tasks"
                mock_path_manager_instance.get_reports_dir.return_value = temp_config_dir / "reports"
                mock_path_manager.return_value = mock_path_manager_instance

                with patch("src.config.settings.Settings") as mock_settings:
                    mock_settings_instance = MagicMock()
                    mock_settings_instance.ssh_timeout = 10
                    mock_settings_instance.default_timeout = 30
                    mock_settings_instance.report_max_size = 100
                    mock_settings.return_value = mock_settings_instance

                    runner = TaskRunner()

                    result = runner.run_task("task001")

                    assert result["task_id"] == "task001"
                    assert "device001" in result["devices"]
                    assert result["devices"]["device001"]["status"] == "pass"

                    report_path = result["devices"]["device001"].get("report_path")
                    if report_path:
                        assert Path(report_path).exists()

    def test_workflow_with_device_failure(
        self,
        temp_config_dir,
        sample_device_config,
        sample_testcase_config,
        sample_task_config,
    ):
        """测试设备连接失败场景"""
        with patch("src.utils.ssh_client.SSHClient") as mock_ssh_class:
            mock_client = MagicMock()
            mock_client.connect.side_effect = ConnectionError("SSH连接超时")
            mock_ssh_class.return_value = mock_client

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

    def test_workflow_with_test_failure(
        self,
        temp_config_dir,
        sample_device_config,
        sample_testcase_config,
        sample_task_config,
        mock_ssh_client,
    ):
        """测试测试用例失败场景"""
        mock_ssh_client.execute_command.return_value = (
            2,
            "ping: unreachable",
            "",
        )

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
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

    def test_workflow_json_report_generation(
        self,
        temp_config_dir,
        sample_device_config,
        sample_testcase_config,
        sample_task_config,
        mock_ssh_client,
    ):
        """测试JSON报告生成"""
        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
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

                    report_path = Path(result["devices"]["device001"]["report_path"])
                    if report_path.exists():
                        with open(report_path, "r", encoding="utf-8") as f:
                            report_data = json.load(f)

                            assert "meta" in report_data
                            assert "summary" in report_data
                            assert report_data["meta"]["overall_result"] == "pass"

    def test_workflow_html_report_generation(
        self,
        temp_config_dir,
        sample_device_config,
        sample_testcase_config,
        mock_ssh_client,
    ):
        """测试HTML报告生成"""
        tasks_file = temp_config_dir / "tasks" / "task.yaml"
        tasks_file.write_text("""
tasks:
  - id: task001
    name: 网络测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: html
""")

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
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

                    report_path = Path(result["devices"]["device001"]["report_path"])
                    if report_path.exists():
                        with open(report_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            assert "<!DOCTYPE html>" in content
                            assert "测试报告" in content


class TestWorkflowComponents:
    """测试工作流组件"""

    def test_device_manager_workflow(self, mock_ssh_client):
        """测试设备管理器工作流"""
        device = Device(
            id="device001",
            name="测试设备",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
        )

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.settings.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.ssh_timeout = 10
                mock_get_settings.return_value = mock_settings

                manager = DeviceManager()

                connected = manager.connect(device)
                assert connected is True

                return_code, output, error = manager.execute_command(
                    device.id, "ls"
                )
                assert return_code == 0

                manager.disconnect(device.id)
                assert not manager.is_connected(device.id)

    def test_test_executor_workflow(self, mock_ssh_client):
        """测试执行器工作流"""
        device = Device(
            id="device001",
            name="测试设备",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
        )

        phase = ExecutionPhase(
            command="echo test",
            check="output_contains",
            expected="test",
        )

        scenario = TestScenario(
            name="测试场景",
            verify=[phase],
        )

        testcase = TestCase(
            id="tc001",
            name="测试用例",
            scenarios=[scenario],
            timeout=30,
            on_failure="stop",
        )

        with patch("src.utils.ssh_client.SSHClient", return_value=mock_ssh_client):
            with patch("src.config.settings.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.ssh_timeout = 10
                mock_settings.default_timeout = 30
                mock_get_settings.return_value = mock_settings

                device_manager = DeviceManager()
                device_manager.connect(device)

                executor = TestExecutor(device_manager)

                passed, steps = executor.execute_testcase(device, testcase)

                assert passed is True
                assert len(steps) > 0

    def test_report_generator_workflow(self, temp_config_dir):
        """测试报告生成器工作流"""
        from src.models import Report, ReportStep

        step = ReportStep(
            scenario_name="测试场景",
            phase="verify",
            command="echo test",
            output="test",
            return_code=0,
            result="pass",
            duration=1.0,
        )

        report = Report(
            task_name="测试任务",
            device_id="device001",
            timestamp=datetime.now(),
            duration=1.0,
            overall_result="pass",
            steps=[step],
        )

        with patch("src.config.paths.get_path_manager") as mock_get_path:
            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = temp_config_dir / "reports"
            mock_get_path.return_value = mock_path_manager

            with patch("src.config.settings.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.report_max_size = 100
                mock_get_settings.return_value = mock_settings

                generator = ReportGenerator()

                json_path = generator.generate_report(report, format="json")
                assert Path(json_path).exists()

                html_path = generator.generate_report(report, format="html")
                assert Path(html_path).exists()


class TestErrorHandling:
    """测试错误处理"""

    def test_invalid_task_id(self, temp_config_dir, sample_device_config, sample_testcase_config):
        """测试无效任务ID"""
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

                with pytest.raises(ValueError, match="任务不存在"):
                    runner.run_task("invalid_task")

    def test_invalid_yaml_config(self, temp_config_dir):
        """测试无效YAML配置"""
        devices_file = temp_config_dir / "devices" / "invalid.yaml"
        devices_file.write_text("invalid: yaml: content:")

        with patch("src.config.paths.PathManager") as mock_path_manager:
            mock_pm_instance = MagicMock()
            mock_pm_instance.get_devices_dir.return_value = temp_config_dir / "devices"
            mock_path_manager.return_value = mock_pm_instance

            with patch("src.config.settings.Settings") as mock_settings:
                mock_s_instance = MagicMock()
                mock_settings.return_value = mock_s_instance

                with pytest.raises(Exception):
                    TaskRunner()