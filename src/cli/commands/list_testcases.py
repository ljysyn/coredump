"""
列出测试用例命令

实现 `coredump list testcases` 命令
"""

import click

from ...core import TaskRunner


@click.command("testcases")
def list_testcases():
    """列出所有测试用例"""
    runner = TaskRunner()

    testcases = runner.get_testcase_list()

    if not testcases:
        click.echo("无测试用例配置")
        return

    click.echo("=" * 90)
    click.echo(
        f"{'ID':<15} {'名称':<25} {'场景数':<10} {'超时(秒)':<12} {'失败行为':<10}"
    )
    click.echo("=" * 90)

    for tc in testcases:
        click.echo(
            f"{tc['id']:<15} {tc['name']:<25} {tc['scenarios']:<10} "
            f"{tc['timeout']:<12} {tc['on_failure']:<10}"
        )

    click.echo("=" * 90)
    click.echo(f"总计: {len(testcases)} 个测试用例")
