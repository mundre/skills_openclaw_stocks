---
name: blog-writer
description: 为张向阳（Astral Wave）的个人博客 astralwaveorg 生成高质量技术博客文章。当用户说"写博客xxx"、"帮我写一篇xxx"、"引用消息写成博客"、"总结今天聊天"，或者 cron 触发每日聊天总结时，使用此技能。文章风格必须模拟作者本人：用工程师第一人称视角，诚实直接，有踩坑说踩坑，读起来像同事之间的经验分享，而不是翻译官方文档。绝不出现"非常优秀""极其强大"等废话词汇。目标是让读者感觉这是技术大牛写的，不是"AI 生成的"。
---

# Blog Writer

自动生成张向阳个人博客（astralwaveorg）的技能。

## 两种工作模式

### 模式 A：搜索生成（主动写博客）

**触发词**：
- "写博客 XXX"
- "帮我写一篇 XXX"
- "把 XXX 写成博客"
- "引用消息写成博客"
- "这个话题写一篇"

**流程**：

1. **读取风格指南** → 先读 `references/style.md`，不要跳过
2. **解析诉求** → 提取技术关键词、判断话题分类（ai/devops/frontend/backend/tools/arch/db）
3. **搜索资料** → `web_search` 至少 5 篇
   - 优先来源：官方文档 / GitHub / 知名技术博客（掘金、CSDN、InfoQ）
   - 不采信：个人随手笔记、无来源文章、低质量论坛回复
   - 中英文各一半
4. **抓取核心内容** → `web_fetch` 2-3 篇最相关的文章，提取关键数据、代码示例、实测数字
5. **生成 front matter** → 用 `scripts/new_post.py`，自动分配 topic，随机时间 19:00-23:59:59
6. **生成正文** → 严格按 `references/style.md` 风格写作，字数 2500-7000
7. **写入文件** → 写入 `source/_posts/`
8. **质量自查** → 逐项过质量清单（见下文）
9. **commit** → 用 scripts/commit_msg.py 生成 message，执行 git add + commit，格式：
   - 文章类：`post: <标题>`
   - 功能类：`feat: <功能>`
   - 不 push，等用户确认后再部署
10. **通知用户** → Telegram 发送 `✅ [文章标题]`，简洁不冗余

### 模式 B：聊天总结（定时写博客）

**触发**：每日 23:45 cron

**流程**：

1. **读取聊天记录** → 用 `sessions_history` 读取当天所有 session
2. **提取话题** → 
   a. 用 `sessions_history` API 读取当天所有 session 的消息
   b. 将消息 JSON 通过 `exec` 调用 `scripts/extract_topics.py`，stdin 传入消息列表 JSON
   c. 解析 stdout 的 JSON 输出，得到 2-3 个核心话题及其上下文摘要
3. **生成文章** → 判断话题关联度：
   - 话题关联紧密（同一个技术主题的不同维度）→ 合并为一篇深度长文
   - 话题相对独立 → 每话题独立成篇
   - 最多 3 篇（2-3 个话题）
4. **写作** → 严格按 `references/style.md`，特别注意第一人称 + 判断力语气
5. **随机日期** → 当天 19:00-23:59:59 随机时间戳
6. **写入 + commit** → 用 `scripts/commit_msg.py` 生成 message（`post: <标题>`），执行 git add + commit，不 push
7. **Telegram 通知** → 每篇一条 `✅ [文章标题]`

## 话题分类速查

| 话题 | categories | tags 典型值 |
|------|-----------|------------|
| ai | AI、LLM | OpenAI、Claude、LLM、MCP |
| devops | 运维、DevOps | Docker、Nginx、Linux、CI/CD |
| frontend | 前端 | TypeScript、Vue、React |
| backend | 后端 | Java、Python、API |
| tools | 工具 | CLI、MCP、Cursor |
| arch | 架构 | 微服务、分布式 |
| db | 数据库 | Redis、MySQL、SQLite |

## 文章质量检查清单

生成后逐项确认：

- [ ] 读完了 `references/style.md` 才动笔
- [ ] 语气是第一人身称，不是"开发者应该..."
- [ ] 开头有背景：为什么做这事，当时怎么想的，有过什么犹豫
- [ ] 有方案对比表格（适用时），判断理由具体，不是模糊词
- [ ] 代码块有中文注释，注释说 why 不说 what
- [ ] 结尾有实测结论：好不好、哪里坑、达到预期了吗
- [ ] 没有"非常""极其""相当"等废话副词
- [ ] description 是精准一句话，不夸张
- [ ] 字数 2500-7000（不够就补充决策过程）
- [ ] front matter 的 topic/date/categories/tags 完整正确
- [ ] 读起来像人写的，不是"以下是关于 XXX 的技术文章"

## 禁止事项

- 不自动 push（部署是高风险操作）
- 不生成标题党文章
- 不洗稿官方文档（要有自己的实战经验）
- 不写纯翻译或摘要文章（要有观点和判断）
- 不出现"AI 生成的"痕迹语气

## 参考文件

- `references/style.md` — 完整风格指南（**每次生成前必读**）
- `scripts/new_post.py` — 生成 front matter 和文件
- `scripts/extract_topics.py` — 从聊天中提取核心话题
