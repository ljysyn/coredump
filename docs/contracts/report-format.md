# Test Report Format Contract

**Feature**: 001-automated-test-framework  
**Created**: 2026-04-08  
**Purpose**: 定义测试报告格式规范（JSON和HTML）

## 报告文件命名规范

**格式**: `{task_name}_{device_id}_{timestamp}.{format}`

**示例**:
- JSON格式: `task001_device001_20260408_143022.json`
- HTML格式: `task001_device001_20260408_143022.html`

**字段说明**:
- `task_name`: 测试任务名称（从Task.name获取）
- `device_id`: 待测设备ID（从Device.id获取）
- `timestamp`: 执行时间戳（格式：YYYYMMDD_HHMMSS）
- `format`: 报告格式（json或html）

**存储位置**: 统一存储在 `reports/` 目录

---

## 1. JSON报告格式

**文件扩展名**: `.json`

**数据结构**:

```json
{
  "meta": {
    "task_id": "task001",
    "task_name": "网络测试任务",
    "device_id": "device001",
    "device_name": "测试设备1",
    "device_ip": "192.168.1.100",
    "timestamp": "2026-04-08T14:30:22",
    "duration_seconds": 14.5,
    "overall_result": "pass"
  },
  "summary": {
    "total_testcases": 2,
    "passed_testcases": 2,
    "failed_testcases": 0,
    "total_scenarios": 3,
    "passed_scenarios": 3,
    "failed_scenarios": 0,
    "total_steps": 12,
    "passed_steps": 12,
    "failed_steps": 0
  },
  "testcases": [
    {
      "testcase_id": "tc001",
      "testcase_name": "网络连通性测试",
      "result": "pass",
      "duration_seconds": 8.2,
      "scenarios": [
        {
          "scenario_name": "ping测试",
          "result": "pass",
          "duration_seconds": 8.2,
          "phases": {
            "setup": {
              "steps": [
                {
                  "command": "ping -c 1 192.168.1.1",
                  "output": "PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.\n64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms\n\n--- 192.168.1.1 ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.123/0.123/0.123/0.000 ms",
                  "return_code": 0,
                  "result": "pass",
                  "duration_seconds": 1.2,
                  "check": "output_contains",
                  "expected": "1 packets transmitted",
                  "check_passed": true
                }
              ],
              "result": "pass",
              "duration_seconds": 1.2
            },
            "execute": {
              "steps": [
                {
                  "command": "echo '本地执行测试'",
                  "output": "本地执行测试\n",
                  "return_code": 0,
                  "result": "pass",
                  "duration_seconds": 0.01
                }
              ],
              "result": "pass",
              "duration_seconds": 0.01
            },
            "verify": {
              "steps": [
                {
                  "command": "ping -c 3 192.168.1.1",
                  "output": "PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.\n64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms\n64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.124 ms\n64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.125 ms\n\n--- 192.168.1.1 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2001ms\nrtt min/avg/max/mdev = 0.123/0.124/0.125/0.001 ms",
                  "return_code": 0,
                  "result": "pass",
                  "duration_seconds": 3.2,
                  "check": "output_contains",
                  "expected": "0% packet loss",
                  "check_passed": true
                }
              ],
              "result": "pass",
              "duration_seconds": 3.2
            },
            "cleanup": {
              "steps": [
                {
                  "command": "rm -f /tmp/ping_test.log",
                  "output": "",
                  "return_code": 0,
                  "result": "pass",
                  "duration_seconds": 0.5
                }
              ],
              "result": "pass",
              "duration_seconds": 0.5
            }
          }
        }
      ]
    }
  ]
}
```

**字段说明**:

### meta（元数据）

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 测试任务ID |
| task_name | string | 测试任务名称 |
| device_id | string | 待测设备ID |
| device_name | string | 待测设备名称 |
| device_ip | string | 待测设备IP地址 |
| timestamp | string | 执行时间戳（ISO 8601格式） |
| duration_seconds | float | 执行总时间（秒） |
| overall_result | enum | 整体测试结果（"pass"或"fail"） |

