#!/usr/bin/env python3
"""
Coredump CLI主入口

提供命令行工具的主入口点
"""
import click

from ..config import init_path_manager
from ..core import TaskRunner
from .utils.progress import ProgressDisplay


@click.group()
@click.version_option(version="0.1.0", prog_name="coredump")
def cli():
    """Coredump自动化测试框架 - 基于SSH的设备测试工具"""
    init_path_manager()


@cli.command("list")
@click.argument("resource", type=click.Choice(["devices", "testcases", "tasks"]))
def list_resources(resource: str):
    """列出资源列表
    
    RESOURCE: devices, testcases 或 tasks
    """
    runner = TaskRunner()
    
    if resource == "devices":
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
    
    elif resource == "testcases":
        testcases = runner.get_testcase_list()
        if not testcases:
            click.echo("无测试用例配置")
            return
        
        click.echo("=" * 90)
        click.echo(f"{'ID':<15} {'名称':<25} {'场景数':<10} {'超时(秒)':<12} {'失败行为':<10}")
        click.echo("=" * 90)
        for tc in testcases:
            click.echo(
                f"{tc['id']:<15} {tc['name']:<25} {tc['scenarios']:<10} "
                f"{tc['timeout']:<12} {tc['on_failure']:<10}"
            )
    
    elif resource == "tasks":
        tasks = runner.get_task_list()
        if not tasks:
            click.echo("无测试任务配置")
            return
        
        click.echo("=" * 100)
        click.echo(f"{'ID':<15} {'名称':<25} {'设备数':<10} {'用例数':<10} {'报告格式':<12} {'状态':<10}")
        click.echo("=" * 100)
        for task in tasks:
            click.echo(
                f"{task['id']:<15} {task['name']:<25} {task['devices']:<10} "
                f"{task['testcases']:<10} {task['report_format']:<12} {task['status']:<10}"
            )


@cli.command("run")
@click.argument("task_id")
def run_task(task_id: str):
    """执行测试任务
    
    TASK_ID: 任务ID
    """
    runner = TaskRunner()
    progress = ProgressDisplay()
    
    try:
        progress.info(f"开始执行任务: {task_id}")
        result = runner.run_task(task_id)
        
        progress.info("任务执行完成")
        progress.info(f"执行耗时: {result['duration']:.2f}秒")
        click.echo("")
        click.echo("=" * 80)
        click.echo("任务执行结果")
        click.echo("=" * 80)
        click.echo(f"任务ID: {result['task_id']}")
        click.echo(f"任务名称: {result['task_name']}")
        click.echo(f"开始时间: {result['start_time']}")
        click.echo(f"结束时间: {result['end_time']}")
        click.echo("")
        
        click.echo("设备测试结果:")
        for device_id, device_result in result["devices"].items():
            status = "✓ 通过" if device_result["status"] == "pass" else "✗ 失败"
            click.echo(f"  {device_id}: {status}")
            if "report_path" in device_result:
                click.echo(f"    报告: {device_result['report_path']}")
            if "error" in device_result:
                click.echo(f"    错误: {device_result['error']}")
        
        click.echo("=" * 80)
    
    except ValueError as e:
        click.echo(f"[ERROR]   {e}", err=True)
        raise click.Abort()
    except RuntimeError as e:
        click.echo(f"[ERROR]   {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"[ERROR]   执行失败: {e}", err=True)
        raise click.Abort()


def main():
    """CLI主入口"""
    cli()


if __name__ == "__main__":
    main()