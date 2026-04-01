# SFE-SXK 脚本使用说明

本目录包含深西康专属数据查询脚本。

## 脚本列表

| 脚本名称                     | 说明                       |
| ---------------------------- | -------------------------- |
| xhs-ward-rounds-report-v2.py | 新活素查房日采集反馈V2查询 |

## 环境变量

所有脚本依赖以下环境变量：

- `XG_BIZ_API_KEY` 或 `XG_APP_KEY`：appKey（必须）

## 使用示例

### 查询数据列表

```bash
# 设置环境变量
export XG_BIZ_API_KEY="your_app_key"

# 查询新活素查房日采集反馈V2数据
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --periodStart 2025-01-01 --periodEnd 2025-01-31

# 查询指定区域数据
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --regionName "华东大区" --periodStart 2025-01-01 --periodEnd 2025-01-31
```

### 查询总记录数

```bash
# 查询记录总数
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --count --periodStart 2025-01-01 --periodEnd 2025-01-31
```

### 分页查询

```bash
# 查询第 2 页数据
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --periodStart 2025-01-01 --periodEnd 2025-01-31 --page 2
```

## 输出格式

所有脚本输出 TOON 编码格式，便于 LLM 直接阅读和处理。

## 参数说明

| 参数            | 说明         | 必填 |
| --------------- | ------------ | ---- |
| --count         | 查询总记录数 | 否   |
| --zoneId        | 区划 ID      | 否   |
| --regionName    | 大区名称     | 否   |
| --districName   | 区域名称     | 否   |
| --areaName      | 地区名称     | 否   |
| --territoryName | 辖区名称     | 否   |
| --periodStart   | 期间开始日期 | 否   |
| --periodEnd     | 期间结束日期 | 否   |
| --page          | 页码         | 否   |
