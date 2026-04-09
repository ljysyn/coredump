# Coredump自动化测试框架

基于SSH的设备自动化测试框架，使用Python 3.9+开发。

## 功能特性

- ✅ YAML配置文件管理待测设备、测试用例和测试任务
- ✅ SSH远程连接和命令执行
- ✅ 支持环境变量加载
- ✅ 测试场景和阶段执行（setup、execute、verify、cleanup）
- ✅ 多种检查规则（输出包含、返回值、正则表达式）
- ✅ JSON和HTML格式测试报告
- ✅ CLI命令行工具

## 快速开始

### 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用开发模式安装
pip install -e .
```

### 配置示例

1. **配置设备** (`configs/devices/devices.yaml`):

```yaml
devices:
  - id: device001
    name: 测试设备1
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: "/usr/local/bin:/usr/bin:/bin"
```

2. **配置测试用例** (`configs/testcases/example_test.yaml`):

```yaml
testcases:
  - id: tc001
    name: 网络连通性测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping测试
        verify:
          - command: "ping -c 3 192.168.1.1"
            check: "output_contains"
            expected: "0% packet loss"
```

3. **配置测试任务** (`configs/tasks/example_task.yaml`):

```yaml
tasks:
  - id: task001
    name: 网络连通性测试任务
    devices:
      - device001
    testcases:
      - tc001
    report_format: html
```

### 使用CLI

```bash
# 列出所有设备
coredump list devices

# 列出所有测试用例
coredump list testcases

# 列出所有测试任务
coredump list tasks

# 执行测试任务
coredump run task001
```

## 项目结构

```
.
├── configs/              # 配置文件目录
│   ├── devices/         # 设备配置
│   ├── testcases/       # 测试用例配置
│   └── tasks/           # 测试任务配置
├── reports/             # 测试报告输出
├── logs/                # 日志文件
├── src/                 # 源代码
│   ├── cli/            # CLI命令行工具
│   ├── config/         # 配置管理
│   ├── core/           # 核心模块
│   ├── models/         # 数据模型
│   ├── parsers/        # 配置解析器
│   └── utils/          # 工具模块
└── tests/              # 测试代码
    ├── unit/           # 单元测试
    ├── integration/    # 集成测试
    └── contract/       # 契约测试
```

## 核心模块

### DeviceManager
管理SSH连接和命令执行，支持环境变量加载。

### TestExecutor
执行测试场景和阶段，验证检查规则。

### TaskRunner
任务调度和进度跟踪，管理设备顺序执行。

### ReportGenerator
生成JSON和HTML格式测试报告，支持文件大小限制。

## 开发

```bash
# 运行测试
pytest tests/

# 代码格式化
black src/
isort src/

# 代码检查
flake8 src/
pylint src/
mypy src/
```

## 许可证

MIT License