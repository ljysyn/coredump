"""
YAML配置文件解析器

解析设备、测试用例和任务的YAML配置文件
"""
import os
from pathlib import Path
from typing import Dict, List

import yaml

from ..models import Device, Task, TestCase


class YAMLParser:
    """YAML配置文件解析器"""
    
    @staticmethod
    def parse_devices(config_path: str) -> List[Device]:
        """
        解析设备配置文件
        
        Args:
            config_path: YAML配置文件路径
        
        Returns:
            设备对象列表
        """
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data or "devices" not in data:
            raise ValueError(f"配置文件格式错误: {config_path}")
        
        devices = []
        for device_data in data["devices"]:
            device = Device.from_dict(device_data)
            devices.append(device)
        
        return devices
    
    @staticmethod
    def parse_testcases(config_path: str) -> List[TestCase]:
        """
        解析测试用例配置文件
        
        Args:
            config_path: YAML配置文件路径
        
        Returns:
            测试用例对象列表
        """
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data or "testcases" not in data:
            raise ValueError(f"配置文件格式错误: {config_path}")
        
        testcases = []
        for testcase_data in data["testcases"]:
            testcase = TestCase.from_dict(testcase_data)
            testcases.append(testcase)
        
        return testcases
    
    @staticmethod
    def parse_tasks(config_path: str) -> List[Task]:
        """
        解析任务配置文件
        
        Args:
            config_path: YAML配置文件路径
        
        Returns:
            任务对象列表
        """
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data or "tasks" not in data:
            raise ValueError(f"配置文件格式错误: {config_path}")
        
        tasks = []
        for task_data in data["tasks"]:
            task = Task.from_dict(task_data)
            tasks.append(task)
        
        return tasks
    
    @staticmethod
    def load_all_devices(directory: str) -> Dict[str, Device]:
        """
        加载目录下所有设备配置文件
        
        Args:
            directory: 配置文件目录
        
        Returns:
            设备ID到设备对象的映射
        """
        devices = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return devices
        
        for yaml_file in dir_path.glob("*.yaml"):
            file_devices = YAMLParser.parse_devices(str(yaml_file))
            for device in file_devices:
                if device.id in devices:
                    raise ValueError(f"设备ID重复: {device.id}")
                devices[device.id] = device
        
        return devices
    
    @staticmethod
    def load_all_testcases(directory: str) -> Dict[str, TestCase]:
        """
        加载目录下所有测试用例配置文件
        
        Args:
            directory: 配置文件目录
        
        Returns:
            测试用例ID到测试用例对象的映射
        """
        testcases = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return testcases
        
        for yaml_file in dir_path.glob("*.yaml"):
            file_testcases = YAMLParser.parse_testcases(str(yaml_file))
            for testcase in file_testcases:
                if testcase.id in testcases:
                    raise ValueError(f"测试用例ID重复: {testcase.id}")
                testcases[testcase.id] = testcase
        
        return testcases
    
    @staticmethod
    def load_all_tasks(directory: str) -> Dict[str, Task]:
        """
        加载目录下所有任务配置文件
        
        Args:
            directory: 配置文件目录
        
        Returns:
            任务ID到任务对象的映射
        """
        tasks = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return tasks
        
        for yaml_file in dir_path.glob("*.yaml"):
            file_tasks = YAMLParser.parse_tasks(str(yaml_file))
            for task in file_tasks:
                if task.id in tasks:
                    raise ValueError(f"任务ID重复: {task.id}")
                tasks[task.id] = task
        
        return tasks