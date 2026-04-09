# Coredump API 参考

本文档提供Coredump框架的Python API参考，适用于需要编程方式使用或扩展框架的开发者。

## 核心 API

### DeviceManager

设备管理器，负责SSH连接和命令执行。

**位置**: `src.core.device_manager.DeviceManager`

#### 初始化

```python
from src.core.device_manager import DeviceManager

device_manager = DeviceManager(ssh_timeout=10)
```

**参数**:
- `ssh_timeout` (int, optional): SSH连接超时时间（秒），默认10秒

#### 方法

##### connect()

连接到指定设备。

```python
def connect(device: Device) -> bool
```

**参数**:
- `device` (Device): 设备对象

**返回**:
- `bool`: 连接是否成功

**异常**:
- `ConnectionError`: 连接失败
- `RuntimeError`: 设备正忙

**示例**:

```python
from src.models import Device

device = Device(
    id="device001",
    name="测试设备",
    ip="192.168.1.100",
    port=22,
    username="root",
    password="password123"
)

success = device_manager.connect(device)
if success:
    print("连接成功")
```

##### execute_command()

在指定设备上执行命令。

```python
def execute_command(
    device_id: str,
    command: str,
    timeout: Optional[int] = None
) -> Tuple[int, str, str]
```

**参数**:
- `device_id` (str): 设备ID
- `command` (str): 要执行的命令
- `timeout` (int, optional): 命令执行超时时间（秒）

**返回**:
- `Tuple[int, str, str]`: (返回码, 标准输出, 标准错误)

**异常**:
- `RuntimeError`: 设备未连接

**示例**:

```python
return_code, stdout, stderr = device_manager.execute_command(
    device_id="device001",
    command="ls -la",
    timeout=30
)

print(f"返回码: {return_code}")
print(f"输出: {stdout}")
```

##### disconnect()

断开与指定设备的连接。

```python
def disconnect(device_id: str) -> None
```

**参数**:
- `device_id` (str): 设备ID

**示例**:

```python
device_manager.disconnect("device001")
```

##### disconnect_all()

断开所有设备连接。

```python
def disconnect_all() -> None
```

##### is_connected()

检查设备是否已连接。

```python
def is_connected(device_id: str) -> bool
```

**参数**:
- `device_id` (str): 设备ID

**返回**:
- `bool`: 是否已连接

##### is_busy()

检查设备是否正忙。

```python
def is_busy(device_id: str) -> bool
```

**参数**:
- `device_id` (str): 设备ID

**返回**:
- `bool`: 是否正忙

#### 上下文管理器

支持使用`with`语句自动管理连接：

```python
with DeviceManager() as manager:
    manager.connect(device)
    # 执行操作
    # 自动断开连接
```

---

### TestExecutor

测试执行器，负责执行测试用例和验证结果。

**位置**: `src.core.test_executor.TestExecutor`

#### 初始化

```python
from src.core.test_executor import TestExecutor
from src.core.device_manager import DeviceManager

device_manager = DeviceManager()
test_executor = TestExecutor(device_manager)
```

**参数**:
- `device_manager` (DeviceManager): 设备管理器实例

#### 方法

##### execute_testcase()

执行测试用例。

```python
def execute_testcase(
    device: Device,
    testcase: TestCase
) -> Tuple[bool, List[ReportStep]]
```

**参数**:
- `device` (Device): 待测设备
- `testcase` (TestCase): 测试用例

**返回**:
- `Tuple[bool, List[ReportStep]]`: (是否通过, 步骤报告列表)

**示例**:

```python
from src.models import TestCase, TestScenario, ExecutionPhase

scenario = TestScenario(
    name="ping测试",
    verify=[
        ExecutionPhase(
            command="ping -c 3 192.168.1.1",
            check="output_contains",
            expected="0% packet loss"
        )
    ]
)

testcase = TestCase(
    id="tc001",
    name="网络测试",
    scenarios=[scenario],
    timeout=30,
    on_failure="stop"
)

passed, steps = test_executor.execute_testcase(device, testcase)
print(f"测试{'通过' if passed else '失败'}")
```

