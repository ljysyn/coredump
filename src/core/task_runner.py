"""
任务运行器模块

管理测试任务的执行流程
"""
from datetime import datetime
from typing import Dict, List, Optional

from ..config import get_path_manager, get_settings
from ..models import Device, Report, ReportStep, Task, TestCase
from ..parsers import YAMLParser
from ..utils import TimeUtils
from .device_manager import DeviceManager
from .report_generator import ReportGenerator
from .test_executor import TestExecutor


class TaskRunner:
    """
    任务运行器
    
    负责任务调度、进度跟踪和设备顺序执行
    """
    
    def __init__(self):
        """初始化任务运行器"""
        self.settings = get_settings()
        self.path_manager = get_path_manager()
        self.device_manager = DeviceManager()
        self.test_executor = TestExecutor(self.device_manager)
        self.report_generator = ReportGenerator()
        
        # 加载配置
        self.devices: Dict[str, Device] = {}
        self.testcases: Dict[str, TestCase] = {}
        self.tasks: Dict[str, Task] = {}
        
        self._load_configs()
    
    def _load_configs(self) -> None:
        """加载所有配置文件"""
        self.devices = YAMLParser.load_all_devices(
            str(self.path_manager.get_devices_dir())
        )
        self.testcases = YAMLParser.load_all_testcases(
            str(self.path_manager.get_testcases_dir())
        )
        self.tasks = YAMLParser.load_all_tasks(
            str(self.path_manager.get_tasks_dir())
        )
    
    def run_task(self, task_id: str) -> Dict:
        """
        执行测试任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            执行结果字典
        """
        # 验证任务是否存在
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")
        
        task = self.tasks[task_id]
        
        # 验证设备和测试用例是否存在
        self._validate_task(task)
        
        # 检查设备是否正忙
        busy_devices = self._check_busy_devices(task.devices)
        if busy_devices:
            raise RuntimeError(
                f"设备正忙: {', '.join(busy_devices)}，请等待当前任务完成"
            )
        
        # 执行任务
        results = {
            "task_id": task_id,
            "task_name": task.name,
            "devices": {},
            "start_time": datetime.now().isoformat(),
        }
        
        start_timestamp = TimeUtils.get_current_timestamp()
        
        for device_id in task.devices:
            device_result = self._execute_for_device(
                device_id=device_id,
                task=task,
            )
            results["devices"][device_id] = device_result
        
        end_timestamp = TimeUtils.get_current_timestamp()
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = TimeUtils.calculate_duration(start_timestamp, end_timestamp)
        
        return results
    
    def _validate_task(self, task: Task) -> None:
        """
        验证任务配置
        
        Args:
            task: 任务对象
        """
        # 验证设备ID
        for device_id in task.devices:
            if device_id not in self.devices:
                raise ValueError(f"设备不存在: {device_id}")
        
        # 验证测试用例ID
        for testcase_id in task.testcases:
            if testcase_id not in self.testcases:
                raise ValueError(f"测试用例不存在: {testcase_id}")
    
    def _check_busy_devices(self, device_ids: List[str]) -> List[str]:
        """
        检查哪些设备正忙
        
        Args:
            device_ids: 设备ID列表
        
        Returns:
            正忙的设备ID列表
        """
        busy = []
        for device_id in device_ids:
            if self.device_manager.is_busy(device_id):
                busy.append(device_id)
        return busy
    
    def _execute_for_device(self, device_id: str, task: Task) -> Dict:
        """
        对单个设备执行测试任务
        
        Args:
            device_id: 设备ID
            task: 任务对象
        
        Returns:
            设备执行结果
        """
        from datetime import datetime
        
        device = self.devices[device_id]
        all_steps: List[ReportStep] = []
        
        result = {
            "device_id": device_id,
            "device_name": device.name,
            "status": "running",
        }
        
        try:
            # 连接设备
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [INFO]    正在连接设备: {device_id} ({device.ip})")
            
            self.device_manager.connect(device)
            
            # 执行测试用例
            for testcase_id in task.testcases:
                testcase = self.testcases[testcase_id]
                
                # 输出测试用例开始信息
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [INFO]    执行测试用例: {testcase_id} - {testcase.name}")
                
                passed, steps = self.test_executor.execute_testcase(
                    device=device,
                    testcase=testcase,
                )
                
                all_steps.extend(steps)
                
                # 如果测试用例失败且配置为停止
                if not passed and task.on_testcase_failure == "stop":
                    result["status"] = "failed"
                    result["stopped_at"] = testcase_id
                    break
            
            # 生成报告
            overall_result = "pass" if all(s.result == "pass" for s in all_steps) else "fail"
            
            report = Report(
                task_name=task.name,
                device_id=device_id,
                timestamp=datetime.now(),
                duration=sum(step.duration for step in all_steps),
                overall_result=overall_result,
                steps=all_steps,
            )
            
            report_path = self.report_generator.generate_report(
                report=report,
                format=task.report_format,
            )
            
            # 输出报告生成信息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [INFO]    生成测试报告: {report_path}")
            
            result["status"] = overall_result
            result["report_path"] = report_path
        
        except ConnectionError as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [ERROR]   设备连接失败: {str(e)}")
            result["status"] = "failed"
            result["error"] = f"设备连接失败: {str(e)}"
        
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [ERROR]   执行失败: {str(e)}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            # 断开设备连接
            self.device_manager.disconnect(device_id)
        
        return result
    
    def get_task_list(self) -> List[Dict]:
        """
        获取任务列表
        
        Returns:
            任务信息列表
        """
        task_list = []
        for task_id, task in self.tasks.items():
            task_list.append({
                "id": task.id,
                "name": task.name,
                "devices": len(task.devices),
                "testcases": len(task.testcases),
                "report_format": task.report_format,
                "status": "pending",
            })
        return task_list
    
    def get_device_list(self) -> List[Dict]:
        """
        获取设备列表
        
        Returns:
            设备信息列表
        """
        device_list = []
        for device_id, device in self.devices.items():
            device_list.append({
                "id": device.id,
                "name": device.name,
                "ip": device.ip,
                "port": device.port,
                "username": device.username,
            })
        return device_list
    
    def get_testcase_list(self) -> List[Dict]:
        """
        获取测试用例列表
        
        Returns:
            测试用例信息列表
        """
        testcase_list = []
        for testcase_id, testcase in self.testcases.items():
            testcase_list.append({
                "id": testcase.id,
                "name": testcase.name,
                "scenarios": len(testcase.scenarios),
                "timeout": testcase.timeout,
                "on_failure": testcase.on_failure,
            })
        return testcase_list