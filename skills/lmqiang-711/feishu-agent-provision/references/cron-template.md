# 定时报告 Cron 配置模板

## 日报 Cron

```json
{
  "name": "<AGENT_ID>-daily-report",
  "schedule": { "kind": "cron", "expr": "0 <HOUR> * * 1-5", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "<日报提示词，告知读取数据文件、生成报告、发送到飞书群>",
    "timeoutSeconds": 120
  },
  "sessionTarget": "session:<AGENT_ID>-reports",
  "delivery": { "mode": "announce" }
}
```

## 周报 Cron（周五合并发送）

```json
{
  "name": "<AGENT_ID>-weekly-report",
  "schedule": { "kind": "cron", "expr": "0 <HOUR> * * 5", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "<周报提示词：总结本周+下周计划，注意周五时合并到日报而非单独发送>",
    "timeoutSeconds": 120
  },
  "sessionTarget": "session:<AGENT_ID>-reports",
  "delivery": { "mode": "announce" }
}
```

## 备注

- `sessionTarget` 使用命名 session（`session:<AGENT_ID>-reports`），确保报告历史可追溯
- `delivery.mode: "announce"` 将结果发送到触发时的 channel（即飞书群）
- cron 表达式格式：`分 时 日 月 周`
  - 每日 17:00：`0 17 * * 1-5`
  - 每周五 17:00：`0 17 * * 5`
