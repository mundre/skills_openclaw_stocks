---
name: uapp-event
version: 1.1.0
description: "友盟 App 自定义事件查询入口 skill。当用户想查看埋点事件的触发次数、独立用户数、参数分布，或确认某个事件是否存在时使用。触发词：自定义事件、埋点查询、事件统计、事件触发次数、独立用户、事件列表、事件参数。"
entry: scripts/event.py
---

## 使用流程

**Step 1：确认应用名称**
- 用户未提及应用名时，询问：「请问是哪个 App？」

**Step 2：确认查询意图**
- 如不确定事件名，先用 `--list-events` 查询列表
- 确定事件名后，匹配：触发次数→`--metric count`、独立用户→`--metric unique_users`、参数分布→`--param`

**Step 3：执行并解读输出**
- 事件统计：指出总次数/独立用户、趋势走向
- 参数分布：指出占比最高的 Top 3 参数値

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说 App 名 | 先询问，不要猜测 |
| App名找不到 | 提示「可用 uapp-assets 查询应用列表」 |
| 事件名不确定 | 先用 `--list-events` 查询列表，也可用 `--check-display "中文名"` 通过显示名查找 |
| 事件不存在 | 提示「该事件不存在，可用 uapp-event-manage 创建」 |
| 返回数据为空 | 提示「该时段此事件暂无数据，可能是埋点还未上线或该时间段未触发」 |

## 典型问法与内部意图映射

| 典型问法 | 内部意图（CLI 参数） |
|---------|-------------------|
| "有哪些自定义事件？" | `--list-events` |
| "某个按钮点击了多少次？" | `--query click_button --metric count` |
| "有多少独立用户触发了注册事件？" | `--query register --metric unique_users` |
| "支付事件有哪些参数？" | `--list-params payment` |
| "不同来源渠道的事件分布怎样？" | `--query login --param channel` |
| "事件 xxx 存在吗？" | `--check-event xxx` |
| "显示名称为'开始'的事件存在吗？" | `--check-display "开始"` |

## 支持的查询模式

### 事件存在性检查

| 参数 | 说明 |
|-----|------|
| `--check-event EVENT_NAME` | 通过事件名称检查事件是否存在 |
| `--check-display DISPLAY_NAME` | 通过显示名称检查事件是否存在（对人类更友好） |

### 事件列表查询（分页）

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--list-events` | - | 查询事件列表 |
| `--page` | 1 | 页码 |
| `--per-page` | 50 | 每页数量（最大 100） |
| `--all` | - | 查询全部事件 |

### 事件统计查询

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--query EVENT_NAME` | - | 指定事件名称 |
| `--metric count` | - | 触发次数 |
| `--metric unique_users` | - | 独立用户数 |
| `--metric all` | all | 综合统计 |

### 参数分析

| 参数 | 说明 |
|-----|------|
| `--list-params EVENT_NAME` | 查询事件参数列表 |
| `--query EVENT_NAME --param PARAM_NAME` | 查询参数值分布 |
| `--param-metric duration` | 查询参数值时长统计 |
| `--param-value VALUE` | 查询特定参数值的趋势 |

## 支持的时间范围

- `yesterday`: 昨天
- `last_7_days`: 过去7天（默认）
- `last_30_days`: 过去30天
- `yyyy-mm-dd`: 指定日期

## 调用示例

### 事件存在性检查

```bash
# 通过事件名称检查
python3 scripts/event.py --check-event "app_start" --app "MyApp"

# 通过显示名称检查（对人类更友好）
python3 scripts/event.py --check-display "开始" --app "MyApp"

# JSON 输出
python3 scripts/event.py --check-display "开始" --app "MyApp" --json
```

### 事件列表查询

```bash
# 查询事件列表（默认第1页，每页50条）
python3 scripts/event.py --list-events --app "MyApp"

# 分页查询
python3 scripts/event.py --list-events --page 2 --per-page 20 --app "MyApp"

# 查询全部事件
python3 scripts/event.py --list-events --all --app "MyApp"
```

### 事件统计查询

```bash
# 查询事件触发次数
python3 scripts/event.py --query "click_button" --metric count --app "MyApp"

# 查询独立用户数
python3 scripts/event.py --query "click_button" --metric unique_users --app "MyApp"

# 综合统计（默认）
python3 scripts/event.py --query "click_button" --app "MyApp"

# 指定时间范围
python3 scripts/event.py --query "click_button" --range last_30_days --app "MyApp"
```

### 参数分析

```bash
# 查询事件参数列表
python3 scripts/event.py --list-params "click_button" --app "MyApp"

# 查询参数值分布
python3 scripts/event.py --query "click_button" --param "button_id" --app "MyApp"

# 查询参数值时长统计
python3 scripts/event.py --query "click_button" --param "button_id" --param-metric duration --app "MyApp"
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/event.py --list-events --app "MyApp" --json
python3 scripts/event.py --query "click_button" --app "MyApp" --json
```

## 配置方式

1. `--config /path/to/umeng-config.json`: 显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`: 环境变量
3. 在当前目录创建 `umeng-config.json`: 默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 注意事项

1. **分页限制**：事件列表默认每页 50 条，最大 100 条，避免大数据量查询
2. **eventId 映射**：参数列表查询需要 eventId，脚本会自动从事件列表中解析
3. **事件名称匹配**：支持精确匹配和忽略大小写匹配
4. **显示名称查询**：`--check-display` 通过中文显示名称查询，对人类更友好
5. **输出截断规则**：
   - 事件列表：事件名称超过32字符、显示名称超过64字符会被截断并追加 `...`
   - 参数列表：参数名称超过32字符、显示名称超过64字符会被截断并追加 `...`
   - 单个事件/参数查询：完整显示，不做截断
   - JSON 输出（`--json`）：完整显示，不做截断
