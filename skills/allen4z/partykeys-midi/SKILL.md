---
name: partykeys_midi
description: "Control PartyKeys MIDI keyboard via BLE - connect device, light up keys, listen to playing, play sequences, and follow mode for music teaching. Use when user mentions: MIDI keyboard, PartyKeys, 音乐密码, light up keys, 点亮按键, listen to playing, 监听弹奏, music hardware control."
metadata: {"openclaw": {"requires": {"bins": ["python3"]}, "os": ["darwin", "linux"]}}
---

# PartyKeys MIDI 键盘控制

通过 MCP 控制 PartyKeys MIDI 键盘（音乐密码）的 LED 灯光和监听弹奏。

## 安装

首次使用前运行安装脚本：

```bash
bash {baseDir}/scripts/setup.sh
```

脚本会自动创建 Python 虚拟环境、安装依赖，并将 MCP 服务器配置注册到 OpenClaw。

## 可用工具

### music_connect
连接 MIDI 键盘设备。

参数：
- `mode`: 连接模式 — `script`（直接 BLE，推荐）、`web`（浏览器 Web Bluetooth）、`mobile`（待实现）
- `address`: 设备地址（script 模式可选，用于直连指定设备）

Script 模式自动扫描并连接，无需浏览器。
Web 模式启动 Gateway Server (http://localhost:9527)，需在 Chromium 浏览器中操作。

### music_disconnect
断开设备连接。

### music_light_keys
点亮指定按键的 LED 灯。

参数：
- `keys`（必填）: 音符数组，如 `["C4", "E4", "G4"]`，也支持十六进制 `["3c", "40", "43"]`
- `color`: 颜色，如 `"red"`, `"green"`, `"blue"`（默认 `"blue"`）
- `brightness`: 亮度 0-100（默认 100）

### music_listen
监听用户弹奏输入。

参数：
- `timeout`: 超时时间，毫秒（默认 5000）
- `mode`: `"single"`（单音符）或 `"continuous"`（持续监听）

### music_play_sequence
播放音符序列（仅 script 模式）。

参数：
- `sequence`: 音符序列数组，每个元素含 `keys`（音符数组）和 `delay`（延迟毫秒）

### music_follow_mode
跟弹模式 — 点亮音符并等待用户弹奏正确后继续（仅 script 模式）。

参数：
- `notes`（必填）: 音符序列
- `timeout`: 每个音符超时，毫秒（默认 30000）

### music_status
获取硬件连接状态，无参数。

## 使用流程

1. **连接设备**: 调用 `music_connect`（推荐 `mode="script"`）
2. **执行操作**: 点亮按键、播放序列或监听弹奏
3. **断开连接**: 调用 `music_disconnect`

## 示例

**教学模式**:
```
music_connect(mode="script")
music_light_keys(keys=["C4", "E4", "G4"], color="blue")
music_follow_mode(notes=["C4", "E4", "G4"], timeout=30000)
music_disconnect()
```

**演示模式**:
```
music_connect(mode="script")
music_play_sequence(sequence=[
  {"keys": ["C4"], "delay": 500},
  {"keys": ["E4"], "delay": 500},
  {"keys": ["G4"], "delay": 500}
])
music_disconnect()
```

## 架构

```
AI Agent (OpenClaw)
    ↓ MCP Protocol (stdio)
MCP Server (Python, {baseDir}/server/mcp_server.py)
    ├─ Script 模式 → BLE (bleak) → MIDI 键盘
    └─ Web 模式 → HTTP → Gateway (Node.js:9527) → WebSocket → Browser (Web Bluetooth) → BLE → MIDI 键盘
```

## 故障排查

- **Python 虚拟环境问题**: 重新运行 `bash {baseDir}/scripts/setup.sh`
- **端口 9527 被占用**: `lsof -i :9527 | awk 'NR>1{print $2}' | xargs kill`
- **Web Bluetooth 不可用**: 仅 Chromium 内核浏览器支持（Chrome/Edge/Opera）
- **设备连不上**: 确认键盘已开启蓝牙，距离不超过 5 米
