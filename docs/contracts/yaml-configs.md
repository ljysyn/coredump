# YAML Configuration File Contract

**Feature**: 001-automated-test-framework  
**Created**: 2026-04-08  
**Updated**: 2026-04-08 - 根据a.yaml示例调整格式  
**Purpose**: 定义YAML配置文件格式规范

## 配置文件目录结构

```
configs/
├── devices/          # 待测设备配置文件目录
│   ├── devices.yaml  # 示例配置文件
│   └── ...
├── testcases/        # 测试用例配置文件目录
│   ├── network.yaml  # 网络测试用例
│   ├── system.yaml   # 系统测试用例
│   └── ...
├── tasks/            # 测试任务配置文件目录
│   ├── daily.yaml    # 日常测试任务
│   └── ...
└── settings.yaml     # 全局配置文件
```

## 1. 设备配置文件格式

**文件位置**: `configs/devices/*.yaml`

**格式规范**:

```yaml
devices:
  - id: device001                    # 设备ID（必需，全局唯一）
    name: 测试设备1                   # 设备名称（必需）
    ip: 192.168.1.100                # IP地址（必需，IPv4格式）
    port: 22                         # SSH端口（必需，1-65535）
    username: root                   # SSH用户名（必需）
    password: password123            # SSH密码（必需，明文存储）
    env_vars:                        # 环境变量（可选）
      PATH: "/usr/local/bin:/usr/bin:/bin"
      JAVA_HOME: "/usr/lib/jvm/java-11"
      PYTHONPATH: "/opt/myapp/lib"
  
  - id: device002
    name: 测试设备2
    ip: 192.168.1.101
    port: 22
    username: root
    password: password456
    env_vars:                        # 环境变量（可选）
      PATH: "/usr/bin:/bin"
```

**字段验证规则**:

| 字段 | 类型 | 必需 | 验证规则 |
|------|------|------|----------|
| id | string | 是 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 非空，1-100字符 |
| ip | string | 是 | IPv4格式（正则：`^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$`） |
| port | integer | 是 | 1-65535，默认22 |
| username | string | 是 | 非空，1-50字符 |
| password | string | 是 | 非空，1-100字符 |
| env_vars | dict | 否 | 环境变量字典，键值对格式 |

**环境变量说明**:
- `env_vars`字段用于配置SSH连接后需要加载的环境变量
- 避免执行命令时找不到路径的问题
- 常见环境变量：PATH、JAVA_HOME、PYTHONPATH、LD_LIBRARY_PATH等
- SSH连接后会先执行`export KEY=VALUE`设置环境变量

**多文件支持**: 可以有多个YAML文件，每个文件可包含多个设备定义，ID必须全局唯一

**示例错误**:

```yaml
devices:
  - id: device001
    name: 测试设备1
    ip: 192.168.1.100
    # 缺少 port、username、password 字段
```

**验证错误信息**:
```
文件: configs/devices/devices.yaml
错误: 缺少必需字段
位置: devices[0]
缺少字段: port, username, password
```

---

## 2. 测试用例配置文件格式

**文件位置**: `configs/testcases/*.yaml`

**格式规范** (基于a.yaml示例):

```yaml
testcases:
  - id: tc001                          # 测试用例ID（必需，全局唯一）
    name: 网络连通性测试                 # 测试用例名称（必需）
    timeout: 30                        # 命令执行超时时间（可选，默认30秒）
    on_failure: stop                   # 失败后行为（可选，stop或continue，默认stop）
    scenarios:                         # 测试场景列表（必需，至少1个）
      - name: ping测试                  # 场景名称（必需）
        setup:                         # 建立阶段（可选，SSH远程执行）
          commands:                    # 使用commands列表（推荐）
            - "mkdir -p /tmp/test"
            - "cd /tmp/test"
            - "touch testfile"
        
        execute:                       # 执行阶段（可选，本地执行）
          commands:
            - "echo '本地执行测试'"
            - "ls -la"
        
        verify:                        # 校验阶段（必需，SSH远程执行）
          - command: "ping -c 3 192.168.1.1"
            check: "output_contains"   # 检查类型
            expected: "0% packet loss" # 期望值
          - command: "ping -c 1 192.168.1.1"
            check: "output_contains"
            expected: "1 packets transmitted"
        
        cleanup:                       # 清理阶段（可选，SSH远程执行）
          commands:
            - "rm -f /tmp/ping_test.log"
            - "rm -rf /tmp/test"
  
  - id: tc002
    name: 系统服务检查
    timeout: 60
    on_failure: continue
    scenarios:
      - name: SSH服务检查
        verify:
          - command: "systemctl status sshd"
            check: "return_code"
            expected: "0"
      
      - name: 磁盘空间检查
        verify:
          - command: "df -h /"
            check: "output_contains"
            expected: "Filesystem"
          - command: "df -h / | grep -v Use%"
            check: "regex"
            expected: "\\d+G\\s+\\d+G\\s+\\d+G\\s+\\d+%"
```

**字段验证规则**:

