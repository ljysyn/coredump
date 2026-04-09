# Models 模块

数据模型定义，包含所有核心实体。

## 模块组成

### 1. Device (`device.py`)

设备实体，代表待测设备。

**字段**:
```python
@dataclass
class Device:
    id: str                  # 设备唯一标识符
    name: str                # 设备名称
    ip: str                  # IP地址（IPv4格式）
    port: int                # SSH端口（1-65535）
    username: str            # SSH用户名
    password: str            # SSH密码
    env_vars: Optional[Dict[str, str]] = None  # 环境变量（可选）
```

**使用示例**:
```python
from src.models import Device

device = Device(
    id="device001",
    name="测试设备",
    ip="192.168.1.100",
    port=22,
    username="root",
    password="password123",
    env_vars={"PATH": "/usr/local/bin:/usr/bin:/bin"}
)
```

---

### 2. TestCase (`testcase.py`)

测试用例实体。

**字段**:
```python
@dataclass
class TestCase:
    id: str                          # 测试用例ID
    name: str                        # 测试用例名称
    scenarios: List[TestScenario]    # 测试场景列表
    timeout: int = 30                # 超时时间（秒）
    on_failure: str = "stop"         # 失败行为：stop/continue
```

**使用示例**:
```python
from src.models import TestCase, TestScenario

testcase = TestCase(
    id="tc001",
    name="网络测试",
    scenarios=[scenario1, scenario2],
    timeout=30,
    on_failure="stop"
)
```

---

### 3. TestScenario (`scenario.py`)

测试场景实体。

**字段**:
```python
@dataclass
class TestScenario:
    name: str                                # 场景名称
    setup: Optional[List[ExecutionPhase]]    # setup阶段（可选）
    execute: Optional[List[ExecutionPhase]]  # execute阶段（可选）
    verify: List[ExecutionPhase]             # verify阶段（必需）
    cleanup: Optional[List[ExecutionPhase]]  # cleanup阶段（可选）
```

**阶段执行顺序**:
```
setup → execute → verify → cleanup
```

**阶段特性**:
- **setup**: SSH远程执行，准备测试环境
- **execute**: 本地执行，执行测试命令
- **verify**: SSH远程执行，验证测试结果（必需）
- **cleanup**: SSH远程执行，清理测试环境

---

### 4. ExecutionPhase (`phase.py`)

执行阶段实体。

**字段**:
```python
@dataclass
class ExecutionPhase:
    command: str                 # 执行的命令
    check: Optional[str] = None  # 检查类型
    expected: Optional[str] = None  # 期望值
```

**检查类型**:
- `output_contains`: 输出包含指定字符串
- `return_code`: 返回值检查
- `regex`: 正则表达式匹配
- `none`: 不检查

**使用示例**:
```python
from src.models import ExecutionPhase

# 输出包含检查
phase1 = ExecutionPhase(
    command="ping -c 3 192.168.1.1",
    check="output_contains",
    expected="0% packet loss"
)

# 返回值检查
phase2 = ExecutionPhase(
    command="systemctl status nginx",
    check="return_code",
    expected="0"
)

# 正则表达式检查
phase3 = ExecutionPhase(
    command="uname -a",
    check="regex",
    expected=r"Linux \d+\.\d+"
)

# 不检查
phase4 = ExecutionPhase(
    command="hostname",
    check="none"
)
```

---

### 5. Task (`task.py`)

测试任务实体。

**字段**:
```python
@dataclass
class Task:
    id: str                              # 任务ID
    name: str                            # 任务名称
    devices: List[str]                   # 设备ID列表
    testcases: List[str]                 # 测试用例ID列表
    on_testcase_failure: str = "stop"    # 用例失败行为
    report_format: str = "json"          # 报告格式：json/html
```

**使用示例**:
```python
from src.models import Task

task = Task(
    id="task001",
    name="网络测试任务",
    devices=["device001", "device002"],
    testcases=["tc001", "tc002"],
    on_testcase_failure="continue",
    report_format="html"
)
```

---

### 6. Report (`report.py`)

测试报告实体。

**字段**:
```python
@dataclass
class Report:
    task_name: str                   # 任务名称
    device_id: str                   # 设备ID
    timestamp: datetime              # 时间戳
    duration: float                  # 执行时间（秒）
    overall_result: str              # 整体结果：pass/fail
    steps: List[ReportStep]          # 步骤列表
```

---

### 7. ReportStep (`report.py`)

报告步骤实体。

**字段**:
```python
@dataclass
class ReportStep:
    scenario_name: str               # 场景名称
    phase: str                       # 阶段名称
    command: str                     # 执行的命令
    output: str                      # 命令输出
    return_code: int                 # 返回码
    result: str                      # 步骤结果：pass/fail
    duration: float                  # 执行时间（秒）
    check: Optional[str] = None      # 检查类型
    expected: Optional[str] = None   # 期望值
    error_message: Optional[str] = None  # 错误信息
```

**使用示例**:
```python
from src.models import ReportStep

step = ReportStep(
    scenario_name="ping测试",
    phase="verify",
    command="ping -c 3 192.168.1.1",
    output="PING ...",
    return_code=0,
    result="pass",
    duration=3.2,
    check="output_contains",
    expected="0% packet loss"
)
```

---

## 设计原则

1. **使用dataclass**: 简化模型定义，自动生成`__init__`等方法
2. **类型提示**: 所有字段都有明确的类型提示
3. **字段验证**: 在`__post_init__`中验证字段有效性
4. **不可变数据**: 使用frozen=True创建不可变对象（可选）

## 实体关系

```
Device 1:N Task N:M TestCase 1:N TestScenario 1:4 ExecutionPhase
Task 1:N Report
```

## 相关文档

- [数据模型文档](../../specs/001-automated-test-framework/data-model.md)
- [API参考](../../docs/api-reference.md)