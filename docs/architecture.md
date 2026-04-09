# Coredump 架构文档

## 概述

Coredump是一个基于SSH的自动化测试框架，采用模块化设计，支持多设备、多测试用例的批量测试。

## 架构设计

### 设计原则

1. **模块化设计**：功能划分为独立模块，职责清晰
2. **配置驱动**：通过YAML配置文件管理测试资源
3. **可扩展性**：支持插件扩展和自定义功能
4. **测试优先**：遵循TDD流程，保证代码质量

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer (Click)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   list   │  │   run    │  │  utils   │  │  main   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Core Business Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Task      │  │     Test     │  │    Device    │  │
│  │    Runner    │  │   Executor   │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐                                       │
│  │    Report    │                                       │
│  │  Generator   │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Foundation Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Models  │  │ Parsers  │  │   Utils  │  │  Config │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   SSH    │  │   YAML   │  │  Jinja2  │  │ File IO │ │
│  │  Client  │  │  Parser  │  │ Template │  │  Utils  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. CLI层 (src/cli/)

**职责**：提供命令行交互界面

**主要组件**：
- `main.py`: CLI主入口，使用Click框架
- `commands/`: 子命令实现
  - `list_devices.py`: 列出设备
  - `list_testcases.py`: 列出测试用例
  - `list_tasks.py`: 列出任务
  - `run_task.py`: 执行任务
- `utils/`: CLI工具
  - `progress.py`: 进度显示
  - `display.py`: 格式化输出

**设计特点**：
- 使用Click框架简化命令定义
- 支持彩色输出和进度显示
- 统一的错误处理机制

### 2. 核心业务层 (src/core/)

#### 2.1 DeviceManager

**职责**：管理SSH连接和命令执行

**主要功能**：
- SSH连接建立和断开
- 命令执行和超时控制
- 环境变量加载
- 设备状态管理（正忙检测）

**关键方法**：
```python
connect(device: Device) -> bool
execute_command(device_id: str, command: str, timeout: int) -> Tuple[int, str, str]
disconnect(device_id: str) -> None
is_busy(device_id: str) -> bool
```

#### 2.2 TestExecutor

**职责**：执行测试用例和验证结果

**主要功能**：
- 执行测试场景
- 管理四个测试阶段
- 验证检查规则
- 生成测试步骤报告

**测试流程**：
```
setup → execute → verify → cleanup
```

**检查规则**：
- output_contains: 输出包含检查
- return_code: 返回值检查
- regex: 正则表达式匹配
- none: 不检查

#### 2.3 TaskRunner

**职责**：任务调度和执行控制

**主要功能**：
- 加载配置文件
- 验证任务配置
- 检查设备正忙
- 顺序执行设备测试
- 生成测试报告

**执行流程**：
```
1. 加载配置（设备、测试用例、任务）
2. 验证配置完整性
3. 检查设备状态
4. 对每台设备：
   a. 连接设备
   b. 执行所有测试用例
   c. 生成报告
   d. 断开连接
5. 汇总结果
```

#### 2.4 ReportGenerator

**职责**：生成测试报告

**主要功能**：
- 生成JSON格式报告
- 生成HTML格式报告
- 报告文件大小控制（100M限制）
- 使用Jinja2模板渲染

**报告结构**：
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

### 3. 基础层 (src/models/, src/parsers/, src/utils/, src/config/)

#### 3.1 Models (数据模型)

**实体定义**：
- `Device`: 待测设备
- `TestCase`: 测试用例
- `TestScenario`: 测试场景
- `ExecutionPhase`: 执行阶段
- `Task`: 测试任务
- `Report`: 测试报告
- `ReportStep`: 报告步骤

**设计特点**：
- 使用dataclass简化模型定义
- 类型提示保证类型安全
- 字段验证确保数据完整性

#### 3.2 Parsers (配置解析)

**YAMLParser**:
- 解析设备配置文件
- 解析测试用例配置文件
- 解析任务配置文件
- ID唯一性验证

**ConfigValidator**:
- 验证必需字段
- 验证字段类型
- 验证字段值有效性
- 验证引用完整性

#### 3.3 Utils (工具模块)

- `SSHClient`: SSH客户端封装
- `FileUtils`: 文件操作工具
- `TimeUtils`: 时间计算工具
- `Logger`: 日志记录

#### 3.4 Config (配置管理)

- `Settings`: 全局配置
- `PathManager`: 路径管理
- `Loader`: 配置加载器

### 4. 基础设施层

#### 4.1 SSH客户端

**技术选型**：Paramiko

**功能**：
- SSH连接建立
- 命令执行
- 超时控制
- 异常处理

#### 4.2 YAML解析

**技术选型**：PyYAML

**功能**：
- YAML文件解析
- 配置文件加载
- 格式验证

#### 4.3 模板引擎

**技术选型**：Jinja2

**功能**：
- HTML报告模板渲染
- 模板继承和复用
- 中文内容支持

## 数据流

### 任务执行流程

```
用户命令
    ↓
CLI解析参数
    ↓
TaskRunner加载配置
    ↓
验证配置有效性
    ↓
检查设备状态
    ↓
对每台设备：
    ├─ DeviceManager连接设备
    ├─ TestExecutor执行测试用例
    │   ├─ setup阶段
    │   ├─ execute阶段
    │   ├─ verify阶段（必需）
    │   └─ cleanup阶段
    └─ ReportGenerator生成报告
    ↓
返回执行结果
```