| 字段 | 类型 | 必需 | 验证规则 |
|------|------|------|----------|
| id | string | 是 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 非空，1-100字符 |
| timeout | integer | 否 | 1-3600，默认30 |
| on_failure | enum | 否 | "stop"或"continue"，默认"stop" |
| scenarios | list | 是 | 至少包含1个场景 |

**Scenario字段验证规则**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 是 | 场景名称 |
| setup | list或dict | 否 | 建立阶段（支持两种格式） |
| execute | list或dict | 否 | 执行阶段（支持两种格式） |
| verify | list | 是 | 校验阶段（必须，命令对象列表） |
| cleanup | list或dict | 否 | 清理阶段（支持两种格式） |

**阶段格式说明**:

### 格式1: commands列表（适用于setup/execute/cleanup）

```yaml
setup:
  commands:
    - "mkdir -p /tmp/test"
    - "cd /tmp/test"
    - "touch testfile"
```

**特点**:
- 简洁，适合不需要检查规则的命令序列
- 推荐用于setup、execute、cleanup阶段
- 命令按顺序依次执行

### 格式2: 命令对象列表（适用于所有阶段，verify必须使用）

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
    check: "none"  # 不检查
```

**命令对象字段**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| command | string | 是 | 执行的命令 |
| check | string | 条件 | 检查类型（verify阶段必需） |
| expected | string | 条件 | 期望值（check不为"none"时必需） |

**检查类型说明**:
- **output_contains**: 输出包含指定字符
- **return_code**: 返回值检查（如"0"表示成功）
- **regex**: 输出命中正则表达式
- **none**: 不检查（命令执行成功即判定为通过）

**命令转义规则**:

1. **双引号字符串内使用反斜杠转义**:
```yaml
command: "echo \"Hello World\""
```

2. **单引号字符串无需转义**:
```yaml
command: 'echo "Hello World"'
```

3. **多行字符串块避免转义**:
```yaml
command: |
  echo "Hello World"
  echo "Multiple lines"
```

**完整示例：复杂测试用例**:

```yaml
testcases:
  - id: tc003
    name: 综合系统测试
    timeout: 120
    on_failure: continue
    scenarios:
      - name: 环境准备
        setup:
          commands:
            - "mkdir -p /tmp/test"
            - "chmod 755 /tmp/test"
      
      - name: 系统信息收集
        execute:
          commands:
            - "hostname"
            - "uname -a"
        
        verify:
          - command: "uname -a"
            check: "regex"
            expected: "Linux \\d+\\.\\d+"
          
          - command: "df -h"
            check: "output_contains"
            expected: "Filesystem"
          
          - command: "free -m"
            check: "output_contains"
            expected: "Mem:"
          
          - command: "hostname"
            check: "none"  # 不检查，命令执行成功即通过
      
      - name: 清理环境
        cleanup:
          commands:
            - "rm -rf /tmp/test"
            - "echo 'Cleanup completed'"
