---
name: stock-price-alert
description: 股价异动实时提醒技能，支持对接股票行情接口、邮件提醒和Sonos语音播报，实时监控持仓股票价格波动并触发告警
license: LICENSE-CC-BY-NC-SA 4.0 in LICENSE.txt
author: OpenClaw FinanceOps
tags: ['stocks', 'finance', 'alert', 'notification', 'trading']
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3", "clawhub"], "pip": ["yfinance", "pandas", "python-dotenv", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"] },
        "install":
          [
            {
              "id": "deps",
              "kind": "pip",
              "packages": ["yfinance", "pandas", "python-dotenv", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"],
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Stock Price Alert Skill

股价异动实时提醒技能，用于实时监控股票持仓的价格波动，当价格涨跌幅超过预设阈值时触发多渠道告警通知。

## 使用场景

- 实时监控持仓股票的异常波动
- 价格突破支撑位或压力位时的提醒
- 重要价格点位到达通知
- 单日涨跌幅超过阈值时的紧急告警

## 前置条件

1. Python 3.7+ 环境
2. yfinance 股票行情接口库
3. Gmail API 凭证（用于邮件提醒）
4. Sonos CLI 已配置（用于语音播报）
5. 在 .env 文件中配置相关参数

## 工作流

### 1. 监控初始化
- 加载用户配置的持仓股票列表
- 读取告警阈值配置（默认 ±5%）
- 初始化行情接口和通知渠道

### 2. 实时行情获取
- 调用 Yahoo Finance API 获取实时价格
- 计算涨跌幅和价格变动
- 与基准价格进行对比

### 3. 异动检测
- 检查单只股票涨跌幅是否超过阈值
- 检测价格是否突破关键点位
- 验证是否需要去重（避免重复告警）

### 4. 告警触发
- 生成详细的告警报告
- 通过 Gmail 发送邮件提醒
- 通过 Sonos 扬声器进行语音播报
- 记录告警历史到日志文件

### 5. 持续监控
- 按照设定的时间间隔循环执行
- 更新告警状态和静默期
- 生成每日监控汇总报告

## 配置参数

| 参数名 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 持仓配置 | PORTFOLIO | - | 股票代码和持仓数量字典，如：{"AAPL": 15, "MSFT": 10} |
| 告警阈值 | ALERT_THRESHOLD | 5.0 | 涨跌幅告警阈值（百分比） |
| 检查间隔 | CHECK_INTERVAL | 300 | 行情检查间隔（秒） |
| Sonos音箱 | SONOS_SPEAKER | 'Living Room' | 语音播报的Sonos音箱名称 |
| 收件邮箱 | RECIPIENT_EMAIL | 'user@example.com' | 告警邮件收件人 |
| 静默期 | ALERT_COOLDOWN | 3600 | 单只股票重复告警间隔（秒） |

## 输出格式

### 告警邮件示例
```
⚠️ 股价异动告警：AAPL
时间：2026-04-09 10:30:00
当前价格：$175.50
涨跌幅：+6.2%
变动金额：+$10.25
告警原因：单日涨幅超过5.0%阈值
建议：关注成交量变化，考虑止盈
```

### Sonos语音播报示例
```
注意！股价异动提醒：苹果公司当前涨幅已达到百分之六点二，当前价格为一百七十五美元五十分，请您及时关注。
```

## 使用示例

### 基本使用 - 启动实时监控
```bash
python3 scripts/stock_price_alert.py --monitor
```

### 单次检测并退出
```bash
python3 scripts/stock_price_alert.py --check-once
```

### 指定自定义阈值
```bash
python3 scripts/stock_price_alert.py --threshold 3.0 --monitor
```

### 测试告警通知
```bash
python3 scripts/stock_price_alert.py --test-alert
```

### 添加到crontab定时执行
```bash
# 每5分钟检查一次
*/5 * * * * cd /workspace && python3 scripts/stock_price_alert.py --check-once >> /var/log/stock_alert.log 2>&1
```

## 注意事项

1. **行情接口限制**：yfinance 免费接口有调用频率限制，建议检查间隔不低于 60 秒
2. **告警风暴**：合理设置静默期，避免短时间内收到大量重复告警
3. **时区问题**：注意美股交易时间，非交易时段价格不会更新
4. **凭证安全**：Gmail token.json 文件请勿提交到公开仓库
5. **网络依赖**：确保服务器网络稳定，能正常访问 Yahoo Finance 和 Google API

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 行情接口调用失败 | 重试 3 次，每次间隔 10 秒，仍失败则跳过本次检查 |
| Gmail 发送失败 | 记录错误日志，继续执行 Sonos 播报 |
| Sonos 播报失败 | 记录错误日志，继续执行邮件发送 |
| 价格数据异常 | 跳过该股票，记录警告日志 |

## 文件结构

```
stock-price-alert/
├── SKILL.md                    # 本技能说明文件
├── README.md                   # 使用说明文档
├── scripts/
│   └── stock_price_alert.py    # 主运行脚本
└── config/
    └── .env.example            # 配置示例文件
```
