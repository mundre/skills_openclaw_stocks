---
name: zwds-openclaw
version: 1.0.0
description: 通过 zwds-cli（Node、iztro 2.5.0）生成紫微斗数结构化命盘 JSON，并仅依据该 JSON 解盘。在用户提及紫微斗数、排盘、命盘、十二宫、四化、解盘、生辰八字时辰、命宫、大限、流年时使用。含 iztro 官方 API 速查；禁止 py-iztro 与脱离 JSON 臆造星曜。真太阳时与地名规则见 reference.md。
---

# 紫微斗数（OpenClaw / zwds 技能）

## 何时使用

用户需要**紫微斗数结构化命盘**（十二宫、主星、四化、流年年龄列表等），或在此基础上**解盘、论命**时启用本技能。

## 硬禁止

- **不得**在运行环境中 `pip install py-iztro` 或依赖 `pythonmonkey`。
- **不得**用 Python 直接调用 iztro。
- **不得**依赖外部在线排盘 API、地理编码服务或远程数据库；经度仅来自本技能自带的 `zwds-cli/data/longitudes.json` 或用户提供的 `longitude`。

**标准排盘**：须使用本目录下的 **`zwds-cli`**（内置真太阳时、`time_index` 映射及统一 JSON 输出，见下文 shell 契约）。

**直接调用 `iztro` npm 库**：仅当你要写**额外** Node 脚本（例如按官方文档试验 `horoscope`、流耀 API）时使用；见下文「iztro 官方文档与库用法」。跳过 CLI 时**不会**自动套用 `zwds-cli` 内的时辰与真太阳时规则，产盘可能与标准流程不一致。

## 环境前置

1. 安装 **Node.js >= 18**。
2. 在仓库中进入：

   `openclaw-skill/zwds/zwds-cli`

3. 安装依赖：

   `npm ci`

   若失败可改用 `npm install`，并检查网络、registry、文件权限。

## Shell 契约（避免「虚构工具名」）

- **工作目录**：`openclaw-skill/zwds/zwds-cli`
- **命令**：

  `node src/index.js`

- **标准输入**：一段 JSON（可多行，解析前会 `trim`）。
- **标准输出**：单行 JSON。先解析 `success`；为 `true` 时使用 `data` 解盘，为 `false` 时读取 `error`。

示例：

```bash
cd openclaw-skill/zwds/zwds-cli
echo '{"birth_time":"2000-08-16T06:00:00","gender":"female","birth_place":"上海市"}' | node src/index.js
```

不要将排盘封装为平台未注册的「工具名」；统一用上述 **终端 + stdin/stdout** 方式（或平台等价的进程调用）。

## iztro 官方文档与库用法（给 Agent 的 API 速查）

