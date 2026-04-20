---
name: uapp-umini
version: 1.1.0
description: "友盟小程序数据查询入口 skill。当用户询问小程序的概况、留存、页面访问、分享、场景分析、自定义事件时使用。触发词：小程序概况、小程序留存、小程序活跃用户、页面访问、入口页、分享分析、场景分析、小程序事件。注意：仅支持小程序/H5/小游戏应用。"
entry: scripts/umini.py
---

## 使用流程

**Step 1：确认小程序名称**
- 用户未提及小程序名时，询问：「请问是哪个小程序？」
- 若应用是 Android/iOS App，告知不支持，建议使用 uapp-core-index

**Step 2：确认查询意图**
- 概况/指标 → `--overview`
- 留存 → `--retention`，注意数据延迟，默认用 `last_7_days`
- 页面访问 → `--visit-pages` 或 `--landing-pages`
- 分享 → `--share-overview`
- 场景分析 → `--scene-stats`，需要场景値编码（如 `wx_1011`）
- 自定义事件 → `--list-events` / `--event-stats`

**Step 3：执行并解读输出**
- 概况数据：用自然语言总结各指标和趋势
- 留存数据：指出 v1（次日留存）最高、日均牙留存率
- 页面数据：指出 Top 3 页面及访问量

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 应用是 Android/iOS App | 告知不支持，小程序数据仅限小程序类应用；建议使用 uapp-core-index |
| 小程序名找不到 | 提示「可用 uapp-assets 查询小程序列表」 |
| 留存数据为空 | 提示「留存数据延迟，昨日留存需次日才能生成，建议查询 last_7_days」 |
| 周粒度留存为空 | 提示「周留存需等该周结束后才生成，未完成的周不会出现在结果中」 |
| 场景値编码不确定 | 先用 `--list-scenes-wx` 查询内置场景値列表（共 89 个） |
| `--list-scenes` 返回的 code 用于 `--scene-stats` | 告知不可，`--list-scenes` 返回的是渠道/活动 code，不是场景値 |

## 典型问法与内部意图映射

| 典型问法 | 内部意图（CLI 参数） |
|---------|-------------------|
| "小程序昨天的访问次数？" | `--overview --indicators visit` |
| "小程序过去一周活跃用户趋势？" | `--overview --range last_7_days` |
| "小程序累计用户有多少？" | `--total-user` |
| "小程序留存怎么样？" | `--retention --indicator activeUser` |
| "小程序过去一周页面访问排行？" | `--visit-pages --range last_7_days` |
| "哪个入口页带来最多用户？" | `--landing-pages --order-by visitUser` |
| "分享数据怎么样？" | `--share-overview` |
| "有哪些渠道来源？" | `--list-scenes --source-type channel` |
| "自定义事件有哪些？" | `--list-events` |

## 支持的查询模式

### 概况数据

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--overview` | - | 查询概况数据 |
| `--indicators` | 全部 | 指标列表：visit/activeUser/newUser/launch/avgSessionTime/avgUserSessionTime |

### 累计用户

| 参数 | 说明 |
|-----|------|
| `--total-user` | 查询累计用户数 |

### 留存数据

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--retention` | - | 查询留存数据 |
| `--indicator` | newUser | 留存指标：newUser(新增用户)/activeUser(活跃用户) |
| `--value-type` | rate | 数据类型：rate(留存率)/num(留存数) |
| `--time-unit` | day | 时间粒度：day(日)/week(周) |
| `--from` | - | 开始日期 (yyyy-mm-dd) |
| `--to` | - | 结束日期 (yyyy-mm-dd) |

**留存数据说明：**
- 返回数据包含 1-7 日/周留存率（v1=次日留存，v2=第2日留存，以此类推，v7=第7日留存）
- `--value-type` 参数：
  - `rate`（默认）：返回留存率百分比（如 `5.36%`）
  - `num`：返回留存人数（绝对数值）
- `--indicator` 参数：
  - `newUser`（默认）：新增用户留存
  - `activeUser`：活跃用户留存
- 注意：`newUser`/`activeUser` 区分大小写
- 支持自定义日期范围（`--from` 和 `--to`）或预设范围（`--range`）
- 查询范围较大时自动分页获取全量数据（API 每页固定返回10条，按 `pageIndex` 翻页）
- **数据延迟说明**：day 粒度昨日留存需次日才能生成，默认查询使用 `last_7_days`；week 粒度某周的留存率需等该周结束后才逐步生成，未完成的周不会出现在结果中

### 页面分析

| 参数 | 说明 |
|-----|------|
| `--visit-pages` | 查询受访页面列表 |
| `--landing-pages` | 查询入口页面列表 |
| `--order-by` | 排序字段 |
| `--direction` | 排序方向：asc/desc |
| `--page` | 页码 |
| `--per-page` | 每页数量 |

### 分享分析

| 参数 | 说明 |
|-----|------|
| `--share-overview` | 查询分享概况 |
| `--share-pages` | 查询页面分享数据 |
| `--share-users` | 查询分享用户列表 |

