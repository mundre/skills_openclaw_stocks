---
name: skill-manager-all-in-one
description: "Manage OpenClaw skills and ClawFlows end to end: create, modify, publish with checklist and two-step workflow, changelog, audit. 一站式管理技能创建、修改、发布(含检查清单两步流程)、ClawFlows工作流、审计与宣传。"
---

# Skill Manager | 技能管理器

Manage OpenClaw skills from local discovery to ClawHub publishing. 负责 OpenClaw 技能从本地发现到 ClawHub 发布的全流程管理。

## Core rules | 核心规则

1. **Local first, network second** - check installed skills before searching ClawHub.
   **先本地,后网络**--先检查已安装技能,再决定是否搜索 ClawHub。

2. **User approval first** - do not publish, update, delete, hide, or materially rewrite a skill without explicit user consent.
   **先获用户同意**--未经明确确认,不要发布、更新、删除、隐藏,或实质性改写技能。

3. **Be concrete** - report exact paths, exact commands, and exact version changes.
   **表达具体**--汇报时写清楚准确路径、准确命令、准确版本变化。

4. **Prefer formal release language** - ClawHub release text should read like a product release note, not a casual chat log.
   **发布语言要正式**--ClawHub 发布文本应像正式发布说明,而不是聊天记录。

5. **Teach good output, not just good structure** - this is a supervisory skill, so its guidance must produce clean, publishable names, descriptions, changelogs, and promotion copy.
   **不仅结构达标,输出也要达标**--这是指导性技能,它给出的名称、描述、changelog 和宣传文案也必须干净、可发布、对外体面。

6. **Write for both AI and humans** - future skills should be readable by agents and by people, especially Chinese-speaking users.
   **同时面向 AI 和人类**--后续制作的技能应兼顾 agent 与人类可读性,尤其要照顾中文用户。

## Skill creation/modification checklist | 技能制作/修改清单

When creating or modifying **any** skill (including this one), verify all of the following:

### Language order | 语言顺序
- [ ] **Title**: English first, then Chinese. Format: `English | 中文名`
- [ ] **Description**: English first, then Chinese; ≤ **150 characters** total; comprehensive enough to serve as the primary trigger mechanism
- [ ] **Body**: English as main structural spine; Chinese for key rules and critical workflows; both languages must be complete, not an afterthought

### De-identification & Scientificity | 去标识化与科学性
- [ ] **De-identification**: no personal identity info, no internal system paths, no private details
- [ ] **Scientificity**: no pseudoscience, no folk remedies, logically self-consistent

### Readability & Maintainability | 可读性与可维护性
- [ ] **AI readability**: clear structure, explicit hierarchy, no ambiguous expressions, no hidden information the AI might miss
- [ ] **Human maintainability**: sufficient comments, modular organization, no excessive nesting
- [ ] **Contextual coherence**: systematic, organically integrated, no scattered patches, no "east then west" disorganization

### Stability & Efficiency | 稳定性与高效性
- [ ] **Stability**: no dangling references, no dead links, command paths are accurate
- [ ] **Efficiency**: no token waste (no keyword stuffing, no verbose filler), reduces hallucination risk

## Publishing workflow | 发布工作流（两步流程）

### Step 1: Pre-publish checks | 第一步：发布前检查

Before any publish action, perform all checks and report to user:

**A. Checklist verification | 清单核对**
- Verify all items in the "Skill creation/modification checklist" above.
  逐项核对"技能制作/修改清单"全部项目。

**B. File size check | 文件大小检查**
- Run `du -sh <skill-dir>` to check total size.
- If the skill directory **exceeds 50MB**, the upload will fail.
  - Report to user immediately.
  - Move oversized files (e.g., model files) to a workspace backup location.
  - Wait for user's explicit confirmation before proceeding.
  - After successful upload, move files back (again wait for user confirmation).
  如果 skill 目录**超过 50MB**，上传会失败。立即报告用户，等待明确指示后再操作。

**C. Draft changelog | 拟定 changelog**
- Write bilingual changelog: English first, Chinese after.
  英文在前,中文在后。
- Use **formal release-note tone**. Do NOT include: personal corrections, format-only adjustments, private debugging notes, jokes, self-deprecating language, or apology-style wording.
  使用**正式发布说明语气**。禁止写入：个人纠错、格式调整、私人调试记录、玩笑、自嘲、道歉式表述。

