---
name: tmux-bridge
description: Bundled CLI for tmux cross-pane messaging and pane interaction.
metadata:
  { "openclaw": { "emoji": "🌉", "os": ["darwin", "linux"], "requires": { "bins": ["tmux"] } } }
---

# tmux-bridge

在这个 skill 里默认优先使用本机已安装的 `tmux-bridge` 命令。不要使用任何相对路径，因为 agent 看到的 skill 目录可能是软链接。命令不存在时，先解析脚本真实路径；如果还不可用，就让用户先安装。

## 快速理解

`tmux-bridge` 做 3 件事：

- 读取别的 pane
- 给别的 pane 发任务
- 管理“这条消息要不要等回复”

## 关键规则

- agent pane 默认用 `read -> send`
- `type` 或 `keys` 前必须先 `read`
- `send` / `message` 必须显式声明 `--expect-reply` 或 `--no-reply`
- 不要持续抓取对方状态；只有期待回复且超时未回时才检查
- 发给 agent 后不要等待或轮询；回复会回到你的 pane
- label 只有在当前 session 内唯一时才可靠

## 常用命令

```bash
tmux-bridge list
tmux-bridge read <target> [lines]
tmux-bridge send --expect-reply <target> <text>
tmux-bridge send --no-reply <target> <text>
tmux-bridge message --expect-reply <target> <text>
tmux-bridge message --no-reply <target> <text>
tmux-bridge type <target> <text>
tmux-bridge keys <target> <key>...
tmux-bridge name <target> <label>
tmux-bridge resolve <label>
tmux-bridge id
tmux-bridge pending
tmux-bridge check <target>
```

## 最小模式

给 agent 发消息：

```bash
tmux-bridge read %39 20
tmux-bridge send --no-reply %39 'Please review src/auth.ts'
```

When a reply is required:

```bash
tmux-bridge read %39 20
tmux-bridge send --expect-reply %39 'Please review src/auth.ts and reply with the result'
```

Follow up only after timeout:

```bash
tmux-bridge pending
tmux-bridge check %39
```

检查草稿后提交：

```bash
tmux-bridge read %39 20
tmux-bridge message --expect-reply %39 'Please review src/auth.ts'
tmux-bridge read %39 20
tmux-bridge keys %39 Enter
```

## Practical defaults

- Use `--no-reply` for normal delegation
- Use `--expect-reply` only when you really need a response
- Do not poll the target pane repeatedly
- If no reply arrives after 120 seconds, use `pending` / `check`
