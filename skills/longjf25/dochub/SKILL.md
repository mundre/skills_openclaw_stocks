---
name: dochub
description: >
  All-in-one document management: batch convert to Markdown, auto-categorize, full-text search, and intelligent output.
  全能文档管理技能，整合文档生命周期管理与智能检索。
  Trigger: init/run/process workflows, search documents, generate reports from content.
description_en: "All-in-one document management: batch convert to Markdown, auto-categorize, full-text search, and intelligent output"
description_zh: "全能文档管理技能：批量转 Markdown、自动分类、全文检索、智能输出"
version: 1.3.0
---

# DocHub - Document Workbench / 文档工作台

> **Document Lifecycle Manager** — Convert, categorize, index, search, and output documents in one place.
>
> **文档生命周期管理中枢** —— 从文档"入库"到"检索"再到"输出"，全链路覆盖。

## What's New in v1.3.0

### Naming Convention Enforcement / 命名规范强制执行

**Problem / 问题**: Directory and file names containing spaces or special characters (e.g., `[]` `（）` `——` spaces) cause `read_file` tool to fail on Windows.

**Solution / 解决方案**: A unified naming convention is enforced at ALL stages:

#### Naming Rule / 命名规则
Only the following characters are allowed in directory and file names:
- **Chinese characters** (中文)
- **English letters** (a-z, A-Z)
- **Digits** (0-9)
- **Underscore** `_`
- **Hyphen** `-`

All other characters (spaces, `（）` `【】` `——` `·` etc.) are **replaced by underscore `_`**.

#### Where Applied / 应用范围
| Stage | Action | Example |
|-------|--------|---------|
| **init** | RAW dirs/files renamed first | `2026-1-10 进港全流程招标文书/` → `2026-1-10_进港全流程招标文书/` |
| **init** | Old `_docs_md/` deleted and rebuilt | Clean slate every init |
| **init** | Output MD names normalized | Same rule applied |
| **run** | RAW names re-checked | Catches any manually-added un-normalized names |
| **process** | New files from `update/` renamed | Before category matching and conversion |

#### Bug Fixes / Bug 修复
- Fixed init timeout: added try/except error handling and progress output
- Fixed stale `_docs_md/` accumulation: init now deletes old output before rebuild
- Fixed `run_incremental` source matching for normalized paths

```
Ingest → Categorize → Convert to Markdown → Search → Output
入库 → 分类索引 → Markdown转换 → 智能检索 → 按需输出
```

---

## Prerequisites / 工具依赖

| Tool / 工具 | Install / 安装命令 | Purpose / 用途 |
|------------|-------------------|---------------|
| markitdown | `pip install markitdown` | Document → Markdown core engine / 文档转 Markdown 核心引擎 |
| python-docx | `pip install python-docx` | Word document processing / Word 文档处理 |
| openpyxl | `pip install openpyxl` | Excel document processing / Excel 文档处理 |
| pdfplumber | `pip install pdfplumber` | PDF text extraction / PDF 文字提取 |

> Ensure dependencies before first use / 首次使用前需确保：`pip install markitdown python-docx openpyxl pdfplumber`

---

## Trigger Scenarios / 触发场景

| Scenario / 场景 | Trigger Words / 触发词 |
|-----------------|----------------------|
| Init / 初始化 | 「初始化文档工作流」「文档工作台初始化」「init doc workflow」 |
| Incremental / 增量 | 「增量更新」「批量转换文档」「incremental convert」 |
| New docs / 新文档 | 「有新文档要处理」「处理新文档」「process new documents」 |
| Search / 检索 | 「查找」「搜索」「有没有」「关于...的文档」「...在哪里」「latest/historical docs」 |
| Output / 输出 | 「生成摘要」「整理成报告」「对比分析」「summarize」「generate report」 |

---

## Part 1: Document Management / 第一部分：文档管理流程

### Core Design / 核心设计理念

**Flexibility first / 灵活性优先**: Two categorization modes, user-selected at initialization:
**灵活性优先**：支持两种分类模式，用户可在初始化时自行选择：

1. **Keep original structure / 保持原有目录结构**: Preserve existing folder hierarchy / 保留用户已有的文件夹分类
2. **Auto-analyze / 系统自动分析创建分类**: Dynamic keyword-based categorization / 动态分析文档内容，根据关键词相似度自动生成分类

