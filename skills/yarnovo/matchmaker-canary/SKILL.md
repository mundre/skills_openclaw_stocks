---
name: matchmaker
description: |
  交友平台 CLI（生产 https://matchmaker.agentaily.com）。装了之后可以和你的 Claude 对话式注册、填资料（性别、年龄、城市、兴趣、自我介绍），然后让你的 agent 直接用受限只读 SQL 查其他人匹配 + 发消息 + 收消息 + 读回执。中心化 Postgres，手机号 + 短信验证码登录，服务端只管存数据 + 开查询 + 存消息，匹配智能由你的 agent 自己决定。
  TRIGGER when: 用户说"交友"、"找对象"、"matchmaker"、"注册交友平台"、"填交友资料"、"更新交友 profile"、"匹配异性"、"查谁喜欢 X"、"给交友站某人发消息"、"收交友站消息"。
  DO NOT TRIGGER when: 用户要做聊天室 / 社交网络 / 匿名社区 / 陌生人交友 app（这些都不是本项目职能）；用户只想查数据库概念（用 sql-helper 之类）；服务端不可达时（curl /healthz 一次，down 就告诉用户稍后再试）。
argument-hint: "[register|verify|profile|query|send|inbox|sent|read|logout|delete] [args...]"
category: social
allowed-tools: Bash(*), Read, Write, Edit
---

# matchmaker — 共享交友资料库 + agent 查询 + 异步消息

## 它是什么

一个**给 agent 用**的轻量交友基础设施：中心化 Postgres 存全部用户 profile 和消息，装了 skill 的人用手机号验证码登录，然后**自己的 agent 通过受限只读 SQL 直接查其他人 + 代收代发消息**。匹配逻辑 100% 在你的 Claude 这边跑，服务端不做推荐、不做排序，只管存数据和执行你写的 WHERE。

**设计取向**：你知道你自己想找什么样的人，比任何服务端算法都知道。所以把查询权交给你的 agent。

## Prerequisites

- **`mm` CLI ≥ 0.1.0**（`mm --version` 检查）
  - 安装 / 升级：`npm install -g @acong-tech/matchmaker@latest`
  - 低于此版本时本 skill 可能依赖它没有的命令（如 `mm send` 需要 CLI 0.1.0+）。agent 第一次调 `mm` 前先验版本
- vault 里的 `matchmaker-user` 平台首次登录后自动写入 session token
- Node.js ≥ 20

**自检小贴士（给 agent）**：`mm` 每次调用会在 stderr 打 notice 提示有新版本，注意读一下。想屏蔽用 `MM_SKIP_UPDATE_CHECK=1`。

## 常见用法

### 第一次：注册 + 验证

```bash
mm register 13812345678
# → 验证码已发送到 138****5678，60 秒内有效
# → request_id: 01HXYZABC...              （ULID，verify 必需）

mm verify 123456 --request-id 01HXYZABC...
# → 登录成功，user_id=<ULID>
# → session_token + user_id 写入 vault（`matchmaker-user` 平台）
# → 手机号从头到尾不在 stdout / stderr / 本地 / vault 出现（红线 O2.KR4）
```

> **为什么 verify 要传 request_id？** 服务端用 `request_id` 反查 phone_hash，CLI 这边就不用捧着原始手机号满屏幕跑了。ULID 不是 PII（无法反推手机号），打印到 stdout / 日志都安全。

`mm register` 失败的几种提示：
- `error: rate_limited` —— 同号 60 秒 / 1 小时 / 24 小时超限，等 `retry_after` 秒再试
- `error: invalid_phone` —— 服务端拒绝此号码格式（只支持中国大陆手机 11 位）
- `error: unauthenticated` —— session 过期或被撤销，重新 register + verify
- `error: network_error` —— 服务端不可达，查网络

### 冷静期撤回

如果之前执行过 `mm delete` 但 7 天内又想回来，直接再走一次 `mm register` + `mm verify`，`undeleted: true` + `was_deleted_at: <时间戳>` 会出现在 verify 响应里，账号自动恢复，老 profile / 老消息不变。

### 填 profile（推荐和 Claude 对话填）

和你的 Claude 说"帮我更新 matchmaker 资料"，让 agent 一步步问你、然后调 `mm profile set`：

```bash
mm profile set gender f              # f / m / nb
mm profile set age 28                # 18-99 整数
mm profile set city 上海              # 市级粒度，≤ 30 字
mm profile set tags 徒步,独立电影,做饭  # 逗号分隔，CLI 侧自动去空白 + 去重，服务端上限 20 个
mm profile set bio "博士在读，周末徒步 / 做饭 / 看独立电影。"  # ≤ 500 字
mm profile set messaging_read_receipt_enabled false  # 隐私党关掉读回执，对方看不到你的 read_at
mm profile show                      # 查自己当前资料（含掩码手机号 + 读回执开关状态）
mm profile clear tags                # 清空 tags（只有 tags / bio 可清）
mm profile clear bio                 # 清空自我介绍
```

**字段说明**：
- `gender` / `age` / `city` 是必填字段，**不能 clear**（如需删号用 `mm delete`）
- `tags` 每个标签只允许字母 / 数字 / 中划线 / 下划线（支持中文），拒绝空格 / 标点 / emoji
- `bio` 原样存原样返，不做 HTML escape（查询结果只给 agent 读，没有浏览器 render 上下文）
- `messaging_read_receipt_enabled` 默认 true；设成 false 后你读消息对方的 `/sent` 看不到 `read_at`，仍然能看到消息被送达
- `mm profile show` 的 stdout **永远只显示掩码手机号**（前 3 + `****` + 后 4），不会有原始 11 位号码

