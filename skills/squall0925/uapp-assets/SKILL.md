name: uapp-assets
version: 1.0.0
summary: 友盟应用资产查询 skill，帮助用户快速了解"我在友盟有哪些应用"。支持查询 App 数量、App 列表、小程序列表。
entry: scripts/assets.py

## When to Use

- 用户询问"我一共注册了多少个应用？"
- 用户询问"列出我所有的 App？"
- 用户询问"我的小程序列表？"
- 用户需要了解应用资产概况
- 关键词：应用列表、小程序列表、应用数量、应用资产

## When NOT to Use

- 查询具体应用的统计数据（应使用 uapp-core-index）
- 查询渠道/版本分布（应使用 uapp-channel-version）
- 查询留存数据（应使用 uapp-retention）
- 查询事件数据（应使用 uapp-event）
- 查询 APM 性能数据（应使用 uapp-apm）

## 典型问法与 CLI 映射

| 典型问法 | CLI 命令 |
|---------|----------|
| "我一共注册了多少个应用？" | `--count` |
| "列出我所有的 App？" | `--list-apps` |
| "我的小程序列表？" | `--list-minis` |
| "我有多少小程序？" | `--list-minis` |
| "列出所有应用和小程序" | `--list-all` |

## CLI 命令

### 查询 App 数量

```bash
python3 scripts/assets.py --count
```

### 列出 App 列表

```bash
# 第 1 页
python3 scripts/assets.py --list-apps

# 指定页码
python3 scripts/assets.py --list-apps --page 2

# 按 Android 平台过滤
python3 scripts/assets.py --list-apps --platform android
```

### 列出小程序列表

```bash
# 第 1 页
python3 scripts/assets.py --list-minis

# 按小程序平台过滤（模糊匹配）
python3 scripts/assets.py --list-minis --platform mini
```

### 同时列出 App 和小程序

```bash
python3 scripts/assets.py --list-all
```

## 通用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 配置文件路径 | 自动查找 |
| `--page` | 页码 | 1 |
| `--per-page` | 每页记录数（最大 100） | 100 |
| `--platform` | 平台过滤（支持模糊匹配） | 无 |
| `--output` | 输出格式：table/json | table |

## 平台过滤

支持模糊匹配：

| 过滤值 | 匹配平台 |
|--------|----------|
| `android` | android |
| `iphone` / `ios` | iphone |
| `mini` | 所有小程序平台（mini_weixin, mini_bytedance 等） |
| `mini_bytedance` | mini_bytedance（精确匹配） |

## 输出格式

### Table 格式（默认）

```
名称            平台      AppKey                    创建时间
友盟SDK         android   4f83c5d852701564c0000011   2012-04-10

共 893 个应用，当前显示第 1-100 条（第 1/9 页）
提示：输入 "下一页" 查看后续数据
```

### JSON 格式

```bash
python3 scripts/assets.py --list-apps --output json
```

返回结构化 JSON，便于脚本调用。

## 配置方式

1. `--config /path/to/umeng-config.json`: 显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`: 环境变量
3. 在当前目录创建 `umeng-config.json`: 默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 独立部署

该 skill 内置友盟 OpenAPI Python SDK，可直接复制 `skills/uapp-assets/` 目录到其他位置独立运行。

## 相关 Skill

- **uapp-core-index**: 核心指标查询（DAU、新增用户等）
- **uapp-channel-version**: 渠道和版本分布查询
- **uapp-retention**: 留存数据查询
- **uapp-event**: 自定义事件查询
- **uapp-umini**: 小程序统计指标查询
