---
name: hn-news-agent
description: Hacker News 新闻采集与推送智能体。定时抓取HN热点、自动分类、支持中英文双语输出，可推送到飞书。
emoji: 📰
tags:
  - hacker-news
  - news
  - aggregator
  - feed
  - automation
license: MIT
---

# Hacker News 新闻采集与推送 Agent

> 自动化采集 Hacker News 热点新闻，支持分类筛选、中英双语、定时推送。

---

## 功能

- 📰 **实时采集** — 抓取 HN 首页 / newest / ask-hn 等列表
- 🏷️ **智能分类** — AI/开源/科技/创业/生活五大分类
- 🌍 **双语输出** — 中文摘要 + 原文链接
- 🔔 **定时推送** — 每天早晚报，推送到飞书
- ⭐ **Star追踪** — 监控特定关键词，超过阈值触发告警

---

## 语言

根据用户**第一条消息**的语言自动切换：
- 用户发英文 → 英文输出
- 用户发中文 → 中文输出

---

## 触发方式

| 命令 | 说明 |
|------|------|
| ` HN今日热点` / `HN top today` | 获取今日 Top 15 热点 |
| ` HN最新消息` / `HN newest` | 获取最新 15 条 |
| ` HN AI新闻` / `HN AI news` | 过滤AI相关 |
| ` HN开源项目` / `HN OSS` | 过滤开源/工具类 |
| ` HN设置` / `HN settings` | 查看/修改订阅配置 |

---

## 配置项（config.json）

```json
{
  "keywords": ["AI", "open source", "LLM", "startup"],
  "threshold_score": 100,
  "daily_report_time": "09:00,21:00",
  "language": "auto",
  "max_items": 15
}
```

---

## 输出格式

```
📰 Hacker News 热点 — {日期}

[分类标签] 标题
⭐ {分数} | 💬 {评论数}
🔗 {URL}
📝 摘要（AI生成的中文/英文摘要）

---
```

---

## 定时任务

每天 09:00（北京时间）推送早报
每天 21:00（北京时间）推送晚报

通过 OpenClaw cron 设置：
```
cron: "0 9,21 * * *"
notify_channel: feishu
```

---

## 项目结构

```
hn-news-agent/
├── SKILL.md
├── scripts/
│   ├── fetch_hn.py      # 抓取脚本
│   └── classify.py      # 分类脚本
├── prompts/
│   └── summary.md       # 摘要生成prompt
└── config.json          # 配置文件
```

---

*Built with OpenClaw • 数据来源：news.ycombinator.com*
