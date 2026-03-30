---
name: weixin-mp-push
description: 支持通过AI生成符合公众号规范的图文（文章和贴图），并推送到公众号草稿箱或直接发布，兼容其它SKILL生成的图文、图片进行推送。通过配置向导扫码授权，无需泄露公众号Secret密钥，无需配置公众号IP白名单。
---

# weixin-mp-push · 微信公众号图文生成与推送技能

## 文件路径与作用

| 文件                        | 位置                           | 作用                   |
| ------------------------- | ---------------------------- | -------------------- |
| **SKILL.md**              | `weixin-mp-push 目录/` | 本说明                  |
| **design.md**             | 同上                           | HTML格式规范             |
| **config.json**           | 同上                           | 配置向导生成后的真实配置         |
| **config.example.json**   | 同上                           | 字段说明（fieldsHelp）+ 示例 |
| **push-to-wechat-mp.js**  | 同上                           | 推送脚本                 |

---

## 第一步：配置向导

| 项          | 内容                                                                                                                         |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| **配置向导地址** | [https://app.pcloud.ac.cn/design/weixin-mp-push.html](https://app.pcloud.ac.cn/design/weixin-mp-push.html) |
| **流程**     | AI发送配置向导给用户 → 用户微信扫码 → 用户选择推送账号 → 用户复制发给AI                                                                                 |

AI检查在 **weixin-mp-push 目录** 下是否存在 **`config.json`**。如果不存在，则无法使用本技能，AI需要发送配置向导地址给用户扫码授权。

---

## 第二步：配置文件

AI将配置向导得到的配置参数保存为 **weixin-mp-push 目录** 下的 **`config.json`**，编码 **UTF-8**。

在已进入该目录时，可：

```bash
cat > config.json << 'EOF'
{ … 粘贴配置向导 JSON … }
EOF
```

（Windows 可用编辑器在该目录新建 `config.json` 并粘贴）

---

`config.json` 字段 `pushMode` 和 `isBindPhoneNumber` 说明：

| `pushMode` | `isBindPhoneNumber` | 调用 `sendToWechat` 时 `sendMode` 的取值 | 含义 |
| ---------- | ------------------- | ---------------------------------------- | ---- |
| `default`  | `true`              | `draft` 或 `send` | 使用系统默认公众号且已绑定手机号时，可草稿或直接发布 |
| `default`  | `false` 或缺省 | `draft` | 未绑定手机号时仅能草稿 |
| `custom`   | `null`              | `draft` 或 `send` 或 `masssend` | 自定义公众号；`send`/`masssend` 需已认证，否则可能失败 |

---

## 第三步：写公众号图文

用户发送图文创作要求给AI，AI根据 `design.md` 规范生成标准的 HTML 文件。后续在推送图文的时候，标准的 HTML 会自动适配公众号格式。

- **文章或通用**：默认宽度 677px，适合文章或通用类型
- **图文卡片**：宽度 375px，固定分页比例（默认 3:4），适合贴图类型（俗称小绿书，类似小红书图文卡片），可截图分发至朋友圈、小红书或其它社群

---

## 第四步：推送到公众号

推送方式：`html` 模式传入生成的 HTML 文件（可由本技能或外部产出，其它素材可先按 `design.md` 整理成 HTML）；`img` 模式传入已是公网可访问地址的图片 URL 数组及标题、正文，无需再把图片链转成大段 HTML。

### 推送 HTML

AI 调用脚本，首参为 `html`，再传与脚本同目录下的 HTML 文件名，再传 `sendMode`（可选）：

```bash
cd weixin-mp-push
node push-to-wechat-mp.js html 你的文件.html draft
```

### 推送图片链接

AI 调用脚本，首参为 `img`，第二参为**图片链接的 JSON 数组字符串**（整段一个参数；Bash 与 PowerShell 都可用单引号包住整段 JSON，例如 `'["https://...","https://..."]'`）。再依次传标题、正文、`sendMode`（可选）。

```bash
cd weixin-mp-push
node push-to-wechat-mp.js img '["https://cdn.example.com/1.png","https://cdn.example.com/2.png"]' "标题" "正文" draft
```

**标题、正文**（命令行各一个参数，含空格时用英文双引号）：标题和正文可为空。

### 说明

- **sendMode 说明**：`draft` 推送到草稿箱（缺省）；发布用 `send`；群发用 `masssend`（需已认证号等条件）。
- **接口说明**（供查阅）：请求地址为 `config.json` 中的 `apiBase`（缺省 `https://api.pcloud.ac.cn/openClawService`），**POST**、`Content-Type: application/json`，Body 含 `action: sendToWechat`、`openId`、`title`、`content`、`sendMode`；`img` 模式另含 `imgUrls`；`custom` 模式需加 `accountId`。默认草稿箱；未认证号勿用群发/直接发布。
- **超时说明**：推送链路较长，若返回「超时」可视为可能已成功，勿重复狂推；请用户看服务通知或草稿箱。
