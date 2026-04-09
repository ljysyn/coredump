"""
ReportGenerator单元测试

测试JSON和HTML格式报告生成及文件大小控制
"""
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.report_generator import ReportGenerator
from src.models import Report, ReportStep


@pytest.fixture
def sample_report_step():
    """示例报告步骤"""
    return ReportStep(
        scenario_name="测试场景",
        phase="verify",
        command="echo test",
        output="test",
        return_code=0,
        result="pass",
        duration=1.0,
        check="output_contains",
        expected="test",
        error_message=None,
    )


@pytest.fixture
def sample_report(sample_report_step):
    """示例报告"""
    return Report(
        task_name="测试任务",
        device_id="device001",
        timestamp=datetime.now(),
        duration=5.0,
        overall_result="pass",
        steps=[sample_report_step],
    )


@pytest.fixture
def mock_path_manager():
    """Mock路径管理器"""
    manager = MagicMock()
    manager.get_reports_dir.return_value = Path("/tmp/reports")
    return manager


@pytest.fixture
def mock_settings():
    """Mock配置"""
    settings = MagicMock()
    settings.report_max_size = 100
    return settings


@pytest.fixture
def report_generator(mock_path_manager, mock_settings):
    """报告生成器实例"""
    with patch("src.core.report_generator.get_path_manager", return_value=mock_path_manager):
        with patch("src.core.report_generator.get_settings", return_value=mock_settings):
            generator = ReportGenerator()
            generator.path_manager = mock_path_manager
            generator.settings = mock_settings
            return generator


class TestGenerateReport:
    """测试报告生成"""

    def test_generate_json_report(self, report_generator, sample_report):
        """测试生成JSON报告"""
        report_path = report_generator.generate_report(sample_report, format="json")

        assert report_path.endswith(".json")
        assert "测试任务" in report_path
        assert "device001" in report_path

    def test_generate_html_report(self, report_generator, sample_report):
        """测试生成HTML报告"""
        report_path = report_generator.generate_report(sample_report, format="html")

        assert report_path.endswith(".html")
        assert "测试任务" in report_path
        assert "device001" in report_path

    def test_generate_invalid_format(self, report_generator, sample_report):
        """测试无效格式"""
        with pytest.raises(ValueError, match="不支持的报告格式"):
            report_generator.generate_report(sample_report, format="pdf")


class TestGenerateJSONReport:
    """测试JSON报告生成"""

    def test_json_structure(self, report_generator, sample_report):
        """测试JSON结构"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(sample_report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert "meta" in report_data
            assert "summary" in report_data
            assert "steps" in report_data

    def test_json_meta_fields(self, report_generator, sample_report):
        """测试JSON元数据字段"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(sample_report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert report_data["meta"]["task_name"] == "测试任务"
            assert report_data["meta"]["device_id"] == "device001"
            assert report_data["meta"]["overall_result"] == "pass"

    def test_json_summary_fields(self, report_generator, sample_report):
        """测试JSON摘要字段"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(sample_report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert "total_steps" in report_data["summary"]
            assert "passed_steps" in report_data["summary"]
            assert "failed_steps" in report_data["summary"]

    def test_json_steps_array(self, report_generator, sample_report):
        """测试JSON步骤数组"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(sample_report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert isinstance(report_data["steps"], list)
            assert len(report_data["steps"]) == 1

    def test_json_chinese_encoding(self, report_generator, sample_report):
        """测试中文编码"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(sample_report)

            mock_open.assert_called_with(mock_open.call_args[0][0], "w", encoding="utf-8")


class TestGenerateHTMLReport:
    """测试HTML报告生成"""

    def test_html_structure(self, report_generator, sample_report):
        """测试HTML结构"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_html_report(sample_report)

            written_content = mock_file.write.call_args[0][0]

            assert "<!DOCTYPE html>" in written_content
            assert "<html" in written_content
            assert "zh-CN" in written_content

    def test_html_title(self, report_generator, sample_report):
        """测试HTML标题"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_html_report(sample_report)

            written_content = mock_file.write.call_args[0][0]

            assert "<title>测试报告" in written_content
            assert "测试任务" in written_content
            assert "device001" in written_content

    def test_html_pass_result_display(self, report_generator, sample_report):
        """测试通过结果显示"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_html_report(sample_report)

            written_content = mock_file.write.call_args[0][0]

            assert "通过" in written_content
            assert "pass" in written_content

    def test_html_fail_result_display(self, report_generator, sample_report):
        """测试失败结果显示"""
        sample_report.overall_result = "fail"

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_html_report(sample_report)

            written_content = mock_file.write.call_args[0][0]

            assert "失败" in written_content
            assert "fail" in written_content

    def test_html_step_details(self, report_generator, sample_report):
        """测试步骤详情显示"""
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_html_report(sample_report)

            written_content = mock_file.write.call_args[0][0]

            assert "执行详情" in written_content
            assert sample_report.steps[0].command in written_content
            assert sample_report.steps[0].output in written_content


