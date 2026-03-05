---
name: polymarket-arbitrage-pro
description: Polymarket套利机器人v6.0 - 真实交易版。自动检测套利机会并执行交易，每次调用0.001USDT。
metadata:
  author: BOB-Z-PRO
  version: 6.0.0
  price: 0.001 USDT/call
  payment: SkillPay (BNB Chain)
  skill_id: cc7d6401-0a5c-46eb-8694-673ffa587c8b
  env:
    - OKX_API_KEY
    - OKX_SECRET_KEY
    - OKX_PASSPHRASE
---

# 💰 Polymarket Arbitrage Pro v6.0

**真实交易版 | 自动套利 | 每次0.001U**

---

## ⚠️ 重要说明

- 使用前必须配置OKX API Key
- 真实交易，有亏损风险
- 初始资金100U，亏损20%自动停止

---

## 环境变量

```bash
export OKX_API_KEY="your_key"
export OKX_SECRET_KEY="your_secret"
export OKX_PASSPHRASE="your_pass"
```

---

## 功能

✅ 自动检测套利机会  
✅ 自动执行交易  
✅ 亏损20%自动停止  
✅ 7×24运行  

---

## 使用

```bash
arbitrage start   # 启动托管
arbitrage scan    # 扫描机会
arbitrage balance # 查看余额
```

---

## 风险提示

- 加密货币交易有风险
- 请先用小额测试
- 盈亏自负
