"""
运行任务命令

实现 `coredump run <task_id>` 命令
"""

import click

from ...core import TaskRunner
from ..utils.progress import ProgressDisplay


@click.command("run")
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
        passed_count = 0
        failed_count = 0

        for device_id, device_result in result["devices"].items():
            if device_result["status"] == "pass":
                status = "✓ 通过"
                passed_count += 1
            else:
                status = "✗ 失败"
                failed_count += 1

            click.echo(f"  {device_id}: {status}")

            if "report_path" in device_result:
                click.echo(f"    报告: {device_result['report_path']}")

            if "error" in device_result:
                click.echo(f"    错误: {device_result['error']}")

        click.echo("")
        click.echo(f"通过设备: {passed_count}")
        click.echo(f"失败设备: {failed_count}")
        click.echo("=" * 80)

    except ValueError as e:
        progress.error(str(e))
        raise click.Abort()

    except RuntimeError as e:
        progress.error(str(e))
        raise click.Abort()

    except Exception as e:
        progress.error(f"执行失败: {e}")
        raise click.Abort()