class TestGenerateSummary:
    """测试摘要生成"""

    def test_summary_calculation(self, report_generator, sample_report):
        """测试摘要计算"""
        summary = report_generator._generate_summary(sample_report)

        assert summary["total_steps"] == 1
        assert summary["passed_steps"] == 1
        assert summary["failed_steps"] == 0

    def test_summary_with_failed_steps(self, report_generator, sample_report):
        """测试包含失败步骤的摘要"""
        failed_step = ReportStep(
            scenario_name="失败场景",
            phase="verify",
            command="false",
            output="",
            return_code=1,
            result="fail",
            duration=0.5,
        )
        sample_report.steps.append(failed_step)

        summary = report_generator._generate_summary(sample_report)

        assert summary["total_steps"] == 2
        assert summary["passed_steps"] == 1
        assert summary["failed_steps"] == 1


class TestGenerateFilename:
    """测试文件名生成"""

    def test_filename_format(self, report_generator, sample_report):
        """测试文件名格式"""
        filename = report_generator._generate_filename(sample_report, "json")

        assert filename.endswith(".json")
        assert "测试任务" in filename
        assert "device001" in filename
        assert datetime.now().strftime("%Y%m%d") in filename

    def test_filename_json_extension(self, report_generator, sample_report):
        """测试JSON扩展名"""
        filename = report_generator._generate_filename(sample_report, "json")

        assert filename.endswith(".json")

    def test_filename_html_extension(self, report_generator, sample_report):
        """测试HTML扩展名"""
        filename = report_generator._generate_filename(sample_report, "html")

        assert filename.endswith(".html")


class TestWriteFile:
    """测试文件写入"""

    def test_write_file_success(self, report_generator):
        """测试成功写入文件"""
        file_path = Path("/tmp/test.json")
        content = '{"test": "data"}'

        with patch.object(Path, "mkdir"):
            with patch("builtins.open", create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                report_generator._write_file(file_path, content)

                mock_file.write.assert_called_with(content)

    def test_write_file_size_limit(self, report_generator, mock_settings):
        """测试文件大小限制"""
        mock_settings.report_max_size = 1

        large_content = "x" * (2 * 1024 * 1024)
        file_path = Path("/tmp/test.json")

        with patch.object(Path, "mkdir"):
            with patch("builtins.open", create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                report_generator._write_file(file_path, large_content)

                written_content = mock_file.write.call_args[0][0]
                assert len(written_content.encode("utf-8")) <= 1 * 1024 * 1024

    def test_write_file_creates_directory(self, report_generator):
        """测试创建目录"""
        file_path = Path("/tmp/new_dir/test.json")

        with patch.object(Path, "mkdir") as mock_mkdir:
            with patch("builtins.open", create=True):
                report_generator._write_file(file_path, "content")

                mock_mkdir.assert_called_with(parents=True, exist_ok=True)


class TestReportWithMultipleSteps:
    """测试多步骤报告"""

    def test_report_with_multiple_steps(self, report_generator):
        """测试包含多个步骤的报告"""
        steps = [
            ReportStep(
                scenario_name="场景1",
                phase="setup",
                command="mkdir /tmp/test",
                output="",
                return_code=0,
                result="pass",
                duration=0.5,
            ),
            ReportStep(
                scenario_name="场景1",
                phase="verify",
                command="ls /tmp/test",
                output="/tmp/test",
                return_code=0,
                result="pass",
                duration=0.3,
                check="output_contains",
                expected="/tmp/test",
            ),
            ReportStep(
                scenario_name="场景1",
                phase="cleanup",
                command="rm -rf /tmp/test",
                output="",
                return_code=0,
                result="pass",
                duration=0.2,
            ),
        ]

        report = Report(
            task_name="多步骤测试",
            device_id="device001",
            timestamp=datetime.now(),
            duration=sum(step.duration for step in steps),
            overall_result="pass",
            steps=steps,
        )

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert len(report_data["steps"]) == 3
            assert report_data["summary"]["total_steps"] == 3


class TestReportWithFailedSteps:
    """测试失败步骤报告"""

    def test_report_with_failed_steps(self, report_generator):
        """测试包含失败步骤的报告"""
        steps = [
            ReportStep(
                scenario_name="场景1",
                phase="verify",
                command="false",
                output="",
                return_code=1,
                result="fail",
                duration=0.5,
                error_message="命令执行失败",
            ),
        ]

        report = Report(
            task_name="失败测试",
            device_id="device001",
            timestamp=datetime.now(),
            duration=0.5,
            overall_result="fail",
            steps=steps,
        )

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            report_generator._generate_json_report(report)

            written_content = mock_file.write.call_args[0][0]
            report_data = json.loads(written_content)

            assert report_data["meta"]["overall_result"] == "fail"
            assert report_data["summary"]["failed_steps"] == 1
            assert report_data["steps"][0]["error_message"] == "命令执行失败"