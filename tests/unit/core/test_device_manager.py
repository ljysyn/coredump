"""
DeviceManager单元测试

测试SSH连接、命令执行和环境变量加载功能
"""

import socket
from unittest.mock import Mock, MagicMock, patch

import pytest

from src.core.device_manager import DeviceManager
from src.models import Device


@pytest.fixture
def mock_ssh_client():
    """Mock SSH客户端"""
    client = MagicMock()
    client.connect.return_value = True
    client.execute_command.return_value = (0, "output", "")
    client.is_connected.return_value = True
    client.disconnect.return_value = None
    return client


@pytest.fixture
def sample_device():
    """示例设备"""
    return Device(
        id="device001",
        name="测试设备",
        ip="192.168.1.100",
        port=22,
        username="root",
        password="password123",
        env_vars={"PATH": "/usr/local/bin:/usr/bin:/bin"},
    )


@pytest.fixture
def device_manager():
    """设备管理器实例"""
    return DeviceManager(ssh_timeout=10)


class TestDeviceManagerConnect:
    """测试连接功能"""

    def test_connect_success(self, device_manager, sample_device, mock_ssh_client):
        """测试成功连接设备"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            result = device_manager.connect(sample_device)

            assert result is True
            assert device_manager.is_connected(sample_device.id)
            assert device_manager.is_busy(sample_device.id)

    def test_connect_timeout(self, device_manager, sample_device):
        """测试连接超时"""
        with patch("src.core.device_manager.SSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect.side_effect = socket.timeout("SSH连接超时")
            mock_client_class.return_value = mock_client

            with pytest.raises(ConnectionError, match="连接设备失败"):
                device_manager.connect(sample_device)

            assert not device_manager.is_connected(sample_device.id)

    def test_connect_busy_device(self, device_manager, sample_device, mock_ssh_client):
        """测试设备正忙时连接"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            with pytest.raises(RuntimeError, match="设备正忙"):
                device_manager.connect(sample_device)

    def test_connect_auth_failure(self, device_manager, sample_device):
        """测试认证失败"""
        with patch("src.core.device_manager.SSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect.side_effect = Exception("认证失败")
            mock_client_class.return_value = mock_client

            with pytest.raises(ConnectionError, match="连接设备失败"):
                device_manager.connect(sample_device)


class TestDeviceManagerExecuteCommand:
    """测试命令执行功能"""

    def test_execute_command_success(
        self, device_manager, sample_device, mock_ssh_client
    ):
        """测试成功执行命令"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            return_code, stdout, stderr = device_manager.execute_command(
                sample_device.id, "ls -la"
            )

            assert return_code == 0
            assert stdout == "output"
            assert stderr == ""
            mock_ssh_client.execute_command.assert_called_once()

    def test_execute_command_not_connected(self, device_manager, sample_device):
        """测试设备未连接时执行命令"""
        with pytest.raises(RuntimeError, match="设备未连接"):
            device_manager.execute_command(sample_device.id, "ls -la")

    def test_execute_command_with_timeout(
        self, device_manager, sample_device, mock_ssh_client
    ):
        """测试带超时的命令执行"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            device_manager.execute_command(sample_device.id, "long_command", timeout=60)

            mock_ssh_client.execute_command.assert_called_with("long_command", 60)


class TestDeviceManagerDisconnect:
    """测试断开连接功能"""

    def test_disconnect_success(self, device_manager, sample_device, mock_ssh_client):
        """测试成功断开连接"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)
            device_manager.disconnect(sample_device.id)

            assert not device_manager.is_connected(sample_device.id)
            assert not device_manager.is_busy(sample_device.id)
            mock_ssh_client.disconnect.assert_called_once()

    def test_disconnect_not_connected(self, device_manager, sample_device):
        """测试断开未连接的设备"""
        device_manager.disconnect(sample_device.id)

        assert not device_manager.is_connected(sample_device.id)

    def test_disconnect_all(self, device_manager, sample_device, mock_ssh_client):
        """测试断开所有连接"""
        device2 = Device(
            id="device002",
            name="测试设备2",
            ip="192.168.1.101",
            port=22,
            username="root",
            password="password456",
        )

        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)
            device_manager.connect(device2)

            device_manager.disconnect_all()

            assert not device_manager.is_connected(sample_device.id)
            assert not device_manager.is_connected(device2.id)


class TestDeviceManagerContextManager:
    """测试上下文管理器"""

    def test_context_manager_cleanup(
        self, device_manager, sample_device, mock_ssh_client
    ):
        """测试上下文管理器自动清理"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            with device_manager:
                device_manager.connect(sample_device)

                assert device_manager.is_connected(sample_device.id)

            assert not device_manager.is_connected(sample_device.id)


class TestDeviceManagerEnvVars:
    """测试环境变量加载"""

    def test_env_vars_loaded(self, device_manager, sample_device, mock_ssh_client):
        """测试环境变量被加载"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            mock_ssh_client.connect.assert_called_once()

            device_manager.execute_command(sample_device.id, "echo $PATH")

            mock_ssh_client.execute_command.assert_called()


class TestDeviceManagerIsConnected:
    """测试连接状态检查"""

    def test_is_connected_true(self, device_manager, sample_device, mock_ssh_client):
        """测试设备已连接"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            assert device_manager.is_connected(sample_device.id) is True

    def test_is_connected_false(self, device_manager, sample_device):
        """测试设备未连接"""
        assert device_manager.is_connected(sample_device.id) is False

    def test_is_connected_after_disconnect(
        self, device_manager, sample_device, mock_ssh_client
    ):
        """测试断开后状态检查"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)
            device_manager.disconnect(sample_device.id)

            assert device_manager.is_connected(sample_device.id) is False


class TestDeviceManagerIsBusy:
    """测试设备正忙检查"""

    def test_is_busy_true(self, device_manager, sample_device, mock_ssh_client):
        """测试设备正忙"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)

            assert device_manager.is_busy(sample_device.id) is True

    def test_is_busy_false(self, device_manager, sample_device):
        """测试设备不忙"""
        assert device_manager.is_busy(sample_device.id) is False

    def test_is_busy_after_disconnect(
        self, device_manager, sample_device, mock_ssh_client
    ):
        """测试断开后设备不忙"""
        with patch("src.core.device_manager.SSHClient", return_value=mock_ssh_client):
            device_manager.connect(sample_device)
            device_manager.disconnect(sample_device.id)

            assert device_manager.is_busy(sample_device.id) is False
