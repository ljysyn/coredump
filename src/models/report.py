"""
测试报告实体模块

定义测试报告的数据结构
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ReportStep:
    """
    测试步骤实体
    
    记录单个测试步骤的执行详情
    
    Attributes:
        scenario_name: 测试场景名称
        phase: 执行阶段（setup、execute、verify、cleanup）
        command: 执行的命令
        output: 命令输出
        return_code: 命令返回值
        result: 步骤结果（pass或fail）
        duration: 步骤执行时间（秒）
        check: 检查规则类型（可选）
        expected: 检查规则值（可选）
        error_message: 失败时的错误信息（可选）
    """
    
    scenario_name: str
    phase: str
    command: str
    output: str
    return_code: int
    result: str
    duration: float
    check: Optional[str] = None
    expected: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """验证字段有效性"""
        if self.phase not in ["setup", "execute", "verify", "cleanup"]:
            raise ValueError(f"执行阶段无效: {self.phase}")
        if self.result not in ["pass", "fail"]:
            raise ValueError(f"步骤结果无效: {self.result}")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {
            "scenario_name": self.scenario_name,
            "phase": self.phase,
            "command": self.command,
            "output": self.output,
            "return_code": self.return_code,
            "result": self.result,
            "duration": self.duration,
        }
        if self.check:
            result["check"] = self.check
        if self.expected:
            result["expected"] = self.expected
        if self.error_message:
            result["error_message"] = self.error_message
        return result


@dataclass
class Report:
    """
    测试报告实体
    
    记录测试执行结果的文件
    
    Attributes:
        task_name: 测试任务名称
        device_id: 待测设备ID
        timestamp: 执行时间戳
        duration: 执行总时间（秒）
        overall_result: 整体测试结果（pass或fail）
        steps: 测试步骤详情列表
    """
    
    task_name: str
    device_id: str
    timestamp: datetime
    duration: float
    overall_result: str
    steps: List[ReportStep]
    
    def __post_init__(self):
        """验证字段有效性"""
        if self.overall_result not in ["pass", "fail"]:
            raise ValueError(f"整体结果无效: {self.overall_result}")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "meta": {
                "task_name": self.task_name,
                "device_id": self.device_id,
                "timestamp": self.timestamp.isoformat(),
                "duration_seconds": self.duration,
                "overall_result": self.overall_result,
            },
            "steps": [step.to_dict() for step in self.steps],
        }