- Default: keep original structure / 默认选择「保持原有结构」，尊重用户的组织习惯

### Three Modes / 三种工作模式

```
init     → Initialize (first-time setup, ask user for mode) / 初始化（首次设置，询问用户后执行）
run      → Incremental convert (daily use, update changed files) / 增量转换（日常使用，已有结构下增量更新）
process  → Process new docs (from update/: classify + convert + clear) / 处理新文档（从 update/ 分类+转换+清空）
```

---

## Workflow 1: Initialize / 工作流一：初始化

When user says 「初始化文档工作流」/ "init doc workflow", execute / 当用户说时执行：

```bash
# With default mode (keep structure) / 默认模式（保持原有结构）
python scripts/batch_convert.py init <workspace>

# Specify mode / 指定分类模式
python scripts/batch_convert.py init <workspace> --mode 1   # Keep structure / 保持原有结构
python scripts/batch_convert.py init <workspace> --mode 2   # Auto-categorize / 系统自动创建分类
```

### Steps / 执行步骤

**Step 0 — Ask classify preference / 询问分类偏好** (interactive mode only / 仅交互模式)

```
Select categorization mode / 请选择分类结构创建方式：

  [1] Keep original structure / 保持原有目录结构
      - Organize docs into _docs_md/ preserving current folders
      - 不创建新的分类目录

  [2] Auto-analyze & categorize / 系统自动分析创建分类
      - Analyze document keywords
      - Group by content similarity

Enter [1/2] (default 1) / 请输入选择 [1/2]（默认 1）:
```

**Mode 1: Keep original structure / 模式一：保持原有目录结构（默认）**

1. Scan all docx/xlsx/pdf/doc files / 扫描所有文档，保持原有目录层级
2. Create directory structure / 创建目录结构：
```
workspace/                        工作文件夹/
├── _docs_md/                     ← Markdown output / Markdown 输出目录
│   ├── subfolder/                ← Preserved categories / 保持原有分类
│   │   ├── report.md
│   │   └── ...
│   └── ...
├── update/                       ← New document drop zone / 新文档入口（自动创建）
└── _convert_log.txt              ← Processing log / 处理日志
```

**Mode 2: Auto-analyze / 模式二：系统自动分析创建分类**

1. Scan all documents / 扫描所有文档
2. Content analysis (sample up to 30) / 内容分析（采样最多30个），提取关键词
3. Dynamic categorization / 基于关键词相似性将文档分组
4. Create directory structure / 创建目录结构
5. Batch convert to Markdown / 批量转换为 Markdown
6. Generate index: `_docs_md/_index.md` / 生成索引文件
7. Report results / 汇报结果

---

## Workflow 2: Incremental Convert / 工作流二：日常增量转换

When existing structure exists, update changed files only / 当已有初始化后的结构，只需要增量更新时：

```bash
python scripts/batch_convert.py run <workspace>
```

Automatically compare modification times, convert only new/changed files. / 自动扫描 `_docs_md/` 中已有转换，对比源文件修改时间，只更新有变化的文件。

---

## Workflow 3: Process New Documents / 工作流三：处理新文档

When user drops docs into `update/` and says 「有新文档要处理」/ "process new documents"：

```bash
python scripts/batch_convert.py process <workspace>
```

Steps / 执行步骤：Read → Analyze keywords → Match category → Copy to `_docs_md/` → Convert → Clear `update/` → Report / 读取 → 分析关键词 → 匹配分类 → 复制到 `_docs_md/` → 转换 MD → 清空 update/ → 汇报结果。

---

## Categorization Algorithm / 分类算法说明

### Keyword Extraction / 关键词提取
1. Remove punctuation, numbers, English stopwords / 移除标点、数字、英文停用词
2. Count word frequency, take top 20 / 统计词频，取 top 20
3. Use top 5 words as document signature / 取前5个词作为文档签名

### Similarity Matching / 相似度匹配
- Compare document signature with existing category top-10 keywords / 已有类别的关键词 top 10 与新文档签名对比
- Overlap ≥ 1 → assign to category / 重合度 ≥ 1 → 归入该类别
- Overlap = 0 → create new category / 重合度 = 0 → 新建类别

---

## Directory Conventions / 目录结构约定

