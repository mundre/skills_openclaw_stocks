---
name: daily-backup
version: 1.0.0
description: 每日 Git 备份。提交工作区所有变更，记录变更摘要。触发时机：cron 定时任务或手动调用。
---

# Daily Backup

每日 Git 全量备份，记录变更摘要。

## 核心流程

1. 读取 references/spec.md 获取详细规范
2. 运行 `scripts/auto-backup.sh`
3. 检查是否有新提交
4. 读取变更统计
5. 生成报告并发送

## 触发时机

- cron 定时任务（建议每日）
- 用户明确要求时

## 投递规则（必须）

完成报告后，通过消息工具发送。
- 渠道：feishu
- 目标：<飞书群ID或用户ID>
如果报告超过 3800 字符，分成多条消息发送。
每条消息必须语义完整（不断开 URL 或格式）。
如果发送失败，重试一次。如果仍然失败，输出错误——永远不要静默退出。

## 输出

- 报告位置：`data/exec-logs/daily-backup/YYYY-MM-DD.md`
- 消息推送到飞书群
