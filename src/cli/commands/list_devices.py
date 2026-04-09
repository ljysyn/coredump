"""
列出设备命令

实现 `coredump list devices` 命令
"""

import click

from ...core import TaskRunner


@click.command("devices")
def list_devices():
    """列出所有待测设备"""
    runner = TaskRunner()

    devices = runner.get_device_list()

    if not devices:
        click.echo("无待测设备配置")
        return

    click.echo("=" * 80)
    click.echo(f"{'ID':<15} {'名称':<20} {'IP地址':<18} {'端口':<8} {'用户名':<15}")
    click.echo("=" * 80)

    for device in devices:
        click.echo(
            f"{device['id']:<15} {device['name']:<20} {device['ip']:<18} "
            f"{device['port']:<8} {device['username']:<15}"
        )

    click.echo("=" * 80)
    click.echo(f"总计: {len(devices)} 台设备")
