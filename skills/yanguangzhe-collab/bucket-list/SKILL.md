# 愿望清单 (Bucket List)

> 记录主人与龙虾一起完成的人生愿望清单

---
name: bucket-list
version: 1.3.1
description: 记录和追踪人生愿望的伙伴工具。支持CLI聊天和GUI双入口，主人和龙虾共同读写同一份数据。路径已统一，数据有验证。
---

## 功能定位

- **协作**：主人和龙虾共同读写同一份愿望清单
- **记录**：人生愿望清单
- **追踪**：完成进度和成就回顾
- **陪伴**：可选的人生进度显示
- **安全**：HTTP 服务器仅 localhost 访问

## 使用方式

### GUI 界面
启动服务器后，浏览器访问：
```bash
node server.js
# 访问 http://localhost:9999/
```

功能：
- 添加/完成/取消愿望
- 可选的人生进度显示
- 导出/导入备份

### CLI 命令
通过 OpenClaw 直接操作，双方共享数据。

## 数据存储

- **localStorage**：浏览器本地存储
- **导出/导入**：手动备份恢复
- **字段**：`id`, `content`, `status`, `createdAt`, `endedAt`, `endedBy`, `completionNote`, `timeline`
- **状态**：`pending` / `completed` / `cancelled`

## 文件结构

```
skills/bucket-list/
├── SKILL.md          # 本文档
├── bucket-list.html  # GUI 界面
├── server.js         # Node.js HTTP 服务器（仅 localhost）
├── bucket-list.sh    # Shell 脚本
└── data/
    └── bucket-list.json  # 愿望数据
```

## 边界

- **不是**：待办提醒工具、心理治疗师、人生导师
- **只是**：愿望记录工具 + 协作界面