| Directory / 目录 | Purpose / 用途 |
|-----------------|---------------|
| `_docs_md/` | Converted Markdown files (for search & reading) / Markdown 转换文件 |
| `_docs_md/_index.md` | Document index with links / 所有文档的清单和链接 |
| `update/` | New document drop zone / 新文档入口 |
| `_convert_log.txt` | Processing log / 处理过程日志 |

---

## Part 2: Document Search / 第二部分：智能文档检索

### Search Strategy / 核心检索策略

**Three-level funnel search / 三级漏斗检索**：from fast to slow, broad to precise / 从快到慢、从粗到精。

```
Level 1: Knowledge base file (instant, overview) / 工作知识库.md（秒级）
   ↓ Not found or need more detail / 未找到或需要更多细节
Level 2: _docs_md/ folder (fast, full-text Markdown search) / Markdown 全文搜索
   ↓ Not found / 未找到
Level 3: Original documents (slow, search docx/xlsx/pdf) / 原始文档搜索
```

> **Key principle / 关键原则**: Always prefer Markdown versions. Fall back to originals only when MD search yields no results. / 优先使用 Markdown 版本。只有当 MD 搜索无结果时，才降级到原始文档搜索。

### Level 1: Knowledge Base / 第一级

**File**: `工作知识库.md` (workspace root, if exists) / 工作区根目录（如存在）

Read full text → check for relevant info → direct answer or escalate to Level 2.

### Level 2: Markdown Search / 第二级

**Scope / 搜索范围**: `_docs_md/` folder

Use `search_content` tool with Chinese keywords, e.g., `pattern: "纪检.*汇报"`. Check `_index.md` for full file listing.

### Level 3: Original Documents / 第三级（降级）

**Scope / 搜索范围**: All original documents (docx/xlsx/pdf/doc)

Use `search_file` by filename, then `read_file` for content. Lower success rate — use as last resort.

---

## Part 3: Document Output / 第三部分：基于检索结果的文档输出

> **Search is not the end; output is the goal.** / 检索不是终点，输出才是目的。

### Output Modes / 输出模式

| Mode / 模式 | Description / 说明 | Example / 示例 |
|------------|-------------------|---------------|
| Direct answer / 直接回答 | Present key info as text / 以文字形式呈现关键信息 | 「最新纪检工作汇报内容是什么？」 |
| Summary / 摘要生成 | Extract core content, structured summary / 提取核心内容，结构化摘要 | 「帮我总结今年的工作报告」 |
| Comparison / 对比分析 | Compare multiple documents, generate tables / 对比多个文档，生成对比表 | 「对比2024年和2025年的述职报告」 |
| Data extraction / 数据提取 | Extract structured data to Excel/CSV / 提取结构化数据到表格 | 「把各月货量数据整理成Excel」 |
| Integration / 内容整合 | Merge multiple docs into a new document / 整合多个文档为新文档 | 「把几份汇报整合成一份报告」 |

### Output Format Selection / 输出格式选择

| Format / 格式 | Scenario / 适用场景 | Skill / 技能 |
|--------------|-------------------|-------------|
| Text / 文字 | Quick queries / 快速查询 | Direct output / 直接输出 |
| .docx | Reports, memos / 正式报告、公文 | docx skill |
| .xlsx | Data tables, statistics / 数据整理、统计 | xlsx skill |
| .pptx | Presentations / 演示汇报 | pptx skill |
| .pdf | Archive, formal publish / 归档、正式发布 | pdf skill |
| .md | Internal reference / 内部参考 | Direct generation / 直接生成 |

### Output Standards / 输出规范

1. **Cite sources / 标注来源**: `[来源：文档名.md]` for each section
2. **Accuracy / 保持准确性**: Based on retrieved content only / 仅基于检索到的原文内容
3. **Scoping / 按需裁剪**: Respect user-specified scope / 根据用户指定的范围裁剪
4. **Clear structure / 结构清晰**: Proper headings and logical flow / 清晰的标题层级

---

## Query Examples / 常见查询场景示例

| Query / 用户问题 | Processing / 处理方式 |
|-----------------|---------------------|
| "最新的纪检工作汇报" / "latest discipline report" | Three-level search → locate → read → answer or output |
| "ETV的测试结果" / "ETV test results" | Knowledge base → MD search → extract → summarize |
| "2024和2025年货量对比，整理成Excel" | Search both years → extract data → generate xlsx |
| "把最近三份汇报整合成Word报告" | Retrieve 3 docs → extract → organize → generate docx |
| "有没有关于指定仓的资料" / "any docs on warehouse X" | KB → MD search → list all related docs |

