---
name: aws-wechat-article-main
description: 管理微信公众号从选题到发布的完整内容的固定流程，路由到各子能力。任何新任务执行时必须严格按这个流程顺序推进，选题 → 写稿 → 审稿(内容审) → 排版 → 配图 → 审稿(终审) →发布 ，且每一步完成是进入下一步的前提。当用户提到「公众号运营」「自动运营」「发篇文章」「内容规划」「怎么运营」「一条龙」「完整流程」「从头做」「帮我发一篇」「今天发什么」或需要了解整体流程时使用。
---

# 公众号运营总览

## 配置检查 ⛔ BLOCKING

**进入交互顺序「2) 全局账号约束」「3) 本篇准备」及内容流水线前**须完成 **第 0～2 步**配置检测（任一步失败则 **不得** 继续）。**第 3 步**是**调用 `publish.py` 前**的核对（非流水线起点）：**`.aws-article/config.yaml`** 中 **`publish_method`** 默认为 **`draft`**（**`publish.py full`** 只把图文写入**公众号草稿箱**）；仅当用户明确要求「发出去 / 对外发布」时，再将该键改为 **`published`**（或使用 **`full --publish`** 临时强制发布）。**微信**：**`validate_env.py`** 默认要求公众号账号配齐（见第 2 步）；用户**明确不接微信**时，先将 **`publish_method`** 设为 **`none`** 再过校验（脚本会跳过微信组），之后 **`publish.py full`** 仍直接跳过。要走草稿/发布，须补全 **`aws.env`** 与 **`config.yaml`** 微信槽位，并建议 **`check-wechat-env`**。文风与账号约束以 **`config.yaml`** 为准，发文元数据以本篇 **`article.yaml`** 为准。

### 第 0 步：判断操作系统

智能体在执行下列检测命令前，**先判断当前环境**：

- **Linux / macOS**：使用 Bash 命令（`test`、`echo` 等）。
- **Windows**：使用 **PowerShell** 命令（`Test-Path` 等）。

### 第 1 步：`.aws-article/config.yaml` 与 `aws.env` 是否存在

在**仓库根目录**（当前工作目录为项目根）执行：

**Linux / macOS：**

```bash
test -f .aws-article/config.yaml && test -f aws.env && echo "ok" || echo "missing"
```

**Windows（PowerShell）：**

```powershell
if ((Test-Path -LiteralPath ".aws-article\config.yaml") -and (Test-Path -LiteralPath "aws.env")) { "ok" } else { "missing" }
```

⛔ 输出为 `missing`（任一文件不存在）→ 按 [首次引导](references/first-time-setup.md) 创建或补全：可参考 **`.aws-article/config.example.yaml`** 得到 **`config.yaml`**，在仓库根创建 **`aws.env`**（仅密钥与微信 `WECHAT_N_APPID` / `WECHAT_N_APPSECRET` 等，键名可与 `.aws-article/env.example.yaml` 对照）。

### 第 2 步：校验配置内容（`validate_env.py`）

两文件均存在后，在仓库根运行：

```bash
python skills/aws-wechat-article-main/scripts/validate_env.py
```

（默认读取 **`.aws-article/config.yaml`** 与 **`aws.env`**；可用 `--config` / `--env` 指定路径。）

脚本检查：

- **写作模型**：`config.yaml` 中 `writing_model.provider` / `base_url` / `model` 与 `aws.env` 中 **`WRITING_MODEL_API_KEY`** 须同时非空；否则 **`failed`** + **`写作模型配置不完整`**，**退出码 1**。
- **图片模型**：`image_model` 三项 + **`IMAGE_MODEL_API_KEY`**；否则同上，**退出码 1**。
- **微信公众号**：`wechat_accounts`、`wechat_api_base`、各槽位名与 **`aws.env`** 中 **`WECHAT_{i}_APPID` / `WECHAT_{i}_APPSECRET`** 须成对完整；否则 **`failed`** + **`微信公众号配置不完整`**，**退出码 1**。**例外**：**`config.yaml`** 中 **`publish_method: none`**（用户明确不接微信）时，**跳过**微信组校验，仍输出 **`True`**（并附一行说明已跳过）。