##### execute_scenario()

执行测试场景。

```python
def execute_scenario(
    device: Device,
    scenario: TestScenario,
    timeout: Optional[int] = None
) -> Tuple[bool, List[ReportStep]]
```

**参数**:
- `device` (Device): 待测设备
- `scenario` (TestScenario): 测试场景
- `timeout` (int, optional): 超时时间

**返回**:
- `Tuple[bool, List[ReportStep]]`: (是否通过, 步骤报告列表)

##### execute_phase()

执行单个阶段。

```python
def execute_phase(
    device: Device,
    phase: ExecutionPhase,
    phase_name: str,
    scenario_name: str,
    timeout: Optional[int] = None,
    is_remote: bool = True
) -> ReportStep
```

**参数**:
- `device` (Device): 待测设备
- `phase` (ExecutionPhase): 执行阶段
- `phase_name` (str): 阶段名称
- `scenario_name` (str): 场景名称
- `timeout` (int, optional): 超时时间
- `is_remote` (bool): 是否远程执行

**返回**:
- `ReportStep`: 步骤报告

---

### TaskRunner

任务运行器，负责任务调度和执行。

**位置**: `src.core.task_runner.TaskRunner`

#### 初始化

```python
from src.core.task_runner import TaskRunner

task_runner = TaskRunner()
```

初始化时会自动加载所有配置文件。

#### 方法

##### run_task()

执行测试任务。

```python
def run_task(task_id: str) -> Dict
```

**参数**:
- `task_id` (str): 任务ID

**返回**:
- `Dict`: 执行结果字典

**异常**:
- `ValueError`: 任务不存在、设备不存在、测试用例不存在
- `RuntimeError`: 设备正忙

**示例**:

```python
result = task_runner.run_task("task001")

print(f"任务ID: {result['task_id']}")
print(f"执行时间: {result['duration']:.2f}秒")

for device_id, device_result in result['devices'].items():
    print(f"{device_id}: {device_result['status']}")
```

##### get_device_list()

获取设备列表。

```python
def get_device_list() -> List[Dict]
```

**返回**:
- `List[Dict]`: 设备信息列表

##### get_testcase_list()

获取测试用例列表。

```python
def get_testcase_list() -> List[Dict]
```

**返回**:
- `List[Dict]`: 测试用例信息列表

##### get_task_list()

获取任务列表。

```python
def get_task_list() -> List[Dict]
```

**返回**:
- `List[Dict]`: 任务信息列表

---

### ReportGenerator

报告生成器，生成JSON和HTML格式报告。

**位置**: `src.core.report_generator.ReportGenerator`

#### 初始化

```python
from src.core.report_generator import ReportGenerator

report_generator = ReportGenerator()
```

#### 方法

##### generate_report()

生成测试报告。

```python
def generate_report(
    report: Report,
    format: str = "json"
) -> str
```

**参数**:
- `report` (Report): 报告对象
- `format` (str): 报告格式，"json"或"html"

**返回**:
- `str`: 报告文件路径

**异常**:
- `ValueError`: 不支持的报告格式

**示例**:

```python
from src.models import Report, ReportStep
from datetime import datetime

report = Report(
    task_name="测试任务",
    device_id="device001",
    timestamp=datetime.now(),
    duration=5.0,
    overall_result="pass",
    steps=[
        ReportStep(
            scenario_name="测试场景",
            phase="verify",
            command="echo test",
            output="test",
            return_code=0,
            result="pass",
            duration=1.0
        )
    ]
)

report_path = report_generator.generate_report(report, format="html")
print(f"报告已生成: {report_path}")
```

---

## 数据模型 API

### Device

设备实体。

**位置**: `src.models.device.Device`

```python
from src.models import Device

device = Device(
    id="device001",           # 设备ID
    name="测试设备",           # 设备名称
    ip="192.168.1.100",       # IP地址
    port=22,                  # SSH端口
    username="root",          # SSH用户名
    password="password123",   # SSH密码
    env_vars={                # 环境变量（可选）
        "PATH": "/usr/local/bin:/usr/bin:/bin"
    }
)
```

