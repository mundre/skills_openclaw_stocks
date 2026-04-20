---
name: siluzan-cso
description: 当用户提问的内容涉及以下内容时，可以使用本SKILL（1）多媒体平台内容(视频/图文)发布与运营（YouTube、TikTok、Instagram、LinkedIn、X、视频号），以及账号授权、数据报表、任务管理；（2）公众号、小红书等内容文案/选题生成——选题/拆解/口播成稿、三库选题；（3）RAG 知识库检索——回答产品/品牌问题、写需要品牌素材的文案。
compatibility: Requires siluzan-cso-cli installed and authenticated via `siluzan-cso login`
---

# siluzan-cso

## 一键安装

如果 CLI 尚未安装，直接帮用户执行对应平台的安装脚本：

- **macOS / Linux / WSL：**
  ```bash
  bash <(curl -fsSL https://unpkg.com/siluzan-cso-cli@latest/dist/skill/scripts/install.sh)
  ```
- **Windows PowerShell：**
  ```powershell
  irm https://unpkg.com/siluzan-cso-cli@latest/dist/skill/scripts/install.ps1 | iex
  ```

脚本会自动完成 Node.js 检测/安装、CLI 安装、Skill 全局注册，并引导用户配置 API Key。无需选择，本脚本专为 siluzan-cso-cli 定制。

---

## 可执行的操作范围

- **只读**：查询媒体账号列表、账号分组、运营报表、发布任务状态、人设列表、RAG 知识库检索、AI 内容规划详情
- **写入**（需用户确认）：上传素材、提交发布任务、创建/更新账号分组、生成 AI 内容规划、站内信回复
- **本地文件操作**：`extract-cover` 在本地截取视频帧并输出图片文件；`init` 将 Skill 文件写入 AI 助手目录

---

## 可选环境变量

| 变量 | 说明 |
|------|------|
| `SILUZAN_API_KEY` | 从环境变量读取 API Key（优先级高于 config.json，CI/CD 推荐） |
| `SILUZAN_AUTH_TOKEN` | 从环境变量读取 JWT Token（优先级高于 config.json） |
| `SILUZAN_DATA_PERMISSION` | 从环境变量读取数据权限标识（优先级高于 config.json） |

---

## 能力范围

| 业务流程 | 手段 | 说明 |
|------|------|------|
| **发布与运营** | 下方 CLI 命令 + `references/*.md` | 上传、发布、任务、报表、账号、规划等 |
| **文案生产（子流程）** | `three-lib-content-workflow/content-writer.workflow.md` | 选题、三库、口播/成稿|

两类流程同属 CSO 业务。文案生产流程嵌套在本 skill 内，见下文「三库内容工作流」。

## 命令索引

| 命令 | 作用 | 详细文档 |
|------|------|----------|
| `siluzan-cso login` | 登录 / 配置凭据 | `references/setup.md` |
| `siluzan-cso config show/set/clear` | 查看 / 修改 / 清空本地配置 | `references/setup.md` |
| `siluzan-cso init` | Skill 文件初始化（写入 AI 助手目录） | `references/setup.md` |
| `siluzan-cso update` | 更新 CLI 版本并刷新 Skill 文件 | `references/setup.md` |
| `siluzan-cso authorize --media-type <平台>` | 发起媒体账号 OAuth 授权 | `references/authorize.md` |
| `siluzan-cso list-accounts` | 列出媒体账号，获取账号 ID / 数据总览 | `references/list-accounts.md` |
| `siluzan-cso persona list` | 拉取 CSO 人设列表（含 styleGuide Markdown） | `references/persona.md` |
| `siluzan-cso rag list` | 列出知识库文件夹；`--rag-only` 仅已建索引；`--folder-id` 查指定文件夹下的子库 | `references/rag.md` |
| `siluzan-cso rag query` | RAG 知识库检索；默认全量（不过滤标签）；`--folder-id` 限定范围；`--tags` 按标签精确筛选 | `references/rag.md` |
| `siluzan-cso account-group list/create/add-accounts/remove-accounts/update/delete` | 账号分组管理 | `references/account-group.md` |
| `siluzan-cso upload -f <file>` | 上传视频 / 图片到素材库 | `references/upload.md` |
| `siluzan-cso extract-cover -f <video> -p <平台>` | 从视频截取封面帧 | `references/extract-cover.md` |
| `siluzan-cso publish -c config.json` | 提交多平台发布任务 | `references/publish.md` |
| `siluzan-cso task list/detail/item` | 查看任务状态 / 处理失败 / 重试 | `references/task.md` |
| `siluzan-cso report fetch --media <平台>` | 运营报表（核心指标 / 视频排行 / 趋势） | `references/report.md` |
| `siluzan-cso planning ...` | AI 内容规划：生成、监控、详情、导出 | `references/planning.md` |
| —（网页端） | CSO web端全部页面 URL | `references/web-pages.md` |

