"""
TaskRunner单元测试

测试任务调度、进度跟踪和设备顺序执行功能
"""

from datetime import datetime
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.core.task_runner import TaskRunner
from src.models import Device, Report, ReportStep, Task, TestCase, TestScenario


@pytest.fixture
def mock_yaml_parser():
    """Mock YAML解析器"""
    with patch("src.core.task_runner.YAMLParser") as mock:
        mock.load_all_devices.return_value = {
            "device001": Device(
                id="device001",
                name="测试设备1",
                ip="192.168.1.100",
                port=22,
                username="root",
                password="password123",
            )
        }
        mock.load_all_testcases.return_value = {
            "tc001": TestCase(
                id="tc001",
                name="测试用例1",
                scenarios=[
                    TestScenario(
                        name="场景1",
                        verify=[
                            MagicMock(
                                command="echo test",
                                check="output_contains",
                                expected="test",
                            )
                        ],
                    )
                ],
                timeout=30,
                on_failure="stop",
            )
        }
        mock.load_all_tasks.return_value = {
            "task001": Task(
                id="task001",
                name="测试任务",
                devices=["device001"],
                testcases=["tc001"],
                on_testcase_failure="stop",
                report_format="json",
            )
        }
        yield mock


@pytest.fixture
def mock_device_manager():
    """Mock设备管理器"""
    manager = MagicMock()
    manager.connect.return_value = True
    manager.execute_command.return_value = (0, "test", "")
    manager.disconnect.return_value = None
    manager.is_busy.return_value = False
    manager.is_connected.return_value = False
    return manager


@pytest.fixture
def mock_test_executor():
    """Mock测试执行器"""
    executor = MagicMock()
    executor.execute_testcase.return_value = (True, [MagicMock(result="pass")])
    return executor


@pytest.fixture
def mock_report_generator():
    """Mock报告生成器"""
    generator = MagicMock()
    generator.generate_report.return_value = "/reports/test_report.json"
    return generator


@pytest.fixture
def task_runner(
    mock_yaml_parser, mock_device_manager, mock_test_executor, mock_report_generator
):
    """任务运行器实例"""
    with patch("src.core.task_runner.DeviceManager", return_value=mock_device_manager):
        with patch(
            "src.core.task_runner.TestExecutor", return_value=mock_test_executor
        ):
            with patch(
                "src.core.task_runner.ReportGenerator",
                return_value=mock_report_generator,
            ):
                runner = TaskRunner()
                runner.device_manager = mock_device_manager
                runner.test_executor = mock_test_executor
                runner.report_generator = mock_report_generator
                return runner


