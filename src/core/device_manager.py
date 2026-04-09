"""
设备管理器模块

管理SSH连接和命令执行
"""
import time
from typing import Dict, List, Optional, Tuple

from ..config import get_settings
from ..models import Device
from ..utils import SSHClient


class DeviceManager:
    """
    设备管理器
    
    负责管理SSH连接、命令执行和环境变量加载
    """
    
    def __init__(self, ssh_timeout: Optional[int] = None):
        """
        初始化设备管理器
        
        Args:
            ssh_timeout: SSH连接超时时间（秒），None使用全局配置
        """
        settings = get_settings()
        self.ssh_timeout = ssh_timeout or settings.ssh_timeout
        self._clients: Dict[str, SSHClient] = {}
        self._busy_devices: set = set()
    
    def connect(self, device: Device) -> bool:
        """
        连接到指定设备
        
        Args:
            device: 设备对象
        
        Returns:
            连接是否成功
        
        Raises:
            ConnectionError: 连接失败
        """
        # 检查设备是否正忙
        if device.id in self._busy_devices:
            raise RuntimeError(f"设备正忙: {device.id}")
        
        # 创建SSH客户端
        client = SSHClient(timeout=self.ssh_timeout)
        
        try:
            success = client.connect(device)
            if success:
                self._clients[device.id] = client
                self._busy_devices.add(device.id)
            return success
        except Exception as e:
            raise ConnectionError(f"连接设备失败: {device.id} - {e}")
    
    def execute_command(
        self,
        device_id: str,
        command: str,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """
        在指定设备上执行命令
        
        Args:
            device_id: 设备ID
            command: 要执行的命令
            timeout: 命令执行超时时间（秒）
        
        Returns:
            (返回码, 标准输出, 标准错误)
        
        Raises:
            RuntimeError: 设备未连接
        """
        if device_id not in self._clients:
            raise RuntimeError(f"设备未连接: {device_id}")
        
        client = self._clients[device_id]
        return client.execute_command(command, timeout)
    
    def disconnect(self, device_id: str) -> None:
        """
        断开与指定设备的连接
        
        Args:
            device_id: 设备ID
        """
        if device_id in self._clients:
            self._clients[device_id].disconnect()
            del self._clients[device_id]
            self._busy_devices.discard(device_id)
    
    def disconnect_all(self) -> None:
        """断开所有设备连接"""
        for device_id in list(self._clients.keys()):
            self.disconnect(device_id)
    
    def is_connected(self, device_id: str) -> bool:
        """
        检查设备是否已连接
        
        Args:
            device_id: 设备ID
        
        Returns:
            是否已连接
        """
        if device_id not in self._clients:
            return False
        return self._clients[device_id].is_connected()
    
    def is_busy(self, device_id: str) -> bool:
        """
        检查设备是否正忙
        
        Args:
            device_id: 设备ID
        
        Returns:
            是否正忙
        """
        return device_id in self._busy_devices
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect_all()