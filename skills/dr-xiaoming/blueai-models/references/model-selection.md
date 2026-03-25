# BlueAI 模型选型决策树

## 按任务类型选模型

### 日常对话 / 问答
- 预算充足 → `claude-sonnet-4-6` 或 `gpt-4.1`
- 追求性价比 → `DeepSeek-V3.2`（中文）或 `gpt-4.1-mini`（中英）
- 最低成本 → `gpt-4.1-nano` 或 `gemini-2.5-flash`

### 复杂推理 / 数学 / 逻辑
- 最强推理 → `claude-opus-4-6-v1` 或 `o3`
- 性价比推理 → `o4-mini` 或 `DeepSeek-R1`
- 中文推理 → `qwen3-235b-a22b` 或 `DeepSeek-R1`

### 编码 / 代码生成
- Agent级编码 → `claude-opus-4-6-v1`（128K输出）
- 代码专精 → `gpt-5.2-codex` 或 `Doubao-Seed-2.0-Code`
- 轻量代码 → `claude-sonnet-4-6` 或 `gpt-4.1-mini`

### 图片/视觉理解
- 最强视觉 → `claude-opus-4-6-v1` 或 `gemini-3.1-pro-preview`
- 性价比视觉 → `gemini-2.5-flash`（100万上下文+图片）
- 中文OCR → `qwen-vl-ocr-latest`
- 视频理解 → `gemini-3.1-pro-preview` 或 `Doubao-Seed-1.6-vision`

### 超长文档处理
- 100万token → `gemini-2.5-flash`/`gemini-2.5-pro`
- 200万token → `xai.grok-4-fast-non-reasoning`
- 400K token → `gpt-5` 系列
- 262K token → `kimi-k2.5` 或 `qwen3-vl-plus`

### 图像生成
- 最佳质量 → `gpt-image-1.5`
- 标准 → `gpt-image-1` 或 `dall-e-3`
- 图像编辑 → `gemini-2.5-flash-image`
- 中文理解 → `Doubao-Seedream-5.0-lite`

### RAG / 语义搜索
- Embedding → `text-embedding-3-large`（英文）或 `text-embedding-v4`（中英）
- Rerank → `gte-rerank-v2`

---

## 按成本分层

### 💰 旗舰级（最贵，最强）
`claude-opus-4-6-v1`, `o3`, `gpt-5.2`, `xai.grok-4`

### 💵 专业级（均衡）
`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, `DeepSeek-R1`

### 💲 经济级（性价比）
`gpt-4.1-mini`, `gemini-2.5-flash`, `DeepSeek-V3.2`, `claude-haiku-4-5-20251001`

### 🆓 超低成本
`gpt-4.1-nano`, `qwen3-8b`, `Doubao-lite-4k`

---

## OpenClaw 分层策略建议

| 用途 | 推荐模型 | 理由 |
|------|---------|------|
| 主Agent（primary） | claude-opus-4-6-v1 | 最强综合+128K输出 |
| 子Agent任务 | claude-sonnet-4-6 或 gemini-2.5-flash | 省成本，大部分任务够用 |
| 截图/图片识别 | gemini-2.5-flash 或 gpt-4o-mini | 视觉+便宜 |
| 中文内容生成 | DeepSeek-V3.2 或 qwen3-235b-a22b | 中文质量高 |
| 批量/重复操作 | gpt-4.1-nano | 最低成本 |
| Heartbeat/文案 | gemini-3.1-pro-preview | 1M上下文+强推理 |
