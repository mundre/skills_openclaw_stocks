---

## A/B/C/D 响应处理（self-improvement 闭环）

当用户在 channel 回复 A / B / C/D 时，主代理接收并执行：

### 识别触发

消息内容为以下之一（忽略大小写，允许前后空格）：

- `A` / `a` — 创建新技能
- `B` / `b` — 优化现有技能
- `C` / `c` — 跳过
- `D` / `d` — 升华到 SOUL/AGENTS/TOOLS

### 执行逻辑（批量处理 — 一次处理所有 pattern）

**核心改动**：收到 A/B/C/D 后，处理完当前 pattern，继续扫描 `pending_notifications/` 目录下**所有**其他 JSON 文件，逐条处理，防止孤儿文件。

```bash
PENDING_DIR="~/.openclaw/workspace/.learnings/.pending_notifications"
for json_file in "$PENDING_DIR"/*.json; do
  # 读取每个 pending JSON
  # 检测用户消息是否匹配 A/B/C/D（支持带序号格式，如 A1、B2）
  # 如果匹配，执行对应操作，然后删除该 JSON 文件
done
```

**收到 A：**

1. 扫描 `~/.openclaw/workspace/.learnings/.pending_notifications/` 下的所有 .json 文件
2. 读取每个 pattern 的 raw_md，理解要创建什么技能
3. 调用 skill-creator：`sessions_spawn` → 传入 skill-creator prompt（包含 pattern 上下文）
4. 执行完成后，更新对应 learnings 条目为 `resolved`，删除已处理的 JSON 文件

**收到 B：**

1. 同上，扫描所有 pending JSON
2. 调用 skill-creator（optimize 模式）
3. 执行完成后，更新对应 learnings 条目为 `resolved`，删除已处理的 JSON 文件

**收到 C：**

1. 同上，扫描所有 pending JSON
2. 将对应 learnings 条目标记为 `dormant`（不在骚扰用户）
3. 静默，不发送任何消息

**收到 D：**

1. 同上，扫描所有 pending JSON
2. 判断升华目标：
   - 行为/风格规则 → SOUL.md
   - 工作流/过程规则 → AGENTS.md
   - 工具坑点 → TOOLS.md
3. 将 pattern 提炼为一条简洁规则，追加写入目标文件
4. 在原 learnings 条目标注 `Status: promoted`
5. 更新 Recurrence-Count
6. 删除已处理的 pending JSON 文件

### 上下文存储（通知时写入）

每次发送 A/B/C/D 通知前，cron agent 执行：

```bash
mkdir -p ~/.openclaw/workspace/.learnings/.pending_notifications/
# 写入: <unix_ts>_<safe_pattern_name>.json
# 内容: {pattern_name, count, raw_md, action_taken, notified_at}
```

**每次写一个文件（多个 pattern → 多个文件）。** 收到 A/B/C/D 后，主代理读取**所有** pending JSON 文件，逐条处理，**防止孤儿文件**。

### 约束

- skill-creator 调用使用 `sessions_spawn`（runtime=subagent, mode=run）
- 操作完成后删除 `pending_notifications/` 中对应的 JSON 文件
- 如果 pending_notifications/ 为空但收到 A/B/C/D → 忽略（可能是误触）

---