### 配置加载流程

```
YAML配置文件
    ↓
YAMLParser解析
    ↓
转换为Model对象
    ↓
ConfigValidator验证
    ↓
存入内存字典
    ↓
TaskRunner使用
```

## 并发控制

### 设备锁机制

```python
# 任务开始时锁定设备
if device_id in busy_devices:
    raise RuntimeError("设备正忙")

busy_devices.add(device_id)

try:
    # 执行测试
    ...
finally:
    # 任务结束时释放设备
    busy_devices.remove(device_id)
```

### 设计考虑

- **不支持并发执行**：根据需求明确不支持并发
- **设备正忙检测**：防止多个任务同时操作同一设备
- **优雅降级**：设备连接失败跳过并继续下一台设备

## 错误处理

### 错误类型

1. **配置错误** (ValueError)
   - 配置文件不存在
   - 配置字段缺失
   - 配置格式错误
   - 引用不存在

2. **连接错误** (ConnectionError)
   - SSH连接超时
   - 认证失败
   - 网络不通

3. **执行错误** (RuntimeError)
   - 命令执行失败
   - 检查规则失败
   - 设备正忙

### 错误处理策略

```python
try:
    # 尝试执行
    result = execute_test()
except ConfigurationError:
    # 配置错误：立即停止，提示用户修复
    logger.error("配置错误")
    raise
except ConnectionError:
    # 连接错误：跳过设备，继续下一台
    logger.warning("连接失败，跳过设备")
    continue
except ExecutionError:
    # 执行错误：根据配置决定是否继续
    if on_failure == "stop":
        break
    else:
        continue
```

## 性能考虑

### 性能指标

- SSH连接超时：10秒
- 命令执行超时：30秒（可配置）
- 报告文件大小限制：100MB
- 支持10台设备、20条测试用例

### 优化策略

1. **配置缓存**：加载后缓存在内存中
2. **顺序执行**：避免并发带来的资源竞争
3. **报告大小控制**：超过限制自动截断
4. **错误快速失败**：配置错误立即停止

## 扩展点

### 1. 检查规则扩展

在`TestExecutor._verify_output()`中添加新的检查规则：

```python
elif check == "custom_check":
    # 自定义检查逻辑
    return custom_verify(output, expected)
```

### 2. 报告格式扩展

在`ReportGenerator`中添加新的报告格式：

```python
def generate_report(self, report: Report, format: str) -> str:
    if format == "custom":
        return self._generate_custom_report(report)
```

### 3. 测试阶段扩展

在`TestExecutor.execute_scenario()`中添加新的测试阶段：

```python
# 在verify之后添加新阶段
if scenario.post_validate:
    step = self.execute_phase(...)
    steps.append(step)
```

## 测试策略

### 测试层次

1. **单元测试** (tests/unit/)
   - 测试每个模块的独立功能
   - 使用Mock隔离依赖
   - 覆盖率目标：90%+

2. **集成测试** (tests/integration/)
   - 测试模块间协作
   - 测试完整工作流
   - 测试错误场景

3. **契约测试** (tests/contract/)
   - 测试CLI命令格式
   - 测试报告格式
   - 测试YAML格式

### 测试数据

- 使用临时目录存放测试配置
- 使用Mock SSH客户端模拟远程执行
- 使用fixture管理测试资源

## 部署考虑

### 环境要求

- Python 3.9+
- Linux操作系统
- SSH服务（待测设备）

### 安装方式

```bash
# 开发模式
pip install -e .

# 生产模式
pip install .
```

### 配置管理

- 配置文件存储在`configs/`目录
- 日志文件存储在`logs/`目录
- 报告文件存储在`reports/`目录
- 环境变量覆盖配置（COREDUMP_*）

## 监控和日志

### 日志级别

- **INFO**: 正常执行流程
- **WARNING**: 警告信息（连接失败、检查失败）
- **ERROR**: 错误信息（配置错误、执行错误）

### 日志格式

```
[2026-04-08 14:30:22] [INFO]    开始执行任务: task001
[2026-04-08 14:30:22] [INFO]    正在连接设备: device001
[2026-04-08 14:30:25] [INFO]    执行测试用例: tc001
[2026-04-08 14:30:28] [WARNING] 检查规则失败
[2026-04-08 14:30:28] [ERROR]   测试用例失败
```

## 安全考虑

### 密码存储

- **当前方案**：明文存储在配置文件
- **建议**：使用环境变量或密钥管理服务
- **权限**：配置文件权限设置为600

### SSH安全

- 不保存SSH密钥
- 使用密码认证
- 连接超时控制
- 禁用SSH代理转发

### 配置文件安全

```bash
# 设置配置文件权限
chmod 600 configs/devices/devices.yaml

# 不提交敏感信息到版本控制
echo "configs/devices/*.yaml" >> .gitignore
```

## 未来改进

### 短期改进

- [ ] 添加更多检查规则
- [ ] 支持SSH密钥认证
- [ ] 支持配置文件加密
- [ ] 支持测试报告归档

### 长期改进

- [ ] 支持并发执行（可选）
- [ ] 支持Web界面
- [ ] 支持测试计划调度
- [ ] 支持测试结果统计分析
- [ ] 支持插件系统