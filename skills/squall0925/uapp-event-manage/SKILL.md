---
name: uapp-event-manage
version: 1.1.0
description: "友盟自定义事件管理入口 skill。当用户需要创建埋点事件定义、批量创建事件、查询事件列表时使用。触发词：创建事件、添加埋点、批量创建事件、事件列表、自定义事件管理。"
entry: scripts/event_manage.py
---

## 使用流程

**Step 1：确认应用名称**
- 用户未提及应用名时，询问：「请问是哪个应用？」

**Step 2：确认操作意图和参数**
- 创建单个事件 → 确认事件名（英文+下划线）和显示名称（中文）
- 批量创建 → 仅小程序支持，确认 JSON 格式列表或文件路径
- 查询事件列表 → 直接执行 `--list-events`

**Step 3：执行并反馈**
- 创建成功后明确告知用户事件名称
- 创建失败时，如无返回错误信息，可用 `--verify` 确认是否已存在

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说应用名 | 先询问，不要猜测 |
| App名找不到 | 提示「可用 uapp-assets 查询应用列表」 |
| 事件名包含特殊字符 | 告知仅支持英文字母、数字和下划线，不允许 `? / . \ < >` 等特殊符号 |
| App 类型使用批量创建 | 告知「批量创建仅支持小程序类型应用，请逐个使用 --create」 |
| 创建后立即验证不存在 | 告知「事件同步需要几秒，`--verify` 可能暂时返回不存在，稍后再查即可」 |

## 典型问法与内部意图映射

| 典型问法 | 内部意图（CLI 参数） |
|---------|-------------------|
| "创建一个叫purchase_click的事件" | `--create "purchase_click" --display-name "购买点击" --app "Android_Demo"` |
| "帮我批量创建这几个小程序事件" | `--batch-create --events '[...]' --app "友小盟数据官"` |
| "创建一个数值型事件" | `--create "purchase_amount" --display-name "购买金额" --event-type true --app "Android_Demo"` |
| "创建事件并确认是否成功" | `--create "test_event" --display-name "测试事件" --verify --app "Android_Demo"` |
| "查看当前应用有哪些自定义事件" | `--list-events --app "友小盟数据官"` |

## 支持的操作模式

### 事件列表查询

| 参数 | 说明 |
|-----|------|
| `--list-events` | 查询当前应用的所有自定义事件 |

**平台支持**：App类型和小程序类型均支持事件列表查询

### 单个事件创建

| 参数 | 必填 | 说明 |
|-----|-----|------|
| `--create EVENT_NAME` | 是 | 事件名称（英文标识） |
| `--display-name DISPLAY_NAME` | 是 | 事件显示名称（中文） |
| `--event-type TYPE` | 否 | 事件类型：`true`=计算事件（数值型），`false`=计数事件（字符串型）。默认不传（API默认false） |
| `--verify` | 否 | 创建后验证事件是否存在 |

**平台支持**：App类型和小程序类型均支持单个事件创建

### 批量事件创建

| 参数 | 必填 | 说明 |
|-----|-----|------|
| `--batch-create` | 是 | 批量创建模式 |
| `--events JSON_STRING` | 二选一 | JSON字符串格式的事件列表 |
| `--from-file FILE_PATH` | 二选一 | JSON文件路径 |

**平台限制**：仅小程序类型应用支持批量创建

### 事件类型说明

| eventType | 类型 | 说明 |
|-----------|-----|------|
| `true` | 计算事件（数值型） | 用于统计数值型变量的累计值、均值及分布 |
| `false` | 计数事件（字符串型） | 用于统计字符串型变量的消息数及触发设备数 |

**注意**：不指定 `--event-type` 时，API默认使用 `false`（计数事件）

### 批量创建JSON格式

```json
[
  {"eventName": "click_btn", "displayName": "点击按钮"},
  {"eventName": "view_page", "displayName": "浏览页面"}
]
```

## 调用示例

### 事件列表查询

```bash
# 查询小程序事件列表
python3 scripts/event_manage.py --list-events --app "友小盟数据官"

# 查询App事件列表
python3 scripts/event_manage.py --list-events --app "Android_Demo"

# JSON 输出
python3 scripts/event_manage.py --list-events --app "友小盟数据官" --json
```

### 单个事件创建

```bash
# 创建App类型事件（计数事件，默认）
python3 scripts/event_manage.py --create "purchase_click" --display-name "购买点击" --app "Android_Demo"

# 创建App类型计算事件（数值型）
python3 scripts/event_manage.py --create "purchase_amount" --display-name "购买金额" --event-type true --app "Android_Demo"

# 创建小程序类型事件
python3 scripts/event_manage.py --create "view_page" --display-name "浏览页面" --app "友小盟数据官"

# 创建并验证
python3 scripts/event_manage.py --create "test_event" --display-name "测试事件" --verify --app "Android_Demo"
```

### 批量事件创建（仅小程序）

```bash
# 使用JSON字符串
python3 scripts/event_manage.py --batch-create --events '[{"eventName":"click1","displayName":"点击1"},{"eventName":"click2","displayName":"点击2"}]' --app "友小盟数据官"

# 使用文件
python3 scripts/event_manage.py --batch-create --from-file events.json --app "友小盟数据官"
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/event_manage.py --create "test_event" --display-name "测试事件" --json --app "Android_Demo"
```

## 配置方式

1. `--config /path/to/umeng-config.json`: 显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`: 环境变量
3. 在当前目录创建 `umeng-config.json`: 默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 平台类型自动识别

脚本根据应用配置中的 `platform` 字段自动选择API：

| 平台 | API接口 |
|-----|---------|
| Android / iOS / HarmonyOS | `umeng.uapp.event.create` |
| 微信小程序 / 支付宝小程序 / 百度小程序 / 字节跳动小程序 / QQ小程序 / H5 / 小游戏 | `umeng.umini.batchCreateEvent` |

## 注意事项

1. **App类型不支持批量创建**：如需创建多个事件，请逐个使用 `--create`
2. **事件名称冲突**：创建已存在的事件可能报错或覆盖，建议使用 `--verify` 验证
3. **中文显示名称**：App类型事件的中文名称会自动进行URL编码
4. **验证延迟**：事件创建后可能需要几秒钟同步，`--verify` 可能在创建后立即验证时返回不存在
5. **参数格式限制**：
   - `eventName`：只能包含英文字母、数字和下划线，不允许特殊符号 `?` `/` `.` `\` `<` `>`
   - `displayName`：只能包含中文、英文、数字和下划线，不允许特殊符号 `?` `/` `.` `\` `<` `>`
