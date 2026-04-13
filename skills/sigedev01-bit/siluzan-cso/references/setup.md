# 安装与配置

## 安装 CLI

```bash
npm install -g siluzan-cso-cli
```

环境要求：Node.js 24+

---

## 初始化 Skill 文件

```bash
siluzan-cso init -d /path/to-your/skills       # 写入自定义目录
```

使用 `init -d /path/to/skills`的方式，将skill复制到你的skill目录下

支持的 `--ai` 目标：
| 值 | 写入路径 |
|----|---------|
| `cursor` | `.cursor/skills/siluzan-cso/` |
| `claude` | `.claude/skills/siluzan-cso/` |
| `openclaw-workspace` | `skills/siluzan-cso/` |
| `openclaw-global` | `~/.openclaw/skills/siluzan-cso/` |
| `workbuddy-workspace` | `.workbuddy/skills/siluzan-cso/` |
| `workbuddy-global` | `~/.workbuddy/skills/siluzan-cso/` |
| `all` | 以上全部 |

---

## 首次登录 / 配置凭据

`siluzan-cso` 与 `siluzan-tso` **共用同一份凭据**，存储在 `~/.siluzan/config.json`，配置一次两个 CLI 均可使用。

```bash
siluzan-cso login                          # 交互式登录，按提示创建 API Key 后粘贴
siluzan-cso login --api-key <YOUR_API_KEY> # 直接设置 API Key（跳过交互）
siluzan-cso config set --api-key <Key>     # 或通过 config set 直接写入
siluzan-cso config set --token <Token>     # 备用：设置 JWT Token
```

> **⚠️ 不要使用 `config set --token <token>` 的方式。** 该方式会将 Token 明文写入 shell history（`~/.bash_history`、`~/.zsh_history`、PowerShell 历史），存在凭证泄露风险。推荐使用 `siluzan-cso login` 交互式输入。

API Key 获取入口：`https://cso.siluzan.com/v3/foreign_trade/settings/apiKeyManagement`

**Token 读取优先级（由高到低）：**
1. 环境变量 `SILUZAN_AUTH_TOKEN`（CI/CD 推荐）
2. `~/.siluzan/config.json` → `authToken`（`login` 写入此处）
3. 命令行 `--token <token>`（仅紧急临时用，用后立即轮换）

> **若用户已配置过凭据，不要重复询问。** 先尝试直接运行命令；只有命令返回认证失败时，才引导用户重新执行 `siluzan-cso login`。

---

## 查看当前配置

```bash
siluzan-cso config show
```
输出示例：
```
  构建环境     : production
  apiBaseUrl   : https://api.siluzan.com
  csoBaseUrl   : https://cso.siluzan.com
  apiKey       : abcd****1234
```

---

## 更新

需要严格按照步骤执行
- 执行 `npm install -g siluzan-cso-cli@[beta|latest]` 根据当前使用的是beta版本还是正式版本更新对应的版本到最新版
- 执行 `siluzan-cso init -d /path/to/skills` 复制项目中最新的skill文件来更新你的skill

---

## 修改其他配置

```bash
siluzan-cso config set --api-base <url>    # 切换 CSO API 地址
siluzan-cso config clear                   # 清空所有凭据
```

---
