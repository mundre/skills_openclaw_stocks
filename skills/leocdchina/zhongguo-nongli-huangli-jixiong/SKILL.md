---
name: zhongguo-nongli-huangli-jixiong
license: MIT
homepage: https://nongli.skill.4glz.com
repository: https://github.com/Leocdchina/huangli-agent-skills
publisher: Leocdchina
version: 1.3.4
compatibility: Requires Python 3.9+ or bash with curl. Set required HUANGLI_TOKEN env var (Bearer token from https://nongli.skill.4glz.com/dashboard). Optional HUANGLI_BASE env var overrides API base. Needs HTTPS outbound access to api.nongli.skill.4glz.com.
required_env:
  - HUANGLI_TOKEN (required)
  - HUANGLI_BASE (optional)
outbound_hosts:
  - api.nongli.skill.4glz.com
tags:
  - 黄历
  - 老黄历
  - 农历
  - nongli
  - 中国农历
  - 黄历吉凶
  - 吉凶
  - 吉日
  - 凶日
  - 宜忌
  - 择日
  - 搬家吉日
  - 结婚吉日
  - 开业吉日
  - 开工吉日
  - 农历查询
  - 黄历查询
  - Nongli
  - Huangli
  - Chinese lunar calendar
  - lunar almanac
description: |
  黄历查询：输入公历日期，查询当日黄历宜忌、吉凶、神煞、冲煞等信息，支持搬家吉日、结婚吉日、开业吉日、开工吉日择日。

  黄历 · 中国农历黄历吉凶 · Zhongguo Nongli Huangli Jixiong · China Lunar Almanac
  
  Unified Huangli skill for common workflows: single-date query, date-range batch query,
  and keyword search over a date range.

  Use this skill when users ask:
  - one specific date: "今天黄历 / 今天宜忌是什么 / 2027-08-08 吉时"
  - a period comparison: "下月哪天适合搬家 / 最近哪些天是吉日"
  - keyword lookup: "2027年哪些日子是甲子日 / 哪些天宜开业 / 农历黄历"

  Convert natural-language time to concrete YYYY-MM-DD first.
  Prefer batch endpoint for multi-date requests.
  Keep ranges focused to reduce quota usage.

  1、默认免费额度：10 个唯一日期/天
  2、超额返回429，并提醒手动重置，用户登陆控制台进行手动重置。
  3、不限制重置次数。
---

# 中国农历黄历吉凶 · Zhongguo Nongli Huangli Jixiong · China Lunar Almanac (Auspicious & Inauspicious)

## 官网与 Token

- 官网（注册/登录）：https://nongli.skill.4glz.com
- 控制台（获取 Token）：https://nongli.skill.4glz.com/dashboard
- API Base：`https://api.nongli.skill.4glz.com`

先配置环境变量：

```bash
export HUANGLI_TOKEN="your_token_here"
export HUANGLI_BASE="https://api.nongli.skill.4glz.com"
```

## 用法（统一入口）

```bash
# 1) 单日查询
python3 toolkit.py by-date 2027-08-08

# 2) 区间批量查询（支持筛选）
python3 toolkit.py batch 2027-08-01 2027-08-31 --filter 搬家

# 3) 关键词搜索
python3 toolkit.py search 甲子日 --year 2027
```

## 何时用哪种模式

- `by-date`：只问一个具体日期
- `batch`：比较多天、整周、整月
- `search`：关键词跨日期范围检索（甲子日/摩羯座/初一/搬家等）

## 关键实践

- 自然语言时间先展开为具体日期（YYYY-MM-DD）
- 多日期请求优先 `POST /api/lunar/batch`
- 关键词检索基于返回数据本地筛选（无服务端关键词搜索接口）

## 配额说明

1、默认免费额度：10 个唯一日期/天
2、超额返回429，并提醒手动重置，用户登陆控制台进行手动重置。
3、不限制重置次数。