---

## Script Parameters / 脚本参数说明

```
python scripts/batch_convert.py <mode> <workspace>

Modes:
  init     Initialize: scan + analyze + categorize + convert + index / 初始化
  run      Incremental: convert only new/changed files / 增量
  process  Process update/ folder: classify + convert + clear / 处理新文档

Workspace:
  Required (or defaults to current directory) / 必填，指定工作目录，省略则默认当前目录

Extra:
  --mode 1  Keep original structure (default) / 保持原有目录结构（默认）
  --mode 2  Auto-analyze & categorize / 系统自动分析创建分类
```

---

## Security Mechanisms / 安全机制

| Mechanism / 机制 | Description / 说明 |
|-----------------|-------------------|
| **Original files untouched / 原文件安全** | Conversion works on copies only; originals are never modified / 转换仅在副本上操作，原文件不变 |
| **Path traversal guard / 路径穿越防护** | Workspace paths are validated to prevent directory traversal attacks / 工区路径校验，防止目录穿越攻击 |
| **Safe subprocess / 安全子进程** | External tool (markitdown) invoked via Python module with timeout / markitdown 通过 Python 模块调用，带超时限制 |
| **Temp file cleanup / 临时文件清理** | Temp files are always cleaned up in `finally` blocks / 临时文件在 finally 块中确保清理 |
| **No external connections / 无外部连接** | Script runs entirely locally with no network access / 脚本完全本地运行，无任何网络访问 |
| **No credential handling / 无凭证处理** | No passwords, tokens, or credentials are processed / 不处理任何密码、令牌或凭证信息 |
| **Log write safety / 日志容错** | Log writes are wrapped in try/except to never crash the main process / 日志写入异常不会中断主流程 |

---

## Supported Formats / 支持格式

| Format / 格式 | Supported / 是否支持 | Notes / 备注 |
|--------------|---------------------|-------------|
| `.docx` | ✅ Yes | Full support / 完全支持 |
| `.xlsx` | ✅ Yes | Full support / 完全支持 |
| `.pdf` | ✅ Yes | Via markitdown + pdfplumber / 通过 markitdown + pdfplumber |
| `.doc` | ❌ No | Legacy binary format; suggest converting to .docx first / 旧版二进制格式，建议先转为 .docx |

---

## FAQ / 常见问题

### Large doc collection, slow init? / 文档量很大初始化很慢？
Sample limited to 30 docs for analysis; conversion is still full. ~300 docs take 10-20 min. / 最多采样30个文档进行分析，转换仍是全量执行。300个文档约需10-20分钟。

### Unsatisfied categorization? / 分类结果不满意？
- Mode 1: structure = your existing folders / 模式一：分类结果就是用户原有的目录结构
- Mode 2: manually adjust `_docs_md/` subdirectories, or re-run `init` / 模式二：可手动调整 `_docs_md/` 下的分类目录，或重新执行 init

### Will original files be moved? / 原始文件会被移动吗？
No. MD files are stored in `_docs_md/`. Only `process` mode copies from `update/` then clears it. / 不会。转换过程中原始文件不动。只有 `process` 模式会将 update/ 中的文件复制到分类目录后清空。

### Can't find a document? / 检索不到需要的文档？
1. Check if MD version exists in `_docs_md/` / 确认 `_docs_md/` 中是否有 MD 版本
2. Try different keywords / 尝试使用不同的关键词搜索
3. Check `_docs_md/_index.md` for full listing / 检查索引文件查看所有可用文档
4. If new docs, run incremental `run` first / 如果是新文档，先执行增量转换

### .doc files failed to convert? / 有 .doc 文件未能转换？
Legacy `.doc` (Word 97-2003 binary) is not supported by markitdown. Solution:
旧版 `.doc` 不支持。处理方式：
1. Open in Word → Save As `.docx` / 用 Word 打开 → 另存为 .docx
2. Put `.docx` into `update/` → trigger process / 放入 update/ 目录 → 触发处理

---

## File Structure / 文件结构

```
dochub/                           文档工作台/
├── SKILL.md                      ← Skill definition / 技能定义文件
└── scripts/
    └── batch_convert.py          ← Core script / 核心脚本 (init/run/process)
```
