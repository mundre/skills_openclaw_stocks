# BlueAI 模型目录

> 来源：BlueAI模型统一代理服务文档 | 更新：2026-03-25

## 端点信息

| 项目 | 值 |
|------|-----|
| 国内API | `https://bmc-llm-relay.bluemediagroup.cn` |
| 国外API | `https://bmc-llm-relay.nextblue.ai` |
| OpenAI端点 | `/v1/chat/completions` |
| Claude端点 | `/v1/messages` |
| Responses端点 | `/v1/responses` |
| 图像生成 | `/v1/images/generations` |
| Embedding | `/v1/embeddings` |
| 语音转文字 | `/v1/audio/transcriptions` |
| 文字转语音 | `/v1/audio/speech` |

---

## Claude 系列（AWS Bedrock）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| claude-opus-4-6-v1 | 200K | 128K | 文本+图片+PDF, 扩展思考, 代码, 函数调用, Agentic Coding | 超长输出、复杂编码、Agent |
| claude-opus-4-5-20251101 | 200K | 64K | 文本+图片+PDF, 推理, 代码, 函数调用 | 复杂决策、长文撰写 |
| claude-sonnet-4-6 | 200K | 64K | 同Opus但更快更便宜 | 日常任务、平衡性价比 |
| claude-sonnet-4-5-20250929 | 200K | 64K | 同上, 增强推理 | 需要推理的日常任务 |
| claude-sonnet-4-20250514 | 200K | 64K | 文本+图片+PDF, 代码, 函数调用 | 标准对话和代码 |
| claude-haiku-4-5-20251001 | 200K | 64K | 文本+图片+PDF, 代码, 快速响应 | 轻量快速、低延迟 |
| claude-3-7-sonnet-20250219 | 200K | 64K | 文本+图片+PDF, 扩展思考, 代码 | 兼容旧版workflow |

**请求端点**：Anthropic Messages (`/v1/messages`)

---

## GPT 系列（Azure）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| gpt-5.4 | 400K | 128K | 最新旗舰 | 最强综合能力 |
| gpt-5.2 | 400K | 128K | 文本+图片+音频, 深度推理, 代码 | 高级推理+多模态 |
| gpt-5.2-codex | 400K | 128K | 代码专精, Agent编码 | 大型代码生成 |
| gpt-5.1 | 400K | 128K | 文本+图片+音频, 推理, 代码 | GPT-5迭代版 |
| gpt-5 | 400K | 12K | 文本+图片+音频, 推理, 代码, Agent | 400K超长上下文旗舰 |
| gpt-4.1 | 128K | 32K | 文本+图片, 代码, 函数调用 | 编码和指令遵循 |
| gpt-4.1-mini | 128K | 32K | 同4.1轻量版 | **性价比首选** |
| gpt-4.1-nano | 128K | 32K | 最轻量 | 速度最快、成本最低 |
| gpt-4o | 128K | 16K | 文本+图片+音频, 代码, JSON模式 | 全能多模态 |
| gpt-4o-mini | 128K | 16K | 文本+图片, 代码 | 经济版多模态 |
| o4-mini | 200K | 100K | 文本+图片, 深度推理, 工具调用 | 高效推理+工具 |
| o3 | 200K | 100K | 最强推理 | 复杂逻辑/数学 |
| o3-mini | 200K | 100K | 推理, 可调effort | 轻量推理 |
| o1 | 200K | 100K | 深度推理, 内部思维链 | 科学/数学问题 |
| gpt-image-1 | - | - | 文生图+图编辑 | 图像生成 |
| gpt-image-1.5 | - | - | 升级版文生图 | 更好的图像生成 |

**请求端点**：OpenAI Completions (`/v1/chat/completions`)

---

## Gemini 系列（Google Cloud）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| gemini-3.1-pro-preview | 1M | 65K | 文本+图片+视频+音频+PDF, 推理, Agent | **最新旗舰** |
| gemini-3-flash-preview | 1M | 65K | 同上但更快 | 速度与效果平衡 |
| gemini-2.5-pro | 1M | 65K | 文本+多模态, 深度思考, Grounding | 长上下文推理 |
| gemini-2.5-flash | 1M | 65K | 同上, 思维链推理 | **超便宜+100万上下文** |
| gemini-2.5-flash-image | 32K | 32K | 文生图+图编辑 | 图像生成/编辑 |
| gemini-3-pro-image-preview | 65K | 32K | 文生图+图编辑 | 3代图像生成 |
| gemini-3.1-flash-image-preview | 131K | 32K | 图像生成 | Flash版图像 |

**请求端点**：OpenAI Completions (`/v1/chat/completions`)
**⚠️ gemini-3-pro-preview 将于2026-03-26弃用，迁移至 gemini-3.1-pro-preview**

---

## DeepSeek 系列（火山引擎/百炼）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| DeepSeek-R1 | 128K | 32K | 深度推理(CoT), 代码, 数学 | 复杂逻辑推理 |
| DeepSeek-V3 | 128K | 16K | 文本, 代码, 多语言, 函数调用 | 通用对话和代码 |
| DeepSeek-V3.1 | 128K | 32K | V3升级, 增强指令遵循 | 中文任务性价比 |
| DeepSeek-V3.2 | 128K | 32K | 最新版, 混合推理, 深度思考 | **中文最佳性价比** |

**请求端点**：OpenAI Completions
**注意**：纯文本模型，不支持图片/视频输入

---

