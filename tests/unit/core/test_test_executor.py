"""
TestExecutor单元测试

测试场景执行、阶段管理和检查规则验证功能
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.test_executor import TestExecutor
from src.models import (
    Device,
    ExecutionPhase,
    ReportStep,
    TestCase,
    TestScenario,
)


@pytest.fixture
def mock_device_manager():
    """Mock设备管理器"""
    manager = MagicMock()
    manager.execute_command.return_value = (0, "output", "")
    return manager


@pytest.fixture
def sample_device():
    """示例设备"""
    return Device(
        id="device001",
        name="测试设备",
        ip="192.168.1.100",
        port=22,
        username="root",
        password="password123",
    )


@pytest.fixture
def sample_phase():
    """示例执行阶段"""
    return ExecutionPhase(
        command="echo 'hello'",
        check="output_contains",
        expected="hello",
    )


@pytest.fixture
def sample_scenario(sample_phase):
    """示例测试场景"""
    return TestScenario(
        name="测试场景",
        setup=[ExecutionPhase(command="mkdir /tmp/test", check=None, expected=None)],
        execute=[ExecutionPhase(command="ls", check=None, expected=None)],
        verify=[sample_phase],
        cleanup=[ExecutionPhase(command="rm -rf /tmp/test", check=None, expected=None)],
    )


@pytest.fixture
def sample_testcase(sample_scenario):
    """示例测试用例"""
    return TestCase(
        id="tc001",
        name="测试用例",
        scenarios=[sample_scenario],
        timeout=30,
        on_failure="stop",
    )


@pytest.fixture
def test_executor(mock_device_manager):
    """测试执行器实例"""
    return TestExecutor(mock_device_manager)


class TestExecuteTestcase:
    """测试执行测试用例"""

    def test_execute_testcase_all_pass(
        self, test_executor, sample_device, sample_testcase, mock_device_manager
    ):
        """测试所有场景通过"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        passed, steps = test_executor.execute_testcase(
            device=sample_device,
            testcase=sample_testcase,
        )

        assert passed is True
        assert len(steps) > 0
        assert all(step.result == "pass" for step in steps)

    def test_execute_testcase_with_failure_stop(
        self, test_executor, sample_device, sample_testcase, mock_device_manager
    ):
        """测试失败后停止"""
        mock_device_manager.execute_command.return_value = (1, "error", "")

        passed, steps = test_executor.execute_testcase(
            device=sample_device,
            testcase=sample_testcase,
        )

        assert passed is False
        assert len(steps) > 0

    def test_execute_testcase_with_failure_continue(
        self, test_executor, sample_device, mock_device_manager
    ):
        """测试失败后继续"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        scenario1 = TestScenario(
            name="场景1",
            verify=[
                ExecutionPhase(
                    command="cmd1", check="output_contains", expected="text1"
                )
            ],
        )
        scenario2 = TestScenario(
            name="场景2",
            verify=[
                ExecutionPhase(
                    command="cmd2", check="output_contains", expected="text2"
                )
            ],
        )

        testcase = TestCase(
            id="tc002",
            name="测试用例",
            scenarios=[scenario1, scenario2],
            timeout=30,
            on_failure="continue",
        )

        passed, steps = test_executor.execute_testcase(
            device=sample_device,
            testcase=testcase,
        )

        assert len(steps) >= 2


class TestExecuteScenario:
    """测试执行场景"""

    def test_execute_scenario_all_phases(
        self, test_executor, sample_device, sample_scenario, mock_device_manager
    ):
        """测试执行所有阶段"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        passed, steps = test_executor.execute_scenario(
            device=sample_device,
            scenario=sample_scenario,
        )

        assert passed is True
        assert len(steps) >= 4

    def test_execute_scenario_setup_failure(
        self, test_executor, sample_device, sample_scenario, mock_device_manager
    ):
        """测试setup阶段失败"""
        mock_device_manager.execute_command.return_value = (1, "error", "")

        passed, steps = test_executor.execute_scenario(
            device=sample_device,
            scenario=sample_scenario,
        )

        assert passed is False
        # 验证cleanup阶段被执行
        cleanup_steps = [s for s in steps if s.phase == "cleanup"]
        assert len(cleanup_steps) > 0, "cleanup阶段应该被执行"

    def test_execute_scenario_execute_failure_runs_cleanup(
        self, test_executor, sample_device, sample_scenario, mock_device_manager
    ):
        """测试execute阶段失败时cleanup仍被执行"""
        mock_device_manager.execute_command.side_effect = [
            (0, "setup success", ""),  # setup成功
            (1, "execute failed", ""),  # execute失败
            (0, "cleanup", ""),  # cleanup被执行
        ]

        passed, steps = test_executor.execute_scenario(
            device=sample_device,
            scenario=sample_scenario,
        )

        assert passed is False
        # 验证cleanup阶段被执行
        cleanup_steps = [s for s in steps if s.phase == "cleanup"]
        assert len(cleanup_steps) > 0, "execute失败后cleanup阶段应该被执行"

    def test_execute_scenario_verify_failure(
        self, test_executor, sample_device, sample_scenario, mock_device_manager
    ):
        """测试verify阶段失败"""
        mock_device_manager.execute_command.side_effect = [
            (0, "setup", ""),
            (0, "execute", ""),
            (0, "wrong output", ""),
            (0, "cleanup", ""),
        ]

        passed, steps = test_executor.execute_scenario(
            device=sample_device,
            scenario=sample_scenario,
        )

        assert passed is False

    def test_execute_scenario_cleanup_failure_marks_fail(
        self, test_executor, sample_device, sample_scenario, mock_device_manager
    ):
        """测试cleanup失败标记场景失败"""
        mock_device_manager.execute_command.side_effect = [
            (0, "setup", ""),
            (0, "execute", ""),
            (0, "hello", ""),
            (1, "cleanup error", ""),
        ]

        passed, steps = test_executor.execute_scenario(
            device=sample_device,
            scenario=sample_scenario,
        )

        assert passed is False


