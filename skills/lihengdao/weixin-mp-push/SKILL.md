---
name: weixin-mp-push
description: 支持通过AI生成符合公众号规范的图文（文章和贴图），并推送到公众号草稿箱或直接发布，兼容其它SKILL生成的图文、图片进行推送。通过配置向导扫码授权，支持多账号。无需泄露公众号Secret密钥，无需配置公众号IP白名单。
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

`config.json` 中 **`accounts`** 说明：第一项为系统默认公众号，后续为已授权的公众号；`selected: true` 表示向导最终选择。

- 选中 **`kind: default`**：该项含 **`isBindPhoneNumber`**。已绑手机 → 调用 `sendToWechat` 时 `sendMode` 可用 `draft` 或 `send`；未绑 → 仅宜 `draft`。
- 选中 **`kind: custom`**：该项含 `appId`；`sendMode` 可用 `draft` / `send` / `masssend` 依公众号认证情况而定。

---

## 第三步：写公众号图文

用户发送图文创作要求给AI，AI必须根据 `design.md` 规范生成标准的 HTML 文件。有二种创作类型：
- **文章**：通用类型，页面默认宽度 677px
- **贴图**：图文卡片类型（俗称小绿书，类似小红书），页面默认宽度 375px，固定分页比例（默认 3:4）。推送到公众号时， 后台会自动把 HTML 内容转换为图片

**⚠️ 注意：** 不管是创作 **文章** 还是 **贴图** ，必须先阅读 `design.md`，按其规范生成标准的 HTML 文件。后续在推送图文过程中，标准的 HTML 会自动适配公众号格式。 

---

## 第四步：推送到公众号

推送方式：`html` 模式传入生成的 HTML 文件（本技能在第三步生成的HTML，也可以是用户或其它技能提供的HTML，非HTML内容可先按 `design.md` 整理成 HTML）；`img` 模式传入公网可访问的图片 URL 数组及标题、正文。**注意** 此模式仅适合用户或其它技能保证所提供的图片可以直接推送，无需本技能基于提供的内容进行创作

### 推送 HTML

AI 调用脚本：首参为目标公众号 AppID（`default` 表示系统默认），第二参为 `html`，再传与脚本同目录下的 HTML 文件名，再传 `sendMode`（可选）：

```bash
cd weixin-mp-push
node push-to-wechat-mp.js default html 你的文件.html draft
```

### 推送图片链接

AI 调用脚本：首参为目标公众号 AppID（`default` 表示系统默认），第二参为 `img`，第三参为**图片链接的 JSON 数组字符串**（整段一个参数；Bash 与 PowerShell 都可用单引号包住整段 JSON，例如 `'["https://...","https://..."]'`）。再依次传标题、正文、`sendMode`（可选）。


```bash
cd weixin-mp-push
node push-to-wechat-mp.js default img '["https://cdn.example.com/1.png","https://cdn.example.com/2.png"]' "标题" "正文" draft
```

**标题、正文**（命令行各一个参数，含空格时用英文双引号）：标题和正文可为空。

### 说明
**目标公众号 AppID**：`default`、`-` 或空字符串表示系统默认公众号；`wx` 开头为已绑定公众号的 AppID（可与 `config.json` 中 `accounts` 对照）。
- **sendMode 说明**：`draft` 推送到草稿箱（缺省）；发布用 `send`；群发用 `masssend`（需已认证号等条件）。
- **接口说明**（供查阅）：请求地址为 `config.json` 中的 `apiBase`（缺省 `https://api.pcloud.ac.cn/openClawService`），**POST**、`Content-Type: application/json`，Body 含 `action: sendToWechat`、`openId`、`title`、`content`、`sendMode`；`img` 模式另含 `imgUrls`；推送到自定义公众号时 Body 含 `appId`。默认草稿箱；未认证号勿用群发/直接发布。
- **超时说明**：推送链路较长，若返回「超时」可视为可能已成功，勿重复狂推；请用户看服务通知或草稿箱。