```

---

## 3. 测试任务配置文件格式

**文件位置**: `configs/tasks/*.yaml`

**格式规范**:

```yaml
tasks:
  - id: task001                       # 任务ID（必需，全局唯一）
    name: 网络测试任务                  # 任务名称（必需）
    devices:                          # 目标设备ID列表（必需，至少1个）
      - device001
      - device002
    testcases:                        # 测试用例ID列表（必需，至少1个）
      - tc001
      - tc002
    on_testcase_failure: continue     # 测试用例失败时是否结束（可选，continue或stop，默认stop）
    report_format: html               # 报告格式（可选，json或html，默认json）
  
  - id: task002
    name: 系统测试任务
    devices:
      - device001
    testcases:
      - tc003
    on_testcase_failure: stop
    report_format: json
```

**字段验证规则**:

| 字段 | 类型 | 必需 | 验证规则 |
|------|------|------|----------|
| id | string | 是 | 全局唯一，字母数字下划线，1-50字符 |
| name | string | 是 | 非空，1-100字符 |
| devices | list[string] | 是 | 至少包含1个设备ID，引用的ID必须存在 |
| testcases | list[string] | 是 | 至少包含1个测试用例ID，引用的ID必须存在 |
| on_testcase_failure | enum | 否 | "continue"或"stop"，默认"stop" |
| report_format | enum | 否 | "json"或"html"，默认"json" |

**引用完整性验证**:

任务执行前验证：
- `devices`列表中的所有设备ID必须在设备配置文件中存在
- `testcases`列表中的所有测试用例ID必须在测试用例配置文件中存在

**示例错误**:

```yaml
tasks:
  - id: task003
    name: 错误任务
    devices:
      - device999  # 不存在的设备ID
    testcases:
      - tc999      # 不存在的测试用例ID
```

**验证错误信息**:
```
文件: configs/tasks/tasks.yaml
错误: 引用的设备ID不存在
位置: tasks[0].devices[0]
设备ID: device999

错误: 引用的测试用例ID不存在
位置: tasks[0].testcases[0]
测试用例ID: tc999
```

---

## 4. 全局配置文件格式

**文件位置**: `configs/settings.yaml`

**格式规范**:

```yaml
ssh:
  timeout: 10              # SSH连接超时时间（秒），默认10
  retry_count: 0           # SSH连接重试次数，默认0

execution:
  default_timeout: 30      # 默认命令执行超时时间（秒），默认30

report:
  max_size_mb: 100         # 报告文件最大大小（MB），默认100
  default_format: json     # 默认报告格式，默认json

logging:
  level: INFO              # 日志级别，默认INFO
  file: logs/coredump.log  # 日志文件路径

paths:
  devices_dir: configs/devices      # 设备配置文件目录
  testcases_dir: configs/testcases  # 测试用例配置文件目录
  tasks_dir: configs/tasks          # 任务配置文件目录
  reports_dir: reports              # 报告输出目录
```

**配置层级覆盖**:
1. 全局配置: `configs/settings.yaml`
2. 环境变量覆盖:
   - `COREDUMP_SSH_TIMEOUT`
   - `COREDUMP_DEFAULT_TIMEOUT`
   - `COREDUMP_REPORT_MAX_SIZE`
   - `COREDUMP_LOG_LEVEL`
   - `COREDUMP_DEVICES_DIR`
   - `COREDUMP_REPORTS_DIR`

---

## 验证机制

### 验证时机
- 任务执行前（`coredump run <task_id>`命令）
- 配置文件加载时

### 验证内容
1. **YAML格式正确性**: 语法错误、缩进错误、编码错误
2. **必需字段完整性**: 检查所有必需字段是否存在
3. **字段类型正确性**: 检查字段类型是否符合定义
4. **字段值有效性**: 检查字段值是否在允许范围内
5. **唯一性约束**: 检查ID是否全局唯一
6. **引用完整性**: 检查引用的ID是否存在
7. **环境变量格式**: 检查env_vars字段格式是否正确

### 错误处理
- 验证失败时拒绝执行任务
- 显示详细错误信息：文件路径、字段位置、错误类型、修复建议
- 返回非零退出码

---

## 最佳实践

### 1. 配置文件组织
- 按功能模块拆分配置文件（网络测试、系统测试、性能测试）
- 使用有意义的文件名（`network.yaml`、`system.yaml`）
- 为复杂配置添加注释说明

### 2. ID命名规范
- 使用有意义的前缀（`dev_`、`tc_`、`task_`）
- 使用描述性名称（`dev_firewall_01`、`tc_network_ping`）

### 3. 环境变量管理
- 为需要特殊路径的设备配置env_vars
- 常见环境变量：PATH、JAVA_HOME、PYTHONPATH
- 避免硬编码路径，使用环境变量提高可移植性

### 4. 测试用例设计
- verify阶段必须使用命令对象列表（格式2）
- setup/execute/cleanup推荐使用commands列表（格式1）
- 为每个测试场景提供清晰的名称
- 合理设置timeout和on_failure策略

### 5. 安全建议
- 配置文件权限设置为600（仅用户可读）
- 避免在版本控制中提交敏感信息（密码）
- 使用环境变量覆盖敏感配置

### 6. 版本控制
- 将配置文件纳入版本控制
- 使用示例配置文件（`.example.yaml`）
- 文档化配置文件结构和字段说明

---

## 完整示例

### 设备配置示例

```yaml
# configs/devices/servers.yaml
devices:
  - id: web_server_01
    name: Web服务器01
    ip: 192.168.1.100
    port: 22
    username: testuser
    password: testpass123
    env_vars:                        # 可选：环境变量
      PATH: "/usr/local/nginx/sbin:/usr/local/bin:/usr/bin:/bin"
      NGINX_HOME: "/usr/local/nginx"
  
  - id: db_server_01
    name: 数据库服务器01
    ip: 192.168.1.101
    port: 22
    username: testuser
    password: testpass456
    env_vars:                        # 可选：环境变量
      PATH: "/usr/local/mysql/bin:/usr/bin:/bin"
      MYSQL_HOME: "/usr/local/mysql"
```

### 测试用例配置示例

```yaml
# configs/testcases/network.yaml
testcases:
  - id: tc_network_001
    name: 网络连通性测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping网关
        setup:
          commands:
            - "date > /tmp/network_test.log"
        verify:
          - command: "ping -c 3 192.168.1.1"
            check: "output_contains"
            expected: "0% packet loss"
        cleanup:
          commands:
            - "rm -f /tmp/network_test.log"
  
  - id: tc_network_002
    name: DNS解析测试
    timeout: 20
    on_failure: continue
    scenarios:
      - name: 解析百度域名
        verify:
          - command: "nslookup www.baidu.com"
            check: "output_contains"
            expected: "Server:"
```

### 测试任务配置示例

```yaml
# configs/tasks/daily_check.yaml
tasks:
  - id: task_daily_001
    name: 每日网络检查
    devices:
      - web_server_01
      - db_server_01
    testcases:
      - tc_network_001
      - tc_network_002
    on_testcase_failure: continue
    report_format: html
```