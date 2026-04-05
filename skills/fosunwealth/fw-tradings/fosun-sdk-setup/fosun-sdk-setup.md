---
name: fosun-sdk-setup

description: 复星集团旗下复星财富（Fosun Wealth，星财富 APP）OpenAPI SDK 初始化与凭证管理工具，支持在专用虚拟环境安装、校验与修复 `fsopenapi`，并通过 `fosun.env`、自动凭证状态管理和开通二维码/链接完成端到端接入；适用于初始化或修复 SDK、导入与鉴权问题，以及刷新 API Key、Ticket、设备 ID 与客户端密钥。
requires:
  bins:
    - python3
    - openssl
---

# Fosun OpenAPI SDK 初始化

---

## 语言风格（非常重要）

通俗易懂，客户人群都是小白用户，必须使用大白话的形式进行内容输出，内容必须简洁，语言亲切，不要出现大量代码输出。
再次强调**不能出现大量代码和变量名称！！**

## 1. 安装 SDK

按以下步骤顺序执行。

### 环境约束（必须遵守）

- **严格以专用虚拟环境执行**：Fosun SDK 必须安装在独立的 Python 虚拟环境中， **禁止安装 Fosun OpenAPI SDK 到系统 Python 或其他非专属环境**
- **虚拟环境路径从记忆获取**：每次执行前，读取 `MEMORY.md`，查找 `Fosun SDK` 记录的虚拟环境路径 `$FOSUN_VENV`
- **统一使用 `$FOSUN_VENV/bin/python` 和 `$FOSUN_VENV/bin/pip` 完成程序执行与安装**
- **虚拟环境不存在，自动创建虚拟环境，创建后将完整路径写入 `MEMORY.md`

> 创建命令示例：`python3 -m venv {workspace_root}/.venv-fosun`

**Step 1 — 确认虚拟环境并检查 SDK**

检查 SDK 是否已安装：

```bash
$FOSUN_VENV/bin/python -c "import fsopenapi; print(fsopenapi.__file__)"
```

- 成功打印路径 → SDK 已安装，跳到 Step 4 验证。
- 报 `ModuleNotFoundError` → 检查 `MEMORY.md` 中是否记录了 SDK 源码路径：
  - 记忆中有路径但目录已不存在 → **删除记忆中对应记录**，继续 Step 2。
  - 记忆中有路径且目录存在 → 执行 `$FOSUN_VENV/bin/pip install <路径>`，跳到 Step 4。
  - 无记录 → 继续 Step 2。

**Step 2 — 定位或下载 SDK，并安装到虚拟环境**

优先从 GitHub 下载，若失败则使用备用地址：

```bash
mkdir -p /tmp/fosun-sdk
curl -L --fail -o /tmp/fosun-sdk/openapi-sdk.zip \
  https://github.com/fosunwealth/openapi-python-sdk/archive/refs/tags/v1.1.0.zip \
  || curl -L --fail -o /tmp/fosun-sdk/openapi-sdk.zip \
  https://openapi-docs.fosunxcz.com/download/openapi-python-sdk-1.1.0.zip
unzip -o /tmp/fosun-sdk/openapi-sdk.zip -d /tmp/fosun-sdk
$FOSUN_VENV/bin/pip install /tmp/fosun-sdk/openapi-python-sdk-main/
```

必须将包安装到 `$FOSUN_VENV` 对应 Python 的 `site-packages` 目录中。

**Step 3 — 安装二维码生成依赖**

在 `$FOSUN_VENV` 中安装 `qrcode` 和 `Pillow`（生成二维码图片所需）：

```bash
$FOSUN_VENV/bin/pip install -r skills/fw-tradings/fosun-sdk-setup/scripts/requirements-gen-access-url.txt
```

该命令会安装 `qrcode[pil]>=7.3.1`（含 Pillow）。**未安装时后续生成二维码脚本会报 `ModuleNotFoundError` 并退出**。

**Step 4 — 验证安装**

```bash
$FOSUN_VENV/bin/python -c "import fsopenapi, pathlib, sysconfig; module_path = pathlib.Path(fsopenapi.__file__).resolve(); site_packages = pathlib.Path(sysconfig.get_paths()['purelib']).resolve(); print(module_path); assert site_packages in module_path.parents, f'SDK 未安装到 site-packages: {module_path}'"
```

必须确认打印出的路径位于当前虚拟环境的 `site-packages` 下；如果安装失败，请联系星财富客服人员

**Step 5 — 记录路径到记忆**

安装成功后写入 `MEMORY.md`（若已有 `## Fosun SDK` 章节则更新）：

```
## Fosun SDK
- 虚拟环境路径: <$FOSUN_VENV 的实际绝对路径>
- SDK 安装路径: <虚拟环境 site-packages 内的实际路径>
```

