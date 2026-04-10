# CLI 模块

命令行工具模块，提供用户交互界面。

## 模块组成

### 1. Main (`main.py`)

CLI主入口，使用Click框架。

**主要功能**:
- 定义命令组
- 版本信息
- 帮助信息

**命令列表**:
- `coredump list devices`: 列出设备
- `coredump list testcases`: 列出测试用例
- `coredump list tasks`: 列出任务
- `coredump run <task_id>`: 执行任务

**使用示例**:

```bash
# 查看版本
coredump --version

# 查看帮助
coredump --help

# 列出设备
coredump list devices

# 执行任务
coredump run task001
```

---

### 2. Commands (`commands/`)

子命令实现。

#### list_devices.py

列出所有设备。

**命令**: `coredump list devices`

**输出格式**:
```
================================================================================
ID              名称                 IP地址              端口      用户名
================================================================================
device001      测试设备1            192.168.1.100       22        root
device002      测试设备2            192.168.1.101       22        root
================================================================================
总计: 2 台设备
```

---

#### list_testcases.py

列出所有测试用例。

**命令**: `coredump list testcases`

**输出格式**:
```
==========================================================================================
ID              名称                      场景数      超时(秒)    失败行为
==========================================================================================
tc001          网络连通性测试             1           30          stop
tc002          系统服务检查               2           60          continue
==========================================================================================
总计: 2 个测试用例
```

---

#### list_tasks.py

列出所有任务。

**命令**: `coredump list tasks`

**输出格式**:
```
====================================================================================================
ID              名称                      设备数      用例数      报告格式      状态
====================================================================================================
task001        网络测试任务               2           2           html          pending
task002        系统测试任务               1           3           json          pending
====================================================================================================
总计: 2 个测试任务
```

---

#### run_task.py

执行测试任务。

**命令**: `coredump run <task_id>`

**参数**:
- `task_id`: 任务ID

**输出示例**:
```
[2026-04-08 14:30:22] [INFO]    开始执行任务: task001
[2026-04-08 14:30:22] [INFO]    正在连接设备: device001 (192.168.1.100)
[2026-04-08 14:30:25] [INFO]    执行测试用例: tc001 - 网络连通性测试
[2026-04-08 14:30:28] [INFO]    测试用例结果: 通过
[2026-04-08 14:30:28] [INFO]    任务执行完成

================================================================================
任务执行结果
================================================================================
任务ID: task001
任务名称: 网络测试任务
执行耗时: 6.00秒

设备测试结果:
  device001: ✓ 通过
    报告: reports/task001_device001_20260408_143022.html

通过设备: 1
失败设备: 0
================================================================================
```

---

### 3. Utils (`utils/`)

CLI工具模块。

#### progress.py

进度显示工具。

**主要功能**:
- 日志级别显示（INFO/WARNING/ERROR）
- 时间戳格式化
- 进度跟踪

**使用示例**:

```python
from src.cli.utils.progress import ProgressDisplay

progress = ProgressDisplay()

# 显示不同级别的日志
progress.info("开始执行任务")
progress.warning("设备连接失败")
progress.error("任务执行失败")

# 显示命令执行结果
progress.command_result("ls -la", passed=True)

# 显示成功/失败
progress.success("测试通过")
progress.failure("测试失败")
```

**输出格式**:
```
[2026-04-08 14:30:22] [INFO]    开始执行任务
[2026-04-08 14:30:22] [WARNING] 设备连接失败
[2026-04-08 14:30:22] [ERROR]   任务执行失败
[2026-04-08 14:30:22] [INFO]    执行命令: ls -la - 通过
[2026-04-08 14:30:22] [INFO]    ✓ 测试通过
[2026-04-08 14:30:22] [ERROR]   ✗ 测试失败
```

---

#### display.py

显示格式化工具。

**主要功能**:
- 表格格式化
- 设备/测试用例/任务表格
- 结果摘要格式化
- 字符串处理

**使用示例**:

```python
from src.cli.utils.display import DisplayFormatter

# 格式化设备表格
devices = [
    {"id": "device001", "name": "测试设备", "ip": "192.168.1.100", "port": 22, "username": "root"}
]
table = DisplayFormatter.format_device_table(devices)
print(table)

# 格式化结果摘要
result = {
    "task_id": "task001",
    "task_name": "测试任务",
    "start_time": "2026-04-08T10:00:00",
    "end_time": "2026-04-08T10:00:05",
    "duration": 5.0,
    "devices": {"device001": {"status": "pass"}}
}
summary = DisplayFormatter.format_result_summary(result)
print(summary)

# 格式化持续时间
print(DisplayFormatter.format_duration(5.5))      # 5.50秒
print(DisplayFormatter.format_duration(125))     # 2分5秒
print(DisplayFormatter.format_duration(3665))    # 1小时1分钟
```

---

## 设计原则

1. **Click框架**: 使用Click简化命令定义
2. **模块化**: 每个命令独立模块
3. **错误处理**: 统一的错误处理和退出码
4. **用户体验**: 彩色输出、格式化表格、清晰提示

## 退出码

- `0`: 成功
- `1`: 失败
- `2`: 配置错误
- `3`: 并发冲突

## 测试

单元测试位于 `tests/unit/cli/`:

- `test_commands.py`: 命令测试

契约测试位于 `tests/contract/`:

- `test_cli_commands.py`: CLI契约测试

运行测试:
```bash
# 单元测试
pytest tests/unit/cli/ -v

# 契约测试
pytest tests/contract/test_cli_commands.py -v
```

## 相关文档

- [CLI命令契约](../../docs/contracts/cli-commands.md)
- [用户指南](../../docs/user-guide.md)
