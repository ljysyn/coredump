"""
配置验证集成测试

测试配置文件验证功能
"""

import tempfile
from pathlib import Path

import pytest

from src.core.task_runner import TaskRunner


@pytest.fixture
def temp_config_dir():
    """临时配置目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        yield config_path


class TestConfigValidation:
    """配置验证测试"""

    def test_missing_device_in_task(self, temp_config_dir):
        """测试任务引用不存在的设备"""
        devices_dir = temp_config_dir / "devices"
        testcases_dir = temp_config_dir / "testcases"
        tasks_dir = temp_config_dir / "tasks"
        reports_dir = temp_config_dir / "reports"

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
      - device999
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: json
""")

        with pytest.raises(ValueError, match="设备不存在"):
            TaskRunner()

    def test_missing_testcase_in_task(self, temp_config_dir):
        """测试任务引用不存在的测试用例"""
        devices_dir = temp_config_dir / "devices"
        testcases_dir = temp_config_dir / "testcases"
        tasks_dir = temp_config_dir / "tasks"
        reports_dir = temp_config_dir / "reports"

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
      - tc999
    on_testcase_failure: stop
    report_format: json
""")

        with pytest.raises(ValueError, match="测试用例不存在"):
            TaskRunner()

    def test_invalid_yaml_syntax(self, temp_config_dir):
        """测试无效的YAML语法"""
        devices_dir = temp_config_dir / "devices"
        devices_dir.mkdir()

        devices_file = devices_dir / "devices.yaml"
        devices_file.write_text("invalid: yaml: syntax:")

        with pytest.raises(Exception):
            TaskRunner()