> 如果虚拟环境或 SDK 源码目录后续被删除，必须同步删除或更新记忆中的对应记录。

---

## 认证校验流程（3种结果）

每次运行脚本时，`credential_flow.py` 会自动执行前置校验，只会有以下 3 种结果：

| 结果 | 触发条件 | 系统行为 |
|------|----------|----------|
| **1️⃣ 直接执行** | API Key 已生效（`valid`） | 自动加载凭证，直接执行您的交易命令 |
| **2️⃣ 生成新二维码** | API Key 失效/不存在 或 Ticket 过期 | 自动申请新的 API Key 和开通 URL，生成二维码供扫码 |
| **3️⃣ 复用现有二维码** | Ticket 有效但未完成授权 | 直接返回已有的开通 URL，生成二维码供扫码 |

> **您无需手动判断状态**：脚本会自动识别当前情况，按上述 3 种结果之一处理。如显示二维码，请扫码完成授权后重试原命令。

---

## 首次开通流程（小白用户必读）

如果您是第一次使用，系统会自动帮您完成以下步骤：

1. 📋 **自动检查**：运行任意脚本会自动检查 `fosun.env` 配置
2. 🔑 **自动生成**：如缺少密钥，会自动生成设备编码和客户端密钥
3. 🎫 **自动申请**：自动向复星服务器申请开通票据（Ticket）
4. 📱 **生成二维码**：系统会生成开通页二维码（结果 2 或结果 3）
5. ✅ **扫码授权**：用手机扫描二维码，在复星开通页完成授权
6. 🔄 **重试操作**：授权完成后，重新运行您的操作命令即可

---

## 2. 开通引导（首次使用）

当前流程统一由 `fw-tradings/fosun-trading/code/credential_flow.py` 自动完成：优先复用 `fosun.env` 里已有的设备编码、客户端私钥、API Key 和 Ticket，缺失时自动补齐，并在需要时重新申请 Ticket、回写最新凭证。若开通尚未完成，脚本会输出开通链接并中止，等待用户完成授权后再重试。

通常不需要手动执行初始化脚本，直接运行业务脚本即可：

```bash
cd fw-tradings/fosun-trading/code
python list_orders.py
```

如果只想单独检查初始化结果，可执行：

```bash
cd fw-tradings/fosun-trading/code
python -c "from credential_flow import prepare_client_runtime; print(prepare_client_runtime())"
```