## 豆包 Doubao 系列（火山引擎）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| Doubao-Seed-2.0-pro | 256K | 128K | 最新旗舰 | 顶级中文能力 |
| Doubao-Seed-2.0-lite | 256K | 128K | 轻量版 | 经济版 |
| Doubao-Seed-2.0-mini | 256K | 128K | 最小版 | 低成本 |
| Doubao-Seed-2.0-Code | 256K | 128K | 代码专精 | 编程任务 |
| Doubao-Seed-1.8 | 256K | 32K | 文本, 推理, 代码 | 综合能力 |
| Doubao-Seed-1.6-thinking | 256K | 32K | 多模态+思维链 | 需要推理的多模态 |
| Doubao-Seed-1.6-vision | 256K | 32K | 图片+视频理解, OCR | 视觉理解 |
| Doubao-Seed-1.6-flash | 256K | 32K | 多模态, 速度优化 | 低延迟场景 |
| Doubao-1.5-vision-pro-32k | 128K | 16K | 图片+视频, OCR | 图像/视频理解 |
| Doubao-Seedream-5.0-lite | - | - | 文生图 | 图像生成 |
| Doubao-Seedream-4.5 | - | - | 文生图 | 图像生成 |
| Doubao-embedding | 4K | - | 文本向量化 | 语义搜索/RAG |

**请求端点**：OpenAI Completions

---

## 通义千问 Qwen 系列（百炼）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| qwen3-235b-a22b | 131K | 16K | MoE旗舰, 混合推理 | 中文推理最强 |
| qwen3-32b | 131K | 16K | Dense架构 | 通用中文任务 |
| qwen3-14b | 131K | 8K | 中等规模 | 轻量中文 |
| qwen3-8b | 131K | 8K | 轻量级 | 最低成本 |
| qwen3-vl-plus | 262K | 32K | 图片+视频理解, OCR | 视觉理解 |
| qwen-vl-max-latest | 131K | 8K | 视觉旗舰 | 最强视觉理解 |
| qwen-vl-ocr-latest | 32K | 2K | OCR专用 | 文字识别 |
| qwen-omni-turbo-latest | 32K | 2K | 全模态(图片+视频+音频)+语音输出 | 语音对话 |
| qwen-max | 32K | 8K | 旗舰文本 | 通用对话 |
| qwen-plus | 131K | 16K | 长上下文 | 长文档 |
| text-embedding-v4 | 8K | - | 中英文向量化 | RAG/搜索 |
| gte-rerank-v2 | 4K | - | 重排序 | 搜索结果优化 |

**请求端点**：OpenAI Completions

---

## Kimi / 月之暗面

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| kimi-k2.5 | 262K | - | 最新版 | 中文+Agent |
| kimi-k2-thinking | 262K | - | 深度思考, Agent | 长上下文推理+编码 |
| moonshot-v1-128k | 128K | - | 超长文本, 代码 | 长文档分析 |
| moonshot-v1-128k-vision-preview | 128K | - | 多模态 | 128K+图片 |
| moonshot-v1-32k | 32K | - | 文本, 代码 | 标准对话 |

---

## Grok 系列（Oracle/xAI）

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| xai.grok-4 | 128K | 16K | 文本+图片, 深度推理, 代码 | 最强推理 |
| xai.grok-4-fast-reasoning | 2M | 16K | 推理+速度优化 | 超长上下文推理 |
| xai.grok-4-fast-non-reasoning | 2M | 16K | 极速回答, 跳过推理 | **2M上下文+最快** |
| xai.grok-code-fast-1 | 256K | 16K | 代码专精 | 大型代码库 |
| xai.grok-3 | 131K | 16K | 推理, 代码 | 标准版 |
| xai.grok-3-fast | 131K | 16K | 速度优化 | 快速版 |

---

## MiniMax 系列

| 模型ID | 上下文 | 最大输出 | 能力 | 推荐场景 |
|--------|--------|---------|------|---------|
| MiniMax-M2.7 | 204K | 2K | 最新版 | 编程+Agent |
| MiniMax-M2.5 | 204K | 2K | 编程+Agent | 通用 |
| MiniMax-M2.1-lightning | 204K | 2K | 极速版 | 低延迟 |

**⚠️ 不支持Claude端点，必须使用OpenAI端点**

---

## Embedding / 向量模型

| 模型ID | 维度 | 提供商 | 推荐场景 |
|--------|------|--------|---------|
| text-embedding-3-large | 3072 | OpenAI | 最强向量化 |
| text-embedding-3-small | 1536 | OpenAI | 轻量向量化 |
| text-embedding-ada-002 | 1536 | OpenAI | 旧版兼容 |
| text-embedding-v4 | - | 阿里 | 中英双语 |
| Doubao-embedding | - | 火山 | 中文向量化 |

---

## 图像生成模型

| 模型ID | 提供商 | 推荐场景 |
|--------|--------|---------|
| gpt-image-1.5 | OpenAI | 最佳文生图 |
| gpt-image-1 | OpenAI | 标准文生图 |
| dall-e-3 | OpenAI | 经典文生图 |
| gemini-2.5-flash-image | Google | 图像生成+编辑 |
| gemini-3-pro-image-preview | Google | 3代图像 |
| Doubao-Seedream-5.0-lite | 火山 | 中文文生图 |
| Doubao-Seedream-4.5 | 火山 | 中文文生图 |

---

## 语音模型

| 端点 | 用途 |
|------|------|
| `/v1/audio/speech` | 文字转语音 |
| `/v1/audio/transcriptions` | 语音转文字（whisper-1） |
| `/v1/audio/translations` | 语音翻译 |
