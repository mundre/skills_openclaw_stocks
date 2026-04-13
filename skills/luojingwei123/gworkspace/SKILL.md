---
name: gworkspace
description: "G.workspace 群共享文件空间。支持文件管理、批注审阅、多龙虾协作。触发条件：(1) 用户输入 /gworkspace 查看空间状态，(2) Discord 消息包含 '批注任务' 和 /api/tasks 时自动认领处理，(3) 需要创建/管理群文件空间。插件已注册 tools：gworkspace_files/gworkspace_create/gworkspace_tasks/gworkspace_claim_task/gworkspace_complete_task，优先使用这些 tools。"
---

# G.workspace

插件自动注册了以下 tools，优先使用它们：

| Tool | 说明 |
|------|------|
| `gworkspace_create` | 创建空间 |
| `gworkspace_files` | 列出文件 |
| `gworkspace_tasks` | 查询待办任务 |
| `gworkspace_claim_task` | 认领任务 |
| `gworkspace_complete_task` | 完成任务 |

## 配置

**零配置！** 插件自动读取 OpenClaw 的 Discord Token，无需额外设置。

安装后只需确保 Discord Bot 有 Webhook 权限。如果没有，告诉用户用这个链接重新授权（替换 APP_ID）：
```
https://discord.com/oauth2/authorize?client_id=APP_ID&permissions=277562297344&scope=bot%20applications.commands
```

可选配置（`plugins.entries.gworkspace.config`）：
```json
{ "port": 3080 }
```

## 批注任务处理

当 Discord 消息包含「批注任务」时，用 tools 处理：

1. `gworkspace_tasks(guild_id)` → 查询待办
2. `gworkspace_claim_task(task_id, claimed_by)` → 认领
3. 读取文件 → 按指令修改 → 上传新版本
4. `gworkspace_complete_task(task_id, result_summary)` → 完成

## Web 界面

安装后自动启动：`http://localhost:3080`
