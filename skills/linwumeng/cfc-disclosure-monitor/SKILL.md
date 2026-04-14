---
name: cfc-disclosure-monitor
description: 30家持牌消费金融公司官网公告信披采集，支持增量每日Cron。
version: 1.0.0
tags: [consumption-finance, scraping, china, compliance]
---

# cfc-disclosure-monitor — 消金信披采集 Skill

30家持牌消金公司官网公告抓取，配置驱动，统一入口。

## 架构

```
cfc-disclosure-monitor/
├── SKILL.md            ← 本文件
├── companies.json      ← 唯一配置源（30家公司 URL + 方法）
├── collect.py          ← 统一入口（Phase-1 列表采集）
├── core.py             ← 提取引擎（extract_from_text / normalize_date）
├── collectors.py        ← 30个采集方法（按架构模式分组）
├── processors/         ← Phase-2 内容处理器（图片/PDF/Cloudflare）
└── fetch/              ← Phase-2 批量内容抓取（未完成）
```

**设计原则：**
- `companies.json` 是唯一配置源，所有入口读同一文件
- `core.py` 是唯一日期提取实现，禁止复制粘贴
- 采集方法按架构模式分组（静态HTML / 翻页 / Vue SPA / 多栏等）
- 每个方法以 `collect_<name>` 命名，自动注册到 `COLLECTORS` 字典

## 执行

```bash
# 全量采集（3次重试，延迟2秒）
python3 collect.py

# 增量采集（自动从上次采集日期推断，只抓新公告）
python3 collect.py --incremental

# 增量采集（指定起始日期）
python3 collect.py --since 2026-04-11

# 指定公司增量采集
python3 collect.py --incremental --company "招联消费金融,中邮消费金融"

# 快速测试
python3 collect.py --retry 1 --delay 0

# 指定公司
python3 collect.py --company "中银消费金融"

# 检查浏览器可用性
python3 collect.py --check
```

**参数说明：**
- `--retry N`：单家公司最大重试次数（默认3，指数退避）
- `--delay S`：公司间延迟秒数（默认2，防止限流）
- `--incremental`：增量模式，自动从 `_summary.json` 读取上次采集日期，只抓该日期后的新公告
- `--since YYYY-MM-DD`：增量起始日期（手动指定）
- `--resume`：保留历史目录（不清空今日目录），但不按日期过滤
- `--company`：逗号分隔的公司名
- `--date`：采集日期目录（默认今天）

**输出：** `~/.openclaw/workspace/cfc_raw_data/{日期}/{公司名}/{announcements.json, index.json}`

**每日Cron：** 每天 9:00 AM（Asia/Shanghai）自动增量采集，结果推送到当前会话。

## 方法一览（8组架构模式）

### GROUP_A — 静态 HTML（滚动提取）
| 方法 | 公司 |
|------|------|
| `html_dom` | 蚂蚁/中信/宁银/陕西长银 |
| `cdp_rpa` | 哈银（大量滚动） |

### GROUP_B — 翻页型
| 方法 | 公司 |
|------|------|
| `paginated` | 马上（通用下一页） |
| `el_pagination` | 海尔（Element UI） |

### GROUP_C — 首页滚动（JS动态加载）
| 方法 | 公司 |
|------|------|
| `homepage_scroll` | 金美信 |
| `pingan_detail` | 平安（fullPage.js + 弹层关闭） |

### GROUP_D — 详情页 URL 可枚举
| 方法 | 公司 |
|------|------|
| `zhongyou_detail` | 中邮（/xxgg/{id}.html） |
| `xiaomi_detail` | 小米（/newsDetail?id=） |
| `jinmixin_detail` | 金美信（/xxpl/{id}） |
| `xingye_detail` | 兴业（.new_title + .new_time + 附件） |
| `haier_news_detail` | 海尔（.newsList + 图片URL） |
| `beiyin_marquee` | 北银（滚动区URL→详情页日期） |
| `jincheng_detail` | 锦程（标题嵌YYYYMM日期） |

### GROUP_E — Vue / SPA / JS框架
| 方法 | 公司 |
|------|------|
| `vue_pagination` | 招联（Vue '>' 翻页） |
| `jianxin_dmyy` | 建信（Vue SPA） |
| `suyinkaiji_vue` | 苏银凯基（Vue Tab + Cloudflare bypass） |

