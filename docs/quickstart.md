# Quick Start Guide: Coredump自动化测试框架

**Feature**: 001-automated-test-framework  
**Created**: 2026-04-08  
**Updated**: 2026-04-08 - 更新配置目录和YAML格式  
**Purpose**: 快速开始指南，帮助用户在5分钟内完成第一个测试任务

## 前置条件

- Linux操作系统
- Python 3.9+已安装
- 待测设备已配置SSH服务并允许远程连接

## 安装

```bash
# 克隆项目（假设）
git clone <repository-url>
cd coredump

# 安装依赖
pip install -r requirements.txt

# 验证安装
coredump --version
```

## 5分钟快速开始

### 步骤1: 配置待测设备（1分钟）

创建设备配置文件 `configs/devices/devices.yaml`:

```yaml
devices:
  - id: device001
    name: 我的测试设备
    ip: 192.168.1.100        # 替换为实际IP
    port: 22
    username: root           # 替换为实际用户名
    password: password123    # 替换为实际密码
    env_vars:                # 环境变量（可选，避免找不到命令路径）
      PATH: "/usr/local/bin:/usr/bin:/bin"
      JAVA_HOME: "/usr/lib/jvm/java-11"
```

**验证设备配置**:

```bash
coredump list devices
```

输出示例:
```
ID          Name            IP Address       Port    Username
----------  --------------  ---------------  ------  ----------
device001   我的测试设备     192.168.1.100    22      root
```

---

### 步骤2: 配置测试用例（2分钟）

创建测试用例配置文件 `configs/testcases/ping-test.yaml`:

```yaml
testcases:
  - id: tc001
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

**验证测试用例配置**:

```bash
coredump list testcases
```

输出示例:
```
ID          Name                Scenarios    Timeout    On Failure
----------  ------------------  -----------  ---------  -----------
tc001       网络连通性测试       1            30         stop
```

---

### 步骤3: 配置测试任务（1分钟）

创建测试任务配置文件 `configs/tasks/my-task.yaml`:

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

**验证测试任务配置**:

```bash
coredump list tasks
```

输出示例:
```
ID          Name                Devices    Testcases    Report Format    Status
----------  ------------------  ---------  -----------  ---------------  --------
task001     我的第一个测试任务   1          1            html             pending
```

---

### 步骤4: 执行测试任务（1分钟）

```bash
coredump run task001
```

**执行过程输出**:

```
[2026-04-08 14:30:22] [INFO]    开始执行任务: task001
[2026-04-08 14:30:22] [INFO]    正在连接设备: device001 (192.168.1.100)
[2026-04-08 14:30:22] [INFO]    加载环境变量: PATH=/usr/local/bin:/usr/bin:/bin, JAVA_HOME=/usr/lib/jvm/java-11
[2026-04-08 14:30:25] [INFO]    执行测试用例: tc001 - 网络连通性测试
[2026-04-08 14:30:25] [INFO]    场景 1: ping测试
[2026-04-08 14:30:25] [INFO]    阶段: setup
[2026-04-08 14:30:25] [INFO]    执行命令: date > /tmp/network_test.log - 通过
[2026-04-08 14:30:25] [INFO]    阶段: execute
[2026-04-08 14:30:25] [INFO]    执行命令: echo '开始测试' - 通过
[2026-04-08 14:30:25] [INFO]    阶段: verify
[2026-04-08 14:30:28] [INFO]    执行命令: ping -c 3 192.168.1.1 - 通过
[2026-04-08 14:30:28] [INFO]    检查规则: 输出包含 "0% packet loss" - 通过
[2026-04-08 14:30:28] [INFO]    阶段: cleanup
[2026-04-08 14:30:28] [INFO]    执行命令: rm -f /tmp/network_test.log - 通过
[2026-04-08 14:30:28] [INFO]    测试用例结果: 通过
[2026-04-08 14:30:28] [INFO]    生成测试报告: reports/task001_device001_20260408_143022.html
[2026-04-08 14:30:28] [INFO]    设备 device001 测试完成
[2026-04-08 14:30:28] [INFO]    任务执行完成

==================== 任务执行结果 ====================
任务ID: task001
任务名称: 我的第一个测试任务
执行时间: 6秒
测试设备数: 1
通过设备数: 1
失败设备数: 0
报告位置: reports/

设备详情:
  device001 (192.168.1.100): 通过
====================================================
```

---

### 步骤5: 查看测试报告

**HTML格式**:

```bash
# 使用浏览器打开
firefox reports/task001_device001_20260408_143022.html
# 或
google-chrome reports/task001_device001_20260408_143022.html
```

**JSON格式**:

```bash
# 使用jq工具查看
cat reports/task001_device001_20260408_143022.json | jq .

# 或直接查看
less reports/task001_device001_20260408_143022.json
```

---

## 环境变量配置说明

### 为什么需要配置环境变量？

在SSH连接远程设备执行命令时，可能会遇到以下问题：
- 提示"command not found"
- 找不到特定路径下的可执行文件
- 依赖的环境变量未设置

### 如何配置环境变量？

在设备配置文件中添加`env_vars`字段：

```yaml
devices:
  - id: device001
    name: Web服务器
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:
      PATH: "/usr/local/nginx/sbin:/usr/local/bin:/usr/bin:/bin"
      NGINX_HOME: "/usr/local/nginx"
      JAVA_HOME: "/usr/lib/jvm/java-11"
      PYTHONPATH: "/opt/myapp/lib"
```

### 执行流程

1. SSH连接成功后
2. 框架自动执行：`export PATH="/usr/local/nginx/sbin:..."`
3. 设置所有配置的环境变量
4. 然后执行测试命令

---

## 测试用例格式说明

### 两种阶段格式

#### 格式1: commands列表（推荐用于setup/execute/cleanup）

```yaml
setup:
  commands:
    - "mkdir -p /tmp/test"
    - "cd /tmp/test"
    - "touch testfile"
