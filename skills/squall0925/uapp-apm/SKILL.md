---
name: uapp-apm
version: 1.1.0
description: "友盟 APM 数据查询 Skill。当用户询问应用崩溃、ANR、启动性能、网络性能、页面性能等稳定性与性能指标时使用。触发词：崩溃、崩溃率、ANR、启动耐时、启动性能、网络性能、页面性能、APM、稳定性、卡顿。"
entry: scripts/apm.py
---

## 使用流程

**Step 1：确认应用名称**
- 用户未提及应用名时，询问：「请问是哪个 App？」

**Step 2：确认查询类型和参数**
- 根据用户问法匹配下方查询类型表中的 `--query-type`
- 崩溃类型默认查全部（`--error-type 0`），仅 ANR 查询用 `--error-type 3`（且仅 Android）
- 分钟级实时数据需要 `--start-time`，格式 `yyyy-mm-dd HH:MM`

**Step 3：执行并解读输出**
- 稳定性数据：指出崩溃率、影响用户数等关键指标
- 性能数据：指出平均耗时、P90/P95 分位数等

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说 App 名 | 先询问，不要猜测 |
| App名找不到 | 提示「可用 uapp-assets 查询应用列表」 |
| iOS 查询 ANR | 告知「ANR 仅支持 Android，iOS 请用崩溃类型查询」 |
| 分钟级时间超出当天 | 提示「当天 01:00 后仅支持当天数据，01:00 前可查昨天」 |
| 首次运行报少 Tea 模块 | 运行脚本会自动安装依赖，若自动安装失败，参考部署说明手动执行 `pip3 uninstall tea -y && pip3 install alibabacloud-tea` |

## 典型问法与 CLI 参数映射

| 典型问法 | CLI 参数 |
|---------|---------|
| "今天崩溃率多少？" | `--query-type today_stability --app "iOS_Apm测试Demo"` |
| "今天ANR情况？" | `--query-type today_stability --error-type 3 --app "Android_Apm测试Demo"` |
| "过去一周崩溃趋势？" | `--query-type history_stability --range last_7_days --app "iOS_Apm测试Demo"` |
| "App启动耗时怎么样？" | `--query-type launch --range yesterday --app "iOS_Apm测试Demo"` |
| "网络请求平均响应时间？" | `--query-type network --range last_7_days --app "iOS_Apm测试Demo"` |
| "原生页面加载性能？" | `--query-type native_page --range last_30_days --app "iOS_Apm测试Demo"` |
| "H5页面性能数据？" | `--query-type h5_page --range last_7_days --app "iOS_Apm测试Demo"` |
| "最近10分钟网络错误？" | `--query-type network_minute --start-time "2024-09-27 09:07" --app "iOS_Apm测试Demo"` |
| "实时崩溃数据？" | `--query-type error_minute --start-time "2024-09-27 09:07" --app "iOS_Apm测试Demo"` |

## 支持的查询类型

| 类型 | 参数值 | 说明 |
|-----|-------|------|
| 今日稳定性统计 | `today_stability` | 获取今日实时崩溃率、错误数等稳定性指标 |
| 历史稳定性统计 | `history_stability` | 获取历史崩溃率、影响用户数等趋势数据 |
| 启动性能统计 | `launch` | 获取冷启动、热启动、首次启动的耗时统计 |
| 网络性能统计 | `network` | 获取响应时间、错误率、请求量等指标 |
| 原生页面性能统计 | `native_page` | 获取页面加载耗时、慢加载率等指标 |
| H5页面性能统计 | `h5_page` | 获取H5页面DNS、TCP、首字节等指标 |
| 分钟粒度网络统计 | `network_minute` | 获取实时网络请求数、错误数数据 |
| 分钟粒度稳定性统计 | `error_minute` | 获取实时崩溃数、启动数数据 |

## 稳定性类型枚举

`--error-type` 参数支持的值：