**退出码 0**：写作、图片均通过，且（未声明 **`none`** 时）微信也通过 → **`True`** + **`配置校验通过`**。**退出码 1**：任一组未通过 → 不得进入一条龙默认流水线，并引导 [首次引导](references/first-time-setup.md) 补全或 **`publish_method: none`** 后重跑。

### 第 3 步：调用 `publish.py` 前（`publish_method` + 微信）

- **`publish_method`**（**`draft`** / **`published`** / **`none`**）写在 **`config.yaml`**，**默认 `draft`**。**`none`** = 用户明确不填微信：**`full`** 不调 API。要「发布出去」→ **`published`** 或 **`full --publish`**。
- **微信**：在 **`aws.env`**；槽位在 **`config.yaml`**。**`draft`/`published`** 走 **`full`** 前须就绪；**`none`** 下不调用微信。
- 运行 **`publish.py full`** 前：确认 **`publish_method`** 合法（小写）；**非 `none`** 时建议 **`check-wechat-env`**。

### 智能体行为约束（禁止自作主张）

检测到 **`.aws-article/config.yaml` 或 `aws.env` 缺失**、**`validate_env.py` 退出码 1**（写作 / 图片 / 微信任一组未就绪，且未声明 **`publish_method: none`**），或用户**已要求调用 `publish.py`** 而微信槽位 / 凭证未就绪时：

- **禁止**在未询问用户、未取得用户**明确文字确认**的情况下，自行决定：用当前 Agent 代写、跳过 `write.py`/`image_create.py`、仅出 prompt 却继续宣称「一条龙已完成」、或继续排版/发布并假装配置已就绪。
- **必须先**：向用户说明**具体缺哪一类**（脚本 **`failed`** 下的 **`写作模型配置不完整`** / **`图片模型配置不完整`** / **`微信公众号配置不完整`**；或即将 **`publish.py`** 但微信未配齐）；再请用户选择：
  - **A. 补全配置**：按 [首次引导](references/first-time-setup.md) 编辑 **`config.yaml`** 与 **`aws.env`** 后重跑 **`validate_env.py`**；若要发布再运行 **`publish.py check-wechat-env`**；
  - **不接微信**：将 **`publish_method`** 设为 **`none`** 后重跑 **`validate_env.py`**（将跳过微信组），内容流水线可继续，**`publish.py full`** 仍会按 **`none`** 跳过；
  - **B. 本次例外**：用户**明确打字**接受降级（例如：「确认本次不用写作 API，由当前对话模型直接写稿」）——未取得此类确认前，**不得**进入写稿/生图/发布实操。
- 用户选 **A** 后，智能体可协助逐项写入 **`config.yaml` 非密钥项**；**`aws.env` 内密钥由用户自行粘贴到本地文件更安全**；不要在无必要时让用户重复口述 `AppSecret`。

> **单步子 skill**：用户只触发某一子能力（如仅排版、仅审稿）且**未走本总览流水线**时，仍以各子 skill 内说明为准；**一条龙 / 完整流程 / 从选题到发布** 必须满足本节 BLOCKING 与上条「禁止自作主张」。

## 主要配置文件（不要混用）

