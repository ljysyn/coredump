"""
测试用例实体模块

定义测试用例的数据结构
"""
from dataclasses import dataclass
from typing import List, Optional

from .scenario import TestScenario


@dataclass
class TestCase:
    """
    测试用例实体
    
    定义具体测试内容和流程的配置单元
    
    Attributes:
        id: 测试用例唯一标识符
        name: 测试用例名称
        scenarios: 测试场景列表
        timeout: 命令执行超时时间（秒）
        on_failure: 失败后行为（continue或stop）
    """
    
    id: str
    name: str
    scenarios: List[TestScenario]
    timeout: int = 30
    on_failure: str = "stop"
    
    def __post_init__(self):
        """验证字段有效性"""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("测试用例ID必须是非空字符串")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("测试用例名称必须是非空字符串")
        if not self.scenarios or not isinstance(self.scenarios, list):
            raise ValueError("测试场景列表必须是非空列表")
        if not isinstance(self.timeout, int) or not (1 <= self.timeout <= 3600):
            raise ValueError("超时时间必须是1-3600之间的整数")
        if self.on_failure not in ["continue", "stop"]:
            raise ValueError(f"失败行为无效: {self.on_failure}")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "timeout": self.timeout,
            "on_failure": self.on_failure,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TestCase":
        """从字典创建TestCase实例"""
        scenarios = [TestScenario.from_dict(s) for s in data["scenarios"]]
        return cls(
            id=data["id"],
            name=data["name"],
            scenarios=scenarios,
            timeout=data.get("timeout", 30),
            on_failure=data.get("on_failure", "stop"),
        )