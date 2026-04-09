"""
SSH客户端封装

提供SSH连接、命令执行和环境变量加载功能
"""

import time
from typing import Dict, List, Optional, Tuple

import paramiko

from ..models import Device


class SSHClient:
    """SSH客户端封装类"""

    def __init__(self, timeout: int = 10):
        """
        初始化SSH客户端

        Args:
            timeout: SSH连接超时时间（秒）
        """
        self.timeout = timeout
        self._client: Optional[paramiko.SSHClient] = None
        self._device: Optional[Device] = None

    def connect(self, device: Device) -> bool:
        """
        连接到目标设备

        Args:
            device: 待测设备对象

        Returns:
            连接是否成功
        """
        try:
            self._device = device
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self._client.connect(
                hostname=device.ip,
                port=device.port,
                username=device.username,
                password=device.password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )

            return True

        except paramiko.AuthenticationException:
            raise ConnectionError(f"SSH认证失败: {device.ip}")
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH连接失败: {e}")
        except TimeoutError:
            raise ConnectionError(f"SSH连接超时 ({self.timeout}秒): {device.ip}")
        except Exception as e:
            raise ConnectionError(f"SSH连接错误: {e}")

    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """
        执行远程命令

        Args:
            command: 要执行的命令
            timeout: 命令执行超时时间（秒）

        Returns:
            (返回码, 标准输出, 标准错误)
        """
        if not self._client:
            raise RuntimeError("SSH未连接")

        actual_timeout = timeout or 30

        # 如果设备有环境变量，注入到命令中
        if self._device and self._device.env_vars:
            env_prefix = " ".join(
                f'{key}="{value}"' for key, value in self._device.env_vars.items()
            )
            command = f"{env_prefix} {command}"

        try:
            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=actual_timeout,
            )

            # 等待命令执行完成
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")

            return exit_code, output, error

        except paramiko.SSHException as e:
            raise RuntimeError(f"命令执行失败: {e}")
        except Exception as e:
            raise RuntimeError(f"命令执行错误: {e}")

    def disconnect(self) -> None:
        """断开SSH连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._device = None

    def is_connected(self) -> bool:
        """
        检查SSH连接状态

        Returns:
            是否已连接
        """
        if not self._client:
            return False

        try:
            transport = self._client.get_transport()
            return transport is not None and transport.is_active()
        except Exception:
            return False

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
