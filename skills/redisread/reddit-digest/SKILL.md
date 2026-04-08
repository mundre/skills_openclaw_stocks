---
name: reddit-digest
description: |
  获取 Reddit Subreddit 每日热门内容摘要。对每个配置的 Subreddit 最近 24 小时热门 Post 逐一总结、提炼核心要点、给出可实践建议、灵感启发，以及生成社交媒体分享文案。
---

# Reddit Subreddit 每日摘要技能

获取配置的多个 Subreddit 最近 24 小时热门 Post，逐一抓取 Post 详情（含评论），生成摘要、核心要点、可实践建议、灵感启发及社交媒体分享文案，按 Subreddit 维度输出文档，最终合并为一篇每日精选文档。

## 配置

| 配置方式 | 优先级 | 示例 |
|---------|--------|------|
| 命令行参数 `--base-dir` | 最高 | `/reddit-digest --base-dir /tmp/reddit` |
| 环境变量 `REDDIT_DIGEST_BASE_DIR` | 中 | `export REDDIT_DIGEST_BASE_DIR=...` |
| 默认值 | 最低 | `/Users/victor/Desktop/resource/daily-info/reddit` |

| 配置方式 | 优先级 | 示例 |
|---------|--------|------|
| 命令行参数 `--subreddits` | 最高 | `/reddit-digest --subreddits openclaw,codex` |
| 环境变量 `REDDIT_DIGEST_SUBREDDITS` | 中 | `export REDDIT_DIGEST_SUBREDDITS=openclaw,codex` |
| 默认值 | 最低 | `openclaw,ClaudeAI` |

路径规则（`{YYYYMMDD}` 为当天日期）：
- 临时目录：`{BASE_DIR}/{YYYYMMDD}/temp/`
- Subreddit 维度文档：`{BASE_DIR}/{YYYYMMDD}/subreddit/{subreddit_name}.md`
- 最终合并文档：`{BASE_DIR}/{YYYYMMDD}/reddit-daily-{YYYYMMDD}.md`

## 依赖

- **autocli**: 获取 Reddit Subreddit 热门列表和 Post 详情
- **agent-browser**: 容错备用，当 autocli 无法获取内容时使用

## 执行流程

### Step 1: 初始化

1. 按优先级确定 `BASE_DIR`（参数 > 环境变量 > 默认值）
2. 按优先级确定 `SUBREDDITS` 列表（参数 > 环境变量 > 默认值），以逗号分隔
3. 获取当天日期，计算 `TEMP_DIR`、`SUBREDDIT_DIR`、`OUTPUT_DIR`
4. **检查并清理已存在文件**：
   - 检查 `{BASE_DIR}/{YYYYMMDD}/` 目录下是否有文件
   - 如果存在，先清空该目录下所有内容
5. `mkdir -p {TEMP_DIR}` 和 `mkdir -p {SUBREDDIT_DIR}`

### Step 2: 逐一处理每个 Subreddit

对配置的每个 Subreddit **逐一**执行 Step 2.1 ~ Step 2.4：

#### Step 2.1: 获取 Subreddit 热门 Post 列表

```bash
autocli reddit subreddit {subreddit_name} --sort top --time day --format json
```

返回格式：
```json
[
  {
    "author": "enthusiast_bob",
    "comments": 10,
    "title": "Opinion from those who have used both OpenClaw and Paperclip ?",
    "upvotes": 6,
    "url": "https://www.reddit.com/r/openclaw/comments/1sdgngk/opinion_from_those_who_have_used_both_openclaw/"
  }
]
```

#### Step 2.2: 逐一获取 Post 详情

对列表中的每个 Post URL，执行：

```bash
autocli reddit read {post_url} -f json
```

返回格式（包含 Post 原文和评论）：
```json
[
  {
    "author": "trewert_77",
    "score": 2,
    "text": "...",
    "type": "L0"
  },
  {
    "author": "enthusiast_bob",
    "score": 1,
    "text": "...",
    "type": "L1"
  }
]
```

**容错机制**：
- 如果 `autocli reddit read` 失败或返回空内容，尝试使用 `autocli` 动态判断 URL 类型重新获取
- 如果仍然失败，使用 **agent-browser** 技能访问该 URL 获取内容
- 如果所有方式都失败，记录该 Post 为"无法获取详情"，仅使用列表中的标题和元数据生成简要摘要

#### Step 2.3: 分析并生成每个 Post 的摘要

对每个 Post，结合列表元数据（title, upvotes, comments, author）和详情内容，按以下模板生成分析，写入临时文件 `{TEMP_DIR}/{subreddit_name}-{rank}-{sanitized_title}.md`：

**Post 分析模板：**

```markdown
### [序号]. [Post 标题]

> 链接：[url]
> 👍 [upvotes] | 💬 [comments] | 作者：[author]

#### 摘要
3-5 句话总结 Post 内容及评论区核心讨论，准确、信息密度高。

#### 核心要点
- （3-5 个关键要点，综合 Post 原文和高质量评论）

#### 可实践建议
2-3 条可立即付诸行动的具体建议。

#### 灵感启发
思维模型、跨领域启发、值得深入探索的方向。1-2 段。

#### 社交媒体分享文案

**即刻：**
口语化、有观点、适度 emoji、200 字以内，含 #Reddit热门 #{subreddit_name}

**小红书：**
标题党风格标题 + 正文，善用 emoji，300 字以内，带话题标签

**Twitter/X：**
使用简体中文, 简洁有力，280 字符以内，带 hashtag
```

