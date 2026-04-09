"""
测试任务实体模块

定义测试任务的数据结构
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    """
    测试任务实体
    
    定义测试执行计划的配置单元
    
    Attributes:
        id: 测试任务唯一标识符
        name: 测试任务名称
        devices: 目标待测设备ID列表
        testcases: 执行的测试用例ID列表
        on_testcase_failure: 测试用例失败时是否结束
        report_format: 测试报告格式（json或html）
    """
    
    id: str
    name: str
    devices: List[str]
    testcases: List[str]
    on_testcase_failure: str = "stop"
    report_format: str = "json"
    
    def __post_init__(self):
        """验证字段有效性"""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("任务ID必须是非空字符串")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("任务名称必须是非空字符串")
        if not self.devices or not isinstance(self.devices, list):
            raise ValueError("设备列表必须是非空列表")
        if not self.testcases or not isinstance(self.testcases, list):
            raise ValueError("测试用例列表必须是非空列表")
        if self.on_testcase_failure not in ["continue", "stop"]:
            raise ValueError(f"失败行为无效: {self.on_testcase_failure}")
        if self.report_format not in ["json", "html"]:
            raise ValueError(f"报告格式无效: {self.report_format}")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "devices": self.devices,
            "testcases": self.testcases,
            "on_testcase_failure": self.on_testcase_failure,
            "report_format": self.report_format,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建Task实例"""
        return cls(
            id=data["id"],
            name=data["name"],
            devices=data["devices"],
            testcases=data["testcases"],
            on_testcase_failure=data.get("on_testcase_failure", "stop"),
            report_format=data.get("report_format", "json"),
        )