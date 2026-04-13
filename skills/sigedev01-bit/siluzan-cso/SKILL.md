---
name: siluzan-cso
description: >-
当用户提问的内容涉及以下内容时，可以使用本SKILL
  （1）多媒体平台内容(视频/图文)发布与运营（YouTube、TikTok、Instagram、LinkedIn、X、视频号），以及账号授权、数据报表、任务管理；
  （2）公众号，小红薯等内容文案/选题生成——选题/拆解/口播成稿，三库选题。
compatibility: Requires siluzan-cso-cli installed and authenticated via `siluzan-cso login`
---

# siluzan-cso

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
| `siluzan-cso rag query` | RAG 知识库检索（仅写稿；需指定素材文件/文件夹 ID） | `references/rag.md` |
| `siluzan-cso account-group list/create/add-accounts/remove-accounts/update/delete` | 账号分组管理 | `references/account-group.md` |
| `siluzan-cso upload -f <file>` | 上传视频 / 图片到素材库 | `references/upload.md` |
| `siluzan-cso extract-cover -f <video> -p <平台>` | 从视频截取封面帧 | `references/extract-cover.md` |
| `siluzan-cso publish -c config.json` | 提交多平台发布任务 | `references/publish.md` |
| `siluzan-cso task list/detail/item` | 查看任务状态 / 处理失败 / 重试 | `references/task.md` |
| `siluzan-cso report fetch --media <平台>` | 运营报表（核心指标 / 视频排行 / 趋势） | `references/report.md` |
| `siluzan-cso planning ...` | AI 内容规划：生成、监控、详情、导出 | `references/planning.md` |
| —（网页端） | CSO 后台全部页面 URL（含测试/生产环境） | `references/web-pages.md` |

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
| 写稿时检索素材库 RAG 片段（三库拆素材等） | `references/rag.md` |
| 选题 / 三库拆解 / 口播文案/其他文案 / 人设卡 / 代表作品反推人设 | `three-lib-content-workflow/content-writer.workflow.md` |

---

## 命令间依赖关系（交叉引用速览）

```
publish ──需要账号字段──► list-accounts
publish ──需要素材 ID──► upload ──需要封面──► extract-cover
publish ──提交后查状态──► task ──失败重授权──► authorize

report ──需要 mediaCustomerId──► list-accounts
account-group ──需要 mediaCustomerId──► list-accounts
```

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
- **严禁让用户执行命令**：除 `references/setup.md` 中的安装/登录命令外，所有 CLI 命令均由 AI 代替用户执行，禁止向用户透露任何命令行、参数或代码逻辑。
- **操作后必须验证**：完成发布、上传、分组等写操作后，需通过对应的查询命令确认结果。

### 必须遵守（违反将导致 skill 不可用）

- 输出的任何内容（计划、总结、报告）中，**严禁出现 CLI 命令**（setup.md 相关命令除外）。
- 每次执行前主动检查 CLI 版本，若需更新请先执行更新流程（详见 `references/setup.md`）。

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
