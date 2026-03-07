---
name: memory-system-optimizer
description: OpenCLAW 记忆系统优化 - 三层架构 + 自动衰减 + CRUD验证
version: 1.2.0
author: Odin
tags: [memory, openclaw, optimization, ai]
---

# Memory System Optimizer

> OpenCLAW 记忆系统优化 Skill，基于 Ray Wang 30天实战经验

## 功能

### 1. 三层记忆架构
- **NOW.md** - 工作台，当前任务看板
- **memory/YYYY-MM-DD.md** - 每日日志
- **INDEX.md** - 知识导航 + 健康度仪表盘

### 2. 自动衰减机制
- Hot/Warm/Cold 温度模型
- 自动归档过期记忆
- 优先级标记

### 3. CRUD 验证
- 写入前先读原则
- 冲突检测
- 过时标记

### 4. 写入工具
- auto-memlog.sh - 自动时间戳日志（推荐）
- memlog.sh - 手动日志
- memory-gc.sh - 冷数据归档
- memory-decay.js - 温度分档

### 5. 12个核心配置文件
| # | 文件 | 用途 |
|---|------|------|
| 1 | SOUL.md | 告诉AI它是谁 |
| 2 | IDENTITY.md | 明确身份角色 |
| 3 | USER.md | 了解服务对象 |
| 4 | AGENTS.md | 多代理分工 |
| 5 | TOOLS.md | 配置可用工具 |
| 6 | MEMORY.md | 长期记忆，防止失忆 |
| 7 | FEEDBACK-LOG.md | 错误不再犯 |
| 8 | AUTONOMY.md | 自主权限，减少确认 |
| 9 | SKILLS.md | 技能加载，持续升级 |
| 10 | MULTI-INSTANCE.md | 并行工作 |
| 11 | SECURITY.md | 安全设置，有限授权 |
| 12 | TRAINING.md | 边做边教，每日培训 |

## 安装配置

无收费，纯免费使用。

## 使用方法

```bash
# 写入日志
memlog.sh "标题" "内容"

# 刷新记忆
node memory-decay.js

# 归档
./memory-gc.sh
```

## 技术栈

- OpenCLAW
- Markdown 文件
- Shell 脚本
- Node.js

## 作者

Odin（总舵主）