### summary（摘要）

| 字段 | 类型 | 说明 |
|------|------|------|
| total_testcases | integer | 总测试用例数 |
| passed_testcases | integer | 通过的测试用例数 |
| failed_testcases | integer | 失败的测试用例数 |
| total_scenarios | integer | 总测试场景数 |
| passed_scenarios | integer | 通过的测试场景数 |
| failed_scenarios | integer | 失败的测试场景数 |
| total_steps | integer | 总测试步骤数 |
| passed_steps | integer | 通过的测试步骤数 |
| failed_steps | integer | 失败的测试步骤数 |

### testcases（测试用例详情）

每个测试用例包含：
- testcase_id: 测试用例ID
- testcase_name: 测试用例名称
- result: 测试结果（"pass"或"fail"）
- duration_seconds: 执行时间（秒）
- scenarios: 测试场景列表

### scenarios（测试场景详情）

每个测试场景包含：
- scenario_name: 场景名称
- result: 测试结果
- duration_seconds: 执行时间
- phases: 四个阶段详情（setup、execute、verify、cleanup）

### phases（阶段详情）

每个阶段包含：
- steps: 步骤列表
- result: 阶段结果
- duration_seconds: 阶段执行时间

### steps（步骤详情）

每个步骤包含：
- command: 执行的命令
- output: 命令输出
- return_code: 命令返回值（integer，0表示成功，非0表示失败）
- result: 步骤结果（"pass"或"fail"）
- duration_seconds: 步骤执行时间
- check: 检查类型（可选，verify阶段）
- expected: 期望值（可选，verify阶段）
- error_message: 失败时的错误信息（可选）

---

## 2. HTML报告格式

**文件扩展名**: `.html`

