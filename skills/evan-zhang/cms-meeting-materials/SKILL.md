---
name: cms-meeting-materials
description: Query, sync, and analyze meeting transcripts from CMS AI慧记. Use when listing meetings, getting transcript content, summarizing meetings, extracting todos, real-time monitoring during a meeting, or asking about 会议纪要/慧记/会议内容/转写/待办/实时跟踪.
metadata:
  requires:
    env: [XG_BIZ_API_KEY]
homepage: https://github.com/evan-zhang/agent-factory/issues
---

# AI慧记

**版本**: v1.10.8

四类核心能力：
1. 📋 **查询列表** — 归属维度（我的慧记）或会议号维度查询
2. 📄 **获取原文** — 全量/增量/改写三种模式，统一通过 `get-transcript.py`
3. 🧠 **AI 分析** — 会议总结、待办提取、专题分析
4. 🔴 **会中实时** — T+3s 速记流 + T+45s 滚动摘要

## When to Use

- 查询我的会议记录 / 历史会议 / 进行中的会议
- 获取某场会议的转写原文
- 生成会议纪要 / 提取待办 / 专题分析
- 会议进行中实时跟踪转写内容
- 共享或查看他人共享的会议分析资料

## 接口索引

| # | 接口 | 路径 | 说明 |
|---|---|---|---|
| 4.1 | chatListByPage | /ai-huiji/meetingChat/chatListByPage | 归属维度分页查询 |
| 4.11 | listHuiJiIdsByMeetingNumber | /ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber | 会议号维度查询 |
| 4.4 | splitRecordList | /ai-huiji/meetingChat/splitRecordList | 全量分片转写 |
| 4.10 | splitRecordListV2 | /ai-huiji/meetingChat/splitRecordListV2 | 增量分片转写 |
| 4.8 | checkSecondSttV2 | /ai-huiji/meetingChat/checkSecondSttV2 | 二次改写原文 |

Base URL：`sg-al-ai-voice-assistant.mediportal.com.cn/api`
鉴权：仅需 `XG_BIZ_API_KEY`，无需 access-token。

## 快速开始

```bash
# 1. 设置 API Key
export XG_BIZ_API_KEY='你的 appKey'

# 2. 查询可访问会议（前 20 条）
python3 scripts/huiji/list-my-meetings.py 0 20

# 3. 自动选择并拉取（优先进行中）
python3 scripts/huiji/pull-meeting.py --auto
```

## 意图路由

| 用户说 | 路由 |
|---|---|
| "我的慧记" / "最近会议" | 4.1 chatListByPage |
| "会议号 xxx" | 4.11 listHuiJiIdsByMeetingNumber |
| "会议内容" / "原文" / "转写" | get-transcript.py（统一入口）|
| "总结" / "纪要" / "待办" | AI 分析（基于原文）|
| "实时跟踪" / "开始监控" | start-stream |

## Core Rules

1. **路由严格**：无会议号→4.1；有会议号→4.11；禁止从上下文自动取会议号。
2. **原文必须走统一入口**：`get-transcript.py`，禁止直接调用 4.4/4.10/4.8。
3. **时间戳必须转换**：向用户展示时全部转为人类可读格式，禁止展示原始数字。
4. **隐藏技术细节**：不向用户暴露接口名、JSON 字段名、缓存机制等技术过程。
5. **防幻觉**：分析时禁止虚构时间、人物、数据、决策。见 `references/analysis-rules.md`。
6. **业务错误停止**：resultCode≠1 时停止执行并告知用户，不重试。

## References

- `references/query-guide.md` — 列表查询详解（路由规则/状态过滤/_id处理/无结果引导）
- `references/transcript-guide.md` — 原文获取策略 + 双缓存机制 + 时间戳规范 + 共享资料
- `references/analysis-rules.md` — AI分析规范（防幻觉/输出格式）+ 实时模式命令
