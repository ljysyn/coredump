# Data Model: Coredump自动化测试框架

**Feature**: 001-automated-test-framework  
**Created**: 2026-04-08  
**Purpose**: 定义核心实体模型、字段、关系和验证规则

## 实体关系图

```
Device (待测设备) 1:N Task (测试任务)
Task (测试任务) N:M TestCase (测试用例)
TestCase (测试用例) 1:N TestScenario (测试场景)
TestScenario (测试场景) 1:4 ExecutionPhase (执行阶段)
ExecutionPhase (执行阶段) 1:N VerificationRule (检查规则)
Task (测试任务) 1:N Report (测试报告)
```

## 核心实体定义

### 1. Device (待测设备)

**用途**: 代表需要进行测试的物理或虚拟设备

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| id | string | 是 | 设备唯一标识符 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 设备名称 | 非空，1-100字符 |
| ip | string | 是 | IP地址 | IPv4格式（如192.168.1.1） |
| port | integer | 是 | SSH端口 | 1-65535，默认22 |
| username | string | 是 | SSH用户名 | 非空，1-50字符 |
| password | string | 是 | SSH密码 | 非空，1-100字符（明文存储） |
| env_vars | dict | 否 | 环境变量 | 字典格式，避免命令找不到路径 |

**唯一性约束**: id必须在所有设备配置文件中全局唯一

**环境变量支持**: 通过`env_vars`字段配置环境变量，SSH连接后会先加载这些环境变量，避免执行命令时找不到路径

**示例**:
```yaml
id: device001
name: 测试设备1
ip: 192.168.1.100
port: 22
username: root
password: password123
env_vars:                        # 可选字段
  PATH: "/usr/local/bin:/usr/bin:/bin"
  JAVA_HOME: "/usr/lib/jvm/java-11"
  PYTHONPATH: "/opt/myapp/lib"
```

### 2. TestCase (测试用例)

**用途**: 定义具体测试内容和流程的配置单元

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| id | string | 是 | 测试用例唯一标识符 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 测试用例名称 | 非空，1-100字符 |
| scenarios | list[Scenario] | 是 | 测试场景列表 | 至少包含1个场景 |
| timeout | integer | 否 | 命令执行超时时间（秒） | 1-3600，默认30 |
| on_failure | enum | 否 | 失败后行为 | "continue"或"stop"，默认"stop" |

**唯一性约束**: id必须在所有测试用例配置文件中全局唯一

**示例**:
```yaml
id: tc001
name: 网络连通性测试
timeout: 30
on_failure: stop
scenarios:
  - name: ping测试
    setup:
      commands:
        - "date > /tmp/network_test.log"
    
    execute:
      commands:
        - "echo '开始测试'"
    
    verify:
      - command: "ping -c 3 192.168.1.1"
        check: "output_contains"
        expected: "0% packet loss"
    
    cleanup:
      commands:
        - "rm -f /tmp/network_test.log"
```

### 3. TestScenario (测试场景)

**用途**: 测试用例中的具体测试流程

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| name | string | 是 | 测试场景名称 | 非空，1-100字符 |
| setup | list[PhaseCommand] | 否 | 建立阶段命令列表 | 通过SSH远程执行 |
| execute | list[PhaseCommand] | 否 | 执行阶段命令列表 | 本地执行 |
| verify | list[PhaseCommand] | 是 | 校验阶段命令列表（必选） | 通过SSH远程执行 |
| cleanup | list[PhaseCommand] | 否 | 清理阶段命令列表 | 通过SSH远程执行 |

**阶段执行顺序**: setup → execute → verify → cleanup

**阶段特性**:
- **setup**: 可选，通过SSH远程执行，用于准备测试环境
- **execute**: 可选，本地执行，用于调用框架本地命令或脚本
- **verify**: 必选，通过SSH远程执行，用于验证测试结果
- **cleanup**: 可选，通过SSH远程执行，用于清理测试环境。执行失败将导致整体测试结果标记为失败

### 4. ExecutionPhase (执行阶段)

**用途**: 测试场景的组成部分，包含具体命令和检查规则

**支持两种格式**:

#### 格式1: 命令对象列表（支持检查规则）

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| command | string | 是 | 执行的命令 | 非空，支持双引号转义（\"） |
| check | string | 条件 | 检查类型 | verify阶段必需："output_contains"、"return_code"、"regex"、"none" |
| expected | string | 条件 | 期望值 | check不为"none"时必需 |

**示例**:
```yaml
verify:
  - command: "ping -c 3 192.168.1.1"
    check: "output_contains"
    expected: "0% packet loss"
  - command: "systemctl status sshd"
    check: "return_code"
    expected: "0"
  - command: "uname -a"
    check: "regex"
    expected: "Linux \\d+\\.\\d+"
  - command: "hostname"
    check: "none"  # 不检查，命令执行成功即通过
```

#### 格式2: 命令字符串列表（不支持检查规则）

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| commands | list[string] | 是 | 命令列表 | 非空列表，每个命令非空 |

**示例**:
```yaml
setup:
  commands:
    - "mkdir -p /tmp/test"
    - "cd /tmp/test"
    - "touch testfile"

cleanup:
  commands:
    - "rm -f /tmp/ping_test.log"
    - "rm -rf /tmp/test"
```

