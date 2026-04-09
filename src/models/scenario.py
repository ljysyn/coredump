"""
测试场景实体模块

定义测试场景的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExecutionPhase:
    """
    执行阶段实体

    定义一个执行阶段的命令和检查规则

    Attributes:
        command: 执行的命令
        check: 检查类型（output_contains, return_code, regex, none）
        expected: 期望值
    """

    command: str
    check: Optional[str] = None
    expected: Optional[str] = None

    def __post_init__(self):
        """验证字段有效性"""
        if not self.command or not isinstance(self.command, str):
            raise ValueError("命令必须是非空字符串")
        if self.check and self.check not in [
            "output_contains",
            "return_code",
            "regex",
            "none",
        ]:
            raise ValueError(f"检查类型无效: {self.check}")

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {"command": self.command}
        if self.check:
            result["check"] = self.check
        if self.expected:
            result["expected"] = self.expected
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionPhase":
        """从字典创建ExecutionPhase实例"""
        if isinstance(data, str):
            # 字符串格式，转换为只有command的阶段
            return cls(command=data)
        return cls(
            command=data["command"],
            check=data.get("check"),
            expected=data.get("expected"),
        )


@dataclass
class TestScenario:
    """
    测试场景实体

    定义一个测试场景的四个执行阶段

    Attributes:
        name: 场景名称
        setup: 建立阶段命令列表（可选）
        execute: 执行阶段命令列表（可选）
        verify: 校验阶段命令列表（必需）
        cleanup: 清理阶段命令列表（可选）
    """

    name: str
    verify: List[ExecutionPhase]
    setup: Optional[List[ExecutionPhase]] = None
    execute: Optional[List[ExecutionPhase]] = None
    cleanup: Optional[List[ExecutionPhase]] = None

    def __post_init__(self):
        """验证字段有效性"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("场景名称必须是非空字符串")
        if not self.verify or not isinstance(self.verify, list):
            raise ValueError("verify阶段必须是非空列表")

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {"name": self.name}

        if self.setup:
            result["setup"] = {"commands": [phase.command for phase in self.setup]}

        if self.execute:
            result["execute"] = {"commands": [phase.command for phase in self.execute]}

        result["verify"] = [phase.to_dict() for phase in self.verify]

        if self.cleanup:
            result["cleanup"] = {"commands": [phase.command for phase in self.cleanup]}

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "TestScenario":
        """从字典创建TestScenario实例"""
        # 解析setup阶段
        setup = None
        if "setup" in data:
            if isinstance(data["setup"], dict) and "commands" in data["setup"]:
                setup = [
                    ExecutionPhase(command=cmd) for cmd in data["setup"]["commands"]
                ]
            elif isinstance(data["setup"], list):
                setup = [ExecutionPhase.from_dict(phase) for phase in data["setup"]]

        # 解析execute阶段
        execute = None
        if "execute" in data:
            if isinstance(data["execute"], dict) and "commands" in data["execute"]:
                execute = [
                    ExecutionPhase(command=cmd) for cmd in data["execute"]["commands"]
                ]
            elif isinstance(data["execute"], list):
                execute = [ExecutionPhase.from_dict(phase) for phase in data["execute"]]

        # 解析verify阶段（必需）
        verify = [ExecutionPhase.from_dict(phase) for phase in data["verify"]]

        # 解析cleanup阶段
        cleanup = None
        if "cleanup" in data:
            if isinstance(data["cleanup"], dict) and "commands" in data["cleanup"]:
                cleanup = [
                    ExecutionPhase(command=cmd) for cmd in data["cleanup"]["commands"]
                ]
            elif isinstance(data["cleanup"], list):
                cleanup = [ExecutionPhase.from_dict(phase) for phase in data["cleanup"]]

        return cls(
            name=data["name"],
            verify=verify,
            setup=setup,
            execute=execute,
            cleanup=cleanup,
        )