| 文件 | 位置 | 作用 |
|------|------|------|
| `aws.env` | **仓库根** | **密钥**：写作/图片 `*_API_KEY`、微信 `WECHAT_N_APPID` / `WECHAT_N_APPSECRET` 等（键名见 `.aws-article/env.example.yaml`；与 `config.yaml` 一起由 `validate_env.py` 校验） |
| `.aws-article/config.yaml` | 仓库内 | **非密钥配置**：账号文风、模型 `provider`/`base_url`/`model`、微信槽位数与 `wechat_api_base`、各槽位展示名等（模板见 `config.example.yaml`） |
| `.aws-article/env.example.yaml` | 仓库内示例 | **仅文档**：`aws.env` 键名说明 |
| `.aws-article/config.example.yaml` | 仓库内示例 | **仅文档**：`config.yaml` 结构示例 |
| `article.yaml` | **本篇目录** `drafts/YYYYMMDD-标题slug/` | **发文元数据**（标题/作者/摘要/封面等）及 **`publish_completed`**（发布状态：新建 **`false`**，发布闭环结束 **`true`**），与 **`config.yaml`** 分工 |

### 发布方式与时间线

1. **账号与发布策略**：**文风、选题边界、`publish_method`（默认 **`draft`**）、微信槽位元数据**等均在 **`.aws-article/config.yaml`** 维护；**密钥**仅在 **`aws.env`**。
2. **本篇准备**（须先完成交互顺序 **「2) 全局账号约束」**）：在 **定题与 slug** 之后新建 `drafts/YYYYMMDD-标题slug/`，并**优先**创建 **`article.yaml`**（含 **`publish_completed: false`**、标题/作者/摘要等；通常为本目录内**首个**应落盘的文件），再进入内容流水线。
3. **执行原则（严格顺序）**：必须按下述流水线顺序依次执行，**不能跳过任何部分**；每到一步若缺少必要输入（目录、元数据、主题、用户选择、发布意图等），要**先及时询问用户并获得确认**，再进入下一步，除非用户指出基于某个历史任务继续创作，那么需要智能体根据中间产物判断从哪个阶段开始。
4. **内容流水线**（子 skill 串行，详见下文 **「交互顺序」第 4 步** 与 **「流程」** 表）：**选题**（[topics](../aws-wechat-article-topics/SKILL.md)）→ **写稿**（[writing](../aws-wechat-article-writing/SKILL.md)）→ **审稿（内容审）**（[review](../aws-wechat-article-review/SKILL.md)）→ **排版**（[formatting](../aws-wechat-article-formatting/SKILL.md)）→ **配图**（[images](../aws-wechat-article-images/SKILL.md)）→ **审稿（终审）**（review）。**内容审**产出的 **`article.md` 定稿须满足 [review 第 5 步](../aws-wechat-article-review/SKILL.md)（文末 **`{embed:…}`**，⛔ BLOCKING）后再排版。全程以 **`.aws-article/config.yaml`** 为账号与文风约束；典型产物依次为 `topic-card.md` / `draft.md` → `article.md` → `article.html` 与 `imgs/` 等。
5. **发布**（[publish](../aws-wechat-article-publish/SKILL.md)）：**`draft`** → **`full`** 仅**草稿箱**；**`published`** 或 **`full --publish`** → 再**提交发布**；**`none`** → **`full`** **立即跳过**、不调微信。前两档需微信凭证。

**再强调**：**`aws.env`** = 密钥；**`config.yaml`** = 账号/文风/模型与微信元数据及 **`publish_method`**；**本篇 `article.yaml`** = 发文元数据。

## 交互顺序（一步步，最小提问）

按以下顺序与用户交互，**上一步完成再进下一步**；上一环节就绪后再进入下一环节。

### 1) 配置自检（必做）

- 按上文 **配置检查** 完成：**`config.yaml` 与 `aws.env` 均存在** → 运行 **`validate_env.py` 且退出码 0**（写作、图片、微信均通过，或已设 **`publish_method: none`** 且写作+图片通过）。**退出码 1** 时按 [首次引导](references/first-time-setup.md) 补全环境，或设 **`none`** / 用户 **本次例外**。  
- **校验未通过时**：只展示 [首次引导](references/first-time-setup.md) 中的 **配置选项**，**不要**在同一轮回复里再问「写哪篇 / 继续哪篇草稿 / 新选题」等；须等配置闭环（重跑校验通过或「本次例外」已书面确认）后，**再**进入下方 **「2) 全局账号约束」**。
- **`validate_env.py` 不检查** `account_type`、`target_reader`、`default_author`；须在 **「2) 全局账号约束」** 中单独检查并落盘。

