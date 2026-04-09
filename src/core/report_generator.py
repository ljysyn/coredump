"""
报告生成器模块

生成JSON和HTML格式的测试报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Template

from ..config import get_path_manager, get_settings
from ..models import Report


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.settings = get_settings()
        self.path_manager = get_path_manager()

    def generate_report(
        self,
        report: Report,
        format: str = "json",
    ) -> str:
        """
        生成测试报告

        Args:
            report: 报告对象
            format: 报告格式（json或html）

        Returns:
            报告文件路径
        """
        if format == "json":
            return self._generate_json_report(report)
        elif format == "html":
            return self._generate_html_report(report)
        else:
            raise ValueError(f"不支持的报告格式: {format}")

    def _generate_json_report(self, report: Report) -> str:
        """
        生成JSON格式报告

        Args:
            report: 报告对象

        Returns:
            报告文件路径
        """
        # 构建报告数据
        report_data = {
            "meta": {
                "task_name": report.task_name,
                "device_id": report.device_id,
                "timestamp": report.timestamp.isoformat(),
                "duration_seconds": report.duration,
                "overall_result": report.overall_result,
            },
            "summary": self._generate_summary(report),
            "steps": [step.to_dict() for step in report.steps],
        }

        # 生成文件名
        filename = self._generate_filename(report, "json")
        report_path = self.path_manager.get_reports_dir() / filename

        # 写入文件
        content = json.dumps(report_data, ensure_ascii=False, indent=2)
        self._write_file(report_path, content)

        return str(report_path)

    def _generate_html_report(self, report: Report) -> str:
        """
        生成HTML格式报告

        Args:
            report: 报告对象

        Returns:
            报告文件路径
        """
        # HTML模板
        template_str = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {{ task_name }} - {{ device_id }}</title>
    <style>
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .step {
            background-color: #fff;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .pass {
            color: #28a745;
            font-weight: bold;
        }
        .fail {
            color: #dc3545;
            font-weight: bold;
        }
        .command {
            font-family: "Courier New", monospace;
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .output {
            font-family: "Courier New", monospace;
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>测试报告</h1>
        <p><strong>任务名称:</strong> {{ task_name }}</p>
        <p><strong>设备ID:</strong> {{ device_id }}</p>
        <p><strong>执行时间:</strong> {{ timestamp }}</p>
        <p><strong>执行耗时:</strong> {{ "%.2f"|format(duration) }}秒</p>
        <p><strong>整体结果:</strong> <span class="{{ overall_result }}">{{ "通过" if overall_result == "pass" else "失败" }}</span></p>
    </div>
    
    <div class="summary">
        <h2>执行摘要</h2>
        <p><strong>总步骤数:</strong> {{ steps|length }}</p>
        <p><strong>通过步骤:</strong> {{ steps|selectattr("result", "equalto", "pass")|list|length }}</p>
        <p><strong>失败步骤:</strong> {{ steps|selectattr("result", "equalto", "fail")|list|length }}</p>
    </div>
    
    <div class="steps">
        <h2>执行详情</h2>
        {% for step in steps %}
        <div class="step">
            <p><strong>场景:</strong> {{ step.scenario_name }}</p>
            <p><strong>阶段:</strong> {{ step.phase }}</p>
            <p><strong>命令:</strong></p>
            <div class="command">{{ step.command }}</div>
            <p><strong>输出:</strong></p>
            <div class="output">{{ step.output }}</div>
            <p><strong>返回值:</strong> {{ step.return_code }}</p>
            <p><strong>结果:</strong> <span class="{{ step.result }}">{{ "通过" if step.result == "pass" else "失败" }}</span></p>
            <p><strong>耗时:</strong> {{ "%.2f"|format(step.duration) }}秒</p>
            {% if step.check %}
            <p><strong>检查类型:</strong> {{ step.check }}</p>
            {% endif %}
            {% if step.expected %}
            <p><strong>期望值:</strong> {{ step.expected }}</p>
            {% endif %}
            {% if step.error_message %}
            <p><strong>错误信息:</strong> <span class="fail">{{ step.error_message }}</span></p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>"""

        template = Template(template_str)
        html_content = template.render(
            task_name=report.task_name,
            device_id=report.device_id,
            timestamp=report.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            duration=report.duration,
            overall_result=report.overall_result,
            steps=report.steps,
        )

        # 生成文件名
        filename = self._generate_filename(report, "html")
        report_path = self.path_manager.get_reports_dir() / filename

        # 写入文件
        self._write_file(report_path, html_content)

        return str(report_path)

    def _generate_summary(self, report: Report) -> Dict:
        """
        生成报告摘要

        Args:
            report: 报告对象

        Returns:
            摘要字典
        """
        total_steps = len(report.steps)
        passed_steps = sum(1 for step in report.steps if step.result == "pass")
        failed_steps = total_steps - passed_steps

        return {
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
        }

    def _generate_filename(self, report: Report, format: str) -> str:
        """
        生成报告文件名

        Args:
            report: 报告对象
            format: 文件格式

        Returns:
            文件名
        """
        timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
        return f"{report.task_name}_{report.device_id}_{timestamp_str}.{format}"

    def _write_file(self, file_path: Path, content: str) -> None:
        """
        写入文件，支持大小限制

        Args:
            file_path: 文件路径
            content: 文件内容
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 检查文件大小
        content_bytes = content.encode("utf-8")
        max_size_bytes = self.settings.report_max_size * 1024 * 1024

        if len(content_bytes) > max_size_bytes:
            # 截断内容
            content_bytes = content_bytes[:max_size_bytes]
            content = content_bytes.decode("utf-8", errors="ignore")

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
