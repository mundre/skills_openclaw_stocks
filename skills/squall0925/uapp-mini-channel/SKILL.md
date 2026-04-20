---
name: uapp-mini-channel
version: 1.1.0
description: "友盟小程序推广渠道查询 Skill。当用户想了解小程序的获客来源、渠道/活动效果、场景分析时使用。触发词：获客来源、推广渠道、推广活动、场景分析、渠道排行、活动效果、场景值。注意：仅支持小程序/H5/小游戏应用。"
entry: scripts/mini_channel.py
---

## 使用流程

**Step 1：确认小程序名称**
- 用户未提及名称时，询问：「请问是哪个小程序？」
- 若应用是 Android/iOS App，告知不支持

**Step 2：确认查询意图**
- 获客来源排行 → `--customer-source`，确认排行维度（渠道/活动/场景）
- 趋势分析 → 需要渠道/活动 ID，如未知先用 `--list` 获取
- 场景分析 → 需要场景値编码（如 `wx_1011`）

**Step 3：执行并解读输出**
- 排行结果：指出 Top 1 渠道/来源及其关键数据
- 趋势结果：指出指标峰值/谷値和走势方向

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 应用是 Android/iOS App | 告知不支持，推广渠道查询仅限小程序 |
| 小程序名找不到 | 提示「可用 uapp-assets 查询小程序列表」 |
| 需要渠道/活动 ID 但未知 | 先执行 `--list` 获取 ID，再进行趋势分析 |
| 场景値不确定 | 建议用 `--list-scenes-wx`（如用 uapp-umini skill）查询内置场景値列表 |
| 排行结果为空 | 提示「该日期或类型暂无数据，建议换昨天或近期日期」 |

## 典型问法与 CLI 参数映射

| 典型问法 | CLI 参数 |
|---------|---------|
| "各推广渠道昨天带来了多少用户？" | `--customer-source` 或 `--customer-source --source-type channel` |
| "XX活动的推广效果？" | `--campaign "campaign_id"`（id 可通过 `--list --source-type campaign` 获取） |
| "小程序各场景值的数据对比？" | `--customer-source --source-type scene` |
| "获客来源排行？" | `--customer-source` |
| "某渠道过去一周趋势？" | `--channel "channel_id" --metric activeUser --range last_7_days`（id 可通过 `--list` 获取） |
| "有哪些推广渠道？" | `--list --source-type channel` |
| "有哪些推广活动？" | `--list --source-type campaign` |

## 支持的查询模式

### 获客来源排行（默认）

查询指定类型的获客来源排行数据：

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--customer-source` | - | 查询获客来源排行 |
| `--source-type` | channel | 来源类型：channel/campaign/platform/scene |
| `--order-by` | newUser | 排序字段：newUser/activeUser/launch/visitTimes/onceDuration/createDateTime |
| `--direction` | desc | 排序方向：asc/desc |
| `--top` | 10 | Top N 结果 |

### 指定渠道统计

查询指定推广渠道的统计数据：

| 参数 | 说明 |
|-----|------|
| `--channel ID` | 渠道 ID（通过 `--list` 获取） |
| `--indicators` | 指标列表：newUser/activeUser/launch/visitTimes/onceDuration |

### 指定活动统计

查询指定推广活动的统计数据：

| 参数 | 说明 |
|-----|------|
| `--campaign ID` | 活动 ID（通过 `--list --source-type campaign` 获取） |
| `--indicators` | 指标列表 |

### 指定场景值统计

查询指定场景值的统计数据：

| 参数 | 说明 |
|-----|------|
| `--scene CODE` | 场景值编码（如 wx_1011） |
| `--indicators` | 指标列表 |

### 列表查询

查询渠道或活动列表（返回的编码可直接用于 `--channel` / `--campaign` 参数）：

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--list` | - | 查询列表 |
| `--source-type` | channel | 列表类型：channel/campaign |

**输出说明**：返回的编码（id 字段）可直接作为 `--channel` 或 `--campaign` 的参数值使用。

### 趋势分析

对指定渠道/活动/场景值进行趋势分析：

| 参数 | 说明 |
|-----|------|
| `--metric` | 趋势指标：newUser/activeUser/launch/visitTimes/onceDuration |
| `--range` | 时间范围：last_7_days/last_30_days/last_90_days |

## 支持的时间范围

- `yesterday`：昨天（默认）
- `last_7_days`：过去7天
- `last_30_days`：过去30天
- `last_90_days`：过去90天
- `yyyy-mm-dd`：指定日期

## 调用示例

### 获客来源排行

```bash
# 渠道排行（默认）
python3 scripts/mini_channel.py --app "小程序名称"

# 活动排行
python3 scripts/mini_channel.py --app "小程序名称" --customer-source --source-type campaign

# H5场景排行
python3 scripts/mini_channel.py --app "小程序名称" --customer-source --source-type platform

# 其他场景排行
python3 scripts/mini_channel.py --app "小程序名称" --customer-source --source-type scene

# 按活跃用户排序
python3 scripts/mini_channel.py --app "小程序名称" --customer-source --order-by activeUser
```

### 指定渠道统计

```bash
# 单日统计（ID 从 --list 获取）
python3 scripts/mini_channel.py --app "小程序名称" --channel "channel_id"

# 指定指标
python3 scripts/mini_channel.py --app "小程序名称" --channel "channel_id" --indicators "activeUser,visitTimes"
```

### 指定活动统计

```bash
python3 scripts/mini_channel.py --app "小程序名称" --campaign "campaign_id"
```

### 场景值统计

```bash
# 查询场景值 wx_1011（扫描二维码）的统计
python3 scripts/mini_channel.py --app "小程序名称" --scene "wx_1011"
```

### 列表查询

```bash
# 渠道列表
python3 scripts/mini_channel.py --app "小程序名称" --list

# 活动列表
python3 scripts/mini_channel.py --app "小程序名称" --list --source-type campaign
```

### 趋势分析

```bash
# 渠道活跃用户趋势（ID 从 --list 获取）
python3 scripts/mini_channel.py --app "小程序名称" --channel "channel_id" \
    --metric activeUser --range last_7_days

# 活动新增用户趋势
python3 scripts/mini_channel.py --app "小程序名称" --campaign "campaign_id" \
    --metric newUser --range last_30_days

# 场景值访问次数趋势
python3 scripts/mini_channel.py --app "小程序名称" --scene "wx_1011" \
    --metric visitTimes --range last_7_days
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/mini_channel.py --app "小程序名称" --customer-source --json
```

## 配置方式

配置文件路径优先级：
1. `--config /path/to/umeng-config.json`
2. 环境变量 `UMENG_CONFIG_PATH`
3. 当前目录下的 `umeng-config.json`

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 注意事项

1. **仅支持小程序应用**：本 skill 仅支持 platform 为小程序/H5/小游戏的应用
2. **dataSourceId**：小程序 API 使用 `dataSourceId` 参数，值等同于 `appkey`
3. **timeUnit 默认值**：所有接口默认使用 `day` 作为时间单位
4. **indicators 默认值**：newUser, activeUser, launch
5. **渠道/活动编码获取**：使用 `--list` 查询获取的编码可直接用于 `--channel` / `--campaign` 参数
6. **趋势分析数据顺序**：API 返回数据按日期降序排列（最新日期在前），趋势分析中"初期值"为最早日期，"末期值"为最新日期
