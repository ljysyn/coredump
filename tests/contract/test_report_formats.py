"""
报告格式契约测试

验证报告格式符合契约规范
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.core.report_generator import ReportGenerator
from src.models import Report, ReportStep


@pytest.fixture
def sample_report():
    """示例报告"""
    return Report(
        task_name="测试任务",
        device_id="device001",
        timestamp=datetime.now(),
        duration=5.0,
        overall_result="pass",
        steps=[
            ReportStep(
                scenario_name="测试场景",
                phase="verify",
                command="echo test",
                output="test",
                return_code=0,
                result="pass",
                duration=1.0,
                check="output_contains",
                expected="test",
            )
        ],
    )


@pytest.fixture
def report_generator():
    """报告生成器实例"""
    with tempfile.TemporaryDirectory() as tmpdir:
        reports_dir = Path(tmpdir)

        from unittest.mock import MagicMock

        mock_path_manager = MagicMock()
        mock_path_manager.get_reports_dir.return_value = reports_dir

        mock_settings = MagicMock()
        mock_settings.report_max_size = 100

        with pytest.mock.patch(
            "src.core.report_generator.get_path_manager", return_value=mock_path_manager
        ):
            with pytest.mock.patch(
                "src.core.report_generator.get_settings", return_value=mock_settings
            ):
                yield ReportGenerator()


class TestReportFormatContract:
    """报告格式契约测试"""

    def test_json_report_structure(self, sample_report):
        """测试JSON报告结构"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)

            from unittest.mock import MagicMock, patch

            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = reports_dir

            mock_settings = MagicMock()
            mock_settings.report_max_size = 100

            with patch(
                "src.core.report_generator.get_path_manager",
                return_value=mock_path_manager,
            ):
                with patch(
                    "src.core.report_generator.get_settings", return_value=mock_settings
                ):
                    generator = ReportGenerator()
                    report_path = generator.generate_report(
                        sample_report, format="json"
                    )

                    with open(report_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    assert "meta" in data
                    assert "summary" in data
                    assert "steps" in data

    def test_json_report_meta_fields(self, sample_report):
        """测试JSON报告元数据字段"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)

            from unittest.mock import MagicMock, patch

            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = reports_dir

            mock_settings = MagicMock()
            mock_settings.report_max_size = 100

            with patch(
                "src.core.report_generator.get_path_manager",
                return_value=mock_path_manager,
            ):
                with patch(
                    "src.core.report_generator.get_settings", return_value=mock_settings
                ):
                    generator = ReportGenerator()
                    report_path = generator.generate_report(
                        sample_report, format="json"
                    )

                    with open(report_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    assert "task_name" in data["meta"]
                    assert "device_id" in data["meta"]
                    assert "timestamp" in data["meta"]
                    assert "duration_seconds" in data["meta"]
                    assert "overall_result" in data["meta"]

    def test_json_report_step_fields(self, sample_report):
        """测试JSON报告步骤字段"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)

            from unittest.mock import MagicMock, patch

            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = reports_dir

            mock_settings = MagicMock()
            mock_settings.report_max_size = 100

            with patch(
                "src.core.report_generator.get_path_manager",
                return_value=mock_path_manager,
            ):
                with patch(
                    "src.core.report_generator.get_settings", return_value=mock_settings
                ):
                    generator = ReportGenerator()
                    report_path = generator.generate_report(
                        sample_report, format="json"
                    )

                    with open(report_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    step = data["steps"][0]
                    assert "scenario_name" in step
                    assert "phase" in step
                    assert "command" in step
                    assert "output" in step
                    assert "return_code" in step
                    assert "result" in step
                    assert "duration" in step

    def test_html_report_structure(self, sample_report):
        """测试HTML报告结构"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)

            from unittest.mock import MagicMock, patch

            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = reports_dir

            mock_settings = MagicMock()
            mock_settings.report_max_size = 100

            with patch(
                "src.core.report_generator.get_path_manager",
                return_value=mock_path_manager,
            ):
                with patch(
                    "src.core.report_generator.get_settings", return_value=mock_settings
                ):
                    generator = ReportGenerator()
                    report_path = generator.generate_report(
                        sample_report, format="html"
                    )

                    with open(report_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    assert "<!DOCTYPE html>" in content
                    assert "<html" in content
                    assert "zh-CN" in content

    def test_report_filename_format(self, sample_report):
        """测试报告文件名格式"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)

            from unittest.mock import MagicMock, patch

            mock_path_manager = MagicMock()
            mock_path_manager.get_reports_dir.return_value = reports_dir

            mock_settings = MagicMock()
            mock_settings.report_max_size = 100

            with patch(
                "src.core.report_generator.get_path_manager",
                return_value=mock_path_manager,
            ):
                with patch(
                    "src.core.report_generator.get_settings", return_value=mock_settings
                ):
                    generator = ReportGenerator()

                    json_path = generator.generate_report(sample_report, format="json")
                    html_path = generator.generate_report(sample_report, format="html")

                    assert json_path.endswith(".json")
                    assert html_path.endswith(".html")
                    assert "测试任务" in json_path
                    assert "device001" in json_path
