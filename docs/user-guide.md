# Coredump 用户指南

## 简介

Coredump是一个基于SSH的自动化测试框架，用于远程设备的批量测试。通过YAML配置文件定义测试任务，自动执行测试并生成详细报告。

## 安装

### 系统要求

- Python 3.9 或更高版本
- Linux操作系统
- SSH客户端

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd coredump

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
coredump --version

# 输出: coredump, version 0.1.0
```

## 快速开始

### 第一个测试任务

#### 1. 配置设备

创建 `configs/devices/devices.yaml`:

```yaml
devices:
  - id: device001
    name: 我的测试设备
    ip: 192.168.1.100        # 替换为实际IP
    port: 22
    username: root           # 替换为实际用户名
    password: password123    # 替换为实际密码
```

#### 2. 配置测试用例

创建 `configs/testcases/my_test.yaml`:

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

#### 3. 配置测试任务

创建 `configs/tasks/my_task.yaml`:

```yaml
tasks:
  - id: task001
    name: 我的第一个测试任务
    devices:
      - device001
    testcases:
      - tc001
    on_testcase_failure: stop
    report_format: html
```

#### 4. 执行测试

```bash
coredump run task001
```

#### 5. 查看报告

```bash
# HTML报告
firefox reports/task001_device001_*.html

# JSON报告
cat reports/task001_device001_*.json | jq .
```

## CLI命令详解

### coredump list

列出资源列表。

#### 列出设备

```bash
coredump list devices
```

输出示例：
```
================================================================================
ID              名称                 IP地址              端口      用户名
================================================================================
device001      测试设备1            192.168.1.100       22        root
device002      测试设备2            192.168.1.101       22        root
================================================================================
总计: 2 台设备
```

#### 列出测试用例

```bash
coredump list testcases
```

输出示例：
```
==========================================================================================
ID              名称                      场景数      超时(秒)    失败行为
==========================================================================================
tc001          网络连通性测试             1           30          stop
tc002          系统服务检查               2           60          continue
==========================================================================================
总计: 2 个测试用例
```

#### 列出任务

```bash
coredump list tasks
```

输出示例：
```
====================================================================================================
ID              名称                      设备数      用例数      报告格式      状态
====================================================================================================
task001        网络测试任务               2           2           html          pending
task002        系统测试任务               1           3           json          pending
====================================================================================================
总计: 2 个测试任务
```

### coredump run

执行测试任务。

```bash
coredump run <task_id>
```

示例：
```bash
coredump run task001
```

执行过程输出：
```
[2026-04-08 14:30:22] [INFO]    开始执行任务: task001
[2026-04-08 14:30:22] [INFO]    正在连接设备: device001 (192.168.1.100)
[2026-04-08 14:30:25] [INFO]    执行测试用例: tc001 - 网络连通性测试
[2026-04-08 14:30:25] [INFO]    场景: ping测试
[2026-04-08 14:30:25] [INFO]    阶段: verify
[2026-04-08 14:30:28] [INFO]    执行命令[通过]: ping -c 3 192.168.1.1
[2026-04-08 14:30:28] [INFO]    检查规则[通过]: 输出包含 '0% packet loss'
[2026-04-08 14:30:28] [INFO]    测试用例结果: 通过
[2026-04-08 14:30:28] [INFO]    生成测试报告: reports/task001_device001_20260408_143022.html

================================================================================
任务执行结果
================================================================================
任务ID: task001
任务名称: 网络测试任务
开始时间: 2026-04-08T14:30:22
结束时间: 2026-04-08T14:30:28
执行耗时: 6.00秒

设备测试结果:
  device001: ✓ 通过
    报告: reports/task001_device001_20260408_143022.html

通过设备: 1
失败设备: 0
================================================================================
```

### 帮助命令

```bash
# 查看版本
coredump --version

# 查看帮助
coredump --help

