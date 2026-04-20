---

## 📩 A/B/C 响应处理（self-improvement 闭环）

当用户在 [channel] 回复 A / B / C 时，主代理接收并执行：

### 识别触发

消息内容为以下之一（忽略大小写，允许前后空格）：
- `A` / `a` — 创建新技能
- `B` / `b` — 优化现有技能
- `C` / `c` — 跳过

### 执行逻辑

**收到 A：**
1. 从 `~/.openclaw/workspace/.learnings/.pending_notifications/` 读取待处理通知
2. 读取该 pattern 的 raw_md 和 distill JSON，理解要创建什么技能
3. 调用 skill-creator：`sessions_spawn` → 传入 skill-creator prompt（包含 pattern 上下文）
4. 执行完成后，更新对应 learnings 条目为 `resolved`

**收到 B：**
1. 同上，从 pending_notifications/ 读取上下文
2. 调用 skill-creator（optimize 模式）
3. 执行完成后，更新对应 learnings 条目为 `resolved`

**收到 C：**
1. 同上，读取上下文
2. 将对应 learnings 条目标记为 `dormant`（不在骚扰用户）
3. 静默，不发送任何消息

### 上下文存储（通知时写入）

每次发送 A/B/C 通知前，cron agent 执行：
```bash
mkdir -p ~/.openclaw/workspace/.learnings/.pending_notifications/
# 写入: <unix_ts>_<safe_pattern_name>.json
# 内容: {pattern_name, count, raw_md, action_taken, notified_at}
```

收到 A/B/C 后，主代理读取最新一个 pending notification，执行对应操作。

### 约束
- skill-creator 调用使用 `sessions_spawn`（runtime=subagent, mode=run）
- 操作完成后删除 `pending_notifications/` 中对应的 JSON 文件
- 如果 pending_notifications/ 为空但收到 A/B/C → 忽略（可能是误触）