class TestExecutePhase:
    """测试执行阶段"""

    def test_execute_phase_remote_success(
        self, test_executor, sample_device, sample_phase, mock_device_manager
    ):
        """测试远程执行成功"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        step = test_executor.execute_phase(
            device=sample_device,
            phase=sample_phase,
            phase_name="verify",
            scenario_name="测试场景",
            timeout=30,
            is_remote=True,
        )

        assert isinstance(step, ReportStep)
        assert step.result == "pass"
        assert step.return_code == 0
        assert step.command == "echo 'hello'"
        assert step.phase == "verify"

    def test_execute_phase_local_success(
        self, test_executor, sample_device, sample_phase
    ):
        """测试本地执行成功"""
        phase = ExecutionPhase(command="echo 'test'", check=None, expected=None)

        step = test_executor.execute_phase(
            device=sample_device,
            phase=phase,
            phase_name="execute",
            scenario_name="测试场景",
            timeout=5,
            is_remote=False,
        )

        assert isinstance(step, ReportStep)
        assert step.result == "pass"
        assert step.return_code == 0

    def test_execute_phase_with_timeout(
        self, test_executor, sample_device, sample_phase, mock_device_manager
    ):
        """测试执行超时"""
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
            step = test_executor.execute_phase(
                device=sample_device,
                phase=sample_phase,
                phase_name="execute",
                scenario_name="测试场景",
                timeout=30,
                is_remote=False,
            )

            assert step.result == "fail"
            assert "超时" in step.error_message


class TestVerifyOutput:
    """测试检查规则验证"""

    def test_verify_output_contains_success(self, test_executor):
        """测试output_contains成功"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="hello world",
            check="output_contains",
            expected="hello",
        )

        assert passed is True
        assert error is None

    def test_verify_output_contains_failure(self, test_executor):
        """测试output_contains失败"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="hello world",
            check="output_contains",
            expected="goodbye",
        )

        assert passed is False
        assert "未包含期望值" in error

    def test_verify_return_code_success(self, test_executor):
        """测试return_code成功"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="",
            check="return_code",
            expected="0",
        )

        assert passed is True
        assert error is None

    def test_verify_return_code_failure(self, test_executor):
        """测试return_code失败"""
        passed, error = test_executor._verify_output(
            return_code=1,
            output="",
            check="return_code",
            expected="0",
        )

        assert passed is False
        assert "不匹配" in error

    def test_verify_regex_success(self, test_executor):
        """测试regex成功"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="Linux 5.10.0",
            check="regex",
            expected=r"Linux \d+\.\d+",
        )

        assert passed is True
        assert error is None

    def test_verify_regex_failure(self, test_executor):
        """测试regex失败"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="Windows 10",
            check="regex",
            expected=r"Linux \d+\.\d+",
        )

        assert passed is False
        assert "未匹配正则表达式" in error

    def test_verify_regex_invalid_pattern(self, test_executor):
        """测试regex无效模式"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="test",
            check="regex",
            expected="[invalid",
        )

        assert passed is False
        assert "正则表达式错误" in error

    def test_verify_none_check(self, test_executor):
        """测试none检查（不检查）"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="anything",
            check="none",
            expected=None,
        )

        assert passed is True
        assert error is None

    def test_verify_return_code_invalid_expected(self, test_executor):
        """测试return_code无效期望值"""
        passed, error = test_executor._verify_output(
            return_code=0,
            output="",
            check="return_code",
            expected="abc",
        )

        assert passed is False
        assert "格式错误" in error


class TestReportStep:
    """测试报告步骤生成"""

    def test_step_has_required_fields(
        self, test_executor, sample_device, sample_phase, mock_device_manager
    ):
        """测试步骤包含必需字段"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        step = test_executor.execute_phase(
            device=sample_device,
            phase=sample_phase,
            phase_name="verify",
            scenario_name="测试场景",
            timeout=30,
            is_remote=True,
        )

        assert hasattr(step, "scenario_name")
        assert hasattr(step, "phase")
        assert hasattr(step, "command")
        assert hasattr(step, "output")
        assert hasattr(step, "return_code")
        assert hasattr(step, "result")
        assert hasattr(step, "duration")
        assert hasattr(step, "check")
        assert hasattr(step, "expected")

    def test_step_duration_positive(
        self, test_executor, sample_device, sample_phase, mock_device_manager
    ):
        """测试步骤耗时为正数"""
        mock_device_manager.execute_command.return_value = (0, "hello", "")

        step = test_executor.execute_phase(
            device=sample_device,
            phase=sample_phase,
            phase_name="verify",
            scenario_name="测试场景",
            timeout=30,
            is_remote=True,
        )

        assert step.duration >= 0