**文档结构**:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - task001 - device001</title>
    <style>
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .testcase {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .scenario {
            margin-left: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .phase {
            margin-left: 20px;
            margin-bottom: 10px;
        }
        .step {
            margin-left: 20px;
            padding: 10px;
            background-color: #fff;
            border-left: 3px solid #ddd;
            margin-bottom: 10px;
        }
        .pass {
            color: #28a745;
            font-weight: bold;
        }
        .fail {
            color: #dc3545;
            font-weight: bold;
        }
        .command {
            font-family: "Courier New", monospace;
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .output {
            font-family: "Courier New", monospace;
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 300px;
            overflow-y: auto;
        }
        h1, h2, h3 {
            color: #333;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
        }
        .badge-pass {
            background-color: #28a745;
            color: #fff;
        }
        .badge-fail {
            background-color: #dc3545;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>测试报告</h1>
        <p><strong>任务ID:</strong> task001</p>
        <p><strong>任务名称:</strong> 网络测试任务</p>
        <p><strong>设备ID:</strong> device001</p>
        <p><strong>设备名称:</strong> 测试设备1</p>
        <p><strong>设备IP:</strong> 192.168.1.100</p>
        <p><strong>执行时间:</strong> 2026-04-08 14:30:22</p>
        <p><strong>总耗时:</strong> 14.5秒</p>
        <p><strong>整体结果:</strong> <span class="badge badge-pass">通过</span></p>
    </div>

    <div class="summary">
        <h2>执行摘要</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>总数</th>
                <th>通过</th>
                <th>失败</th>
            </tr>
            <tr>
                <td>测试用例</td>
                <td>2</td>
                <td class="pass">2</td>
                <td class="fail">0</td>
            </tr>
            <tr>
                <td>测试场景</td>
                <td>3</td>
                <td class="pass">3</td>
                <td class="fail">0</td>
            </tr>
            <tr>
                <td>测试步骤</td>
                <td>12</td>
                <td class="pass">12</td>
                <td class="fail">0</td>
            </tr>
        </table>
    </div>

    <div class="testcase">
        <h2>测试用例: tc001 - 网络连通性测试</h2>
        <p><strong>结果:</strong> <span class="pass">通过</span></p>
        <p><strong>耗时:</strong> 8.2秒</p>
        
        <div class="scenario">
            <h3>测试场景: ping测试</h3>
            <p><strong>结果:</strong> <span class="pass">通过</span></p>
            <p><strong>耗时:</strong> 8.2秒</p>
            
            <div class="phase">
                <h4>阶段: setup</h4>
                <p><strong>结果:</strong> <span class="pass">通过</span></p>
                
                <div class="step">
                    <p><strong>命令:</strong></p>
                    <div class="command">ping -c 1 192.168.1.1</div>
                    <p><strong>输出:</strong></p>
                    <div class="output">PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms

--- 192.168.1.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.123/0.123/0.123/0.000 ms</div>
                    <p><strong>返回值:</strong> 0</p>
                    <p><strong>检查类型:</strong> output_contains</p>
                    <p><strong>期望值:</strong> 1 packets transmitted</p>
                    <p><strong>结果:</strong> <span class="pass">通过</span></p>
                    <p><strong>耗时:</strong> 1.2秒</p>
                </div>
            </div>
            
            <!-- execute、verify、cleanup阶段类似 -->
        </div>
    </div>
</body>
</html>
```

**样式要求**:
- 响应式设计，支持移动端查看
- 使用清晰的颜色区分通过/失败状态
- 代码块使用等宽字体
- 长输出支持滚动
- 中文显示友好

---

## 3. 报告内容要求

### 必需信息

**元数据**:
- 任务ID、名称
- 设备ID、名称、IP地址
- 执行时间戳
- 执行总时间
- 整体测试结果

**摘要统计**:
- 测试用例统计（总数、通过数、失败数）
- 测试场景统计
- 测试步骤统计

**详细执行记录**:
- 每个测试用例的执行结果
- 每个测试场景的执行结果
- 每个执行阶段的命令和输出
- 验证规则和检查结果
- 失败时的错误信息

### 可选信息

**性能数据**:
- 每个步骤的执行时间
- SSH连接建立时间
- 阶段耗时分布

**环境信息**:
- 框架版本
- Python版本
- 操作系统信息

---

## 4. 文件大小控制

**限制**: 报告文件最大100M

**实现机制**:
1. 写入前计算当前文件大小
2. 如果写入后超过100M，停止写入
3. 在报告末尾添加截断标记：
   - JSON: `{"truncated": true, "reason": "文件大小超过100M限制"}`
   - HTML: `<p class="warning">报告已截断：文件大小超过100M限制</p>`

**用户提示**:
- CLI输出警告信息
- 报告中标注截断状态

---

## 5. 错误场景处理

### SSH连接失败

```json
{
  "testcase_id": "tc001",
  "testcase_name": "网络连通性测试",
  "result": "fail",
  "error_message": "SSH连接超时（10秒）",
  "error_type": "ssh_timeout"
}
```

### 命令执行失败

```json
{
  "command": "ping -c 3 192.168.1.999",
  "output": "ping: 192.168.1.999: Name or service not known",
  "return_code": 2,
  "result": "fail",
  "error_message": "命令执行失败，返回值: 2",
  "verification": {
    "type": "output_contains",
    "value": "0% packet loss",
    "passed": false
  }
}
```

### 检查规则失败

```json
{
  "command": "ping -c 3 192.168.1.1",
  "output": "PING 192.168.1.1 ... 3 packets transmitted, 0 received, 100% packet loss",
  "return_code": 0,
  "result": "fail",
  "check": "output_contains",
  "expected": "0% packet loss",
  "check_passed": false,
  "actual_output": "100% packet loss"
}
```

---

## 6. 报告查看

**CLI命令**: 无专门命令，直接查看文件

**推荐工具**:
- JSON格式: 使用`jq`、在线JSON查看器
- HTML格式: 使用浏览器打开

**报告管理**:
- 定期清理旧报告
- 归档重要报告
- 报告文件命名包含时间戳，便于查找