```

**特点**: 简洁，适合不需要检查规则的命令序列

#### 格式2: 命令对象列表（必须用于verify阶段）

```yaml
verify:
  - command: "ping -c 3 192.168.1.1"
    check: "output_contains"
    expected: "0% packet loss"
  - command: "systemctl status sshd"
    check: "return_code"
    expected: "0"
```

**特点**: 支持检查规则，verify阶段必须使用

### 检查类型

| check类型 | 说明 | expected示例 |
|-----------|------|--------------|
| output_contains | 输出包含指定字符 | "0% packet loss" |
| return_code | 返回值检查 | "0" |
| regex | 正则表达式匹配 | "Linux \\d+\\.\\d+" |
| none | 不检查 | 不需要expected |

---

## 常见问题

### Q1: SSH连接失败怎么办？

**错误信息**:
```
SSH连接超时 (10秒)
```

**解决方法**:
1. 检查设备IP地址是否正确
2. 检查设备SSH服务是否启动: `systemctl status sshd`
3. 检查网络连通性: `ping <device_ip>`
4. 检查防火墙规则: `iptables -L -n`
5. 尝试手动SSH连接: `ssh username@device_ip`

---

### Q2: 命令找不到怎么办？

**错误信息**:
```
bash: nginx: command not found
```

**解决方法**:
在设备配置中添加环境变量：

```yaml
devices:
  - id: device001
    name: Web服务器
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:                        # 可选：环境变量
      PATH: "/usr/local/nginx/sbin:/usr/bin:/bin"
```

---

### Q3: 配置文件验证失败怎么办？

**错误信息**:
```
错误: 配置文件验证失败
文件: configs/devices/devices.yaml
错误: 缺少必需字段 'password'
位置: devices[0]
```

**解决方法**:
1. 根据错误提示检查配置文件
2. 确保所有必需字段都已填写
3. 检查YAML格式（缩进、语法）
4. 参考示例配置文件

---

### Q4: 测试用例执行失败怎么办？

**错误信息**:
```
命令执行失败
检查规则未通过: 未找到指定字符串 "0% packet loss"
```

**解决方法**:
1. 查看测试报告中的错误信息
2. 检查命令是否正确
3. 手动在目标设备上执行命令验证
4. 检查expected值是否正确

---

### Q5: 如何支持多台设备测试？

**配置示例**:

```yaml
# configs/devices/devices.yaml
devices:
  - id: device001
    name: 测试设备1
    ip: 192.168.1.100
    port: 22
    username: root
    password: password123
    env_vars:                        # 可选：环境变量
      PATH: "/usr/local/bin:/usr/bin:/bin"
  
  - id: device002
    name: 测试设备2
    ip: 192.168.1.101
    port: 22
    username: root
    password: password456
    env_vars:                        # 可选：环境变量
      PATH: "/usr/bin:/bin"

# configs/tasks/multi-device-task.yaml
tasks:
  - id: task002
    name: 多设备测试任务
    devices:
      - device001
      - device002
    testcases:
      - tc001
    report_format: html
```

**执行**:
```bash
coredump run task002
```

系统会按顺序对每台设备执行测试，为每台设备生成一份报告。

---

### Q6: 如何处理测试失败？

**场景1: 测试用例失败后继续执行**

```yaml
testcases:
  - id: tc001
    name: 网络测试
    on_failure: continue  # 失败后继续执行后续步骤
```

**场景2: 测试用例失败后停止执行**

```yaml
testcases:
  - id: tc001
    name: 网络测试
    on_failure: stop  # 失败后停止执行（默认行为）
```

**场景3: 任务中某个测试用例失败后继续执行下一个用例**

```yaml
tasks:
  - id: task001
    name: 测试任务
    devices:
      - device001
    testcases:
      - tc001
      - tc002
    on_testcase_failure: continue  # 测试用例失败后继续执行下一个用例
```

---

## 下一步

### 进阶功能

1. **多测试场景**: 在一个测试用例中定义多个测试场景
2. **四阶段执行**: 使用setup、execute、verify、cleanup完整流程
3. **复杂检查规则**: 使用正则表达式、返回值检查
4. **环境变量管理**: 为不同设备配置不同的环境变量
5. **报告管理**: 定期清理、归档重要报告

### 示例项目

参考 `examples/` 目录中的示例配置文件：

- `examples/basic/`: 基础示例
- `examples/advanced/`: 高级示例
- `examples/real-world/`: 真实场景示例

### 文档

- **用户指南**: `docs/user-guide.md`
- **API文档**: `docs/api-reference.md`
- **架构文档**: `docs/architecture.md`
- **开发者指南**: `docs/developer-guide.md`

---

## 获取帮助

- **CLI帮助**: `coredump --help`
- **命令帮助**: `coredump run --help`
- **配置文件说明**: `contracts/yaml-configs.md`
- **CLI命令说明**: `contracts/cli-commands.md`

---

## 故障排查

### 日志查看

```bash
# 查看框架日志
tail -f logs/coredump.log

# 查看错误日志
grep ERROR logs/coredump.log
```

### 配置文件检查

```bash
# 验证YAML格式
python -c "import yaml; yaml.safe_load(open('configs/devices/devices.yaml'))"

# 查看配置文件内容
cat configs/devices/devices.yaml
```

### 网络连接测试

```bash
# 测试SSH连接
ssh username@device_ip

# 测试网络连通性
ping device_ip
```

---

恭喜！您已完成第一个测试任务。接下来可以探索更多高级功能和真实场景应用。