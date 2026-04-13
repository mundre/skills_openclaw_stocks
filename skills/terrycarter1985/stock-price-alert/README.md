# Stock Price Alert Skill

股价异动实时提醒技能 - 实时监控股票持仓价格波动，触发邮件和语音告警

## 简介

本技能是专为 OpenClaw 个人助手设计的股票价格监控工具，可以实时追踪您的投资组合，当股票价格出现异常波动（涨跌幅超过预设阈值）时，自动通过邮件和 Sonos 语音播报发出告警通知，帮助您及时把握市场动态。

## 功能特性

- ✅ **实时行情监控** - 对接 Yahoo Finance API 获取准实时股票价格
- ✅ **智能异动检测** - 支持自定义涨跌幅阈值，灵活设置告警触发条件
- ✅ **多渠道通知** - 集成 Gmail 邮件提醒 + Sonos 智能音箱语音播报
- ✅ **告警去重机制** - 内置静默期配置，避免告警风暴
- ✅ **灵活运行模式** - 支持常驻监控模式和单次检查模式
- ✅ **完整日志记录** - 自动记录所有告警历史和运行状态

## 快速开始

### 1. 安装依赖

```bash
pip install yfinance pandas python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. 配置环境变量

复制配置模板并编辑：

```bash
cp config/.env.example .env
```

编辑 `.env` 文件：

```env
# Sonos 配置
SONOS_SPEAKER=Living Room

# 邮件配置
RECIPIENT_EMAIL=your-email@example.com

# 告警配置
ALERT_THRESHOLD=5.0
CHECK_INTERVAL=300
ALERT_COOLDOWN=3600
```

### 3. 配置 Gmail API

按照 Gmail Skill 的指引配置 `config/token.json` 凭证文件。

### 4. 启动监控

```bash
# 启动实时监控模式
python3 scripts/stock_price_alert.py --monitor

# 单次检查（用于定时任务）
python3 scripts/stock_price_alert.py --check-once
```

## 使用方式

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--monitor` | 启动常驻监控模式，持续检查价格异动 |
| `--check-once` | 执行单次检查，完成后退出（适合 cron） |
| `--threshold N` | 临时设置告警阈值（覆盖 .env 配置） |
| `--test-alert` | 发送测试告警，验证通知渠道是否正常 |
| `--status` | 显示当前监控状态和配置信息 |

### 配置您的持仓

编辑 `scripts/stock_price_alert.py` 中的 PORTFOLIO 配置：

```python
PORTFOLIO = {
    'AAPL': 15,      # 苹果公司 15 股
    'MSFT': 8,       # 微软 8 股
    'GOOGL': 5,      # 谷歌 5 股
    'TSLA': 12,      # 特斯拉 12 股
    'NVDA': 10       # 英伟达 10 股
}
```

### Cron 定时任务示例

编辑 crontab：

```bash
crontab -e
```

添加以下内容（美股交易时段每 5 分钟检查一次）：

```bash
# 周一至周五，美股交易时间（北京时间 21:30 - 04:00）每5分钟检查一次
*/5 21-23,0-4 * * 1-5 cd /root/.openclaw/workspace/skills/stock-price-alert && python3 scripts/stock_price_alert.py --check-once >> logs/alert.log 2>&1
```

## 告警阈值建议

根据不同的投资风格，可以调整告警阈值：

| 投资风格 | 推荐阈值 | 说明 |
|---------|---------|------|
| 超短线交易 | 1-2% | 敏感捕捉任何波动 |
| 短线交易 | 3-5% | 平衡灵敏度和信噪比 |
| 中长线投资 | 5-8% | 只关注重大异动 |
| 长期持有 | 8-10% | 极端行情才告警 |

## 故障排查

### Gmail 邮件发送失败

1. 确认 `config/token.json` 文件存在且有效
2. 检查网络是否能访问 Google API
3. 确认 Gmail API 已启用且凭证权限正确

### Sonos 语音播报失败

1. 运行 `sonos list` 确认音箱在线
2. 检查音箱名称是否与配置一致（区分大小写）
3. 确认 sonos-cli 已正确安装并配置

### 行情数据获取失败

1. 检查网络连接（需要访问 Yahoo Finance）
2. 确认 yfinance 库版本为最新
3. 适当延长检查间隔，避免触发频率限制

## 更新日志

### v1.0.0
- ✨ 新增股价异动实时提醒功能
- ✨ 支持 Yahoo Finance 行情接口对接
- ✨ 集成 Gmail 邮件告警
- ✨ 支持 Sonos 智能音箱语音播报
- ✨ 内置告警去重和静默期机制
- ✨ 支持常驻监控和单次检查两种模式

## 许可证

本项目采用 CC BY-NC-SA 4.0 许可证。

## 相关链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [ClawHub 技能市场](https://clawhub.com)
- [yfinance 文档](https://pypi.org/project/yfinance/)
