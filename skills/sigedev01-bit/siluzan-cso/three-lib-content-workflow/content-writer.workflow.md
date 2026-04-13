# 三库内容工作流

## 适用场景

用户要做以下事情时，在 `siluzan-cso` 流程中进入本目录：

- 生成口播文案 / 成稿
- 从热点 / 素材选题
- 按三库拆解文案
- 反推代表作品的人设卡
- 梳理可复用的内容工作流

## 执行基本流程
执行流程详情见：`three-lib-content-workflow/sop.md` — 完整成稿链路：人设 → 目标 → 选题 → 提纲 → 正文 → 质检

1. **人设**：先调用 `siluzan-cso persona list`，取目标人设的 列表（Markdown）让用户选择一个人设, 如果没有可以直接让用户描述或跳过
    - 使用 `siluzan-cso persona list --name <人设名> --json `来获取完整人设信息
2. **三库文件**：按以下优先级确定本次创作使用的三库内容：

   **优先级 1 — 用户本次提供的文件**：若用户在对话中直接提供了三库文件（流量因子库 / 产品资产库 / 烹调方法库），则：
   - 将文件内容写入 `~/.siluzan/content-library/`（文件名保持原名，如 `流量因子库.md`）
   - 后续创作过程中直接读取并按需修改这些文件，实现持续优化

   **优先级 2 — 用户目录已有文件**：检查 `~/.siluzan/content-library/` 是否存在三库文件：
   - 若存在，直接读取使用
   - AI 可在每次创作后根据效果，直接修改 `~/.siluzan/content-library/` 中的文件（增补选题、标注效果、淘汰低效条目等）

   **优先级 3 — 内置默认文件**（兜底）：若以上均无，使用 Skill 目录内置的默认三库文件：
   - `assets/流量因子库.md`
   - `assets/产品资产库.md`
   - `assets/烹调方法库.md`

   使用 grep 命令或全量读取以上文件内容。

   > 如用户有联网搜索的SKILL此时可以调用，搜索你需要的内容

3. **RAG**（可选）：如需从平台知识库检索内部素材，调用 `siluzan-cso rag query`，结果归入「拆素材」环节；不用于与文案无关的场景。
   
## 阅读顺序

- 三库如何使用?详情见： `three-lib-content-workflow/collaboration.md` 
- 如何与用户交互详情见：`three-lib-content-workflow/sop.md` — 完整成稿链路：人设 → 目标 → 选题 → 提纲 → 正文 → 质检
- `three-lib-content-workflow/persona-reverse-sop.md` — 从成稿反推人设（若任务为反推）
- `assets/three-lib-content-workflow.example.md` — 实践话术与示例

## 输出

依据任务返回：成稿口播、人设卡、三库拆解、SOP 摘要或选题列表。

## 风格规则

- 表达直白，不堆砌。
- 人设贴合度优先于格式完美。
- 同一结构不要强套不同选题。
- 工作流保持可复用。
