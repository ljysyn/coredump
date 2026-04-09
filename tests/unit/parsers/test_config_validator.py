"""
配置验证器单元测试

测试配置文件验证功能
"""

import pytest

from src.models import Device, TestCase, TestScenario, ExecutionPhase
from src.parsers.config_validator import ConfigValidator


class TestValidateDevice:
    """测试设备验证"""

    def test_validate_device_success(self):
        """测试验证成功"""
        device = Device(
            id="device001",
            name="测试设备",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
        )

        errors = ConfigValidator.validate_device(device)
        assert errors == []

    def test_validate_device_missing_id(self):
        """测试缺少ID"""
        device = Device(
            id="",
            name="测试设备",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
        )

        errors = ConfigValidator.validate_device(device)
        assert "设备缺少ID字段" in errors

    def test_validate_device_missing_name(self):
        """测试缺少名称"""
        device = Device(
            id="device001",
            name="",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
        )

        errors = ConfigValidator.validate_device(device)
        assert "设备缺少名称字段" in errors

    def test_validate_device_invalid_port(self):
        """测试无效端口"""
        device = Device(
            id="device001",
            name="测试设备",
            ip="192.168.1.100",
            port=99999,
            username="root",
            password="password123",
        )

        errors = ConfigValidator.validate_device(device)
        assert "设备端口号无效" in errors

    def test_validate_device_env_vars_not_dict(self):
        """测试环境变量不是字典"""
        device = Device(
            id="device001",
            name="测试设备",
            ip="192.168.1.100",
            port=22,
            username="root",
            password="password123",
            env_vars="invalid",
        )

        errors = ConfigValidator.validate_device(device)
        assert "环境变量必须是字典类型" in errors


class TestValidateTestcase:
    """测试测试用例验证"""

    def test_validate_testcase_success(self):
        """测试验证成功"""
        scenario = TestScenario(
            name="测试场景",
            verify=[
                ExecutionPhase(
                    command="echo test", check="output_contains", expected="test"
                )
            ],
        )

        testcase = TestCase(
            id="tc001",
            name="测试用例",
            scenarios=[scenario],
            timeout=30,
            on_failure="stop",
        )

        errors = ConfigValidator.validate_testcase(testcase)
        assert errors == []

    def test_validate_testcase_missing_id(self):
        """测试缺少ID"""
        scenario = TestScenario(
            name="测试场景",
            verify=[
                ExecutionPhase(
                    command="echo test", check="output_contains", expected="test"
                )
            ],
        )

        testcase = TestCase(
            id="",
            name="测试用例",
            scenarios=[scenario],
            timeout=30,
            on_failure="stop",
        )

        errors = ConfigValidator.validate_testcase(testcase)
        assert "测试用例缺少ID字段" in errors

    def test_validate_testcase_no_scenarios(self):
        """测试没有测试场景"""
        testcase = TestCase(
            id="tc001",
            name="测试用例",
            scenarios=[],
            timeout=30,
            on_failure="stop",
        )

        errors = ConfigValidator.validate_testcase(testcase)
        assert "测试用例缺少测试场景" in errors

    def test_validate_testcase_scenario_missing_name(self):
        """测试场景缺少名称"""
        scenario = TestScenario(
            name="",
            verify=[
                ExecutionPhase(
                    command="echo test", check="output_contains", expected="test"
                )
            ],
        )

        testcase = TestCase(
            id="tc001",
            name="测试用例",
            scenarios=[scenario],
            timeout=30,
            on_failure="stop",
        )

        errors = ConfigValidator.validate_testcase(testcase)
        assert "缺少名称" in errors[0]

    def test_validate_testcase_scenario_missing_verify(self):
        """测试场景缺少verify阶段"""
        scenario = TestScenario(
            name="测试场景",
            verify=[],
        )

        testcase = TestCase(
            id="tc001",
            name="测试用例",
            scenarios=[scenario],
            timeout=30,
            on_failure="stop",
        )

        errors = ConfigValidator.validate_testcase(testcase)
        assert "缺少verify阶段" in errors[0]