### 2) 全局账号约束（`.aws-article/config.yaml`）⛔

**在 `validate_env.py` 已通过**（或已按总览完成「本次例外」）**之后、进入「3) 本篇准备」之前**，**必须**打开 **`.aws-article/config.yaml`**，检查下列键 **trim 后是否非空**：

- **`account_type`**、**`target_reader`**、**`default_author`**

任一项缺失或空白：**逐项询问用户**（1.账号领域2.目标读者3.作者名字），取得**用户当轮明确答复**后再**写回** **`.aws-article/config.yaml`**，再进入 **「3) 本篇准备」**。**禁止**仅在对话里口头确认却不写入文件。**禁止**跳过本步直接假定可写稿。

**⛔ 禁止擅自填写（必须写进行为约束）**

- **不得**从本篇或其它目录的 **`article.yaml`**、历史草稿、**`topic-card.md`**、对话记忆或仓库内任意文件**静默抄录、推断或「顺手补全」**后写入 **`account_type` / `target_reader` / `default_author`**。对 **`tone`** 等与账号画像强相关的全局项，要直接询问用户，**同样禁止**未询问就写盘。
- **允许的做法**：向用户说明「当前为空」，**请用户填写或确认**；若你想根据某篇 `article.yaml` 给**建议**，只能**展示为待选文案**，并问「是否采用 / 要改哪几个字」，**用户明确同意后再写入** `config.yaml`。
- **顺序**：在尚未完成 **「3) 本篇准备」** 中「续旧 / 新开」的确认前，**禁止**用某一 `drafts/…/article.yaml` **反推**全局三键，避免误把单篇元数据当成整号定位。

### 3) 本篇准备（二选一，默认「新建一篇」）

**在完成「2) 全局账号约束」之后**，**在不了解用户是要续写既有草稿还是新开一篇时**（例如未指定 `drafts/…` 路径、且仓库 **`drafts/`** 下存在进行中目录或多个候选）：**须先询问**并让用户选定 **「继续哪一篇」** 或 **「新开一篇」**，**再**进入下列 A/B 或调用写作脚本。**禁止**默认「最近修改」目录、未确认就运行写作脚本、或假定沿用上一轮路径。

#### A. 新建一篇（**严格子顺序**，勿跳步）

1. **写作意图** ⛔ **BLOCKING**：必须问清用户 **本篇要写什么**（具体主题、角度、体裁或目标）。若用户只想「帮我出选题」，须**明确确认**后再当无方向模式处理。  
   - **禁止**在用户未回答本步（且当前对话也未等价说明）之前：**调用 web_search**、**执行 topics 的调研**、**批量生成选题或标题**。  
   - 用户已在当次对话中说清楚「写什么」的，可本步口头确认一句即可，不必重复盘问。
2. **定题与 slug**：在写作意图已明确的前提下，确定**发文章标题**——用户从候选中选一个，或**自定义标题**；据此生成 **slug**，目录名为 `YYYYMMDD-标题slug`（slug 规则：小写、连字符、与项目习惯一致即可）。
3. **建目录与 `article.yaml`**：创建 `{drafts_root}/YYYYMMDD-标题slug/`（`drafts_root` 以 **`config.yaml`** 为准，默认 `drafts/`）。随即初始化本篇 **`article.yaml`**（含 **`publish_completed: false`**，及标题、作者、摘要等；目录内**宜最先写入**；可用 `skills/aws-wechat-article-publish/scripts/article_init.py`）。  
   - **`publish_method`**：默认 **`draft`**；要发出去 → **`published`** 或 **`full --publish`**；用户明确不填微信 → **`none`**。
