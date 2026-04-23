---
name: xiangqin
description: 相亲平台（虚拟信封私信 + 受众查询）的使用入口。TRIGGER when 用户说"相亲"、"找对象"、"xiangqin"、"注册相亲"、"填资料"、"查匹配"、"想联系 TA"、"发私信"、"给对方写信"、"有新消息吗"、"查收件箱"、"买信封"、"拉黑 / 举报"。DO NOT TRIGGER when 用户要聊天/推荐/匹配算法（本项目不做）、服务端不可达时先 curl health。
---

# xiangqin — 相亲平台 skill

**两层商品**：
1. 查询匹配（免费）—— 你用 DSL 自己查，服务端不做推荐
2. 虚拟信封私信（每天 3 封免费，超额 ¥1/封）—— 主动接触对方的唯一付费点

## 前置

用户本地需要装 `xq` CLI（Python 包）。

### 系统要求

- **Python 3.12 或更高**（`python3 --version` 检查）
- 网络能访问 PyPI 和 xiangqin 服务端（`https://xq.agentaily.com` 或自定义 endpoint）

### 安装

推荐 `uv`（现代 Python 包管理器，隔离环境省心）：

```bash
# uv（推荐）
uv tool install acong-tech-xiangqin

# 或 pipx（隔离环境）
pipx install acong-tech-xiangqin

# 或传统 pip（在 venv 里装避免污染系统 Python）
python3 -m venv ~/.venv/xiangqin
source ~/.venv/xiangqin/bin/activate
pip install acong-tech-xiangqin
```

**SOCKS 代理环境**：包含 `httpx[socks]` 依赖，全局 SOCKS 代理下也能工作。

### 验证

```bash
xq --version           # 显示当前版本号
xq health              # 打服务端 /health，返回 {"status":"ok","version":"X.Y.Z"}
```

如果 `xq health` 返回错误，检查：
- 网络能否访问 xiangqin 默认 endpoint
- 如走自定义服务端：`xq --endpoint https://<your-endpoint> health` 或设置 `XIANGQIN_ENDPOINT` 环境变量

## 心智模型

- **查询**：受限 WHERE DSL（字段白名单 + 操作符白名单 + 值白名单），agent 构造 SQL-like 查询，服务端不做推荐也不做排序算法
- **私信**：A 写信 → 进 B 的信箱（保留 30 天）+ 可选通过 B 的 agent gateway 推通知
- **通知去重**：B 有未读且 < 12h 不再推；≥ 12h 兜底再提醒一次
- **隐私**：手机号 HMAC-SHA256 不落明文；通信双方 agent_gateway_url 不互相透露（平台匿名代理）

## 典型流程

### A. 首次注册

```
用户：帮我在 xiangqin 注册，手机 138xxxx1111
agent: [跑] xq register 13800001111 → request_id=01K...
agent: 把手机收到的 6 位验证码告诉我
用户：123456
agent: [跑] xq verify 123456 --request-id 01K...
```

### B. 填 profile

```bash
xq profile set gender m
xq profile set age 28
xq profile set city hangzhou
xq profile set height 178
xq profile set education master
xq profile set tags '程序,登山,做饭'
xq profile set bio '程序员，想找能一起爬山的人'
xq profile show
```

可选：开通知（让 xiangqin 推新信到用户的 agent gateway）：

```bash
xq profile set agent_gateway_url https://my-gateway.example.com
xq profile set agent_hooks_token <token>
xq profile set notify_on_new_mail on
```

### C. 查匹配

```bash
xq query 'gender=f AND city=hangzhou AND age>=25 AND age<=30 AND height>=165' --limit 20
```

### D. 给 TA 发私信

```
用户：我喜欢上面那个 user_id 01JG... 的女生，帮我写信
agent: [起草内容，和用户确认]
       [跑] xq dm send 01JG... "我是杭州的程序员..."
       → ✓ 已投递（免费额度）msg=01JH...
```

**TRIGGER 触发 `xq dm send` 的用户原话**：
- "想联系 TA" / "给他发私信" / "和她打招呼"
- "我对这个人感兴趣"
- "写一封信给 user_id xxx"

### E. 查信封余额

```bash
xq envelope state       # 今日免费剩 / 付费余量
xq envelope buy --count 10 --mock   # 0.1 期用 mock；真付待接入
```

**TRIGGER agent 主动提示**：当用户已发 3 封私信后想发第 4 封 → 提示"今日免费已用完，¥1/封，买 N 个？"

### F. 查收件箱

```bash
xq inbox list           # ● 未读标记；平铺按时间倒序
xq inbox show 01JH...   # 看 + 标已读
xq inbox reply 01JH... "你好..."   # 回信（消耗信封）
```

**TRIGGER**：用户说"有新消息吗 / 谁给我发私信了 / 查收件箱"

### G. 处置骚扰

```bash
xq inbox report 01JH... --reason '骚扰'   # 举报（留档取证）
xq block 01JG...                            # 拉黑（对方后续发信拦截）
```

### H. 新版本自动提示

`xq` 任何命令执行时，若检测到 PyPI 有新版本，会在 **stderr** 打印一行：

```
[xq] 新版本 0.4.0 可用（当前 0.3.0）。跑 `pip install -U acong-tech-xiangqin` 更新。
```

**TRIGGER**：当 `xq` 命令 stderr **包含 `[xq] 新版本` 字样**时，agent 应向用户转述并问是否更新：

> "你的 xiangqin CLI 有新版本 X.Y.Z 可用（当前 A.B.C），要我帮你更新吗？"

用户同意后跑升级命令（按用户安装方式）：

```bash
pip install -U acong-tech-xiangqin
# 或 uv tool upgrade acong-tech-xiangqin
```

用户要关闭：`export XIANGQIN_NO_UPDATE_CHECK=1`。CI 环境自动关。

## 不变量

- 服务端零推荐 / 零排序算法
- WHERE 不能为空；LIMIT 默认 50 最大 100
- 信封：免费额度 0 点 UTC 重置；投递失败（拉黑 / 对方不存在）不扣
- 通知去重：12h 窗口（有未读 + <12h 不推；≥12h 兜底）
- xiangqin 不存对话历史 —— 信件内容落库 30 天 TTL，超期清
- 匿名代理：发信方 / 收信方互不知对方 agent_gateway_url / hooks_token

## 更多

[文档站](https://agentaily-xiangqin.pages.dev/) —— 设计 / 装机 / CLI / FAQ。
