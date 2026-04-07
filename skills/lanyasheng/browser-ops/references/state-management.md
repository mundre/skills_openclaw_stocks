# Session 与 Cookie 持久化

## 核心设计：统一 Cookie 存储

**登录一次，所有工具复用。**

```
~/.browser-ops/
├── cookie-store/
│   └── unified-state.json       # 统一 Cookie 存储（所有工具共享）
├── profiles/
│   └── shared/                  # agent-browser 共享 profile
└── stagehand-cache/             # Stagehand 元素缓存
```

### 首次登录

```bash
# 方式 1: 用脚本（推荐，弹出浏览器窗口手动登录）
bash scripts/sync-cookies.sh login https://your-company-sso.example.com

# 方式 2: agent-browser 手动登录后导出
agent-browser --headed --profile ~/.browser-ops/profiles/shared open https://your-company-sso.example.com
# （手动登录）
agent-browser state save ~/.browser-ops/cookie-store/unified-state.json
agent-browser close
```

### 各工具如何复用统一 Cookie

#### opencli（天然复用，无需操作）

opencli 通过 Chrome 扩展复用用户 Chrome 的登录态。统一存储对它透明——你在 Chrome 里登录了什么，opencli 就能访问什么。

#### agent-browser

```bash
# 每次启动时加载统一 Cookie
agent-browser state load ~/.browser-ops/cookie-store/unified-state.json
agent-browser open https://internal.example.com  # 直接访问内网

# 或者用 sync 脚本一键导入
bash scripts/sync-cookies.sh import
```

#### Stagehand v3

```typescript
import { Stagehand } from "@browserbasehq/stagehand";
import { chromium } from "@playwright/test";
import { readFileSync } from "fs";

const stagehand = new Stagehand({ env: "LOCAL", model: "anthropic/claude-sonnet-4-5" });
await stagehand.init();

// 通过 CDP 桥接注入统一 Cookie
const browser = await chromium.connectOverCDP(stagehand.connectURL());
const ctx = browser.contexts()[0];
const state = JSON.parse(readFileSync(
  `${process.env.HOME}/.browser-ops/cookie-store/unified-state.json`, "utf8"
));
await ctx.addCookies(state.cookies);

// 现在可以访问需要登录的站点
const page = stagehand.context.pages()[0];
await page.goto("https://internal.example.com");
```

#### Zendriver

```python
import json, asyncio
import zendriver as zd

async def with_unified_cookies(url):
    state = json.load(open(f"{os.environ['HOME']}/.browser-ops/cookie-store/unified-state.json"))
    browser = await zd.start()
    # 先访问目标域名（设置 Cookie 需要同源）
    page = await browser.get(url)
    # 通过 CDP 注入 Cookie
    for c in state["cookies"]:
        await page.send(zd.cdp.network.set_cookie(
            name=c["name"], value=c["value"], domain=c["domain"], path=c.get("path","/")
        ))
    await page.reload()
    return page
```

### Cookie 更新流程

```
登录态过期
  → opencli 报 exit 77 / agent-browser 跳转 SSO
  → 重新登录: bash scripts/sync-cookies.sh login <url>
  → 统一存储自动更新
  → 所有工具自动获得新 Cookie
```

### 管理命令

```bash
# 查看统一存储状态
bash scripts/sync-cookies.sh status

# 从 agent-browser 导出到统一存储
bash scripts/sync-cookies.sh export

# 从统一存储导入到 agent-browser
bash scripts/sync-cookies.sh import
```

## agent-browser 独立 Session（高级）

统一 Cookie 存储覆盖大多数场景。以下是需要独立 session 的高级用法：

### --profile（按站点隔离）

```bash
agent-browser --profile ~/.browser-ops/profiles/twitter open https://twitter.com
```

### --session-name（自动保存/恢复）

```bash
agent-browser --session-name twitter open https://twitter.com
```

> macOS 上可能写空文件 (issue #677)，优先用 `--profile`。

### Cookie 直接操作

```bash
agent-browser cookies                        # 查看
agent-browser cookies set name value         # 设置
agent-browser cookies clear                  # 清除
```

### 状态加密

```bash
export AGENT_BROWSER_ENCRYPTION_KEY=$(openssl rand -hex 32)
agent-browser --session-name bank open https://mybank.com
```

## CDP 直连模式

复用已登录的 Chrome：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.browser-ops/profiles/shared \
  --no-first-run

agent-browser connect 9222
agent-browser open https://internal-site.com
```

> See also: `setup.md` (工具安装), `routing.md` (路由决策), `opencli-usage.md` (opencli Session)