| 值 | 名称 | 说明 |
|---|------|------|
| 0 | 全部崩溃 | 默认值，查询所有类型的崩溃 |
| 1 | java/ios崩溃 | Java或iOS层崩溃 |
| 2 | native崩溃 | Native层崩溃 |
| 3 | ANR | 应用无响应（**仅Android支持，iOS不支持**） |
| 4 | 自定义异常 | 用户上报异常 |
| 5 | 卡顿 | 应用卡顿 |

## 支持的时间范围

| 参数值 | 说明 |
|-------|------|
| `yesterday` | 昨天（默认） |
| `last_7_days` | 过去7天 |
| `last_30_days` | 过去30天 |
| `yyyy-mm-dd` | 指定日期 |

## 分钟级时间参数

`--start-time` 参数说明：
- 格式：`yyyy-mm-dd HH:MM`
- 示例：`2024-09-27 09:07`
- 限制：最多返回startTime后10分钟的数据
- 查询规则：当天01点前可查昨天，01点后仅支持当天时间查询

## 调用示例

### 今日稳定性统计

```bash
# 查询今日全部崩溃
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type today_stability

# 查询今日ANR（仅Android）
python3 scripts/apm.py --app "Android_Apm测试Demo" --query-type today_stability --error-type 3
```

### 历史稳定性统计

```bash
# 过去7天崩溃趋势
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type history_stability --range last_7_days

# 过去30天native崩溃趋势
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type history_stability --range last_30_days --error-type 2
```

### 启动性能统计

```bash
# 昨天启动性能
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type launch --range yesterday

# 过去7天启动性能趋势
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type launch --range last_7_days
```

### 网络性能统计

```bash
# 昨天网络性能
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type network --range yesterday

# 过去30天网络性能趋势
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type network --range last_30_days
```

### 页面性能统计

```bash
# 原生页面性能
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type native_page --range last_7_days

# H5页面性能
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type h5_page --range last_7_days
```

### 分钟级实时数据

```bash
# 分钟级网络统计
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type network_minute --start-time "2024-09-27 09:07"

# 分钟级稳定性统计
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type error_minute --start-time "2024-09-27 09:07"
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/apm.py --app "iOS_Apm测试Demo" --query-type today_stability --json
```

## 配置方式

配置文件路径优先级：
1. `--config /path/to/umeng-config.json`
2. 环境变量 `UMENG_CONFIG_PATH`
3. 当前目录下的 `umeng-config.json`

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 注意事项

1. **鉴权信息**：使用 `umeng-config.json` 中的 `apiKey` 和 `apiSecurity` 进行API鉴权
2. **dataSourceId**：APM API使用 `dataSourceId` 参数，值等同于 `appkey`
3. **依赖安装**：首次运行时会自动通过 pip 安装 `alibabacloud_umeng_apm20220214` SDK 及其依赖
4. **API域名**：友盟APM OpenAPI 的 endpoint 为 `apm.openapi.umeng.com`

## 部署说明

### 依赖安装

在 OpenClaw 环境中，首次运行脚本会自动安装依赖。如需手动安装：

```bash
pip3 install alibabacloud_umeng_apm20220214
```

### 常见问题：Tea 模块冲突

**问题现象**：
```
ModuleNotFoundError: No module named 'Tea'
```
或
```
ImportError: cannot import name 'deprecated' from 'Tea.decorators'
```

**原因**：系统中可能存在第三方的 `tea` 包（utility library），与阿里云 `alibabacloud-tea` 包冲突。在 macOS 不区分大小写的文件系统上，`tea` 和 `Tea` 目录会互相覆盖。

**解决方案**：

脚本已内置自动检测和修复逻辑。如自动修复失败，请手动执行：

```bash
pip3 uninstall tea -y
pip3 install alibabacloud-tea
```

**验证安装**：
```bash
python3 -c "from Tea.core import TeaCore; print('OK')"
```