完整说明、类型定义、运限与流耀细节见官方文档：[iztro 快速开始](https://iztro.com/quick-start.html)（紫微研习社 / ziwei.pro）。以下摘录排盘最常用的调用面，便于在 **Node** 中与文档对照。

### 安装与引入

```bash
npm install iztro
```

```javascript
// CommonJS（与 zwds-cli 一致）
const { astro } = require("iztro");

// ES Module
// import { astro } from "iztro";
```

### 取本命盘：`astro.bySolar`

```javascript
const astrolabe = astro.bySolar(solarDateStr, timeIndex, gender, fixLeap, language);
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `solarDateStr` | string | 是 | 阳历 `YYYY-M-D`（月日可不补零，如 `2000-8-16`） |
| `timeIndex` | number | 是 | 时辰序号 **0～12**（早子 0 到晚子 12，含义以官方文档为准） |
| `gender` | string | 是 | `男` 或 `女` |
| `fixLeap` | boolean | 否 | 默认 `true`；闰月前半月算上月、后半月算下月 |
| `language` | string | 否 | 默认 `zh-CN`；另有 `zh-TW`、`en-US`、`ko-KR`、`ja-JP` 等 |

农历入口为 `astro.byLunar(lunarDateStr, timeIndex, gender, isLeapMonth?, fixLeap?, language?)`，内部会换算阳历后再排盘（见[快速开始](https://iztro.com/quick-start.html)）。

返回值为**星盘对象**：含 `solarDate`、`lunarDate`、`chineseDate`、`time`、`palaces`（十二宫数组，每宫含 `majorStars` / `minorStars` / `adjectiveStars` 等）。字段名为 **camelCase**；`zwds-cli` 对外 JSON 转为 **snake_case**，便于解盘阶段阅读。

### 取运限：`astrolabe.horoscope`

```javascript
const h = astrolabe.horoscope("2023-8-28"); // 或 new Date()
// h.decadal / h.yearly / h.monthly / h.daily / h.hourly
// 各层含 palaceNames、mutagen、天干地支等（结构以官方文档为准）
```

第二参数可传 `timeIndex`；若 `date` 中带小时，可省略 `timeIndex`（见文档）。

### 流耀（进阶）

大限/流年流耀一般在 `horoscope()` 返回结构里；单独按干支取流耀可用 `star.getHoroscopeStar`（见[快速开始](https://iztro.com/quick-start.html) 中「获取流耀」一节）。

```javascript
const { star } = require("iztro");
// star.getHoroscopeStar(heavenlyStem, earthlyBranch, "decadal" | "yearly")
```

### 与 `zwds-cli` 的分工（重要）

| 方式 | 何时用 |
|------|--------|
| `zwds-cli` | 需要**统一排盘流程**、或解盘所依据的 JSON 须带 `birth_info.true_solar_time` / `meta` 等本技能约定字段时。 |
| 直接 `astro.bySolar` | 阅读官方示例、写独立小工具、或需要链式 API（如 `astrolabe.star("紫微")...`）时；若要与 `zwds-cli` 同一套时辰与真太阳时，应复用其 `solarTime.js` / `timeIndex.js` 或继续调用 CLI。 |

---

## 两阶段工作流

1. **阶段 A — 排盘**：仅运行 CLI，得到 `data`（命盘 JSON）。不要在此阶段长篇解盘。
2. **阶段 B — 解盘**：**仅基于** `data` 与用户需求做分析；不要重新臆造宫位或星曜。解盘方法与约束见下一节。

**固定存档（可选）**：若同一命盘会多次解读，可将「入参 + CLI 完整输出」存为 `fixtures/*.json`（在 `zwds-cli` 下执行 `npm run save-fixture`，见 `examples.md`）。之后对话直接 **@** 该文件即可，无需每次重跑排盘；读盘仍只使用其中的 `data`（及 `meta` 告警），`_fixture` 仅说明该盘对应的生辰与地点。

---

## 阶段 B — 解盘（必读约束）

### 数据来源与诚实性

- **唯一事实来源**：`success === true` 时响应里的 **`data`**。`meta` 仅用于判断经度是否降级、是否缺出生地等，**不**参与星曜判断。
- **逐字引用**：提到的宫位名、主星/辅星/杂曜名、四化（禄权科忌）、亮度（庙旺利陷等）必须能在对应宫位的 `major_stars` / `minor_stars` / `adjective_stars` 的 `name`、`mutagen`、`brightness` 中找到；**禁止**凭记忆往盘里加星或改宫。
- 若用户问的内容在 `data` 里**没有**对应字段（例如未提供额外流月流日 API），应说明「当前 JSON 未包含该层运限」，不要编造。

### 建议阅读顺序（本命盘）

1. **`birth_info`**：确认阳历、农历四柱摘要、`time`/`time_range`、性别；若有 **`true_solar_time`**，解盘开头可一句说明「已按出生地经度做了简化真太阳时校正」。
2. **`five_elements_class`（五行局）** 与 **`soul_palace` / `body_palace`（命身）**：命宫主星见 `soul_palace.soul`，身宫地支见 `body_palace`；再在 **`palaces`** 里找到 `name === "命宫"` 的那一项，读取其 `major_stars`（可能多主星或空宫借星，以数组为准）。
3. **十二宫**：对 `palaces` 逐项查看 `name`、`heavenly_stem`、`earthly_branch`、三类星曜列表、长生十二神等字段。
4. **四化**：只认各星对象上的 **`mutagen`** 非空值；无则该星在所列层级未标四化。
5. **大限**：每宫有 **`decadal.range`**（起止虚岁）与干支；论「当前大限」时需用户告知年龄或年份，再在对应宫找到覆盖该年龄区间的 `decadal`。
6. **流年**：每宫有 **`yearly`**（年龄列表，表示该宫当流年命宫时的岁数）。用户问某年运势时，用「目标年份 − 出生年」得到岁数，再在盘中查找该岁数出现在哪些宫的 `yearly` 里，这些宫在该年与「流年命宫」相关（解释时仍只引用 JSON 中已有星曜）。

### 三方四正（简则）

- 本命盘上：**本宫索引 `i`，对宫为 `(i+6)%12`，财帛位 `(i+4)%12`，官禄位 `(i+8)%12`**（本技能内三方四正取宫规则）。
- 解某一宫时：除读本宫外，应结合上述三宫的星曜与四化作综合叙述，且**每一处论断仍须指向具体宫位条目中的星曜数据**。

### 按用户问题映射宫位（常见）

| 用户意图（示例） | 优先对照宫位（`palaces[].name`） |
|------------------|----------------------------------|
| 性格、自我、人生基调 | 命宫；可参身宫所在宫 |
| 财运、收入、理财 | 财帛；可参福德、田宅 |
| 事业、学业、社会成就 | 官禄；可参命宫、财帛 |
| 感情、配偶 | 夫妻；可参福德、迁移 |
| 家庭、父母、长辈 | 父母；可参田宅 |
| 子女、生育、晚辈 | 子女 |
| 健康、体质 | 疾厄 |
| 人际、同事、下属 | 仆役 |
| 外出、搬迁、外部环境 | 迁移 |
| 精神状态、嗜好、福气 | 福德 |
| 不动产、家庭资产 | 田宅 |
| 兄弟、同辈 | 兄弟 |

用户若明确指定宫位名称，以用户指定为准，但仍只在 `data.palaces` 中查找该 `name` 对应的项。

### 输出风格与边界

- 先简要列出**依据**（宫位 + 星曜 + 四化原文），再作**推论**；推论使用「倾向」「常见」「需注意」等表述，避免绝对化断语。
- 若 `meta.warnings` 非空或 `longitude_resolution.source === "default"`，应在解盘前或文末提醒：出生地经度可能为默认 120°，**时辰与真太阳时仅供参考**。
- 流派差异（如晚子时换日、中州派安星）与本 CLI 默认（全书系、早子映射）不一致时，应主动说明「本盘按技能约定规则排定」，避免与用户从其他渠道看到的盘硬争对错。

---

## 输入与精度说明

- `birth_time` 使用 ISO 字符串中的**字面**年月日时分参与时辰划分（不按时区把同一时刻换算成另一套钟表时间）；请确保与用户约定好字符串写法与时区含义。
- 有 `birth_place` 时：经度来自内置表或用户提供的 `longitude`；表外地名会退回东经 **120°** 并在 `meta.warnings` 中提示。
- 真太阳时为 **简化模型**：1986–1991 年中国夏令时 + 相对东八区 120° 的经度修正，**不含**均时差。

更细的规则与字段说明见同目录 `reference.md`；示例见 `examples.md`。
