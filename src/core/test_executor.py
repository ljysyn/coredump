"""
测试执行器模块

执行测试场景和阶段
"""

import re
from typing import Dict, List, Optional, Tuple

from ..config import get_settings
from ..models import Device, ExecutionPhase, ReportStep, TestCase, TestScenario
from ..utils import TimeUtils
from .device_manager import DeviceManager


class TestExecutor:
    """
    测试执行器

    负责执行测试场景和阶段，验证检查规则
    """

    def __init__(self, device_manager: DeviceManager):
        """
        初始化测试执行器

        Args:
            device_manager: 设备管理器实例
        """
        self.device_manager = device_manager
        self.settings = get_settings()

    def execute_testcase(
        self,
        device: Device,
        testcase: TestCase,
    ) -> Tuple[bool, List[ReportStep]]:
        """
        执行测试用例

        Args:
            device: 待测设备
            testcase: 测试用例

        Returns:
            (是否通过, 步骤报告列表)
        """
        all_steps = []

        for scenario in testcase.scenarios:
            passed, steps = self.execute_scenario(
                device=device,
                scenario=scenario,
                timeout=testcase.timeout,
            )
            all_steps.extend(steps)

            # 如果场景失败且配置为停止，则结束
            if not passed and testcase.on_failure == "stop":
                return False, all_steps

        # 检查是否有失败的步骤
        all_passed = all(step.result == "pass" for step in all_steps)
        return all_passed, all_steps

    def execute_scenario(
        self,
        device: Device,
        scenario: TestScenario,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, List[ReportStep]]:
        """
        执行测试场景

        Args:
            device: 待测设备
            scenario: 测试场景
            timeout: 超时时间

        Returns:
            (是否通过, 步骤报告列表)
        """
        from datetime import datetime

        steps = []
        scenario_passed = True

        # 输出场景开始信息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [INFO]    场景: {scenario.name}")

        try:
            # 执行setup阶段
            if scenario.setup:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [INFO]    阶段: setup")

                for phase in scenario.setup:
                    step = self.execute_phase(
                        device=device,
                        phase=phase,
                        phase_name="setup",
                        scenario_name=scenario.name,
                        timeout=timeout,
                        is_remote=True,
                    )
                    steps.append(step)

                    if step.result == "fail":
                        # setup失败，标记失败，跳过后续阶段（但会执行cleanup）
                        scenario_passed = False
                        break

            # 执行execute阶段
            if scenario_passed and scenario.execute:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [INFO]    阶段: execute")

                for phase in scenario.execute:
                    step = self.execute_phase(
                        device=device,
                        phase=phase,
                        phase_name="execute",
                        scenario_name=scenario.name,
                        timeout=timeout,
                        is_remote=False,
                    )
                    steps.append(step)

                    if step.result == "fail":
                        # execute失败，标记失败，跳过verify（但会执行cleanup）
                        scenario_passed = False
                        break

            # 执行verify阶段（必需，仅在setup和execute成功时执行）
            if scenario_passed:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [INFO]    阶段: verify")

                for phase in scenario.verify:
                    step = self.execute_phase(
                        device=device,
                        phase=phase,
                        phase_name="verify",
                        scenario_name=scenario.name,
                        timeout=timeout,
                        is_remote=True,
                    )
                    steps.append(step)

                    if step.result == "fail":
                        scenario_passed = False

        finally:
            # 始终执行cleanup阶段（无论前面阶段是否失败）
            if scenario.cleanup:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [INFO]    阶段: cleanup")

                for phase in scenario.cleanup:
                    step = self.execute_phase(
                        device=device,
                        phase=phase,
                        phase_name="cleanup",
                        scenario_name=scenario.name,
                        timeout=timeout,
                        is_remote=True,
                    )
                    steps.append(step)

                    # cleanup失败标记整个场景失败
                    if step.result == "fail":
                        scenario_passed = False

        return scenario_passed, steps

    def execute_phase(
        self,
        device: Device,
        phase: ExecutionPhase,
        phase_name: str,
        scenario_name: str,
        timeout: Optional[int] = None,
        is_remote: bool = True,
    ) -> ReportStep:
        """
        执行单个阶段

        Args:
            device: 待测设备
            phase: 执行阶段
            phase_name: 阶段名称
            scenario_name: 场景名称
            timeout: 超时时间
            is_remote: 是否远程执行

        Returns:
            步骤报告
        """
        from datetime import datetime

        start_time = TimeUtils.get_current_timestamp()

        try:
            # 执行命令
            if is_remote:
                # 远程执行（SSH）
                return_code, output, error = self.device_manager.execute_command(
                    device_id=device.id,
                    command=phase.command,
                    timeout=timeout or self.settings.default_timeout,
                )
            else:
                # 本地执行
                return_code, output, error = self._execute_local(
                    command=phase.command,
                    timeout=timeout,
                )

            # 合并输出
            full_output = output + error

            # 判断执行结果
            result = "pass"
            error_message = None

            # 检查规则（如果有）
            if phase.check and phase.check != "none":
                # 有检查规则，按检查规则判断
                passed, check_error = self._verify_output(
                    return_code=return_code,
                    output=full_output,
                    check=phase.check,
                    expected=phase.expected,
                )

                if not passed:
                    result = "fail"
                    error_message = check_error
            else:
                # 没有检查规则，根据返回值判断
                if return_code != 0:
                    result = "fail"
                    error_message = f"命令执行失败，返回值: {return_code}"

            # 输出命令执行结果
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_text = "通过" if result == "pass" else "失败"
            log_level = "[INFO]   " if result == "pass" else "[WARNING]"
            print(
                f"[{timestamp}] {log_level} 执行命令[{result_text}]: {phase.command}",
                flush=True,
            )

            # 输出检查规则结果（如果有）
            if phase.check and phase.check != "none":
                check_passed = (result == "pass")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                check_result_text = "通过" if check_passed else "失败"
                check_log_level = "[INFO]   " if check_passed else "[WARNING]"
                check_desc = self._get_check_description(phase.check, phase.expected)
                print(
                    f"[{timestamp}] {check_log_level} 检查规则[{check_result_text}]: {check_desc}",
                    flush=True,
                )

            duration = TimeUtils.calculate_duration(
                start_time, TimeUtils.get_current_timestamp()
            )

            return ReportStep(
                scenario_name=scenario_name,
                phase=phase_name,
                command=phase.command,
                output=full_output,
                return_code=return_code,
                result=result,
                duration=duration,
                check=phase.check,
                expected=phase.expected,
                error_message=error_message,
            )

        except Exception as e:
            duration = TimeUtils.calculate_duration(
                start_time, TimeUtils.get_current_timestamp()
            )

            return ReportStep(
                scenario_name=scenario_name,
                phase=phase_name,
                command=phase.command,
                output="",
                return_code=-1,
                result="fail",
                duration=duration,
                check=phase.check,
                expected=phase.expected,
                error_message=str(e),
            )

    def _execute_local(
        self,
        command: str,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """
        在本地执行命令

        Args:
            command: 命令
            timeout: 超时时间

        Returns:
            (返回码, 标准输出, 标准错误)
        """
        import subprocess

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout or self.settings.default_timeout,
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"命令执行超时: {command}")
        except Exception as e:
            raise RuntimeError(f"命令执行失败: {e}")

    def _get_check_description(self, check: str, expected: str) -> str:
        """
        获取检查规则的描述

        Args:
            check: 检查类型
            expected: 期望值

        Returns:
            检查规则描述
        """
        if check == "output_contains":
            return f"输出包含 '{expected}'"
        elif check == "return_code":
            return f"返回码等于 {expected}"
        elif check == "regex":
            return f"匹配正则表达式 '{expected}'"
        elif check == "none":
            return "不检查"
        return f"{check} {expected}"

    def _verify_output(
        self,
        return_code: int,
        output: str,
        check: str,
        expected: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        验证输出结果

        Args:
            return_code: 命令返回码
            output: 命令输出
            check: 检查类型
            expected: 期望值

        Returns:
            (是否通过, 错误信息)
        """
        if check == "output_contains":
            if expected in output:
                return True, None
            return False, f"输出未包含期望值: {expected}"

        elif check == "return_code":
            try:
                expected_code = int(expected)
                if return_code == expected_code:
                    return True, None
                return False, f"返回码不匹配: 期望 {expected_code}, 实际 {return_code}"
            except ValueError:
                return False, f"期望返回码格式错误: {expected}"

        elif check == "regex":
            try:
                if re.search(expected, output):
                    return True, None
                return False, f"输出未匹配正则表达式: {expected}"
            except re.error as e:
                return False, f"正则表达式错误: {e}"

        elif check == "none":
            # 不检查，默认通过
            return True, None

        return True, None
