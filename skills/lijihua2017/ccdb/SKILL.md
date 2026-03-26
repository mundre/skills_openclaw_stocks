---
name: ccdb
description: |
  CCDB 碳排放因子搜索工具。基于碳阻迹（Carbonstop）CCDB 数据库，通过 ccdb-mcp-server 查询碳排放因子数据。
  支持关键词搜索碳排放因子、获取结构化 JSON 数据、多关键词对比。

  **当以下情况时使用此 Skill**：
  (1) 用户查询碳排放因子（如"电力排放因子"、"水泥碳排放"、"天然气排放系数"等）
  (2) 用户需要进行碳排放计算（需要先查因子再乘以活动量）
  (3) 用户需要对比不同能源/材料的碳排放因子
  (4) 用户提到 "CCDB"、"碳排放因子"、"排放系数"、"碳足迹"、"LCA"、"emission factor"
  (5) 需要查询特定国家/地区、特定年份的碳排放因子数据
---

# CCDB 碳排放因子搜索

通过 [ccdb-mcp-server](https://www.npmjs.com/package/ccdb-mcp-server) 调用碳阻迹 CCDB 碳排放因子数据库。

## 前置条件

需要全局安装 ccdb-mcp-server：

```bash
npm install -g ccdb-mcp-server
```

无需 API Key，公开接口。

## 可用工具

通过 `mcporter` 以 stdio 模式调用 `ccdb-mcp` CLI，暴露 3 个 MCP 工具：

### 1. search_factors — 搜索碳排放因子（格式化输出）

**用途**：按关键词搜索碳排放因子，返回人类可读的格式化文本。

```bash
mcporter call ccdb-mcp --stdio -- search_factors '{"name":"电力","lang":"zh"}'
```

参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 搜索关键词，如"电力"、"水泥"、"钢铁"、"天然气" |
| `lang` | `"zh"` \| `"en"` | ❌ | 搜索语言，默认 `zh` |

返回：格式化文本，包含因子值、单位、适用地区、年份、发布机构等。

### 2. search_factors_json — 搜索碳排放因子（JSON 输出）

**用途**：与 search_factors 相同，但返回结构化 JSON，适合程序化处理和碳排放计算。

```bash
mcporter call ccdb-mcp --stdio -- search_factors_json '{"name":"电力","lang":"zh"}'
```

参数同 `search_factors`。

返回 JSON 字段说明：
| 字段 | 说明 |
|------|------|
| `name` | 因子名称 |
| `factor` | 排放因子值 |
| `unit` | 单位（如 kgCO₂e/kWh） |
| `countries` | 适用国家/地区 |
| `year` | 发布年份 |
| `institution` | 发布机构 |
| `specification` | 规格说明 |
| `description` | 描述 |
| `sourceLevel` | 因子级别 |
| `business` | 所属行业 |
| `documentType` | 文件类型 |

### 3. compare_factors — 多关键词碳排放因子对比

**用途**：同时对比最多 5 个关键词的碳排放因子，用于横向比较不同能源/材料。

```bash
mcporter call ccdb-mcp --stdio -- compare_factors '{"keywords":["电力","天然气","煤炭"],"lang":"zh"}'
```

参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keywords` | string[] | ✅ | 搜索关键词列表，1-5 个 |
| `lang` | `"zh"` \| `"en"` | ❌ | 搜索语言，默认 `zh` |

## 调用方式

本 Skill 通过 `mcporter` CLI 以 stdio 模式桥接 ccdb-mcp-server：

```bash
# 通用格式
mcporter call ccdb-mcp --stdio -- <tool_name> '<json_arguments>'
```

如果 `mcporter` 尚未配置 ccdb-mcp，先注册：

```bash
mcporter add ccdb-mcp --command "ccdb-mcp" --args "--stdio"
```

**备选方案**（直接用 npx，无需 mcporter）：

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"agent","version":"1.0.0"}}}' | npx -y ccdb-mcp-server --stdio 2>/dev/null
```

或使用下方的**直接 HTTP 调用脚本**（推荐，最轻量）。

## 直接调用脚本（推荐 · 无需安装 MCP Server）

Skill 自带轻量 CLI 脚本 `scripts/ccdb-search.mjs`，直接调用 CCDB 公开 HTTP API，无需安装任何依赖。

### 搜索因子（格式化输出）

```bash
node /workspace/skills/ccdb/scripts/ccdb-search.mjs "电力"
node /workspace/skills/ccdb/scripts/ccdb-search.mjs "cement" en
```

### 搜索因子（JSON 输出，适合计算）

```bash
node /workspace/skills/ccdb/scripts/ccdb-search.mjs "电力" zh --json
```

### 多关键词对比

```bash
node /workspace/skills/ccdb/scripts/ccdb-search.mjs --compare 电力 天然气 柴油
node /workspace/skills/ccdb/scripts/ccdb-search.mjs --compare 电力 天然气 --json
```

### Node.js 一行式（备选）

```bash
node -e "const c=require('crypto'),n=process.argv[1],s=c.createHash('md5').update('mcp_ccdb_search'+n).digest('hex');fetch('https://gateway.carbonstop.com/management/system/website/searchFactorDataMcp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sign:s,name:n,lang:'zh'})}).then(r=>r.json()).then(d=>console.log(JSON.stringify(d,null,2)))" "电力"
```

## 使用场景与示例

### 场景 1：查询某种能源的排放因子

> 用户：中国电网的碳排放因子是多少？

→ 搜索关键词 `"电力"` 或 `"中国电网"`，筛选中国地区、最新年份

### 场景 2：碳排放量计算

> 用户：我公司去年用了 50 万度电，碳排放是多少？

→ 步骤：
1. 搜索 `"电力"` 因子，选中国、最新年份
2. 碳排放 = 500000 kWh × 因子值 (kgCO₂e/kWh)

### 场景 3：不同能源对比

> 用户：对比电力、天然气和柴油的碳排放因子

→ 使用 `compare_factors`，keywords = `["电力", "天然气", "柴油"]`

### 场景 4：特定行业查询

> 用户：水泥行业的碳排放因子

→ 搜索 `"水泥"`

## 注意事项

1. **优先推荐中国大陆地区、最新年份**的因子（除非用户指定其他地区）
2. **因子值需注意单位换算**：不同因子的单位可能不同（kgCO₂/kWh vs tCO₂/TJ 等）
3. **数据来源权威性**：关注发布机构（如生态环境部、IPCC、IEA 等）
4. **搜索无结果时**：尝试换同义词（如"电"→"电力"→"电网"→"electricity"）
5. **计算场景用 JSON 版本**：`search_factors_json` 返回精确数值，适合计算