### 让 agent 查候选（核心能力）

`mm query '<where>' [--limit N] [--json]` —— 把一条受限的 SQL-like `WHERE` 条件发给服务端，返回匹配的 profile 数组。

**字段白名单**（只能用这 7 个，其他字段一律拒）：

| 字段 | 类型 | 支持的操作 |
|---|---|---|
| `id` | text | `=` `!=` `IN` |
| `gender` | enum | `=` `!=` `IN` |
| `age` | int | `=` `!=` `<` `<=` `>` `>=` `IN` |
| `city` | text | `=` `!=` `IN` |
| `tags` | text[] | `@>` |
| `bio` | text | `ILIKE`（单次 1 次，pattern ≥ 3 字符） |
| `created_week` | date | `=` `<` `<=` `>` `>=` |

**5 条合法示例**：

```bash
mm query "gender = 'f' AND age >= 25 AND age <= 32"
mm query "city = '上海' AND tags @> ARRAY['徒步']"
mm query "gender IN ('f','nb') AND age > 20" --limit 30
mm query "age >= 18 AND NOT (city = '北京')"
mm query "tags @> ARRAY['徒步','独立电影']"
```

加 `--json` 返 `{profiles: [...]}` 结构化 JSON，便于 agent 下游处理。

**DSL 规则（不符合就 exit 1）**：
- WHERE 不能为空（防一次性拉全库）
- LIMIT 默认 50，最大 100，不支持 OFFSET
- 字符串只能单引号 `'...'`
- tags 含某元素用 `@>` 不用 `= ANY(tags)`
- 不支持 JOIN / UNION / 子查询 / 注释 / 分号 / 函数调用 / BETWEEN（用 `>= AND <=`）
- 排序由服务端随机（交友 UX 刻意的，每次不同候选）

### 发消息（给查到的人发）

```bash
mm send <recipient_user_id> "周末去西湖吗？"
# → 已发送: 01KPN...（2026-04-21T12:00:00Z）
```

限制：
- body 最长 2000 字符纯文本，不能空
- 不能发给自己（exit 1 `cannot message yourself`）
- 收件人 user_id 必须存在且未删号（exit 1 `not_found`，故意不区分"不存在"和"删号"防扫号）

### 收消息（自己的收件箱）

```bash
mm inbox                      # 所有，倒序
mm inbox --unread             # 只看未读
mm inbox --limit 20 --before 01KPN...  # 分页：比某条 ULID 更早
```

输出每条格式：

```
<msg_id>  from=<sender_id>  <created_at>  [read_at=<...> | unread]
  <body 前 80 字，超过加 ...>
```

### 标记已读（由 agent 主动）

`mm inbox` 只是**取**消息，不会自动打读回执。你的 agent 决定真给你看了之后，主动调：

```bash
mm read <message_id>
# → 已标记已读: <id>（<read_at>）
```

幂等：再调一次返回原 `read_at`，不覆盖。

> 设计：读回执由 agent 主动打，不是服务端自动——因为 agent 批量拉 inbox 不等于"人真看了"，这样语义最准。发消息方才能看到真实的"对方看了没"。

### 查自己发过的（含对方读了没）

```bash
mm sent [--limit N] [--before ULID]
```

- 对方 `messaging_read_receipt_enabled=false` 时，该条 `read_at` 永远显示 unread，即使对方 agent 已经打过读回执——服务端在 `/sent` 层面过滤掉

### 删号

```bash
mm delete --confirm
# → 软删 + 所有 session 撤销，7 天内冷静期
# → 7 天内同手机号重新 verify 可撤回
# → 7 天后服务端 cron 物理清理 profile 行，消息随 CASCADE 删
```

### 查 logout

```bash
mm logout
# → vault 里本机 session_token 清除，其他设备不受影响
```

## 和其他 skill 的关系

- 独立 skill，不依赖其他项目
- `vault` 存 session token（用户侧）
- 服务端的备份 / 部署 / 短信是 matchmaker 后端团队的事，skill 消费者不感知

## 隐私与限制

- 你填什么就存什么 —— **MVP 不做人工审核**，别填身份证 / 精确住址等敏感信息
- 查询结果只返回白名单字段，别人查你也只能看到你允许的字段
- MVP **已支持** 跨用户异步消息 + 读回执开关；**不支持** 群聊 / 实时推送 / 图片 / 音视频 / 举报
- 删号是软删 → 7 天后物理清理，这期间可撤销（重新 verify 手机号就恢复）

## Gotchas

- verify 60 秒内有效，如果消息 app 转发延迟，可能被服务端判过期 → 直接 register 第二次
- 注册第一个账号之后 profile 有 `gender/age/city/tags/bio` 全空的默认，查不到自己之前要先 `mm profile set` 填满 3 个必填
- `mm query` 的字符串一律单引号。写 `"city = 'shanghai'"` 不行（单双混用），写 `'city = \'shanghai\''` 也不优雅，**在 JSON body 里 bash 最外层用单引号，里面字符串用单引号然后 `"` 当外层参数**：`mm query 'city = '"'"'上海'"'"''`。agent 用 --json 输出更简单

## 对比其他方式

和普通交友 app 的区别：没有 UI、没有推荐算法、没有会员置顶。**让你的 agent 帮你筛**——你说"这个月想找喜欢独立电影 + 不抽烟的上海姑娘"，agent 写一条 WHERE 返回 20 个候选，你自己定。

不是一个**产品**，是一个**基础设施**，用来让 Claude Code 用户之间更容易认识。