**格式选择建议**:
- **verify阶段**: 必须使用格式1（命令对象列表），因为需要检查规则
- **setup/execute/cleanup阶段**: 可选择格式1或格式2，推荐使用格式2（更简洁）

**命令转义规则**:
- 双引号字符串内使用`\"`转义
- 单引号字符串内无需转义
- YAML多行字符串块（`|-`或`>-`）可避免转义

### 5. Task (测试任务)

**用途**: 定义测试执行计划的配置单元

**字段定义**:

| 字段名 | 类型 | 必需 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| id | string | 是 | 测试任务唯一标识符 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 测试任务名称 | 非空，1-100字符 |
| devices | list[string] | 是 | 目标待测设备ID列表 | 至少包含1个设备ID，ID必须存在 |
| testcases | list[string] | 是 | 执行的测试用例ID列表 | 至少包含1个测试用例ID，ID必须存在 |
| on_testcase_failure | enum | 否 | 测试用例失败时是否结束 | "continue"或"stop"，默认"stop" |
| report_format | enum | 否 | 测试报告格式 | "json"或"html"，默认"json" |

**唯一性约束**: id必须在所有任务配置文件中全局唯一

**执行策略**:
- 按设备顺序依次对每台设备执行所有测试用例
- 对同一台设备，按测试用例顺序依次执行
- 为每台设备生成一份测试报告

**示例**:
```yaml
id: task001
name: 网络测试任务
devices:
  - device001
  - device002
testcases:
  - tc001
  - tc002
on_testcase_failure: continue
report_format: html
```

### 7. Report (测试报告)

**用途**: 记录测试执行结果的文件

**字段定义**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| task_name | string | 测试任务名称 |
| device_id | string | 待测设备ID |
| timestamp | datetime | 执行时间戳 |
| duration | float | 执行总时间（秒） |
| overall_result | enum | 整体测试结果（"pass"或"fail"） |
| steps | list[ReportStep] | 测试步骤详情列表 |

**文件命名规则**: `{task_name}_{device_id}_{timestamp}.json` 或 `{task_name}_{device_id}_{timestamp}.html`

**存储位置**: 统一存储在`reports/`目录

**文件大小限制**: 最大100M，超出部分不存储

**ReportStep字段定义**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| scenario_name | string | 测试场景名称 |
| phase | enum | 执行阶段（"setup"、"execute"、"verify"、"cleanup"） |
| command | string | 执行的命令 |
| output | string | 命令输出结果 |
| return_code | integer | 命令返回值（0表示成功，非0表示失败） |
| result | enum | 步骤结果（"pass"或"fail"） |
| error_message | string | 失败时的错误信息（可选） |
| duration | float | 步骤执行时间（秒） |
| check | string | 检查规则类型（可选，verify阶段） |
| expected | string | 检查规则值（可选，verify阶段） |

**部分失败标记规则**:
- 当测试用例配置"失败后继续"且有步骤失败时，报告标记整体结果为"fail"
- 详细记录失败步骤信息（命令、输出、错误原因、失败时间）

## 实体关系说明

### Device与Task关系
- **关系类型**: 一对多（1:N）
- **说明**: 一台设备可以被多个任务测试，一个任务可以测试多台设备
- **关联方式**: Task.devices字段存储Device.id列表

### Task与TestCase关系
- **关系类型**: 多对多（N:M）
- **说明**: 一个任务可以执行多个测试用例，一个测试用例可以被多个任务使用
- **关联方式**: Task.testcases字段存储TestCase.id列表

### TestCase与TestScenario关系
- **关系类型**: 一对多（1:N）
- **说明**: 一个测试用例包含多个测试场景
- **关联方式**: TestCase.scenarios字段存储TestScenario列表

### TestScenario与ExecutionPhase关系
- **关系类型**: 一对多（1:4）
- **说明**: 一个测试场景包含四个阶段（setup、execute、verify、cleanup）
- **关联方式**: TestScenario各阶段字段存储ExecutionPhase列表

### Task与Report关系
- **关系类型**: 一对多（1:N）
- **说明**: 一个任务为每台设备生成一份报告
- **关联方式**: 报告文件名包含task_name和device_id

## 数据验证规则

### 配置文件验证时机
- **时机**: 任务执行前
- **触发**: `coredump run <task_id>`命令执行时
- **范围**: 任务配置文件、关联的设备配置文件、测试用例配置文件

### 验证内容
1. **YAML格式正确性**: 语法错误、缩进错误
2. **必需字段完整性**: 检查所有必需字段是否存在
3. **字段类型正确性**: 检查字段类型是否符合定义
4. **字段值有效性**: 检查字段值是否在允许范围内
5. **唯一性约束**: 检查ID是否全局唯一
6. **引用完整性**: 检查Task.devices和Task.testcases引用的ID是否存在

### 错误处理
- 验证失败时拒绝执行任务
- 显示详细错误信息：文件路径、字段名称、错误类型
- 建议修复方案

## 状态转换

### Task执行状态

```
pending (待执行) → running (执行中) → completed (已完成) 或 failed (失败)
```

### TestCase执行结果

```
pass (通过) 或 fail (失败)
```

**失败判定条件**:
- SSH连接失败或超时
- 命令执行超时
- verify阶段检查失败
- cleanup阶段执行失败

### Step执行结果

```
pass (通过) 或 fail (失败)
```

**失败判定条件**:
- 命令执行失败（非零返回值）
- SSH连接断开
- 检查规则未通过