### GROUP_F — 多 Tab / 多栏
| 方法 | 公司 |
|------|------|
| `multi_page` | 湖北（3 Tab × N页） |
| `jinshang_detail` | 晋商（col23 + col22 双栏） |
| `nyfb_two_page` | 南银法巴（gsgg + xwzx） |

### GROUP_G — 特殊格式
| 方法 | 公司 |
|------|------|
| `zhongyin_layui` | 中银（layui 分页 13页） |
| `yangguang_detail` | 阳光（DOM + URL路径日期解析） |
| `zhongyuan` | 中原（查看更多 + split-line日期） |
| `hangyin_two_line` | 杭银（MM/DD 双行） |
| `static_list` | 蒙商（静态列表多页） |
| `mengshang_detail` | 蒙商（详情URL枚举） |
| `hebei_detail` | 河北幸福（DD-MM-YY 格式） |
| `time_prefix` | 盛银（时间在前标题在后） |
| `shangcheng_news` | 尚诚 |
| `pdf_link` | 天津京东（PDF附件列表） |

### GROUP_H — WSL2 受限
| 方法 | 公司 |
|------|------|
| `changyin58_telling` | 长银五八（telling.html，2018年停更） |

## 核心算法：两遍扫描双向最近邻

```
Pass1: 扫描所有行，建立 date_map {line_idx: date_str}
       PARTIAL 日期（只有年月日之一）标记后留待合并

Pass2: 非日期行，计算到最近日期行的距离
       同距离时正向优先（dj > i 胜出）
       距离 ≤ max_dist(默认8) 才配对
```

**支持日期格式（30家全覆盖）：**

| 格式 | 示例 | 公司 |
|------|------|------|
| `YYYY-MM-DD` | 2026-04-02 | 通用 |
| `YYYY年MM月DD日 HH:mm:ss` | 2026年03月23日 15:30:00 | 盛银/尚诚 |
| `YYYY年MM月` | （2026年3月） | 阳光（嵌标题） |
| `YYYY.MM.DD` | 2026.01.14 | 晋商 |
| `DD YYYY.MM` | 14 2026.01 | 蒙商 |
| `DD-MM-YYYY` | 03-05-2026 | 蒙商 |
| `DD-MM-YY` | 26-04-02 → 2026-04-02 | 河北幸福 |
| `MM-DD + YYYY`（split-line） | 03-14 + 2026 | 中原 |
| `MM/DD + YYYY`（split-line） | 12/05 + 2026 | 杭银 |
| `时间：YYYY-MM-DD` | 时间：2025-07-22 浏览量：1278 | 马上 |
| `YYYY/MM` | 2026/04 | 海尔 |

## 新增公司步骤

1. 在 `companies.json` 的 `companies` 列表末尾加一行
2. 选择已有方法（测试是否 work）
3. 如需新方法：
   - 在 `collectors.py` 写新 async 函数，命名 `collect_<name>`
   - 用 `@collector("方法名")` 装饰器注册
   - 同一函数支持多别名：`@collector("foo|bar")`

## 浏览器说明

**使用 playwright 内置 Chromium**，路径：
```
~/.cache/ms-playwright/chromium-XXXX/chrome-linux64/chrome
```

系统 Chrome（`/usr/bin/google-chrome`）在 WSL2 里会 crash，不要用。

启动参数（WSL2 已验证）：
```python
STEALTH_ARGS = [
    "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security", "--enable-webgl",
    "--ignore-certificate-errors", "--allow-running-insecure-content",
    "--headless=new",
]
```

## 已知问题

- **海尔~770条**：Element UI 误采接访日/消保之声/关联交易等非信披内容，`el_pagination` 有 skip 规则但不够
- **兴业7条**：可能动态加载未完成
- **长银五八3条**：telling.html 最后更新 2018年，无新公告

## 关键Bug修复记录

| 日期 | Bug | 修复 |
|------|-----|------|
| 2026-04-07 | `extract_from_text` 日期行被 `\s` 误过滤 | `DATE_PAT` 检查后才做跳过判断 |
| 2026-04-10 | 三个专用方法 dispatch 缺失，走 html_dom 兜底 | `run_company` 补全 dispatch |
| 2026-04-10 | Cloudflare WAF 拦截（boccfc/sykcfc） | 加全 stealth args |
| 2026-04-11 | WSL2 系统 Chrome crash | 改用 playwright 内置 Chromium |
| 2026-04-11 | `collectors.py` 装饰器别名注册位置错误 | 移入 `decor()` 内部 |