---



## 常见业务场景 → 阅读哪个文件

| 用户在做什么 | 先阅读 |
|--------------|--------|
| 首次安装 / 登录 / 更新 | `references/setup.md` |
| 发布视频或图文 | `references/publish.md` |
| 上传素材 | `references/upload.md` |
| 截取视频封面 | `references/extract-cover.md` |
| 查发布记录 / 处理失败 | `references/task.md` |
| 查账号数据 / 运营报表 | `references/report.md` |
| 查找账号 ID 或账号详情 | `references/list-accounts.md` |
| 账号 Token 失效 / 重新授权 | `references/authorize.md` |
| 管理账号分组 | `references/account-group.md` |
| AI 内容规划 | `references/planning.md` |
| 需要给用户提供后台页面链接 | `references/web-pages.md` |
| 拉取人设 / styleGuide（写稿前） | `references/persona.md` |
| 写稿时检索素材库 RAG 片段（三库拆素材等） | `references/rag.md`（先 `rag list` 选库，再多次 `rag query` 拆词检索） |
| 选题 / 三库拆解 / 口播文案/其他文案 / 人设卡 / 代表作品反推人设 | `three-lib-content-workflow/content-writer.workflow.md` |

---

## 命令间依赖关系（交叉引用速览）

```
publish ──需要账号字段──► list-accounts
publish ──需要素材 ID──► upload ──需要封面──► extract-cover
publish ──提交后查状态──► task ──失败重授权──► authorize

report ──需要 mediaCustomerId──► list-accounts
account-group ──需要 mediaCustomerId──► list-accounts

rag query ──需要知识库 ID──► rag list（按用户意图自动选择）
```

---

## RAG 知识库检索工作流

> 详细检索策略见 `references/rag.md`，以下为决策摘要。

### 何时使用 RAG

- ✅ 询问特定品牌/产品知识、写需要品牌素材的文案 → **必须先 RAG**
- ✅ 执行三库内容工作流 → **按三库分库检索**
- ❌ 询问平台操作方法、纯通用创作、用户明确不需要 → **跳过 RAG**

### 四步执行流程

**Step 1 — 获取知识库**（只在任务开始时调用一次）

```bash
# 列出所有已建索引的根级知识库
siluzan-cso rag list --rag-only --json

# 若根级库下还有子文件夹，可钻取查看
siluzan-cso rag list --folder-id <父文件夹id> --rag-only --json
```

**Step 2 — 选择知识库**（按名称语义匹配）

- 用户提到品牌名 → 找名称最匹配的文件夹，记录 `id`
- 多品牌 → `--folder-id id1,id2`（逗号分隔）
- 无明确品牌 → 不传 `--folder-id`（全库检索）

**Step 3 — 拆词多轮检索**（2–5 个子查询，每个聚焦一个维度）

