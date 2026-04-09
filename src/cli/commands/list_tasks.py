"""
列出任务命令

实现 `coredump list tasks` 命令
"""

import click

from ...core import TaskRunner


@click.command("tasks")
def list_tasks():
    """列出所有测试任务"""
    runner = TaskRunner()

    tasks = runner.get_task_list()

    if not tasks:
        click.echo("无测试任务配置")
        return

    click.echo("=" * 100)
    click.echo(
        f"{'ID':<15} {'名称':<25} {'设备数':<10} {'用例数':<10} {'报告格式':<12} {'状态':<10}"
    )
    click.echo("=" * 100)

    for task in tasks:
        click.echo(
            f"{task['id']:<15} {task['name']:<25} {task['devices']:<10} "
            f"{task['testcases']:<10} {task['report_format']:<12} {task['status']:<10}"
        )

    click.echo("=" * 100)
    click.echo(f"总计: {len(tasks)} 个测试任务")
