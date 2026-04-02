---
name: smux
description: Control tmux panes and communicate between AI agents. Prefer the installed `tmux-bridge` command. Never use relative paths for the bridge script. If the command is missing, resolve and use the script's real path or ask the user to install it first. Use raw `tmux` only as fallback for target confirmation, layout management, and troubleshooting.
metadata:
  { "openclaw": { "emoji": "🖥️", "os": ["darwin", "linux"], "requires": { "bins": ["tmux"] } } }
---

# smux

默认优先使用本机已安装的 `tmux-bridge` 命令。严禁使用相对路径调用 bridge 脚本，因为 agent 看到的 skill 目录可能是软链接，`./scripts/tmux-bridge` 或“相对 skill 目录”的假设都可能失效。原生 `tmux` 只是 fallback，只在目标确认、布局管理和排障时使用。

## 一句话说明

这是一个给 tmux 多 pane 协作用的技能：你可以安全地读取其他 pane、给其他 agent 派任务、按“是否期待回复”管理跟进，而不是不停轮询对方状态。

## 适合谁

- 在 tmux 里同时跑多个 agent 的人
- 需要跨 pane 委派任务、收结果、看 blocker 的人
- 希望减少“打断别人思考”和“无意义轮询”的团队

## 上手方法

安装或确保本机有 `tmux-bridge` 后，记住这 3 条就够了：

1. 先 `read`，再交互
2. 普通委派用 `--no-reply`
3. 需要结果回传时用 `--expect-reply`

最常用的 3 个命令：

```bash
tmux-bridge read %39 20
tmux-bridge send --no-reply %39 '请审阅 src/auth.ts'
tmux-bridge send --expect-reply %39 '请审阅 src/auth.ts，做完后回复结论'
```

## 何时使用

- 读取别的 tmux pane 输出
- 给别的 agent pane 发消息
- 给 pane 命名、解析 label、列出 pane
- 处理少量 tmux fallback 操作

## 默认规则

- 命令选择顺序：先 `tmux-bridge`，再脚本真实路径
- 不允许使用 `./scripts/tmux-bridge` 这类相对路径
- 如果环境里没有 `tmux-bridge`，先定位脚本真实路径；如果仍不可用，就直接让用户先安装
- agent pane 默认走 `read -> send`
- `send` / `message` 必须显式声明 `--expect-reply` 或 `--no-reply`
- 不要持续抓取对方状态；只有期待回复且超时未回时才去检查
- 不要给其他 tmux session 的 pane 发消息
- 发送前先确认目标属于当前 session
- 发完就继续工作，不要等待或轮询回复
- 只有在你明确要检查草稿时才用 `message -> read -> keys Enter`
- 非 agent pane 才需要在提交后继续 `read`

桥接命令优先级：

```bash
1. tmux-bridge
2. /绝对/真实/路径/tmux-bridge
```

不要这样做：

```bash
./scripts/tmux-bridge
../smux/scripts/tmux-bridge
scripts/tmux-bridge
```

如果需要回退到脚本路径，必须先解析真实路径，例如：

```bash
python3 -c 'import os; print(os.path.realpath("/Users/mkuiwu/mycode/skill-hub/skills/smux/scripts/tmux-bridge"))'
```

## 快速开始

```bash
tmux display-message -p '#S:#I.#P #{pane_id}'
tmux list-panes -F '#S:#I.#P #{pane_id} #{pane_current_command} #{pane_title}'
tmux-bridge read %39 20
tmux-bridge send --no-reply %39 '请审阅 src/auth.ts'
```

## tmux-bridge

常用命令：

| 命令 | 用途 |
|---|---|
| `tmux-bridge list` | 列出 pane、进程、label、cwd |
| `tmux-bridge read <target> [lines]` | 读取 pane 最近输出 |
| `tmux-bridge send --expect-reply <target> <text>` | 发送并记录待回复跟进 |
| `tmux-bridge send --no-reply <target> <text>` | 发送后不跟进 |
| `tmux-bridge message --expect-reply <target> <text>` | 写入草稿并记录待回复跟进 |
| `tmux-bridge message --no-reply <target> <text>` | 写入草稿但不跟进 |
| `tmux-bridge type <target> <text>` | 输入文本，不提交 |
| `tmux-bridge keys <target> <key>...` | 发送特殊按键 |
| `tmux-bridge name <target> <label>` | 设置 pane label |
| `tmux-bridge resolve <label>` | 将 label 解析为 pane target |
| `tmux-bridge id` | 输出当前 pane ID |
| `tmux-bridge pending` | 查看当前 pane 的待回复项 |
| `tmux-bridge check <target>` | 超时后检查某个待回复目标的状态 |

