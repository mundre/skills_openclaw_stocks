# Polymarket Arbitrage Pro

**套利机会检测工具 | 需配置OKX API**

---

## ⚠️ 重要说明

1. 使用前必须配置环境变量
2. 当前版本仅支持套利检测，交易执行开发中
3. 无任何硬编码凭据

---

## 环境变量（必须配置）

```bash
export OKX_API_KEY="your_api_key"
export OKX_SECRET_KEY="your_secret"
export OKX_PASSPHRASE="your_passphrase"
```

---

## 安装

```bash
npm install -g polymarket-arbitrage-pro
```

---

## 使用

```bash
arbitrage scan    # 扫描套利机会
arbitrage start   # 启动持续监控
arbitrage balance  # 查看余额
```

---

## 功能

- ✅ 实时扫描50个Polymarket市场
- ✅ 自动检测套利机会（利润>=2%）
- ✅ OKX账户余额查询
- 🔄 交易执行功能开发中

---

## 安全

- 无硬编码凭据
- 凭据存储在环境变量
- 支持Read-Only API Key

---

**版本：5.0.2**  
**作者：BOB-Z-PRO**
