# 董事长早晚报 (Chairman Daily Brief)

专为上市公司董事长设计的高管视角每日市场简报系统。

## 快速开始

### 1. 安装

将本 skill 复制到 OpenClaw skills 目录：

```bash
cp -r chairman-daily-brief ~/.openclaw/skills/
```

### 2. 配置

复制关注列表示例：

```bash
cp config/watchlist.example.json config/watchlist.json
```

编辑 `config/watchlist.json` 添加你关注的公司和竞争对手。

### 3. 设置 API Key

```bash
export QVERIS_API_KEY="your-api-key-here"
```

从 https://qveris.ai 获取 API Key。

### 4. 运行

```bash
# 生成早班报告
cd ~/.openclaw/skills/chairman-daily-brief
node scripts/chairman_daily.mjs morning --symbol 600519.SS --company 贵州茅台

# 生成晚报
node scripts/chairman_daily.mjs evening --symbol 0700.HK --company 腾讯控股

# 使用关注列表生成多公司简报
node scripts/chairman_daily.mjs morning --watchlist holdings
```

## 功能特点

### 🌅 早班报告 (Morning Brief)
- 隔夜全球市场概览
- 宏观政策速递
- 本公司开盘前瞻
- 行业雷达
- 竞争对手情报
- 风险提示
- 今日重点关注

### 🌙 晚报 (Evening Brief)
- 收盘概览与成交分析
- 今日公告汇总
- 舆情监控
- 机构动向
- 政策解读
- 明日策略建议

## 命令参考

```bash
# 生成早班报告
node scripts/chairman_daily.mjs morning --symbol <代码> --company <名称>

# 生成晚报
node scripts/chairman_daily.mjs evening --symbol <代码> --company <名称>

# 添加关注公司
node scripts/chairman_daily.mjs watch --action add \
  --symbol 600519.SS --company 贵州茅台 --role self

# 添加竞争对手
node scripts/chairman_daily.mjs watch --action add \
  --symbol 002594.SZ --company 比亚迪 --role competitor --peer-group 新能源汽车

# 查看关注列表
node scripts/chairman_daily.mjs watch --action list
```

## 定时任务

设置自动早晚报：

```bash
# 早班 8:00
openclaw cron add --name "董事长早班简报" \
  --cron "0 8 * * 1-5" --tz Asia/Shanghai \
  --message "运行 chairman-daily-brief 生成早班报告"

# 晚报 15:35
openclaw cron add --name "董事长晚报简报" \
  --cron "35 15 * * 1-5" --tz Asia/Shanghai \
  --message "运行 chairman-daily-brief 生成晚报"
```

## 数据源

- THS iFinD (同花顺)
- Caidazi (财达资讯)
- Alpha Vantage
- Finnhub
- X/Twitter Sentiment

## License

MIT