### 场景分析

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--list-scenes` | - | 查询渠道/活动场景值列表（API 返回） |
| `--list-scenes-wx` | - | 查询微信小程序场景值列表（内置 89 个） |
| `--source-type` | channel | 场景类型：channel(渠道)/campaign(活动) |
| `--scene-stats SCENE` | - | 查询指定场景统计，SCENE 传入场景值（如 `wx_1011`） |

**场景统计说明：**
- **微信小程序场景值**：格式为 `wx_` + 数字，共 89 个内置场景值，使用 `--list-scenes-wx` 查看完整列表
- **常用场景值**：
  - `wx_1011`：扫描二维码
  - `wx_1036`：App 分享消息卡片
  - `wx_1047`：扫描小程序码
  - `wx_1096`：聊天记录，打开小程序
- **注意**：`--list-scenes` 返回的是渠道/活动 code，**不能**作为 `--scene-stats` 的参数

### 自定义事件

| 参数 | 说明 |
|-----|------|
| `--list-events` | 查询事件列表 |
| `--event-stats EVENT` | 查询事件统计 |
| `--list-props EVENT` | 查询事件属性列表 |
| `--prop-values EVENT --prop PROP` | 查询属性值分布 |

**自定义事件说明：**
- `--event-stats` 返回字段：`dateTime`（日期）、`count`（触发次数）、`device`（触发设备数）
- `--list-props` 返回属性名称列表（`propertyName`），无显示名称字段
- `--prop-values` 返回字段：`propertyValue`（属性值）、`count`（次数）、`countRatio`（占比%）

## 支持的时间范围

- `yesterday`: 昨天（默认）
- `last_7_days`: 过去7天
- `last_30_days`: 过去30天
- `yyyy-mm-dd`: 指定日期

## 调用示例

### 概况数据

```bash
# 查询昨日概况
python3 scripts/umini.py --overview --app "友小盟数据官"

# 查询过去7天概况
python3 scripts/umini.py --overview --range last_7_days --app "友小盟数据官"

# 指定指标（activeUser/newUser/launch/visitTimes/onceDuration/dailyDuration）
python3 scripts/umini.py --overview --indicators "activeUser,newUser" --app "友小盟数据官"
```

### 留存数据

```bash
# 新增用户留存（默认查询过去7天）
python3 scripts/umini.py --retention --app "友小盟数据官"

# 活跃用户留存
python3 scripts/umini.py --retention --indicator activeUser --app "友小盟数据官"

# 查询过去7天留存
python3 scripts/umini.py --retention --range last_7_days --app "友小盟数据官"

# 自定义日期范围（大范围自动分页，获取全量数据）
python3 scripts/umini.py --retention --from 2026-03-01 --to 2026-03-30 --app "友小盟数据官"

# 周粒度留存（注意：未完成的周因数据延迟不会出现在结果中）
python3 scripts/umini.py --retention --from 2026-03-01 --to 2026-03-30 --time-unit week --app "友小盟数据官"
```

### 页面分析

```bash
# 受访页面排行
python3 scripts/umini.py --visit-pages --app "友小盟数据官"

# 入口页面排行（按访问用户数排序）
python3 scripts/umini.py --landing-pages --order-by visitUser --app "友小盟数据官"

# 入口页面排行（按访问次数排序）
python3 scripts/umini.py --landing-pages --order-by visitTimes --app "友小盟数据官"

# 入口页面排行（按跳出率排序）
python3 scripts/umini.py --landing-pages --order-by jumpRatio --app "友小盟数据官"
```

### 分享分析

```bash
# 分享概况
python3 scripts/umini.py --share-overview --app "友小盟数据官"

# 页面分享
python3 scripts/umini.py --share-pages --app "友小盟数据官"
```

### 场景分析

```bash
# 查看微信小程序场景值列表（内置 89 个）
python3 scripts/umini.py --list-scenes-wx --app "友小盟数据官"

# 微信场景值统计（如 wx_1011=扫描二维码）
python3 scripts/umini.py --scene-stats "wx_1011" --app "友小盟数据官"

# 其他常用场景值
python3 scripts/umini.py --scene-stats "wx_1036" --app "友小盟数据官"  # App分享
python3 scripts/umini.py --scene-stats "wx_1047" --app "友小盟数据官"  # 小程序码
```

### 自定义事件

```bash
# 事件列表
python3 scripts/umini.py --list-events --app "友小盟数据官"

# 事件统计
python3 scripts/umini.py --event-stats "add_appkey_page_click" --app "友小盟数据官"

# 事件属性
python3 scripts/umini.py --list-props "add_appkey_page_click" --app "友小盟数据官"

# 属性值分布
python3 scripts/umini.py --prop-values "add_appkey_page_click" --prop "click_items" --app "友小盟数据官"
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/umini.py --overview --app "友小盟数据官" --json
```

## 配置方式

1. `--config /path/to/umeng-config.json`: 显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`: 环境变量
3. 在当前目录创建 `umeng-config.json`: 默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 注意事项

1. **仅支持小程序应用**：本 skill 仅支持 platform 为小程序/H5/小游戏的应用
2. **dataSourceId**：小程序 API 使用 `dataSourceId` 参数，值等同于 `appkey`
3. **timeUnit 默认值**：所有接口默认使用 `day` 作为时间单位
4. **分页参数**：使用 `pageIndex`/`pageSize`（与 App 接口的 `page`/`perPage` 不同）
