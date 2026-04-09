# Coredump 自动化测试框架

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

基于SSH的自动化设备测试框架，支持多设备、多测试用例的批量测试。

## 功能特性

- ✅ **SSH远程执行**：通过SSH连接待测设备执行测试命令
- ✅ **YAML配置驱动**：使用YAML文件管理设备、测试用例和测试任务
- ✅ **多设备支持**：支持批量测试多台设备，顺序执行
- ✅ **多测试用例**：支持在一个任务中执行多条测试用例
- ✅ **四阶段测试**：setup、execute、verify、cleanup完整测试流程
- ✅ **灵活的失败处理**：支持continue和stop两种失败处理策略
- ✅ **多格式报告**：支持JSON和HTML格式的测试报告
- ✅ **CLI命令行工具**：提供list和run命令进行管理和执行
- ✅ **环境变量支持**：可配置环境变量避免命令找不到路径
- ✅ **并发控制**：防止多个任务同时操作同一设备
- ✅ **配置验证**：执行前验证配置文件完整性和正确性

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd coredump

# 安装依赖
pip install -r requirements.txt

# 验证安装
coredump --version
```

### 配置设备

创建 `configs/devices/devices.yaml`:

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

### 配置测试用例

创建 `configs/testcases/test.yaml`:

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

### 配置测试任务

创建 `configs/tasks/task.yaml`:

```yaml
tasks:
  - id: task001
    name: 网络测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: html
```

### 执行测试

```bash
# 列出设备
coredump list devices

# 列出测试用例
coredump list testcases

# 列出测试任务
coredump list tasks

# 执行测试任务
coredump run task001
```

## 项目结构

```
coredump/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   │   ├── device_manager.py      # 设备管理
│   │   ├── test_executor.py       # 测试执行器
│   │   ├── task_runner.py         # 任务运行器
│   │   └── report_generator.py    # 报告生成器
│   ├── models/            # 数据模型
│   ├── parsers/           # YAML解析器
│   ├── cli/               # CLI命令行工具
│   ├── utils/             # 工具模块
│   └── config/            # 配置管理
├── configs/               # 配置文件
│   ├── devices/          # 设备配置
│   ├── testcases/        # 测试用例配置
│   └── tasks/            # 任务配置
├── tests/                 # 测试代码
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── contract/         # 契约测试
├── reports/               # 测试报告输出
├── logs/                  # 日志文件
└── docs/                  # 文档
```

## 核心功能

### 1. 设备管理

通过SSH连接待测设备，支持：
- SSH连接建立和断开
- 命令执行和超时控制
- 环境变量加载
- 连接状态检查
- 设备正忙检测

### 2. 测试执行

四阶段测试流程：

1. **setup**: 建立测试环境（SSH远程执行）
2. **execute**: 执行测试命令（本地执行）
3. **verify**: 验证测试结果（SSH远程执行，必需）
4. **cleanup**: 清理测试环境（SSH远程执行）

### 3. 检查规则

支持四种检查规则：

- **output_contains**: 输出包含指定字符串
- **return_code**: 返回值检查
- **regex**: 正则表达式匹配
- **none**: 不检查（命令执行成功即通过）

### 4. 报告生成

支持两种报告格式：

- **JSON**: 结构化数据，易于程序处理
- **HTML**: 可视化报告，易于阅读

报告包含：
- 任务元数据
- 执行摘要
- 详细步骤记录
- 失败信息

## 高级用法

### 环境变量配置

在设备配置中添加环境变量，避免命令找不到路径：

```yaml
devices:
  - id: device001
    name: Web服务器
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/nginx/sbin:/usr/bin:/bin
      NGINX_HOME: /usr/local/nginx
```

### 失败处理策略

测试用例级别：

```yaml
testcases:
  - id: tc001
    name: 测试用例
    on_failure: continue  # 失败后继续执行后续步骤
```

任务级别：

```yaml
tasks:
  - id: task001
    name: 测试任务
    on_testcase_failure: continue  # 测试用例失败后继续执行下一个用例
```

### 多设备测试

```yaml
tasks:
  - id: task001
    name: 多设备测试
    devices:
      - device001
      - device002
      - device003
    testcases:
      - tc001
      - tc002
```

系统会按顺序对每台设备执行所有测试用例，为每台设备生成一份报告。

## 配置文件格式

详细的配置文件格式请参考：
- [YAML配置契约](specs/001-automated-test-framework/contracts/yaml-configs.md)
- [CLI命令契约](specs/001-automated-test-framework/contracts/cli-commands.md)
- [报告格式契约](specs/001-automated-test-framework/contracts/report-format.md)

## 开发指南

### 运行测试

```bash
# 单元测试
python3 -m pytest tests/unit/ -v

# 集成测试
python3 -m pytest tests/integration/ -v

# 契约测试
python3 -m pytest tests/contract/ -v

# 测试覆盖率
python3 -m pytest tests/ --cov=src --cov-report=html
```

### 代码质量

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/
pylint src/
mypy src/
```

## 文档

- [架构文档](docs/architecture.md)
- [用户指南](docs/user-guide.md)
- [API参考](docs/api-reference.md)
- [快速开始](specs/001-automated-test-framework/quickstart.md)

## 常见问题

### Q: SSH连接失败怎么办？

检查：
1. 设备IP地址是否正确
2. SSH服务是否启动：`systemctl status sshd`
3. 网络连通性：`ping <device_ip>`
4. 防火墙规则：`iptables -L -n`

### Q: 命令找不到怎么办？

在设备配置中添加环境变量：

```yaml
env_vars:
  PATH: /usr/local/bin:/usr/bin:/bin
```

### Q: 如何查看测试日志？

```bash
tail -f logs/coredump.log
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v0.1.0 (2026-04-08)

- ✨ 初始版本发布
- ✅ 支持SSH远程设备测试
- ✅ 支持YAML配置文件
- ✅ 支持多设备多测试用例
- ✅ 支持CLI命令行工具
- ✅ 支持JSON/HTML报告
- ✅ 完整的测试覆盖