class TestRunTask:
    """测试任务执行"""

    def test_run_task_success(self, task_runner, mock_test_executor):
        """测试成功执行任务"""
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        result = task_runner.run_task("task001")

        assert result["task_id"] == "task001"
        assert "devices" in result
        assert "device001" in result["devices"]
        assert result["devices"]["device001"]["status"] == "pass"

    def test_run_task_not_found(self, task_runner):
        """测试任务不存在"""
        with pytest.raises(ValueError, match="任务不存在"):
            task_runner.run_task("task999")

    def test_run_task_device_not_found(self, task_runner):
        """测试设备不存在"""
        task_runner.tasks["task002"] = Task(
            id="task002",
            name="错误任务",
            devices=["device999"],
            testcases=["tc001"],
            on_testcase_failure="stop",
            report_format="json",
        )

        with pytest.raises(ValueError, match="设备不存在"):
            task_runner.run_task("task002")

    def test_run_task_testcase_not_found(self, task_runner):
        """测试测试用例不存在"""
        task_runner.tasks["task002"] = Task(
            id="task002",
            name="错误任务",
            devices=["device001"],
            testcases=["tc999"],
            on_testcase_failure="stop",
            report_format="json",
        )

        with pytest.raises(ValueError, match="测试用例不存在"):
            task_runner.run_task("task002")

    def test_run_task_device_busy(self, task_runner, mock_device_manager):
        """测试设备正忙"""
        mock_device_manager.is_busy.return_value = True

        with pytest.raises(RuntimeError, match="设备正忙"):
            task_runner.run_task("task001")

    def test_run_task_connection_failure(self, task_runner, mock_device_manager):
        """测试设备连接失败"""
        mock_device_manager.connect.side_effect = ConnectionError("连接失败")

        result = task_runner.run_task("task001")

        assert result["devices"]["device001"]["status"] == "failed"
        assert "连接失败" in result["devices"]["device001"]["error"]

    def test_run_task_testcase_failure_stop(
        self, task_runner, mock_device_manager, mock_test_executor
    ):
        """测试测试用例失败后停止"""
        mock_test_executor.execute_testcase.return_value = (
            False,
            [MagicMock(result="fail", duration=1.0)],
        )

        task_runner.tasks["task001"].testcases = ["tc001", "tc002"]
        task_runner.testcases["tc002"] = TestCase(
            id="tc002",
            name="测试用例2",
            scenarios=[TestScenario(name="场景2", verify=[MagicMock()])],
            timeout=30,
            on_failure="stop",
        )

        result = task_runner.run_task("task001")

        assert result["devices"]["device001"]["status"] == "fail"

    def test_run_task_multiple_devices(self, task_runner, mock_test_executor):
        """测试多设备顺序执行"""
        task_runner.devices["device002"] = Device(
            id="device002",
            name="测试设备2",
            ip="192.168.1.101",
            port=22,
            username="root",
            password="password456",
        )

        task_runner.tasks["task001"].devices = ["device001", "device002"]
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        result = task_runner.run_task("task001")

        assert "device001" in result["devices"]
        assert "device002" in result["devices"]
        assert result["devices"]["device001"]["status"] == "pass"
        assert result["devices"]["device002"]["status"] == "pass"

    def test_sequential_device_execution_order(self, task_runner, mock_device_manager, mock_test_executor):
        """测试设备顺序执行"""
        task_runner.devices["device002"] = Device(
            id="device002",
            name="测试设备2",
            ip="192.168.1.101",
            port=22,
            username="root",
            password="password456",
        )
        task_runner.tasks["task001"].devices = ["device001", "device002"]
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        execution_order = []
        
        def track_disconnect(device_id):
            execution_order.append(device_id)

        mock_device_manager.disconnect.side_effect = track_disconnect

        task_runner.run_task("task001")

        assert execution_order == ["device001", "device002"]

    def test_device_failure_continues_to_next(self, task_runner, mock_device_manager, mock_test_executor):
        """测试设备失败后继续执行下一个设备"""
        task_runner.devices["device002"] = Device(
            id="device002",
            name="测试设备2",
            ip="192.168.1.101",
            port=22,
            username="root",
            password="password456",
        )
        task_runner.tasks["task001"].devices = ["device001", "device002"]

        call_count = [0]
        
        def mock_connect(device):
            call_count[0] += 1
            if device.id == "device001":
                raise ConnectionError("连接失败")
            return True

        mock_device_manager.connect.side_effect = mock_connect
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        result = task_runner.run_task("task001")

        assert result["devices"]["device001"]["status"] == "failed"
        assert result["devices"]["device002"]["status"] == "pass"

    def test_run_task_disconnect_on_completion(
        self, task_runner, mock_device_manager, mock_test_executor
    ):
        """测试完成后断开连接"""
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        task_runner.run_task("task001")

        mock_device_manager.disconnect.assert_called()


class TestValidateTask:
    """测试任务验证"""

    def test_validate_task_success(self, task_runner):
        """测试任务验证成功"""
        task = task_runner.tasks["task001"]

        task_runner._validate_task(task)

    def test_validate_task_missing_device(self, task_runner):
        """测试缺少设备"""
        task = Task(
            id="task002",
            name="错误任务",
            devices=["device999"],
            testcases=["tc001"],
            on_testcase_failure="stop",
            report_format="json",
        )

        with pytest.raises(ValueError, match="设备不存在"):
            task_runner._validate_task(task)

    def test_validate_task_missing_testcase(self, task_runner):
        """测试缺少测试用例"""
        task = Task(
            id="task002",
            name="错误任务",
            devices=["device001"],
            testcases=["tc999"],
            on_testcase_failure="stop",
            report_format="json",
        )

        with pytest.raises(ValueError, match="测试用例不存在"):
            task_runner._validate_task(task)


