---
name: gateway-rescue
version: 2.0.0
description: |
  OpenClaw Gateway 看门狗，纯 systemd/launchd 原生管理。崩溃自动重启，连续失败3次停止等待人工介入。
  支持：install（安装）、uninstall（卸载）、status（状态）、test（故障测试）。
---

# gateway-rescue

OpenClaw Gateway 看门狗，纯 systemd/launchd 原生管理，零自定义守护脚本。

## 一句话

用系统原生服务管理器守护 OpenClaw Gateway 进程，崩溃自动重启，失败3次后停止等待人工介入。

## 核心要点

1. **Linux/WSL2** → systemd service（`Restart=on-failure`，失败 3 次后停止，需人工介入）
2. **macOS** → launchd plist + 轻量 wrapper（计数 3 次后停止，需人工介入）
3. **极简实现** → Linux 零 wrapper，macOS 仅一个 20 行计数脚本
4. **四个操作** → install / uninstall / status / test

## 使用方法

```bash
# 安装看门狗
bash ~/.openclaw/workspace/skills/gateway-rescue/scripts/install.sh

# 卸载看门狗
bash ~/.openclaw/workspace/skills/gateway-rescue/scripts/uninstall.sh

# 查看状态
bash ~/.openclaw/workspace/skills/gateway-rescue/scripts/status.sh

# 测试（停止 gateway，等待自动恢复）
bash ~/.openclaw/workspace/skills/gateway-rescue/scripts/test.sh
```

## 行为说明

| 平台 | 服务管理器 | 失败后 | 失败限制 |
|------|-----------|--------|----------|
| Linux/WSL2 | systemd | 自动重启 | 5 分钟内失败 3 次后停止，需人工介入 |
| macOS | launchd | 自动重启 | 连续失败 3 次后停止，需人工介入 |

## 文件结构

```
gateway-rescue/
├── SKILL.md              # 本文件
├── scripts/
│   ├── install.sh        # 自动检测平台并安装
│   ├── uninstall.sh      # 卸载服务
│   ├── status.sh         # 查看状态和日志
│   ├── test.sh           # 测试自动恢复
│   └── launchd-wrapper.sh # macOS 失败计数（3次停止）
└── units/
    ├── openclaw-gateway.service   # systemd 模板
    └── com.openclaw.gateway.plist # launchd 模板
```
