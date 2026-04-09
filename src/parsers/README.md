# Parsers 模块

配置文件解析和验证模块。

## 模块组成

### 1. YAMLParser (`yaml_parser.py`)

YAML配置文件解析器。

**主要功能**:
- 解析设备配置文件
- 解析测试用例配置文件
- 解析任务配置文件
- ID唯一性验证

**使用示例**:

```python
from src.parsers.yaml_parser import YAMLParser

# 加载所有设备
devices = YAMLParser.load_all_devices("/path/to/configs/devices")
# 返回: Dict[str, Device]

# 加载所有测试用例
testcases = YAMLParser.load_all_testcases("/path/to/configs/testcases")
# 返回: Dict[str, TestCase]

# 加载所有任务
tasks = YAMLParser.load_all_tasks("/path/to/configs/tasks")
# 返回: Dict[str, Task]
```

**静态方法**:

#### load_all_devices()

```python
@staticmethod
def load_all_devices(devices_dir: str) -> Dict[str, Device]
```

加载所有设备配置文件。

**参数**:
- `devices_dir` (str): 设备配置目录路径

**返回**:
- `Dict[str, Device]`: 设备字典，键为设备ID

**异常**:
- `ValueError`: ID重复或配置格式错误

---

#### load_all_testcases()

```python
@staticmethod
def load_all_testcases(testcases_dir: str) -> Dict[str, TestCase]
```

加载所有测试用例配置文件。

**参数**:
- `testcases_dir` (str): 测试用例配置目录路径

**返回**:
- `Dict[str, TestCase]`: 测试用例字典

---

#### load_all_tasks()

```python
@staticmethod
def load_all_tasks(tasks_dir: str) -> Dict[str, Task]
```

加载所有任务配置文件。

**参数**:
- `tasks_dir` (str): 任务配置目录路径

**返回**:
- `Dict[str, Task]`: 任务字典

---

### 2. ConfigValidator (`config_validator.py`)

配置验证器。

**主要功能**:
- 验证设备配置
- 验证测试用例配置
- 验证任务配置
- 提供详细的错误信息

**使用示例**:

```python
from src.parsers.config_validator import ConfigValidator
from src.models import Device

device = Device(
    id="device001",
    name="测试设备",
    ip="192.168.1.100",
    port=22,
    username="root",
    password="password123"
)

errors = ConfigValidator.validate_device(device)
if errors:
    print("验证失败:")
    for error in errors:
        print(f"  - {error}")
else:
    print("验证通过")
```

**静态方法**:

#### validate_device()

```python
@staticmethod
def validate_device(device: Device) -> List[str]
```

验证设备配置。

**验证内容**:
- 必需字段完整性（id, name, ip, port, username, password）
- IP地址格式
- 端口号范围（1-65535）
- 环境变量类型

**返回**:
- `List[str]`: 错误消息列表，空列表表示验证通过

---

#### validate_testcase()

```python
@staticmethod
def validate_testcase(testcase: TestCase) -> List[str]
```

验证测试用例配置。

**验证内容**:
- 必需字段完整性（id, name, scenarios）
- 测试场景列表非空
- 每个场景有名称和verify阶段
- 检查规则有效性

**返回**:
- `List[str]`: 错误消息列表

---

#### validate_task()

```python
@staticmethod
def validate_task(task: Task) -> List[str]
```

验证任务配置。

**验证内容**:
- 必需字段完整性（id, name, devices, testcases）
- 设备列表非空
- 测试用例列表非空

**返回**:
- `List[str]`: 错误消息列表

---

## 配置文件格式

### 设备配置

```yaml
devices:
  - id: device001
    name: 测试设备
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/bin:/usr/bin:/bin
```

### 测试用例配置

```yaml
testcases:
  - id: tc001
    name: 网络测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping测试
        setup:
          commands:
            - "mkdir /tmp/test"
        verify:
          - command: "ping -c 3 192.168.1.1"
            check: "output_contains"
            expected: "0% packet loss"
        cleanup:
          commands:
            - "rm -rf /tmp/test"
```

### 任务配置

```yaml
tasks:
  - id: task001
    name: 测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: json
```

## 验证流程

```
YAML文件
    ↓
YAMLParser解析
    ↓
转换为Model对象
    ↓
ConfigValidator验证
    ↓
返回错误列表（如果有）
```

## 错误处理

### 配置文件错误

```python
try:
    devices = YAMLParser.load_all_devices("/path/to/devices")
except ValueError as e:
    print(f"配置错误: {e}")
```

### 验证错误

```python
errors = ConfigValidator.validate_device(device)
if errors:
    for error in errors:
        print(error)
    raise ValueError("配置验证失败")
```

## 设计原则

1. **静态方法**: 不需要实例化，直接调用
2. **返回字典**: 使用字典快速查找（键为ID）
3. **ID唯一性**: 自动检测ID重复
4. **详细错误**: 提供具体的错误信息

## 测试

单元测试位于 `tests/unit/parsers/`:

- `test_config_validator.py`: ConfigValidator测试

运行测试:
```bash
pytest tests/unit/parsers/ -v
```

## 相关文档

- [YAML配置契约](../../specs/001-automated-test-framework/contracts/yaml-configs.md)
- [数据模型文档](../../specs/001-automated-test-framework/data-model.md)