# Core 模块

核心业务逻辑模块，包含四个主要组件。

## 模块组成

### 1. DeviceManager (`device_manager.py`)

设备管理器，负责SSH连接和命令执行。

**主要功能**:
- SSH连接管理
- 命令执行和超时控制
- 环境变量加载
- 设备状态管理

**使用示例**:

```python
from src.core.device_manager import DeviceManager
from src.models import Device

device = Device(
    id="device001",
    name="测试设备",
    ip="192.168.1.100",
    port=22,
    username="root",
    password="password123"
)

with DeviceManager() as manager:
    manager.connect(device)
    return_code, stdout, stderr = manager.execute_command(
        device.id, "ls -la", timeout=30
    )
    print(stdout)
```

**关键方法**:
- `connect(device)`: 连接设备
- `execute_command(device_id, command, timeout)`: 执行命令
- `disconnect(device_id)`: 断开连接
- `is_busy(device_id)`: 检查设备正忙

---

### 2. TestExecutor (`test_executor.py`)

测试执行器，负责执行测试用例和验证结果。

**主要功能**:
- 执行测试场景
- 管理四个测试阶段（setup/execute/verify/cleanup）
- 验证检查规则
- 生成测试步骤报告

**四阶段流程**:
```
setup (SSH远程) → execute (本地) → verify (SSH远程) → cleanup (SSH远程)
```

**检查规则**:
- `output_contains`: 输出包含检查
- `return_code`: 返回值检查
- `regex`: 正则表达式匹配
- `none`: 不检查

**使用示例**:

```python
from src.core.test_executor import TestExecutor
from src.core.device_manager import DeviceManager
from src.models import TestCase, TestScenario, ExecutionPhase

device_manager = DeviceManager()
executor = TestExecutor(device_manager)

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
    scenarios=[scenario]
)

passed, steps = executor.execute_testcase(device, testcase)
```

---

### 3. TaskRunner (`task_runner.py`)

任务运行器，负责任务调度和执行控制。

**主要功能**:
- 加载和验证配置
- 设备正忙检测
- 顺序执行设备测试
- 生成测试报告
- 失败处理策略

**执行流程**:
```
1. 加载配置文件
2. 验证配置完整性
3. 检查设备状态
4. 对每台设备：
   a. 连接设备
   b. 执行测试用例
   c. 生成报告
   d. 断开连接
5. 返回执行结果
```

**使用示例**:

```python
from src.core.task_runner import TaskRunner

runner = TaskRunner()

# 列出资源
devices = runner.get_device_list()
testcases = runner.get_testcase_list()
tasks = runner.get_task_list()

# 执行任务
result = runner.run_task("task001")
print(f"任务执行{'成功' if result['status'] == 'pass' else '失败'}")
```

---

### 4. ReportGenerator (`report_generator.py`)

报告生成器，生成JSON和HTML格式报告。

**主要功能**:
- 生成JSON格式报告
- 生成HTML格式报告
- 报告文件大小控制（100M限制）
- 使用Jinja2模板渲染

**报告结构**:
```json
{
  "meta": {
    "task_name": "...",
    "device_id": "...",
    "timestamp": "...",
    "duration_seconds": ...,
    "overall_result": "pass/fail"
  },
  "summary": {
    "total_steps": ...,
    "passed_steps": ...,
    "failed_steps": ...
  },
  "steps": [...]
}
```

**使用示例**:

```python
from src.core.report_generator import ReportGenerator
from src.models import Report, ReportStep
from datetime import datetime

generator = ReportGenerator()

report = Report(
    task_name="测试任务",
    device_id="device001",
    timestamp=datetime.now(),
    duration=5.0,
    overall_result="pass",
    steps=[...]
)

# 生成JSON报告
json_path = generator.generate_report(report, format="json")

# 生成HTML报告
html_path = generator.generate_report(report, format="html")
```

---

## 设计原则

1. **单一职责**: 每个模块专注于一个核心功能
2. **依赖注入**: 通过构造函数注入依赖
3. **异常处理**: 明确的异常类型和错误信息
4. **资源管理**: 使用上下文管理器自动清理资源

## 测试

单元测试位于 `tests/unit/core/`:

- `test_device_manager.py`: DeviceManager测试
- `test_test_executor.py`: TestExecutor测试
- `test_task_runner.py`: TaskRunner测试
- `test_report_generator.py`: ReportGenerator测试

运行测试:
```bash
pytest tests/unit/core/ -v
```

## 相关文档

- [架构文档](../../docs/architecture.md)
- [API参考](../../docs/api-reference.md)
- [用户指南](../../docs/user-guide.md)