**筛选规则**：在分析过程中，对以下类型的 Post 标记为"低价值"并从最终文档中剔除：
- 纯 meme / 表情包 / 无实质讨论
- 重复 / 搬运无原创观点
- 评论区无有效互动（如全是 bot 回复）
- 内容过于琐碎（如"大家好我是新人"类）

对被剔除的 Post，在临时文件中记录标题和剔除原因，不写入 Subreddit 文档。

#### Step 2.4: 汇总生成 Subreddit 维度文档

读取该 Subreddit 的所有临时文件，按 rank 排序合并，写入 `{SUBREDDIT_DIR}/{subreddit_name}.md`：

```markdown
---
title: "r/{subreddit_name} 每日精选 - {YYYY-MM-DD}"
date: {ISO 8601}
description: "r/{subreddit_name} 最近 24 小时热门 Post 摘要与深度解读"
tags:
  - Reddit
  - {subreddit_name}
  - Daily Digest
categories:
  - 技术
---

# r/{subreddit_name} 每日精选 - {YYYY-MM-DD}

> 本文精选 r/{subreddit_name} 最近 24 小时热门 Post，为每篇提供摘要、核心要点、可实践建议、灵感启发及社交媒体分享文案。

---

{按 rank 顺序合并所有有价值 Post 的分析内容}

---

## 本版小结

（该 Subreddit 今日整体观察：社区热议话题、共同趋势、值得关注的讨论方向。3-5 句话。）
```

### Step 3: 合并生成最终文档

使用脚本/命令将所有 Subreddit 维度文档直接拼接，生成最终文档 `{BASE_DIR}/{YYYYMMDD}/reddit-daily-{YYYYMMDD}.md`。

#### 拼接方式

使用 `cat` 命令直接拼接（去掉各文档的 frontmatter）：

```bash
# 示例拼接命令
cat {SUBREDDIT_DIR}/Anthropic.md {SUBREDDIT_DIR}/ChatGPT.md ... > {OUTPUT_DIR}/reddit-daily-{YYYYMMDD}.md
```

或逐篇追加：

```bash
# 先写入主文档 frontmatter
echo "---" > {OUTPUT_DIR}/reddit-daily-{YYYYMMDD}.md
echo "title: \"Reddit 每日精选 - {YYYY-MM-DD}\"" >> {OUTPUT_DIR}/reddit-daily-{YYYYMMDD}.md
...

# 然后逐个追加 Subreddit 内容（去掉 frontmatter）
tail -n +12 {SUBREDDIT_DIR}/Anthropic.md >> {OUTPUT_DIR}/reddit-daily-{YYYYMMDD}.md
tail -n +12 {SUBREDDIT_DIR}/ChatGPT.md >> {OUTPUT_DIR}/reddit-daily-{YYYYMMDD}.md
...
```

**最终文档结构：**

```markdown
---
title: "Reddit 每日精选 - {YYYY-MM-DD}"
date: {ISO 8601}
description: "今日 Reddit 多个 Subreddit 热门 Post 摘要与深度解读"
tags:
  - Reddit
  - Daily Digest
categories:
  - 技术
---

# Reddit 每日精选 - {YYYY-MM-DD}

> 本文精选以下 Subreddit 最近 24 小时热门 Post：{subreddit1}, {subreddit2}, ...

---

# r/Anthropic 每日精选 - {YYYY-MM-DD}

> 本文精选 r/Anthropic 最近 24 小时热门 Post...

### 1. [Post 标题]
> 链接：[url]
> 👍 [upvotes] | 💬 [comments] | 作者：[author]

#### 摘要
3-5 句话总结 Post 内容及评论区核心讨论，准确、信息密度高。

#### 核心要点
- （3-5 个关键要点，综合 Post 原文和高质量评论）

#### 可实践建议
2-3 条可立即付诸行动的具体建议。

#### 灵感启发
思维模型、跨领域启发、值得深入探索的方向。1-2 段。

#### 社交媒体分享文案

**即刻：**
口语化、有观点、适度 emoji、200 字以内，含 #Reddit热门 #{subreddit_name}

**小红书：**
标题党风格标题 + 正文，善用 emoji，300 字以内，带话题标签

**Twitter/X：**
使用简体中文, 简洁有力，280 字符以内，带 hashtag

### 2. [Post 标题]
...

## 本版小结
...

---

# r/ChatGPT 每日精选 - {YYYY-MM-DD}

> 本文精选 r/ChatGPT 最近 24 小时热门 Post...

### 1. [Post 标题]
...
## 本版小结
...

---

[继续追加其他 Subreddit 的完整内容...]

---

## 今日总结

（跨 Subreddit 整体观察：共同趋势、值得关注的话题、给读者的综合建议。3-5 句话。）
```

**关键要求：**
1. **直接拼接**：使用命令行工具（cat/tail 等）直接拼接文件内容
2. **完整内容**：包含每个 Subreddit 的全部 Post 分析，不删减
3. **无跳转链接**：最终文档不包含"[查看完整分析 →]"之类的链接
4. **保留分隔**：每个 Subreddit 之间用 `---` 分隔
5. **统一 frontmatter**：仅保留最终文档的 frontmatter，各 Subreddit 文档的 frontmatter 需去除

## 注意事项

1. **逐一处理**：每个 Subreddit 逐一执行，确保资源使用合理
2. **容错**：URL 不可访问时，先使用 autocli 动态判断获取 URL 对应内容，如果还是不行使用 agent-browser 获取内容
3. **语言**：中文撰写
4. **文案风格**：即刻轻松有态度、小红书吸睛有干货、Twitter 简洁专业，一律使用简体中文
5. **筛选机制**：剔除低价值 Post，确保最终文档信息密度高
6. **清理机制**：执行前检查并清空当日目录，避免残留数据干扰