**Step 6 — 生成开通页二维码并在对话中展示**

   - **前提**：`FSOPENAPI_OPEN_URL` 已写入 `fosun.env`，执行时注入该变量或显式传 `--url`。
   - **依赖**：已在 Step 3 安装；其他环境需先 `pip install -r skills/fw-tradings/fosun-sdk-setup/scripts/requirements-gen-access-url.txt`。

   - **生成命令**：
     ```bash
     python3 skills/fw-tradings/fosun-sdk-setup/scripts/gen_access_url.py --markdown-data-uri
     ```

   - **⛔ 展示规则（OpenClaw 腾讯云对话框必须直接看到二维码图片）**：

     **目标**：用户在对话气泡里直接看到一张二维码图片，掏出手机就能扫。

     **优先级 1 — HTTPS 公网图片（首选，最稳定）**

     腾讯云 OpenClaw 环境自带文件上传能力。流程：
     1. 脚本已将 QR PNG 保存到本地（路径见 `<<<FOSUN_QR_PNG_FOR_CHAT>>>` 标记）。
     2. 通过平台内置上传功能将该 PNG 上传，得到 HTTPS 公网地址。
     3. **在助手回复中，用独立段落写 Markdown 图片语法渲染二维码**：

     ---- 回复示例 ----
     请扫描下方二维码完成授权：

     ![OpenAPI申请二维码](https://实际上传后的公网地址/qr.png)

     申请链接：https://sit.mfosunhani.com/…
     ---- 回复结束 ----

     **优先级 2 — Base64 Data URI（上传不可用时的备选）**

     脚本加了 `--markdown-data-uri` 后，stdout 会输出 `<<<FOSUN_QR_MARKDOWN_DATA_URI>>>` 标记块。
     从中提取以 `![` 开头的完整一行，**作为独立段落**粘贴到助手回复中（前后各空一行）。

     **优先级 3 — Read 本地 PNG（兜底）**

     用 Read 工具读取 `<<<FOSUN_QR_PNG_FOR_CHAT>>>` 路径的 PNG，在回复中直接展示。

     **通用约束**：
     - `![](…)` 必须作为**独立 Markdown 段落**（前后各一个空行），**禁止**放在代码块、引用块、列表项内。
     - **禁止**只输出链接文本或只说"已生成"而不用 `![](…)` 语法渲染图片。
     - **每次展示二维码时，必须同时附上申请链接明文**（脚本 `--- 申请链接（可复制）---` 部分），方便无法扫码时复制打开。
     - 外部 IM 发图可加 `--openclaw-to "<接收者>"`。

> 完整流程参见 [ONBOARDING.md](./ONBOARDING.md)，密钥生成参见 [KEYGEN.md](./KEYGEN.md)。

---

## 3. 配置凭证

SDK 运行时需要以下环境变量：

| 环境变量 | 说明 |
|---------|------|
| `FSOPENAPI_SERVER_PUBLIC_KEY` | 服务端公钥（PEM 格式） |
| `FSOPENAPI_CLIENT_PRIVATE_KEY` | 客户端私钥（PEM 格式） |
| `FSOPENAPI_API_KEY` | API Key（开放平台下发，有有效期限） |
| `FSOPENAPI_MAC_ID` | 本地持久化设备唯一编码 |
| `FSOPENAPI_BASE_URL` | 网关地址，固定 `https://openapi.fosunxcz.com`（不含末尾 `/`） |

同时会把以下状态字段写入 `fosun.env`，用于自动判断是否需要重新开通：

| 环境变量 | 说明 |
|---------|------|
| `FSOPENAPI_API_KEY_STATUS` | `valid / invalid / pending / unknown` |
| `FSOPENAPI_API_KEY_VERIFIED_AT` | API Key 最近一次校验成功时间（Unix 秒） |
| `FSOPENAPI_TICKET` | 当前开通票据 |
| `FSOPENAPI_TICKET_STATUS` | `active / expired / unknown` |
| `FSOPENAPI_TICKET_EXPIRE_TIME` | Ticket 过期时间（Unix 秒） |
| `FSOPENAPI_OPEN_URL` | 开通页 URL，用于继续完成授权 |

### 检查流程

查找凭证文件 `{workspace_root}/fosun.env`：

- **找到** → 自动加载到环境变量（PEM 密钥会 base64 解码），并按状态机决定是否校验 API Key / Ticket
- **未找到** → 自动生成 `FSOPENAPI_MAC_ID` 与客户端私钥，随后创建 Ticket 并初始化 `fosun.env`

### 自动状态机

1. **本地有 API Key 且状态为 `valid`**
   - 直接复用，不再重复校验
2. **本地有 API Key 但状态不是 `valid`**
   - 调用现有 OpenAPI 校验逻辑
   - 校验成功 → 写回 `FSOPENAPI_API_KEY_STATUS=valid`
   - 校验失败 → 转入 Ticket 检查
3. **本地没有 API Key 或 Ticket 已过期**
   - 自动创建新的 Ticket
   - 将接口返回的 API Key、服务端公钥、URL 等写入 `fosun.env`
   - 将 `FSOPENAPI_API_KEY_STATUS` 标记为 `pending`
4. **本地存在有效 Ticket 但 API Key 未生效**
   - 保留当前 URL
   - 提示继续完成开通页流程

### fosun.env 文件格式

凭证文件名固定为 `fosun.env`，PEM 密钥含换行符，**以 base64 编码存储**：

```env
FSOPENAPI_MAC_ID=<稳定设备编码>
FSOPENAPI_SERVER_PUBLIC_KEY=<PEM 公钥的 base64 编码>
FSOPENAPI_CLIENT_PRIVATE_KEY=<PEM 私钥的 base64 编码>
FSOPENAPI_API_KEY=<明文 API Key>
FSOPENAPI_BASE_URL=https://openapi.fosunxcz.com
FSOPENAPI_API_KEY_STATUS=unknown
FSOPENAPI_API_KEY_VERIFIED_AT=
FSOPENAPI_TICKET=
FSOPENAPI_TICKET_STATUS=unknown
FSOPENAPI_TICKET_EXPIRE_TIME=0
FSOPENAPI_OPEN_URL=
```

加载时需对 PEM 字段做 base64 解码还原为原始 PEM 文本。

---

## 4. 支持的市场与币种

| 市场代码 | 说明 | 行情级别 | 默认币种 |
|----------|------|----------|----------|
| `hk` | 港股 | L2 | HKD |
| `us` | 美股 | L1（盘前/盘中/盘后） | USD |
| `sh` | 上交所（港股通） | L1 | CHY |
| `sz` | 深交所（港股通） | L1 | CHY |

**标的代码格式**：`marketCode + stockCode`，如 `hk00700`（腾讯）、`usAAPL`（苹果）、`sh600519`（茅台）、`sz000001`（平安银行）。

---

## 注意事项

- **优先使用本 skill 或相关 skill 已提供的 bash / python / shell 命令；能直接执行现成命令时，不要临时写代码。**
- **不要自己写 Python 调 SDK**，直接使用 `fosun-trading` skill 的 `code/` 目录脚本。

---