4. 至此才进入 **第 4 步内容流水线**。

#### B. 我已有目录

- 用户给出路径。必读 **`.aws-article/config.yaml`**（账号与发布策略）；本篇目录内需有 **`article.yaml`**（或按用户状态后补）。若已有 `article.html`/`cover.jpg` 可直接从流水线中靠后的步骤接入。

### 4) 内容流水线（子 skill）

须已具备 **本篇目录** 与 **`article.yaml`**（「已有目录」分支按上条处理）；账号侧约束以 **`config.yaml`** 为准。

```
选题 → 写稿 → 审稿(内容审) → 排版 → 配图 → 审稿(终审)
```

- **topics**：仅在 **写作意图已明确**（见上 3-A-1）之后执行；仍须遵守 **aws-wechat-article-topics** 中「展示后等用户选」等规则。
- **writing**：结合 **`.aws-article/config.yaml`** 与 `topic-card.md`（或用户素材）；**`publish_method`** 见 **`config.yaml`**（上文「发布方式与时间线」）；产物 `draft.md` → 内容审后 `article.md`。
- **review（内容审）**：定稿 **`article.md` 前**须按 [review 第 5 步 ⛔ BLOCKING](../aws-wechat-article-review/SKILL.md) 完成文末 **`{embed:…}`**（或规则允许的省略并留痕）；**未完成不得进入 formatting**。
- **formatting**：`article.md` → `article.html`（用户当次指定排版主题可覆盖默认）。
- **images**：按 **aws-wechat-article-images**（配置与行为约束以本节「配置检查」为准）。
- **review（终审）**：检查 `article.html` 与 `imgs/`；有问题给出清单，等用户确认或修复。

### 5) 发布

- 以 **`config.yaml`** 的 **`publish_method`** 为准；**`draft`** / **`published`** / **`none`** 含义见上文。**`none`** 时运行 **`full`** 会无操作退出。
- **`draft`/`published`**：**微信**须配齐后再调 **`publish.py`**；建议 **`check-wechat-env`**。**`none`**：不调微信，说明即可。
- 完成后输出小结与回执，目录按需移至 `published_root`。

## 流程

```
选题 → 写稿 → 审稿(内容审) → 排版 → 配图 → 审稿(终审) → 发布
```

## 中间产物门禁（缺啥补啥）⛔

进入下一步前，必须先检查本步所需中间产物；缺什么就先补什么，禁止跳步并宣称已完成。

| 阶段 | 必要产物（最小集合） | 缺失时动作 |
|------|----------------------|------------|
| 写稿完成 | `article.md` 存在且非空 | 继续写稿或回滚到 writing |
| 排版完成 | `article.html` 存在，且由当前 `article.md` 重新生成 | 先执行 formatting 重转 |
| 配图完成 | 文章目录存在 `cover.(png/jpg/jpeg/webp)`；`article.md` 与 `article.html` 不含 `placeholder` | 先执行 images 生成并替换 |
| 发布就绪 | `article.yaml` 含 `title/author/digest/content_source`；发布环境检查通过 | 先补齐元数据或环境 |
| 发布闭环 | 发布命令成功且回执可用 | 才允许写回 `publish_completed: true` |

**禁止**：仅凭单一信号（如“草稿创建成功”）就宣称全流程完成。若正文仍有 `placeholder`，状态必须标记为“草稿已提交，正文配图未完成”。