---

### TestCase

测试用例实体。

**位置**: `src.models.testcase.TestCase`

```python
from src.models import TestCase, TestScenario

testcase = TestCase(
    id="tc001",               # 测试用例ID
    name="测试用例",           # 测试用例名称
    scenarios=[...],          # 测试场景列表
    timeout=30,               # 超时时间（可选）
    on_failure="stop"         # 失败行为（可选）
)
```

---

### TestScenario

测试场景实体。

**位置**: `src.models.scenario.TestScenario`

```python
from src.models import TestScenario, ExecutionPhase

scenario = TestScenario(
    name="测试场景",           # 场景名称
    setup=[...],             # setup阶段（可选）
    execute=[...],           # execute阶段（可选）
    verify=[...],            # verify阶段（必需）
    cleanup=[...]            # cleanup阶段（可选）
)
```

---

### ExecutionPhase

执行阶段实体。

**位置**: `src.models.phase.ExecutionPhase`

```python
from src.models import ExecutionPhase

phase = ExecutionPhase(
    command="echo test",      # 执行的命令
    check="output_contains",  # 检查类型（可选）
    expected="test"           # 期望值（可选）
)
```

---

### Task

测试任务实体。

**位置**: `src.models.task.Task`

```python
from src.models import Task

task = Task(
    id="task001",                     # 任务ID
    name="测试任务",                   # 任务名称
    devices=["device001"],            # 设备ID列表
    testcases=["tc001"],              # 测试用例ID列表
    on_testcase_failure="stop",       # 用例失败行为（可选）
    report_format="json"              # 报告格式（可选）
)
```

---

### Report

测试报告实体。

**位置**: `src.models.report.Report`

```python
from src.models import Report
from datetime import datetime

report = Report(
    task_name="测试任务",              # 任务名称
    device_id="device001",            # 设备ID
    timestamp=datetime.now(),         # 时间戳
    duration=5.0,                     # 执行时间（秒）
    overall_result="pass",            # 整体结果
    steps=[...]                       # 步骤列表
)
```

---

### ReportStep

报告步骤实体。

**位置**: `src.models.report.ReportStep`

```python
from src.models import ReportStep

step = ReportStep(
    scenario_name="测试场景",          # 场景名称
    phase="verify",                   # 阶段名称
    command="echo test",              # 执行的命令
    output="test",                    # 命令输出
    return_code=0,                    # 返回码
    result="pass",                    # 步骤结果
    duration=1.0,                     # 执行时间（秒）
    check="output_contains",          # 检查类型（可选）
    expected="test",                  # 期望值（可选）
    error_message=None                # 错误信息（可选）
)
```

---

## 解析器 API

### YAMLParser

YAML配置文件解析器。

**位置**: `src.parsers.yaml_parser.YAMLParser`

#### 静态方法

##### load_all_devices()

加载所有设备配置。

```python
@staticmethod
def load_all_devices(devices_dir: str) -> Dict[str, Device]
```

**参数**:
- `devices_dir` (str): 设备配置目录路径

**返回**:
- `Dict[str, Device]`: 设备字典，键为设备ID

##### load_all_testcases()

加载所有测试用例配置。

```python
@staticmethod
def load_all_testcases(testcases_dir: str) -> Dict[str, TestCase]
```

**参数**:
- `testcases_dir` (str): 测试用例配置目录路径

**返回**:
- `Dict[str, TestCase]`: 测试用例字典

##### load_all_tasks()

加载所有任务配置。

```python
@staticmethod
def load_all_tasks(tasks_dir: str) -> Dict[str, Task]
```

**参数**:
- `tasks_dir` (str): 任务配置目录路径

**返回**:
- `Dict[str, Task]`: 任务字典

---

### ConfigValidator

配置验证器。

**位置**: `src.parsers.config_validator.ConfigValidator`

#### 静态方法

##### validate_device()

验证设备配置。