**Changelog format | changelog 格式：**
Use plain numbered list (1. 2. 3.) with English first, Chinese after for each point.
使用纯数字序号分点（1. 2. 3.），每点英文在前、中文在后。

**Changelog template | 模板：**
```
1. [English update]. [中文更新]。
2. [English update]. [中文更新]。
3. [English update]. [中文更新]。
```

**Changelog examples | 推荐示例：**
```
1. Initial release. 首次发布。
```
```
1. Add comprehensive pre-publish checklist and two-step publishing workflow. 新增发布前检查清单和两步发布流程。
2. Consolidate naming/writing standards and changelog rules into SKILL.md body. 整合命名写作规范与changelog规则至SKILL.md正文。
```
```
1. Improve cross-platform behavior with automatic Windows/macOS detection. 优化跨平台行为，新增 Windows/macOS 自动识别。
2. Fix token inefficiency in large skill bodies. 修复大体技能正文中的 token 使用效率问题。
```

### Step 2: Detailed report → Wait for second confirmation | 第二步：详细汇报 → 等待用户再次确认

After completing Step 1, report the following to the user. **Do NOT upload until the user explicitly confirms.**

| Report item | 内容 |
|---|---|
| Skill name + slug | 准确拼写 |
| ClawHub current published version | 来自 `clawhub inspect <slug>` |
| New version number | 在已发布版本上递增 |
| Changelog | 完整英中文双语内容 |
| Primary update summary | 一句话概括 |
| File size | 是否超 50MB |
| De-identification | 确认通过/需调整 |
| Scientificity | 确认通过/需调整 |
| AI readability | 确认通过/需调整 |
| Contextual coherence | 确认通过/需调整 |
| Stability | 确认通过/需调整 |
| Full publish command | `clawhub publish ...` |

**Important | 重要：**
- Each user modification request triggers a restart of the two-step workflow.
  每次用户提出修改，都必须重新走两步流程。
- Upload only after the user explicitly says "可以发布" or similar confirmation.
  只有用户明确说"可以发布"或类似确认后，才执行上传。

## Required naming and writing rules | 命名与写作规范

### Slug | 部署名

- Use lowercase letters, digits, and hyphens only.
  只使用小写字母、数字和连字符。

### Display name | 显示名

- Use English first, then Chinese.
  英文在前,中文在后。
- Format: `English Name | 中文名`
  格式统一为:`English Name | 中文名`

Example | 示例:
- `Camera YOLO Operator | 摄像头 YOLO 操控者`

### Description | 描述

- Write English first, then Chinese.
  英文在前,中文在后。
- Keep ≤ **150 characters** total (English + Chinese combined).
  英文+中文合计控制在 **150 字符以内**。
- Because description is the **primary trigger mechanism**, it must comprehensively cover all intended use cases and trigger keywords to avoid the AI missing relevant contexts.
  因为 description 是**主要触发机制**，必须全面覆盖该技能的用途、场景、触发关键词，不能残缺导致 AI 漏读。
- Keep it concrete, specific, and attractive.
  要具体、明确、抓眼。
- Avoid keyword stuffing.
  避免关键词堆砌。

### Body text | 正文

- Write skill bodies in bilingual form when practical.
  skill 正文在可行时应写成英中文双语。
- English as the main structural spine, Chinese for key rules and critical workflows.
  英文作为主骨架，中文辅助关键规则与关键流程。
- Do not make the Chinese an afterthought if the skill is meant to be read by human users.
  如果技能预期也会被人类阅读,就不要把中文写成可有可无的附属品。

### Changelog | 发布说明

- Write bilingual changelogs: English first, Chinese after.
  英中文双语，英文在前。
- Tone: **formal and release-ready**.
  语气必须**正式、可直接发布**。
- Focus on user-visible value, stability, compatibility, workflow improvements.
  聚焦用户可感知价值、稳定性、兼容性和流程优化。
- Do **not** add: casual filler, apology-style phrasing, wording that exposes small mistakes, or internal debug notes.
  不要加入：随意口吻、道歉式措辞、暴露小失误的话、内部调试记录。

## Working flow | 工作流

### 1. 查看/搜索技能

- Check local formal skills directory first: `~/.openclaw/workspace/skills/`
  先检查本地正式技能目录
