"""
数据模型模块

定义框架的核心数据实体
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Device:
    """
    待测设备实体
    
    代表需要进行测试的物理或虚拟设备
    
    Attributes:
        id: 设备唯一标识符
        name: 设备名称
        ip: IP地址
        port: SSH端口
        username: SSH用户名
        password: SSH密码
        env_vars: 环境变量字典（可选）
    """
    
    id: str
    name: str
    ip: str
    port: int
    username: str
    password: str
    env_vars: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """验证字段有效性"""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("设备ID必须是非空字符串")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("设备名称必须是非空字符串")
        if not self.ip or not isinstance(self.ip, str):
            raise ValueError("IP地址必须是非空字符串")
        if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
            raise ValueError("SSH端口必须是1-65535之间的整数")
        if not self.username or not isinstance(self.username, str):
            raise ValueError("SSH用户名必须是非空字符串")
        if not self.password or not isinstance(self.password, str):
            raise ValueError("SSH密码必须是非空字符串")
        if self.env_vars is not None and not isinstance(self.env_vars, dict):
            raise ValueError("环境变量必须是字典类型")
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "env_vars": self.env_vars,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Device":
        """从字典创建Device实例"""
        return cls(
            id=data["id"],
            name=data["name"],
            ip=data["ip"],
            port=data["port"],
            username=data["username"],
            password=data["password"],
            env_vars=data.get("env_vars"),
        )