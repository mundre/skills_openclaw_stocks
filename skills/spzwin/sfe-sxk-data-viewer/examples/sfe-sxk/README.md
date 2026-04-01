# SFE-SXK 示例说明

本目录提供深西康专属数据查询的使用示例。

## 可用能力

- **新活素查房日采集反馈V2**：查询新活素查房日采集反馈数据

## 典型场景

### 场景 1：查询指定时间范围的数据

**用户意图**："帮我查询2025年1月的新活素查房日采集反馈数据"

**执行步骤**：

1. 读取 `openapi/sfe-sxk/xhs-ward-rounds-report-v2.md` 确认参数
2. 执行脚本：

```bash
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --periodStart 2025-01-01 --periodEnd 2025-01-31
```

### 场景 2：查询指定区域的数据

**用户意图**："查询华东大区的新活素查房日采集反馈数据"

**执行步骤**：

```bash
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --regionName "华东大区" --periodStart 2025-01-01 --periodEnd 2025-01-31
```

### 场景 3：分页查询大数据量

**用户意图**："查询2025年第一季度的所有数据，数据量可能很大"

**执行步骤**：

1. 先查询总记录数：

```bash
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --count --periodStart 2025-01-01 --periodEnd 2025-03-31
```

2. 根据总数计算页数，分页查询：

```bash
# 第 1 页
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --periodStart 2025-01-01 --periodEnd 2025-03-31 --page 1

# 第 2 页
python3 scripts/sfe-sxk/xhs-ward-rounds-report-v2.py --periodStart 2025-01-01 --periodEnd 2025-03-31 --page 2
```

## 注意事项

1. 每页固定返回 1000 条记录
2. 所有查询参数均为可选，可组合使用
3. 输出为 TOON 编码格式，便于 AI Agent 处理
4. 时间格式：YYYY-MM-DD