- Check built-in skills if relevant.
  如有需要,再检查内置技能。
- If the skill is not local, search ClawHub.
  本地没有时,再搜索 ClawHub。

For search and audit details, read:
搜索与审计细节请读:
- `references/search-and-audit.md`

### 2. 创建/修订技能

For skill creation methodology (authoritative source), read:
技能创建方法论（权威来源）请读:
- `skill-creator`（独立维护，持续更新，skill-manager 只引用不解释）

- Prefer building drafts in `~/.openclaw/workspace/temp-skills/<slug>/`
  草稿优先放在 `~/.openclaw/workspace/temp-skills/<slug>/`
- Let the user review meaningful edits before publish or update actions.
  在发布或升版前,让用户先审阅关键修改。
- Keep `SKILL.md` lean; move long operational details into `references/`.
  保持 `SKILL.md` 精简,把较长操作细节放进 `references/`。
- When a skill is expected to be human-readable, write the body in bilingual form.
  如果技能也预期给人看,正文应写成双语形式。

### 3. ClawHub 发布/升版技能

**Follow the two-step publishing workflow above.**
**严格按照上面的两步发布工作流执行。**

For publish details, read:
发布细节请读:
- `references/clawhub-publish.md`

### 4. 查看已发布技能

- Do not assume the browser is always the best tool.
  不要默认浏览器永远是最优工具。
- Recheck current CLI help before choosing tools, because the CLI can gain new commands and options over time.
  先重新查看当前 CLI help,再决定用什么工具,因为 CLI 会持续增加新命令和新参数。
- Choose CLI or Dashboard based on the current task after that check.
  检查之后,再根据当前任务选择 CLI 或 Dashboard。

For inspection details, read:
查看细节请读:
- `references/clawhub-inspect.md`

### 5. 宣传已发布技能

- Check de-identification first.
  先做去标识化检查。
- Use polished bilingual copy.
  使用体面、清晰的双语文案。
- Keep links and install commands exact.
  保证链接与安装命令准确无误。

For promotion details, read:
宣传细节请读:
- `references/promotion.md`

### 6. ClawFlows 创建/提交工作流

Workflow 是技能之外第二种产出形式。与技能不同,Workflow 走 PR 审核流程提交到 ClawFlows Registry。

**第一步:写 Workflow**
- 参考 `references/clawflows-workflow.md` 编写 `automation.yaml`
- 草稿放 `~/.openclaw/workspace/temp-skills/<workflow-name>/`
- 安装后路径：`~/.openclaw/workspace/automations/<workflow-name>/`
- 安装命令：`clawflows install <workflow-name>`
- **重要**：参考 `references/clawflows-workflow.md` 末尾的 `Practical Experience Notes | 实践经验总结`

**第二步:本地测试**
- `clawflows run \`<workflow.yaml>\`` 本地运行
- `clawflows check \`<workflow>\`` 检查所需 capabilities
- 成熟后再投稿

**第三步:提交到 ClawFlows Registry**
- Fork [github.com/Cluka-399/clawflows-registry](https://github.com/Cluka-399/clawflows-registry)
- 在 fork 中创建 `automations/<workflow-name>/` 目录,包含:
  - `automation.yaml` — workflow 定义
  - `metadata.json` — 元数据
  - `README.md` — 文档(英中文双语)
- 提交 PR,等官方审核合并

For ClawFlows workflow format and practical experience, read:
Workflow 格式权威参考请读:
- `references/clawflows-workflow.md`

## Directory terms | 目录术语

- **Workspace Skills(正式技能)**: `~/.openclaw/workspace/skills/`
- **Built-in Skills(内置技能)**: OpenClaw bundled skills
- **Extra Skills(插件技能)**: OpenClaw extension skills
- **Temporary Draft Skills(临时草稿)**: `~/.openclaw/workspace/temp-skills/`

正式技能目录中的同名技能会覆盖内置/插件技能。

## Practical note | 实用说明

This skill was tested primarily on Linux-style workflows, but the ClawHub CLI guidance should be rechecked with `clawhub --help` on the current machine before sensitive actions.
本技能主要按 Linux 风格流程整理,但在当前机器上执行敏感操作前,仍应先用 `clawhub --help` 重新核对 CLI 行为。
