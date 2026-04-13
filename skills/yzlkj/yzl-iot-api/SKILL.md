---
name: yzl-iot-api
description: 云智联 IoT 设备管理API v1.2.2。一句话说就能获取传感器数据和发送控制指令。激活语：云智联设备，钥匙是xxxxxx，帮我打开开关/获取数据
homepage: https://github.com/openclaw/skills/tree/main/yzl-iot-api
metadata: { "openclaw": { "requires": { "bins": ["python3"], "env": ["YZLIOT_API_KEY"] } } }
---

## ⚙️ 运行时要求

- **Python 3.6+** （需要 json, os, sys, urllib, datetime, collections 等标准库）
- **环境变量 `YZLIOT_API_KEY`** - 必需，在安装后需用户自行配置

## 🌱 云智联 IoT 设备管理

一句话就能获取设备数据和发送控制指令！

## 功能

| 命令 | 说明 |
|------|------|
| `python3 tool.py` | 一句话获取所有设备 |
| `ping` | 验证连接 |
| `all` | 获取所有设备 |
| `list` | 分页获取设备列表 |
| `device <ID>` | 获取设备详情（含设施ID） |
| `history <设施ID> [天数]` | 获取单个设施历史数据 |
| `device-history <设备ID> [天数]` | 获取设备所有设施历史数据 |
| `send <设备ID> <指令类型> [参数]` | 发送控制指令 |
| `cmd-list <设备ID>` | 获取设备支持的指令列表 |
| `cmd-detail <设备ID> <指令ID>` | 获取指令详情 |

## 使用示例

```bash
# 1. 设置 API Key（只需一次）
export YZLIOT_API_KEY="您的API密钥"

# 2. 一句话获取设备数据
python3 tool.py

# 3. 查看设备详情和设施ID
python3 tool.py device YZLSTM1-0000001454

# 4. 查询单个设施历史数据（用上面获取的设施ID）
python3 tool.py history 28DDE03ED3B962BFB424228E88A098A20B36FC49 5

# 5. 一键获取设备所有历史数据
python3 tool.py device-history YZLSTM1-0000001454 5
```

## 获取 API Key

1. 打开微信小程序 **「云智联YZL」**
2. 进入 **「我的」→「开放接口」**
3. 复制 API Token

## 常见设备

| 设备 | 设备ID |
|------|--------|
| 西瓜 154 | YZLSTM1-0000001454 |

## 设施ID说明

使用 `device` 命令查看设备详情时，每个设施（温度、湿度、电压等）都有一个 `id` 字段，这就是用于 `history` 命令的设施ID。

常用设施ID（西瓜154）：
- 温度值: `28DDE03ED3B962BFB424228E88A098A20B36FC49`
- 湿度值: `AEC2DD171332B8796113D96112BFE26EDF765A9D`
- 电压: `725E77442885503A657D1896E60002BCCE78E47C`

## 指令类型

| 类型 | 说明 |
|------|------|
| `GetFac` | 获取设施数据 |
| `SetFac` | 设置设施参数 |
| `Upfs` | 升级固件 |
| `Custom` | 自定义指令 |