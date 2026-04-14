---
name: security-health-check
description: |
  个人数字安全体检工具。一键检查邮箱泄露、密码强度、隐私暴露、安全评分。
  面向普通用户，不是开发者。中文优先。
  当用户提到"安全检查""安全体检""密码泄露""邮箱泄露""隐私""安全评分"时触发。
metadata: {"openclaw": {"emoji": "🔒"}}
---

# Security Health Check — 个人数字安全体检

## 核心能力

### 1. 邮箱泄露检查
- 通过 Have I Been Pwned (HIBP) API 检查邮箱是否出现在已知数据泄露中
- 显示泄露事件名称、日期、涉及数据类型
- 提供修复建议

### 2. 密码强度分析
- 检测密码强度（长度、复杂度、字典词检测）
- 估算暴力破解时间
- 检查密码是否出现在常见泄露密码列表

### 3. 安全评分报告
- 综合评分 0-100 分
- 分维度评分：邮箱安全、密码安全、隐私暴露、2FA建议
- 生成 Markdown 格式报告
- 可同步到飞书文档

### 4. 安全建议
- 基于 HIBP 泄露数据，推荐启用 2FA
- 识别弱密码并建议更换
- 隐私设置检查清单

## 使用方式

```bash
# 完整安全体检
python3 scripts/security_check.py --email your@email.com

# 仅检查邮箱泄露
python3 scripts/security_check.py --email your@email.com --check breach

# 密码强度检测
python3 scripts/security_check.py --password "your_password"

# 生成安全报告
python3 scripts/security_check.py --email your@email.com --report markdown

# JSON格式输出
python3 scripts/security_check.py --email your@email.com --json
```

## 数据来源

| 检查项 | API | 说明 |
|--------|-----|------|
| 邮箱泄露 | HIBP API v3 | 免费API，无需key（truncated模式） |
| 密码泄露 | HIBP Password API | k-匿名前缀查询，密码不离开本地 |
| 密码强度 | 本地计算 | zxcvbn-style 分析 |

## 隐私承诺

- **密码永远不离开本地**：HIBP密码检查使用k-匿名前缀，只发送SHA1前5位
- **邮箱检查结果仅展示摘要**：不存储泄露的原始数据
- **报告可删除**：所有生成的报告可随时清理

## 输出示例

```
🔒 个人数字安全体检报告
━━━━━━━━━━━━━━━━━━━━━

📧 邮箱：u***@gmail.com
📊 安全评分：72/100

├─ 邮箱泄露：⚠️ 发现2次泄露
│  ├─ Adobe (2013) — 姓名、邮箱、密码提示
│  └─ LinkedIn (2016) — 邮箱、密码
│
├─ 密码安全：✅ 未发现泄露
│
├─ 建议：
│  ├─ 🔴 立即更换 Adobe/LinkedIn 相关密码
│  ├─ 🟡 启用2FA（Google Authenticator）
│  └─ 🟢 定期检查泄露情况

━━━━━━━━━━━━━━━━━━━━━
💡 下次检查建议：30天后
```