| 步骤 | 子 skill | 读取 | 产出 |
|------|---------|------|------|
| 选题 | topics | **`.aws-article/config.yaml`**、`aws.env`、web_search | `topic-card.md` `research.md` |
| 写稿 | writing | `topic-card.md`、**`.aws-article/config.yaml`**、`aws.env`（专用写作 API） | `draft.md` |
| 审稿 | review | `draft.md`、`aws.env`、**`.aws-article/config.yaml`** | `review.md` → `article.md`（定稿须含文末 embed，见 [review 第 5 步](../aws-wechat-article-review/SKILL.md)） |
| 排版 | formatting | `article.md`、**`.aws-article/config.yaml`** | `article.html` |
| 配图 | images | `article.md`、`aws.env`、**`.aws-article/config.yaml`** | `imgs/` |
| 终审 | review | `article.html`、`imgs/`、**`.aws-article/config.yaml`** | `review.md` |
| 发布 | publish | `article.html`+`imgs/`、**`config.yaml`**、`aws.env`（调用 publish.py 时） | 草稿 media_id / 发布 publish_id、URL、`out/` 记录 |

**账号与文风约束**：以 **`.aws-article/config.yaml`** 为准。

**topics / `web_search`**：须满足上文 **3-A-1**（用户已说明本篇写什么，或已确认「只帮忙出选题」）之后才可调研与生成选题；不得默认跳过提问直接搜索。

> 提示：发布前需就绪本篇 `article.yaml`（标题/作者/摘要/封面等元数据；`content_source` 默认 `article.html`）。可用 `skills/aws-wechat-article-publish/scripts/article_init.py` 快速初始化或更新。

## 路由

**默认**：与长文发文相关时 **优先 main**，由本 skill 按步编排；不要因用户说了「写」「选题」「发」就跳过 main 直连子 skill。

**何时直连子 skill**（可跳过 main 入口）：用户**明确只要该步产物**、且不隐含「从零到发出」整条链。例如：已有 `article.md` 只要排版；已有稿只要审稿清单；已有 `article.html`+`imgs/` 只要发布前检查或提交；已有选题卡只要扩写等。

| 用户说法 | 路由到 |
|---------|--------|
| 从0开始、从零、从头、一条龙、完整流程、帮我发一篇、发到公众号（含各前置步）、今天发什么/写什么好（要成文并发）、不确定从哪步开始 | **main** |
| **只要**选题卡、标题、摘要、排期、系列策划（明确不做后续编排） | topics |
| **只要**在已有选题/大纲/草稿上写稿、改写、润色、续写（明确不要全流程） | writing |
| **只要**审稿/校对/合规清单（成稿或已定版 HTML） | review |
| 「能不能发」且含代为发布、或要从稿到发出整条收尾 | **main** |
| **只要**排版、换主题、转 HTML | formatting |
| **只要**长文封面/正文配图（有正文或插图位） | images |
| 贴图、图片消息、多图推送、九宫格（非长文图文链路） | **sticker** |
| **只要**执行发布/提交/群发（已有约定产物） | publish |

## 运行模式

### 一条龙

用户说「一条龙」「完整流程」时启用。按 **交互顺序** 的 1→2→3→4→5 执行；**3-A** 内子步骤亦须逐步完成。流水线中每步完成后**暂停**等用户确认。审稿有 🔴 项时进入修改循环。

### 单步

用户**明确只要某一步**且已有对应输入产物（或声明不做全流程）时，可仅执行该步骤；若表述含糊、可能还要后续发文，仍从 **main** 问起或按一条龙拆步确认。

### 贴图

路由到独立的 **aws-wechat-sticker** skill。

## 配置与自定义

- **`aws.env`**（仓库根，密钥）与 **`.aws-article/config.yaml`**（非密钥与模型/微信元数据及 **`publish_method`**）：校验 **`skills/aws-wechat-article-main/scripts/validate_env.py`**；`aws.env` 键名见 **`.aws-article/env.example.yaml`**
- **`config.yaml` / `article.yaml` / `aws.env` 字段说明**：[references/articlescreening-schema.md](references/articlescreening-schema.md)
- 发布前微信：**`skills/aws-wechat-article-publish/scripts/publish.py check-wechat-env`**（仓库根执行，试换微信 **access_token**；凭证在 **`aws.env`**）
