"""
YAML格式契约测试

验证YAML配置文件格式符合契约规范
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.parsers.yaml_parser import YAMLParser


class TestYAMLFormatContract:
    """YAML格式契约测试"""

    def test_device_yaml_format(self):
        """测试设备YAML格式"""
        yaml_content = """
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
"""

        data = yaml.safe_load(yaml_content)

        assert "devices" in data
        assert isinstance(data["devices"], list)

        device = data["devices"][0]
        assert "id" in device
        assert "name" in device
        assert "ip" in device
        assert "port" in device
        assert "username" in device
        assert "password" in device

    def test_testcase_yaml_format(self):
        """测试测试用例YAML格式"""
        yaml_content = """
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
"""

        data = yaml.safe_load(yaml_content)

        assert "testcases" in data
        assert isinstance(data["testcases"], list)

        testcase = data["testcases"][0]
        assert "id" in testcase
        assert "name" in testcase
        assert "scenarios" in testcase

        scenario = testcase["scenarios"][0]
        assert "name" in scenario
        assert "verify" in scenario

    def test_task_yaml_format(self):
        """测试任务YAML格式"""
        yaml_content = """
tasks:
  - id: task001
    name: 测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: json
"""

        data = yaml.safe_load(yaml_content)

        assert "tasks" in data
        assert isinstance(data["tasks"], list)

        task = data["tasks"][0]
        assert "id" in task
        assert "name" in task
        assert "devices" in task
        assert "testcases" in task

    def test_device_env_vars_optional(self):
        """测试设备环境变量可选"""
        yaml_content = """
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/bin:/usr/bin:/bin
"""

        data = yaml.safe_load(yaml_content)
        device = data["devices"][0]

        assert "env_vars" in device
        assert isinstance(device["env_vars"], dict)

    def test_scenario_phases_format(self):
        """测试场景阶段格式"""
        yaml_content = """
testcases:
  - id: tc001
    name: 测试用例
    scenarios:
      - name: 完整场景
        setup:
          commands:
            - "mkdir /tmp/test"
        execute:
          commands:
            - "ls /tmp"
        verify:
          - command: "test -d /tmp/test"
            check: "return_code"
            expected: "0"
        cleanup:
          commands:
            - "rm -rf /tmp/test"
"""

        data = yaml.safe_load(yaml_content)
        scenario = data["testcases"][0]["scenarios"][0]

        assert "setup" in scenario
        assert "execute" in scenario
        assert "verify" in scenario
        assert "cleanup" in scenario

    def test_yaml_parser_load_devices(self):
        """测试YAML解析器加载设备"""
        with tempfile.TemporaryDirectory() as tmpdir:
            devices_dir = Path(tmpdir)
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

            devices = YAMLParser.load_all_devices(str(devices_dir))

            assert "device001" in devices
            assert devices["device001"].name == "测试设备"

    def test_yaml_parser_load_testcases(self):
        """测试YAML解析器加载测试用例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testcases_dir = Path(tmpdir)
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

            testcases = YAMLParser.load_all_testcases(str(testcases_dir))

            assert "tc001" in testcases
            assert testcases["tc001"].name == "测试用例"

    def test_yaml_parser_load_tasks(self):
        """测试YAML解析器加载任务"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_dir = Path(tmpdir)
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

            tasks = YAMLParser.load_all_tasks(str(tasks_dir))

            assert "task001" in tasks
            assert tasks["task001"].name == "测试任务"
