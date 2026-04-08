---
name: jike-digest
description: |
  获取即刻多个 Topic 的每日内容并生成每日摘要汇总。对每个 Topic 下的内容进行筛选（剔除无用 post），生成摘要、可实践建议、灵感。
  触发场景：用户提到 "即刻日报"、"jike digest"、"jike 摘要"、"即刻 topic"、"即刻每日精选" 等。
---

# 即刻每日摘要技能

获取配置的即刻 Topic 列表（串行执行），对每个 Topic 获取最近 20 条内容，筛选有价值的内容，生成摘要、可实践建议、灵感，最终汇总为一篇每日精选文档。

## 配置

### Topic 配置（支持环境变量）

| Topic 名称 | 环境变量 | 默认 Topic ID |
|-----------|---------|--------------|
| AI 探索站 | JIKE_TOPIC_AI | 63579abb6724cc583b9bba9a |
| 产品经理的日常 | JIKE_TOPIC_PM | 563a2995306dab1300a32227 |
| 大产品小细节 | JIKE_TOPIC_PD | 57079a1526b0ab12002c29da |
| 副业探索小分队 | JIKE_TOPIC_SIDE | 65544021a2935ec6b005bcd2 |
| 薅羊毛小分队 | JIKE_TOPIC_WOOL | 5523d164e4b0466c6563cd30 |
| 科技圈大小事 | JIKE_TOPIC_TECH | 597ae4ac096cde0012cf6c06 |

### 路径配置

| 配置方式 | 优先级 | 示例 |
|---------|--------|------|
| 命令行参数 `--base-dir` | 最高 | `/jike-digest --base-dir /tmp/jike` |
| 环境变量 `JIKE_DIGEST_BASE_DIR` | 中 | `export JIKE_DIGEST_BASE_DIR=...` |
| 默认值 | 最低 | `/Users/victor/Desktop/resource/daily-info/jike` |

路径规则（`{YYYYMMDD}` 为当天日期）：
- 临时目录：`{BASE_DIR}/{YYYYMMDD}/temp/`
- Topic 原始数据：`{BASE_DIR}/{YYYYMMDD}/topic/{topic_name}.json`
- Topic 分析文档：`{BASE_DIR}/{YYYYMMDD}/topic/{topic_name}.md`
- 最终文档：`{BASE_DIR}/{YYYYMMDD}/jike-daily-{YYYYMMDD}.md`

## 依赖

- **autocli**: 获取即刻 Topic 内容（`autocli jike topic {topic_id} --limit 20 -f json`）

## 执行流程

### Step 1: 初始化

1. 按优先级确定 `BASE_DIR`（参数 > 环境变量 > 默认值）
2. 获取当天日期，计算 `TEMP_DIR`、`TOPIC_DIR` 和 `OUTPUT_DIR`
3. **检查并清理已存在文件**：
   - 检查 `{BASE_DIR}/{YYYYMMDD}/` 目录是否存在
   - 如果存在，删除该目录下的所有文件和子目录
4. `mkdir -p {TEMP_DIR} {TOPIC_DIR}`

### Step 2: 串行获取各 Topic 内容

**重要：串行执行，一个 Topic 获取完成后再执行下一个**

对每个配置的 Topic（按顺序执行）：

```bash
# 示例（AI 探索站）
autocli jike topic 63579abb6724cc583b9bba9a --limit 20 -f json > {TOPIC_DIR}/ai-explore.json
```

Topic 映射：
- `ai-explore`: AI 探索站 (63579abb6724cc583b9bba9a)
- `pm-daily`: 产品经理的日常 (563a2995306dab1300a32227)
- `product-details`: 大产品小细节 (57079a1526b0ab12002c29da)
- `side-hustle`: 副业探索小分队 (65544021a2935ec6b005bcd2)
- `wool-team`: 薅羊毛小分队 (5523d164e4b0466c6563cd30)
- `tech-news`: 科技圈大小事 (597ae4ac096cde0012cf6c06)

### Step 3: 筛选与内容分析

对每个 Topic 的 JSON 数据进行分析：