找不到命令时：

| 命令 | 用途 |
|---|---|
| `python3 -c 'import os; print(os.path.realpath("/path/to/smux/scripts/tmux-bridge"))'` | 解析 bridge 脚本真实路径 |

目标规则：

- 优先使用 `%pane_id`
- label 只在当前 session 内唯一时才用
- 如果无法证明目标属于当前 session，就不要发送

读取守卫：

- `type` 和 `keys` 前必须先 `read`
- 每次 `type` 或 `keys` 后，下次交互前都要重新 `read`
- `send` 适合 agent pane 默认路径，`message` 只用于检查草稿
- `send` / `message` 不再因为目标正在思考就硬拦截；是否跟进改由回复意图决定
- 只有 `--expect-reply` 的消息才会进入待跟进列表，默认超时 120 秒，可用 `--timeout <secs>` 覆盖

## 推荐流程

给 agent 发消息：

```bash
tmux-bridge read %39 20
tmux-bridge send --no-reply %39 '请审阅 src/auth.ts'
```

需要结果回传时：

```bash
tmux-bridge read %39 20
tmux-bridge send --expect-reply %39 '请审阅 src/auth.ts，做完后回复结论'
```

检查草稿再提交：

```bash
tmux-bridge read %39 20
tmux-bridge message --expect-reply %39 '请审阅 src/auth.ts'
tmux-bridge read %39 20
tmux-bridge keys %39 Enter
```

超过 2 分钟还没回复再跟进：

```bash
tmux-bridge pending
tmux-bridge check %39
```

常见输出含义：

- `waiting`: 已发送，尚未超时
- `overdue`: 已超时，可以决定是否跟进
- `snapshot_status: working`: 对方还在做事
- `snapshot_status: idle`: 对方空闲但还没回
- `snapshot_status: prompt`: 对方卡在交互提示
- `snapshot_status: draft`: 对方 pane 里有未提交草稿

处理非 agent pane：

```bash
tmux-bridge read worker 10
tmux-bridge type worker "y"
tmux-bridge read worker 10
tmux-bridge keys worker Enter
tmux-bridge read worker 20
```

## 消息约定

- 把跨 pane 消息当成任务委派，不是聊天
- 普通委派默认用 `--no-reply`
- 只有确实需要确认、结果或 blocker 时才用 `--expect-reply`
- 不要主动轮询；只有超时未回复时才检查状态
- 一条消息里写清任务、期望输出、结束条件
- 不发“收到”“谢谢”“我来处理”这类空消息
- 有结果或 blocker 再回复
- 回复通常会通过 `tmux-bridge` 直接打回你的 pane，不要轮询目标 pane

## 最佳实践

- 优先用 `%pane_id`，不要滥用 label
- 目标是 agent pane 时，默认用 `send`，不是 `type`
- 除非你真的要检查草稿，否则不要用 `message`
- `pending` 只是提醒，不会自动催促对方
- 如果对方没有按协议回复，`check` 只负责帮你看状态，不会替你做决定

## Raw tmux Fallback

只在这 3 类场景用原生 `tmux`：

- 目标确认
  `tmux display-message -p '#S:#I.#P #{pane_id}'`
  `tmux list-panes -F '#S:#I.#P #{pane_id} #{pane_current_command} #{pane_title}'`
- 布局管理
  `tmux split-window -h -t SESSION`
  `tmux split-window -v -t SESSION`
  `tmux select-layout -t SESSION tiled`
- 排障
  `tmux capture-pane -t SESSION:WINDOW.PANE -p`

## 参考

- `references/tmux-bridge.md`: `tmux-bridge` 命令摘要
- `references/tmux.md`: 原生 `tmux` 命令摘要