class TestCheckBusyDevices:
    """测试设备正忙检查"""

    def test_no_busy_devices(self, task_runner, mock_device_manager):
        """测试没有正忙的设备"""
        mock_device_manager.is_busy.return_value = False

        busy = task_runner._check_busy_devices(["device001"])

        assert busy == []

    def test_some_busy_devices(self, task_runner, mock_device_manager):
        """测试部分设备正忙"""
        mock_device_manager.is_busy.side_effect = lambda dev_id: dev_id == "device001"

        busy = task_runner._check_busy_devices(["device001", "device002"])

        assert busy == ["device001"]


class TestExecuteForDevice:
    """测试单设备执行"""

    def test_execute_for_device_success(
        self, task_runner, mock_test_executor, mock_report_generator
    ):
        """测试单设备成功执行"""
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        result = task_runner._execute_for_device(
            "device001", task_runner.tasks["task001"]
        )

        assert result["device_id"] == "device001"
        assert result["status"] == "pass"
        assert "report_path" in result

    def test_execute_for_device_failure(self, task_runner, mock_test_executor):
        """测试单设备执行失败"""
        mock_test_executor.execute_testcase.return_value = (
            False,
            [MagicMock(result="fail", duration=1.0)],
        )

        result = task_runner._execute_for_device(
            "device001", task_runner.tasks["task001"]
        )

        assert result["status"] == "fail"

    def test_execute_for_device_connection_error(
        self, task_runner, mock_device_manager
    ):
        """测试连接错误"""
        mock_device_manager.connect.side_effect = ConnectionError("SSH连接超时")

        result = task_runner._execute_for_device(
            "device001", task_runner.tasks["task001"]
        )

        assert result["status"] == "failed"
        assert "连接失败" in result["error"]


class TestGetTaskList:
    """测试获取任务列表"""

    def test_get_task_list(self, task_runner):
        """测试获取任务列表"""
        task_list = task_runner.get_task_list()

        assert len(task_list) > 0
        assert task_list[0]["id"] == "task001"
        assert task_list[0]["name"] == "测试任务"
        assert "devices" in task_list[0]
        assert "testcases" in task_list[0]


class TestGetDeviceList:
    """测试获取设备列表"""

    def test_get_device_list(self, task_runner):
        """测试获取设备列表"""
        device_list = task_runner.get_device_list()

        assert len(device_list) > 0
        assert device_list[0]["id"] == "device001"
        assert device_list[0]["name"] == "测试设备1"
        assert device_list[0]["ip"] == "192.168.1.100"


class TestGetTestcaseList:
    """测试获取测试用例列表"""

    def test_get_testcase_list(self, task_runner):
        """测试获取测试用例列表"""
        testcase_list = task_runner.get_testcase_list()

        assert len(testcase_list) > 0
        assert testcase_list[0]["id"] == "tc001"
        assert testcase_list[0]["name"] == "测试用例1"
        assert "scenarios" in testcase_list[0]


class TestReportGeneration:
    """测试报告生成"""

    def test_report_generated_after_execution(
        self, task_runner, mock_test_executor, mock_report_generator
    ):
        """测试执行后生成报告"""
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        result = task_runner.run_task("task001")

        mock_report_generator.generate_report.assert_called()
        assert "report_path" in result["devices"]["device001"]

    def test_json_report_format(self, task_runner, mock_report_generator):
        """测试JSON报告格式"""
        task_runner.tasks["task001"].report_format = "json"

        task_runner.run_task("task001")

        call_args = mock_report_generator.generate_report.call_args
        assert call_args[1]["format"] == "json"

    def test_html_report_format(self, task_runner, mock_report_generator):
        """测试HTML报告格式"""
        task_runner.tasks["task001"].report_format = "html"
        mock_test_executor = task_runner.test_executor
        mock_test_executor.execute_testcase.return_value = (
            True,
            [MagicMock(result="pass", duration=1.0)],
        )

        task_runner.run_task("task001")

        call_args = mock_report_generator.generate_report.call_args
        assert call_args[1]["format"] == "html"
