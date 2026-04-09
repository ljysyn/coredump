"""
配置验证器

验证配置文件的完整性、格式正确性和引用完整性
"""
from typing import Dict, List

from ..models import Device, Task, TestCase


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_device(device: Device) -> List[str]:
        """
        验证设备配置
        
        Args:
            device: 设备对象
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 验证必需字段
        if not device.id:
            errors.append("设备缺少ID字段")
        if not device.name:
            errors.append("设备缺少名称字段")
        if not device.ip:
            errors.append("设备缺少IP字段")
        if not device.port:
            errors.append("设备缺少端口字段")
        if not device.username:
            errors.append("设备缺少用户名字段")
        if not device.password:
            errors.append("设备缺少密码字段")
        
        # 验证端口号范围
        if device.port and not (1 <= device.port <= 65535):
            errors.append(f"设备端口号无效: {device.port}")
        
        # 验证环境变量格式
        if device.env_vars is not None:
            if not isinstance(device.env_vars, dict):
                errors.append("环境变量必须是字典类型")
        
        return errors
    
    @staticmethod
    def validate_testcase(testcase: TestCase) -> List[str]:
        """
        验证测试用例配置
        
        Args:
            testcase: 测试用例对象
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 验证必需字段
        if not testcase.id:
            errors.append("测试用例缺少ID字段")
        if not testcase.name:
            errors.append("测试用例缺少名称字段")
        
        # 验证测试场景
        if not testcase.scenarios:
            errors.append("测试用例缺少测试场景")
        else:
            for i, scenario in enumerate(testcase.scenarios):
                if not scenario.name:
                    errors.append(f"场景{i+1}缺少名称")
                if not scenario.verify:
                    errors.append(f"场景'{scenario.name}'缺少verify阶段")
        
        # 验证超时时间
        if testcase.timeout and not (1 <= testcase.timeout <= 3600):
            errors.append(f"超时时间无效: {testcase.timeout}")
        
        # 验证失败行为
        if testcase.on_failure not in ["continue", "stop"]:
            errors.append(f"失败行为无效: {testcase.on_failure}")
        
        return errors
    
    @staticmethod
    def validate_task(task: Task) -> List[str]:
        """
        验证任务配置
        
        Args:
            task: 任务对象
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 验证必需字段
        if not task.id:
            errors.append("任务缺少ID字段")
        if not task.name:
            errors.append("任务缺少名称字段")
        
        # 验证设备和测试用例列表
        if not task.devices:
            errors.append("任务缺少设备列表")
        if not task.testcases:
            errors.append("任务缺少测试用例列表")
        
        # 验证失败行为
        if task.on_testcase_failure not in ["continue", "stop"]:
            errors.append(f"失败行为无效: {task.on_testcase_failure}")
        
        # 验证报告格式
        if task.report_format not in ["json", "html"]:
            errors.append(f"报告格式无效: {task.report_format}")
        
        return errors
    
    @staticmethod
    def validate_id_uniqueness(items: List, item_type: str) -> List[str]:
        """
        验证ID唯一性
        
        Args:
            items: 对象列表
            item_type: 对象类型名称
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        ids = {}
        
        for item in items:
            if item.id in ids:
                errors.append(f"{item_type} ID重复: {item.id} (首次出现在 {ids[item.id]})")
            else:
                ids[item.id] = item.name
        
        return errors
    
    @staticmethod
    def validate_references(
        task: Task,
        devices: Dict[str, Device],
        testcases: Dict[str, TestCase],
    ) -> List[str]:
        """
        验证任务配置中的引用完整性
        
        Args:
            task: 任务对象
            devices: 设备ID到设备对象的映射
            testcases: 测试用例ID到测试用例对象的映射
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 验证设备引用
        for device_id in task.devices:
            if device_id not in devices:
                errors.append(f"任务'{task.id}'引用的设备不存在: {device_id}")
        
        # 验证测试用例引用
        for testcase_id in task.testcases:
            if testcase_id not in testcases:
                errors.append(f"任务'{task.id}'引用的测试用例不存在: {testcase_id}")
        
        return errors
    
    @staticmethod
    def validate_all(
        devices: Dict[str, Device],
        testcases: Dict[str, TestCase],
        tasks: Dict[str, Task],
    ) -> Dict[str, List[str]]:
        """
        验证所有配置
        
        Args:
            devices: 设备ID到设备对象的映射
            testcases: 测试用例ID到测试用例对象的映射
            tasks: 任务ID到任务对象的映射
        
        Returns:
            错误消息字典，按配置类型分组
        """
        all_errors = {
            "devices": [],
            "testcases": [],
            "tasks": [],
        }
        
        # 验证每个设备
        for device in devices.values():
            errors = ConfigValidator.validate_device(device)
            all_errors["devices"].extend([f"设备'{device.id}': {e}" for e in errors])
        
        # 验证设备ID唯一性
        all_errors["devices"].extend(
            ConfigValidator.validate_id_uniqueness(list(devices.values()), "设备")
        )
        
        # 验证每个测试用例
        for testcase in testcases.values():
            errors = ConfigValidator.validate_testcase(testcase)
            all_errors["testcases"].extend([f"测试用例'{testcase.id}': {e}" for e in errors])
        
        # 验证测试用例ID唯一性
        all_errors["testcases"].extend(
            ConfigValidator.validate_id_uniqueness(list(testcases.values()), "测试用例")
        )
        
        # 验证每个任务
        for task in tasks.values():
            errors = ConfigValidator.validate_task(task)
            all_errors["tasks"].extend([f"任务'{task.id}': {e}" for e in errors])
        
        # 验证任务ID唯一性
        all_errors["tasks"].extend(
            ConfigValidator.validate_id_uniqueness(list(tasks.values()), "任务")
        )
        
        # 验证任务引用完整性
        for task in tasks.values():
            errors = ConfigValidator.validate_references(task, devices, testcases)
            all_errors["tasks"].extend([f"任务'{task.id}': {e}" for e in errors])
        
        return all_errors