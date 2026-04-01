# 原文获取 & 缓存机制

## 统一入口（必须使用）

```bash
python3 scripts/huiji/get-transcript.py <meetingChatId> [--name "会议名称"]
```

禁止直接调用 4.4 / 4.10 / 4.8 脚本，统一走 `get-transcript.py`。

## 自动处理流程

```
用户请求原文
  ├─ _final 缓存存在？ → 返回（二次改写，最优质量）
  ├─ _live 缓存标记 completed？ → 尝试 checkSecondSttV2
  │     ├─ state=2 成功 → 写 _final → 返回
  │     └─ state=1/3 → 返回 _live
  ├─ _live 缓存存在？ → 4.10 增量拉取 → 合并到 _live
  └─ 无缓存 → 4.4 全量拉取 → 写 _live
```

## 双缓存说明

| 缓存文件 | 来源 | 质量 |
|---|---|---|
| `{id}_live.json` | 4.4 + 4.10 | 实时转写 |
| `{id}_final.json` | checkSecondSttV2 | 二次改写（最优，可能有发言人）|

缓存目录：`ai-huiji/.cache/huiji/`

## 防丢失保障

- 原子写入：先写临时文件再 rename
- 自动备份：写入前备份旧缓存为 `.bak`
- 增量校验：合并后分片数不能比旧缓存少
- 去重策略：同 startTime 保留 text 更长的版本

## 时间戳规范

所有接口返回时间字段均为 13 位毫秒级 Unix 时间戳（UTC+8）。

**向用户展示时必须转换，禁止展示原始数字：**
- 日期时间 → `2026-03-29 13:59:10`
- 时长（meetingLength 毫秒）→ `2小时7分钟`
- `startTime`（录音内偏移量）→ `00:12:34`
- `realTime`（现实时间戳）→ 绝对时间 `13:45:02`

## 共享资料机制

目录：`.cache/huiji/shared/{meetingNumber}/{yyyyMMdd}/`

规则：
- 用户明确说"共享"时才写入，不自动共享
- 写入前必须确认内容摘要和文件名
- 文件名格式：`{HHmmss}_{人名}_{原始标题}.md`
- 查询某场会议时主动检查 shared/ 目录，有资料时提示用户
- 超过 15 天自动清理