```python
@staticmethod
def validate_device(device: Device) -> List[str]
```

**参数**:
- `device` (Device): 设备对象

**返回**:
- `List[str]`: 错误消息列表，空列表表示验证通过

##### validate_testcase()

验证测试用例配置。

```python
@staticmethod
def validate_testcase(testcase: TestCase) -> List[str]
```

**参数**:
- `testcase` (TestCase): 测试用例对象

**返回**:
- `List[str]`: 错误消息列表

---

## 工具 API

### SSHClient

SSH客户端封装。

**位置**: `src.utils.ssh_client.SSHClient`

```python
from src.utils.ssh_client import SSHClient

client = SSHClient(timeout=10)
client.connect(device)
return_code, stdout, stderr = client.execute_command("ls -la", timeout=30)
client.disconnect()
```

---

### TimeUtils

时间工具。

**位置**: `src.utils.time_utils.TimeUtils`

```python
from src.utils.time_utils import TimeUtils

# 获取当前时间戳
timestamp = TimeUtils.get_current_timestamp()

# 计算时间差
duration = TimeUtils.calculate_duration(start_time, end_time)

# 格式化时间戳
formatted = TimeUtils.format_timestamp(timestamp)
```

---

### FileUtils

文件工具。

**位置**: `src.utils.file_utils.FileUtils`

```python
from src.utils.file_utils import FileUtils

# 读取文件
content = FileUtils.read_file("/path/to/file")

# 写入文件
FileUtils.write_file("/path/to/file", content)

# 检查文件大小
size_ok = FileUtils.check_size_limit("/path/to/file", max_size_mb=100)
```

---

### Logger

日志记录器。

**位置**: `src.utils.logger`

```python
from src.utils import get_logger

logger = get_logger(__name__)
logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
```

---

## 配置 API

### Settings

全局配置。

**位置**: `src.config.settings.Settings`

```python
from src.config import get_settings

settings = get_settings()
print(settings.ssh_timeout)        # SSH连接超时
print(settings.default_timeout)    # 默认命令超时
print(settings.report_max_size)    # 报告最大大小（MB）
```

---

### PathManager

路径管理器。

**位置**: `src.config.paths.PathManager`

```python
from src.config import get_path_manager

path_manager = get_path_manager()
devices_dir = path_manager.get_devices_dir()
testcases_dir = path_manager.get_testcases_dir()
tasks_dir = path_manager.get_tasks_dir()
reports_dir = path_manager.get_reports_dir()
```

---

## 异常

### 常见异常

- `ValueError`: 配置错误（缺少字段、格式错误、ID不存在等）
- `ConnectionError`: SSH连接失败
- `RuntimeError`: 运行时错误（设备正忙、命令执行失败等）
- `TimeoutError`: 操作超时

---

## 类型提示

框架全面使用类型提示，建议使用mypy进行类型检查：

```bash
mypy src/
```

---

## 扩展指南

### 自定义检查规则

继承`TestExecutor`并重写`_verify_output()`方法：

```python
from src.core.test_executor import TestExecutor

class CustomTestExecutor(TestExecutor):
    def _verify_output(self, return_code, output, check, expected):
        if check == "custom_check":
            # 自定义检查逻辑
            return custom_verify(output, expected)
        
        # 调用父类方法
        return super()._verify_output(return_code, output, check, expected)
```

### 自定义报告格式

继承`ReportGenerator`并添加新方法：

```python
from src.core.report_generator import ReportGenerator

class CustomReportGenerator(ReportGenerator):
    def generate_report(self, report, format):
        if format == "custom":
            return self._generate_custom_report(report)
        
        return super().generate_report(report, format)
    
    def _generate_custom_report(self, report):
        # 自定义报告生成逻辑
        pass
```

---

## 最佳实践

1. **使用上下文管理器**: 自动管理资源
2. **异常处理**: 捕获特定异常并提供有意义的错误信息
3. **类型提示**: 使用类型提示提高代码可读性
4. **日志记录**: 使用logger记录关键操作
5. **配置验证**: 执行前验证配置完整性