# 查看子命令帮助
coredump list --help
coredump run --help
```

## 配置文件详解

### 设备配置

**文件位置**: `configs/devices/*.yaml`

**字段说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 设备唯一标识符，字母数字下划线 |
| name | string | 是 | 设备名称 |
| ip | string | 是 | IPv4地址 |
| port | integer | 是 | SSH端口，1-65535 |
| username | string | 是 | SSH用户名 |
| password | string | 是 | SSH密码 |
| env_vars | dict | 否 | 环境变量字典 |

**示例**:

```yaml
devices:
  - id: web_server_01
    name: Web服务器01
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/nginx/sbin:/usr/bin:/bin
      NGINX_HOME: /usr/local/nginx

  - id: db_server_01
    name: 数据库服务器01
    ip: 192.168.1.101
    port: 22
    username: root
    password: password456
    env_vars:
      PATH: /usr/local/mysql/bin:/usr/bin:/bin
      MYSQL_HOME: /usr/local/mysql
```

### 测试用例配置

**文件位置**: `configs/testcases/*.yaml`

**字段说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 测试用例唯一标识符 |
| name | string | 是 | 测试用例名称 |
| timeout | integer | 否 | 命令执行超时时间（秒），默认30 |
| on_failure | enum | 否 | 失败行为："stop"或"continue"，默认"stop" |
| scenarios | list | 是 | 测试场景列表，至少1个 |

**测试场景字段**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 是 | 场景名称 |
| setup | list/dict | 否 | 建立阶段（SSH远程执行） |
| execute | list/dict | 否 | 执行阶段（本地执行） |
| verify | list | 是 | 验证阶段（SSH远程执行，必需） |
| cleanup | list/dict | 否 | 清理阶段（SSH远程执行） |

**完整示例**:

```yaml
testcases:
  - id: tc_network_001
    name: 网络连通性测试
    timeout: 30
    on_failure: stop
    scenarios:
      - name: ping网关测试
        setup:
          commands:
            - "mkdir -p /tmp/test"
            - "date > /tmp/test/network.log"
        
        execute:
          commands:
            - "echo '开始测试'"
        
        verify:
          - command: "ping -c 3 192.168.1.1"
            check: "output_contains"
            expected: "0% packet loss"
          
          - command: "ping -c 1 192.168.1.1"
            check: "return_code"
            expected: "0"
        
        cleanup:
          commands:
            - "rm -f /tmp/test/network.log"
            - "rm -rf /tmp/test"
```

### 任务配置

**文件位置**: `configs/tasks/*.yaml`

**字段说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 任务唯一标识符 |
| name | string | 是 | 任务名称 |
| devices | list | 是 | 设备ID列表 |
| testcases | list | 是 | 测试用例ID列表 |
| on_testcase_failure | enum | 否 | 用例失败行为："continue"或"stop"，默认"stop" |
| report_format | enum | 否 | 报告格式："json"或"html"，默认"json" |

**示例**:

```yaml
tasks:
  - id: task_daily_001
    name: 每日系统检查
    devices:
      - web_server_01
      - db_server_01
    testcases:
      - tc_network_001
      - tc_system_001
      - tc_service_001
    on_testcase_failure: continue
    report_format: html
```

## 检查规则详解

### 1. output_contains

检查输出是否包含指定字符串。

```yaml
- command: "ping -c 3 192.168.1.1"
  check: "output_contains"
  expected: "0% packet loss"
```

### 2. return_code

检查命令返回值。

```yaml
- command: "systemctl status nginx"
  check: "return_code"
  expected: "0"
```

### 3. regex

使用正则表达式匹配输出。

```yaml
- command: "uname -a"
  check: "regex"
  expected: "Linux \\d+\\.\\d+"
```

### 4. none

不检查，命令执行成功即通过。

```yaml
- command: "hostname"
  check: "none"
```

## 高级用法

### 环境变量配置

避免命令找不到路径：

```yaml
devices:
  - id: device001
    name: Web服务器
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: /usr/local/nginx/sbin:/usr/local/bin:/usr/bin:/bin
      NGINX_HOME: /usr/local/nginx
      JAVA_HOME: /usr/lib/jvm/java-11
```

### 多设备测试

对多台设备执行相同测试：

```yaml
tasks:
  - id: task001
    name: 批量测试
    devices:
      - device001
      - device002
      - device003
    testcases:
      - tc001
      - tc002
```

系统会：
1. 按顺序对每台设备执行测试
2. 为每台设备生成独立报告
3. 设备连接失败时跳过并继续下一台

### 失败处理策略

#### 测试用例级别

```yaml
testcases:
  - id: tc001
    name: 测试用例
    on_failure: continue  # 失败后继续执行后续步骤
```

#### 任务级别

```yaml
tasks:
  - id: task001
    name: 任务
    on_testcase_failure: continue  # 用例失败后继续下一个用例
```

### 报告格式选择

#### JSON格式

适合程序处理：

```yaml
tasks:
  - id: task001
    report_format: json
```

#### HTML格式

适合人工查看：

```yaml
tasks:
  - id: task001
    report_format: html
```

## 故障排查

### SSH连接失败

**错误信息**:
```
SSH连接超时 (10秒)
```

**解决方法**:
1. 检查IP地址是否正确
2. 检查SSH服务是否启动
   ```bash
   systemctl status sshd
   ```
3. 测试网络连通性
   ```bash
   ping 192.168.1.100
   ```
4. 手动测试SSH连接
   ```bash
   ssh root@192.168.1.100
   ```

### 命令找不到

**错误信息**:
```
bash: nginx: command not found
```

**解决方法**:

在设备配置中添加环境变量：

```yaml
env_vars:
  PATH: /usr/local/nginx/sbin:/usr/bin:/bin
```

### 配置文件验证失败

**错误信息**:
```
配置文件验证失败
文件: configs/devices/devices.yaml
错误: 缺少必需字段 'password'
```

**解决方法**:

根据错误提示检查配置文件，确保所有必需字段都已填写。

### 测试用例执行失败

**错误信息**:
```
检查规则失败: 未找到指定字符串 "0% packet loss"
```

**解决方法**:
1. 查看测试报告中的错误信息
2. 手动在目标设备上执行命令验证
3. 检查expected值是否正确

### 设备正忙

**错误信息**:
```
设备正忙: device001，请等待当前任务完成
```

**解决方法**:

等待当前任务完成后再执行新任务。

### 查看详细日志

```bash
# 实时查看日志
tail -f logs/coredump.log

# 查看错误日志
grep ERROR logs/coredump.log
```

## 最佳实践

### 1. 配置文件组织

按功能模块拆分配置文件：

```
configs/
├── devices/
│   ├── web_servers.yaml    # Web服务器
│   ├── db_servers.yaml     # 数据库服务器
│   └── app_servers.yaml    # 应用服务器
├── testcases/
│   ├── network.yaml        # 网络测试
│   ├── system.yaml         # 系统测试
│   └── service.yaml        # 服务测试
└── tasks/
    ├── daily_check.yaml    # 日常检查
    └── weekly_report.yaml  # 周报任务
```

### 2. ID命名规范

使用有意义的前缀：

```yaml
# 设备ID
dev_web_01
dev_db_01

# 测试用例ID
tc_network_001
tc_system_001

# 任务ID
task_daily_check
task_weekly_report
```

### 3. 测试用例设计

- 每个测试用例专注于一个测试目标
- 使用清晰的场景名称
- 合理设置超时时间
- 为失败情况提供有用的错误信息

### 4. 安全建议

- 配置文件权限设置为600
- 不在版本控制中提交敏感信息
- 使用环境变量覆盖敏感配置

```bash
chmod 600 configs/devices/*.yaml
```

### 5. 报告管理

定期清理和归档测试报告：

```bash
# 归档上周报告
mkdir -p reports/archive/$(date -d "last week" +%Y%m%d)
mv reports/*.json reports/archive/$(date -d "last week" +%Y%m%d)/
mv reports/*.html reports/archive/$(date -d "last week" +%Y%m%d)/
```

## 示例场景

### 场景1: Web服务健康检查

```yaml
testcases:
  - id: tc_web_health
    name: Web服务健康检查
    timeout: 60
    on_failure: continue
    scenarios:
      - name: Nginx服务检查
        verify:
          - command: "systemctl status nginx"
            check: "return_code"
            expected: "0"
          - command: "curl -I http://localhost"
            check: "output_contains"
            expected: "HTTP/1.1 200 OK"
      
      - name: 端口监听检查
        verify:
          - command: "netstat -tuln | grep :80"
            check: "output_contains"
            expected: ":80"
```

### 场景2: 数据库连接测试

```yaml
testcases:
  - id: tc_db_connection
    name: 数据库连接测试
    timeout: 30
    scenarios:
      - name: MySQL服务检查
        setup:
          commands:
            - "echo 'Testing MySQL connection' > /tmp/mysql_test.log"
        
        verify:
          - command: "systemctl status mysqld"
            check: "return_code"
            expected: "0"
          - command: "mysql -e 'SELECT 1'"
            check: "return_code"
            expected: "0"
        
        cleanup:
          commands:
            - "rm -f /tmp/mysql_test.log"
```

### 场景3: 系统资源检查

```yaml
testcases:
  - id: tc_system_resource
    name: 系统资源检查
    scenarios:
      - name: 磁盘空间检查
        verify:
          - command: "df -h / | grep -v Use%"
            check: "regex"
            expected: "\\d+G\\s+\\d+G\\s+\\d+G\\s+[0-8]\\d%"
      
      - name: 内存使用检查
        verify:
          - command: "free -m | grep Mem"
            check: "regex"
            expected: "Mem:\\s+\\d+\\s+\\d+\\s+\\d+"
      
      - name: CPU负载检查
        verify:
          - command: "uptime"
            check: "regex"
            expected: "load average: [0-2]\\.\\d+"
```

## 参考文档

- [配置文件格式](specs/001-automated-test-framework/contracts/yaml-configs.md)
- [CLI命令说明](specs/001-automated-test-framework/contracts/cli-commands.md)
- [报告格式说明](specs/001-automated-test-framework/contracts/report-format.md)
- [架构文档](architecture.md)
- [API参考](api-reference.md)