1. **内容筛选**（剔除以下类型）：
   - 纯表情、纯图片无文字的内容
   - 明显的低质量内容（如单字、无意义重复）
   - 过于私人化的内容（除非有普遍参考价值）

2. **筛选后内容处理**：
   - 对筛选出的有价值内容，逐条生成分析

**单条内容分析模板：**

```markdown
### {序号}. @{作者}

> 原文：{content}
> 👍 {likes} | 💬 {comments} | [查看原帖]({url})

**摘要：**
简要概括这条动态的核心观点或信息（1-2 句话）

**价值点：**
- （为什么这条内容值得被收录）

**可实践建议：**
- （1-2 条可以立即行动的建议，如果没有则省略）

**灵感启发：**
（跨领域启发、值得深入思考的方向，1-2 段）
```

3. 将分析内容写入 `{TOPIC_DIR}/{topic_name}.md`

**Topic 文档结构：**

```markdown
---
topic: {Topic 名称}
topic_id: {topic_id}
date: {YYYY-MM-DD}
total_posts: {获取总数}
selected_posts: {筛选后数量}
---

# {Topic 名称} - {YYYY-MM-DD}

> Topic 简介：{根据 Topic 名称生成的简介}

## 精选内容

{逐条内容分析}

---

## Topic 小结

（该 Topic 今日内容的共同趋势、值得关注的话题、2-3 句话总结）
```

### Step 4: 汇总生成最终文档

读取所有 Topic 的分析文档，合并写入 `{OUTPUT_DIR}/jike-daily-{YYYYMMDD}.md`：

```markdown
---
title: "即刻每日精选 - {YYYY-MM-DD}"
date: {ISO 8601}
description: "今日即刻多个 Topic 精选内容汇总"
topics:
  - AI 探索站
  - 产品经理的日常
  - 大产品小细节
  - 副业探索小分队
  - 薅羊毛小分队
  - 科技圈大小事
tags:
  - 即刻
  - Daily Digest
---

# 即刻每日精选 - {YYYY-MM-DD}

> 本文精选即刻多个 Topic 今日有价值的内容，提供摘要、可实践建议与灵感启发。

---

## 📋 目录

- [AI 探索站](#ai-探索站)
- [产品经理的日常](#产品经理的日常)
- [大产品小细节](#大产品小细节)
- [副业探索小分队](#副业探索小分队)
- [薅羊毛小分队](#薅羊毛小分队)
- [科技圈大小事](#科技圈大小事)

---

## AI 探索站

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 产品经理的日常

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 大产品小细节

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 副业探索小分队

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 薅羊毛小分队

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 科技圈大小事

{嵌入该 Topic 的精选内容，每条 post 必须包含：作者、内容摘要、互动数据、原始链接 [查看原帖](url)}

---

## 今日总结

### 跨 Topic 趋势观察

（整体观察：各 Topic 间的关联、共同趋势、值得关注的交叉话题，3-5 句话）

### 今日精选 Top 5

1. **{Topic 名称}** - @{作者}: {一句话概括} [查看原帖]({url})
2. **{Topic 名称}** - @{作者}: {一句话概括} [查看原帖]({url})
3. **{Topic 名称}** - @{作者}: {一句话概括} [查看原帖]({url})
4. **{Topic 名称}** - @{作者}: {一句话概括} [查看原帖]({url})
5. **{Topic 名称}** - @{作者}: {一句话概括} [查看原帖]({url})

### 给读者的建议

（基于今日内容，给出 2-3 条行动建议或思考方向）

---

*文档生成时间：{timestamp}*
```

## 注意事项

1. **串行执行**：使用 autocli 获取 Topic 内容时必须串行，一个执行完再执行下一个
2. **容错处理**：某个 Topic 获取失败时，记录错误并继续处理其他 Topic
3. **内容筛选**：主动剔除低质量内容，宁可少而精不要多而杂
4. **语言风格**：中文撰写，保持即刻社区轻松有态度的风格
5. **价值导向**：优先收录有信息增量、可实践、有启发的内容