```bash
# 默认不传 --tags = 全量检索（适用于绝大多数场景）
siluzan-cso rag query -q "产品核心卖点" --folder-id <id> --top-k 10
siluzan-cso rag query -q "用户使用场景" --folder-id <id>
siluzan-cso rag query -q "品牌差异优势" --folder-id <id>

# 仅当知识库已按标签打标，且需要精确筛选时才传 --tags
siluzan-cso rag query -q "抖音爆款钩子" --tags "流量因子库"
siluzan-cso rag query -q "产品卖点故事" --tags "产品资产库"
```

**Step 4 — 合成使用**

将多轮结果去重 → 按相关度（score 越小越相关）排序 → 作为写稿/回答的事实依据，重新组织表达（不直接粘贴原文）。

---

## AI 行为规范

### 执行任务的标准流程

遵循**计划 → 确认 → 执行 → 验证 → 预测**五步：

1. **计划**：根据用户意图，查阅命令索引与 references，或「三库内容工作流」与 `GetPersonas` 人设要求，制定操作步骤，不暴露命令行细节。
2. **确认**：与用户确认关键信息（目标账号、发布内容、时间等），不替用户做选择。
3. **执行**：按计划调用命令，处理异常。
4. **验证**：
   - 写入/修改操作后，通过读取命令确认结果是否正确。
   - 失败时优先尝试重试或用其他方式补救，而不是直接告知用户"任务失败"。
5. **预测**：任务完成后，结合当前结果对用户下一步操作给出合理建议。

### 硬规范

- **不确定时先读文档**：遇到不熟悉的命令，先查对应 references 文件，不猜参数。
- **先查账号再操作**：对具体账号做操作前，先用 `list-accounts --name <名称> --media-type <平台>` 确认账号存在且 Token 有效。
- **使用 `--json` 处理数据**：需要对返回结果做计算或筛选时，加 `--json` 再用 `node -e` 提取（`node -e "const d=require('fs').readFileSync('/dev/stdin','utf8'); ..."`）。
- **不猜账号 ID**：`entityId` ≠ `mediaCustomerId`，两者均须从 `list-accounts --json` 获取，不可假设。
- **命令透明性**：以简洁的方式向用户说明即将执行的操作意图（如「正在上传视频到素材库」「正在为您查询 YouTube 账号列表」），让用户了解操作进度。用户主动要求查看执行细节时，应如实提供完整命令。安装/登录/更新等一次性命令（见 `references/setup.md`）可直接展示给用户自行执行。
- **操作后必须验证**：完成发布、上传、分组等写操作后，需通过对应的查询命令确认结果。

### 必须遵守

- 主动更新（详情请读取 `references/setup.md`）。
- **破坏性操作必须用户确认**：涉及写入/修改/删除的操作（发布、上传、分组变更等），执行前必须明确告知用户操作内容并获得确认。
- **只读操作可自主执行**：查询类命令（`list-accounts`、`report fetch`、`task list`、`config show` 等）可直接执行，无需额外确认。
- 禁止提供虚假信息，比如web端连接就必须确认 `references/web-pages.md` 中存在才能提供给用户
---

## 常见 HTTP 错误处理

| 状态码 | 原因 | 处理方式 |
|--------|------|----------|
| `400 Bad Request` | 参数错误 | 查对应 references 文档或用 `--help` 确认命令用法 |
| `401 Unauthorized` | 凭据失效 | 引导用户重新执行 `siluzan-cso login`（详见 `references/setup.md`） |
| `500 Internal Server Error` | 服务部署中或数据异常 | 稍后重试；若持续失败，提交给 Siluzan 相关人员处理 |

---

## 平台名称速查
阅读： `references/authorize.md`
---

## Web 功能导航

> 无对应 CLI 命令的模块，或需要引导用户在网页端查看数据时，查阅 `references/web-pages.md` 获取完整页面清单与链接。

URL 格式：`https://www.siluzan.com/v3/foreign_trade/cso/{页面}`

常用页面：`task`（任务管理）· `postVideo`（发布页）· `ManageAccounts`（账号管理）· `planning`（AI 内容规划）· `table`（绩效报表）· `Workdata`（作品数据）
