# HN News Agent

> Hacker News 新闻采集与推送智能体 — 自动化抓取、分类、推送HN热点。

## 快速开始

### 1. 安装依赖

```bash
pip3 install requests
```

### 2. 配置

编辑 `config.json`：

```json
{
  "keywords": ["AI", "open source", "startup", "security"],
  "threshold_score": 50,
  "min_score": 30,
  "max_items": 15,
  "language": "auto",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
  "push_enabled": false
}
```

### 3. 使用方法

```bash
# 获取Top热点（默认15条）
python3 scripts/fetch_hn.py top

# 获取最新消息
python3 scripts/fetch_hn.py newest

# 获取Ask HN
python3 scripts/fetch_hn.py ask

# 获取Show HN
python3 scripts/fetch_hn.py show

# 过滤AI相关（关键词）
python3 scripts/fetch_hn.py top -k AI LLM GPT

# 过滤分数100+
python3 scripts/fetch_hn.py top -s 100

# JSON格式输出
python3 scripts/fetch_hn.py top -o json
```

### 4. 定时推送

配合 OpenClaw cron：

```bash
# 早报 09:00
python3 scripts/daily_report.py top zh

# 晚报 21:00
python3 scripts/daily_report.py new zh
```

## 功能

- 📰 实时采集 HN Top / Newest / Ask HN / Show HN
- 🏷️ 自动分类（AI/开源/技术/创业/安全）
- ⭐ 按分数和关键词过滤
- 🌍 中英双语输出
- 🔔 支持飞书 Webhook 推送
- ⏰ 定时任务支持

## 文件结构

```
hn-news-agent/
├── SKILL.md              # OpenClaw Skill 入口
├── README.md             # 本文档
├── config.json           # 配置文件
├── scripts/
│   ├── fetch_hn.py       # 抓取脚本（核心）
│   └── daily_report.py   # 日报推送脚本
└── prompts/
```

## OpenClaw 集成

1. 把 `hn-news-agent` 目录放入 OpenClaw skills 目录
2. 使用 cron 定时执行 `python3 scripts/daily_report.py`
3. 配置飞书 Webhook 实现自动推送

## License

MIT
