# Electron CVE 数据库与版本风险

## 概述

Electron 版本直接决定了内嵌的 Chromium 和 Node.js 版本。过期的 Electron 版本可能包含大量已公开的 1-day 漏洞，这是最容易利用的攻击面之一。

---

## 一、版本获取方法

```
方法 1: package.json
  解包 asar 后查看 package.json 中的 "electron" 依赖版本

方法 2: node_modules
  node_modules/electron/package.json 中的 version 字段

方法 3: 运行时（DevTools Console）
  process.versions.electron    → Electron 版本
  process.versions.chrome      → Chromium 版本
  process.versions.node        → Node.js 版本
  process.versions.v8          → V8 版本

方法 4: exe 文件属性
  右键 → 属性 → 详细信息 → 产品版本

方法 5: User-Agent
  Network 面板查看请求的 User-Agent 头
  格式: Chrome/xxx Electron/xxx
```

---

## 二、Electron → Chromium → Node.js 版本映射

| Electron | Chromium | Node.js | 发布日期 | 支持状态 |
|:---------|:---------|:--------|:---------|:---------|
| 37.x | 140 | 22.x | 2025.10 | 当前支持 |
| 36.x | 136 | 22.x | 2025.06 | 当前支持 |
| 35.x | 134 | 22.x | 2025.04 | 当前支持 |
| 34.x | 132 | 22.x | 2025.01 | 已过期 |
| 33.x | 130 | 20.x | 2024.10 | 已过期 |
| 32.x | 128 | 20.x | 2024.08 | 已过期 |
| 31.x | 126 | 20.x | 2024.06 | 已过期 |
| 30.x | 124 | 20.x | 2024.04 | 已过期 |
| 29.x | 122 | 20.x | 2024.02 | 已过期 |
| 28.x | 120 | 18.x | 2023.12 | 已过期 |
| 27.x | 118 | 18.x | 2023.10 | 已过期 |
| 26.x | 116 | 18.x | 2023.08 | 已过期 |
| 25.x | 114 | 18.x | 2023.05 | 已过期 |
| 24.x | 112 | 18.x | 2023.04 | 已过期 |
| 23.x | 110 | 18.x | 2023.02 | 已过期 |
| 22.x | 108 | 16.x | 2022.11 | 已过期 |
| 21.x | 106 | 16.x | 2022.09 | 已过期 |
| 20.x | 104 | 16.x | 2022.08 | 已过期 |
| 19.x | 102 | 16.x | 2022.05 | 已过期 |
| 18.x | 100 | 16.x | 2022.03 | 已过期 |
| 17.x | 98 | 16.x | 2022.02 | 已过期 |
| 16.x | 96 | 16.x | 2021.11 | 已过期 |
| 15.x | 94 | 16.x | 2021.09 | 已过期 |
| 14.x | 93 | 14.x | 2021.08 | 已过期 |
| 13.x | 91 | 14.x | 2021.05 | 已过期 |
| 12.x | 89 | 14.x | 2021.03 | 已过期 |
| 11.x | 87 | 12.x | 2020.11 | 已过期 |
| 10.x | 85 | 12.x | 2020.08 | 已过期 |
| 9.x | 83 | 12.x | 2020.05 | 已过期 |
| 8.x | 80 | 12.x | 2020.02 | 已过期 |

**注意**: 截至 2026 年 4 月，当前支持的 Electron 版本为 35.x / 36.x / 37.x。
**完整映射**: https://releases.electronjs.org/

---

## 三、版本风险分级

| Electron 版本范围 | Chromium | 风险等级 | 说明 |
|:-----------------|:---------|:---------|:-----|
| 最新 3 个大版本 | 最新 | **安全** | 在支持范围内，持续接收安全补丁 |
| 落后 4-6 个大版本 | 较新 | **中危** | 已过期但漏洞利用难度较高 |
| 落后 7-12 个大版本 | 100-120 | **高危** | 存在多个已知可利用漏洞 |
| 落后 >12 个大版本 | <100 | **严重** | 大量已知 RCE 和沙箱逃逸 |

---

## 四、Electron 自身安全漏洞

### 4.1 高危 Electron CVE

| CVE | 影响版本 | 类型 | 描述 | 修复版本 |
|:----|:---------|:-----|:-----|:---------|
| CVE-2023-44402 | < 27.1.0 | RCE | ASAR 完整性绕过导致代码执行 | 27.1.0 |
| CVE-2023-39956 | < 26.2.1 | 沙箱逃逸 | WebRequest 重定向导致沙箱绕过 | 26.2.1 |
| CVE-2023-29198 | < 25.8.1 | 沙箱逃逸 | Context Isolation 绕过 | 25.8.1 |
| CVE-2022-36077 | < 21.3.1 | RCE | ASAR 完整性验证绕过 | 21.3.1 |
| CVE-2022-29247 | < 19.0.11 | RCE | 渲染进程代码执行 | 19.0.11 |
| CVE-2022-21718 | < 17.1.0 | 信息泄露 | IPC 消息泄露到错误的渲染进程 | 17.1.0 |
| CVE-2021-39184 | < 15.1.0 | RCE | 沙箱标志被重置 | 15.1.0 |
| CVE-2020-15215 | < 11.0.0 | RCE | 打开的子窗口可逃逸沙箱 | 11.0.0-beta.6 |
| CVE-2020-4076 | < 9.0.0 | RCE | contextIsolation 绕过 | 9.0.0-beta.21 |
| CVE-2020-4075 | < 8.0.0 | 信息泄露 | WebFrame 不遵守 contextIsolation | 8.0.0 |

### 4.2 Electron 安全默认值变更历史

| 版本 | 变更 | 安全影响 |
|:-----|:-----|:---------|
| Electron 5 | `nodeIntegration` 默认改为 `false` | 新应用默认不再有 XSS→RCE |
| Electron 12 | `contextIsolation` 默认改为 `true` | 新应用默认隔离上下文 |
| Electron 20 | `sandbox` 默认改为 `true` | 渲染进程默认沙箱化 |
| Electron 22 | `webviewTag` 默认改为 `false` | 禁用 webview 标签 |

**审计要点**: 如果应用基于旧版 Electron 开发，可能显式设置了不安全的默认值（如 `nodeIntegration: true`），即使后来升级了 Electron 版本。

---

## 五、Chromium 高危 CVE（按类型）

### 5.1 V8 引擎 RCE

```
V8 引擎漏洞可通过恶意 JavaScript 触发:
  - 类型混淆 (Type Confusion)
  - 堆溢出 (Heap Overflow)
  - UAF (Use-After-Free)

如果 Electron 应用加载不受信任的网页内容:
  → V8 RCE 可以在渲染进程中执行代码
  → 如果 sandbox: false → 直接获得 Node.js 权限
  → 如果 sandbox: true → 需要沙箱逃逸链

查询: chrome://version 查看 V8 版本
CVE 来源: https://v8.dev/blog
```

### 5.2 沙箱逃逸

```
Chromium 沙箱逃逸漏洞:
  - Mojo IPC 漏洞
  - GPU 进程漏洞
  - 网络服务漏洞

在 Electron 中的影响:
  如果 sandbox: true → 沙箱逃逸 = 突破渲染进程限制
  如果 sandbox: false → 不需要沙箱逃逸

CVE 来源: https://chromereleases.googleblog.com/
```

### 5.3 Chromium 版本风险速查

| Chromium 版本范围 | 大致时间 | 已知高危漏洞数量 | 建议 |
|:-----------------|:---------|:----------------|:-----|
| 136+ | 2025.06+ | 较少 | 关注最新修复 |
| 130-135 | 2024.10-2025.05 | 中等 | 建议升级 |
| 120-129 | 2023.12-2024.09 | 较多 | 应当升级 |
| 110-119 | 2023.02-2023.09 | 多 | 必须升级 |
| 100-109 | 2022.04-2023.01 | 很多 | 严重风险 |
| 90-99 | 2021.04-2022.03 | 大量 | 极其危险 |
| <90 | 2021.03 之前 | 大量 | 极其危险 |

**⚠️ 注意: 版本风险不等于漏洞。报告中应将版本信息放在"供应链风险"章节，给出升级建议。不要将版本落后本身作为严重/高危漏洞上报，除非你能证明某个具体 CVE 在此应用上下文中有直接可利用路径。**

---

## 六、Node.js 高危 CVE

| CVE | 影响版本 | 类型 | 描述 |
|:----|:---------|:-----|:-----|
| CVE-2024-22019 | Node.js < 21.6.1 | DoS | HTTP 请求走私 |
| CVE-2024-21896 | Node.js < 21.6.1 | 路径穿越 | path.resolve() 路径穿越 |
| CVE-2023-44487 | Node.js < 20.8.1 | DoS | HTTP/2 Rapid Reset |
| CVE-2023-32002 | Node.js < 20.5.1 | 权限绕过 | 模块加载策略绕过 |
| CVE-2023-30590 | Node.js < 20.3.1 | 证书验证 | generateKeys 绕过 |

---

## 七、版本审计流程

```
1. 获取版本信息:
   Electron 版本 → Chromium 版本 → Node.js 版本

2. 判断支持状态:
   是否在最新 3 个大版本内？
   是否有未修复的安全补丁？

3. 查询已知 CVE:
   Electron: https://www.electronjs.org/blog/tags/security
   Chromium: https://chromereleases.googleblog.com/
   Node.js: https://nodejs.org/en/blog/vulnerability
   
4. 评估风险:
   [严重] 已过期 + 有已知 RCE CVE
   [高危] 已过期 + 有已知沙箱逃逸
   [中危] 在支持范围但未及时更新
   [低危] 最新版本

5. 检查特殊条件:
   如果 sandbox: false → Chromium RCE 直接获得 Node.js 权限
   如果 nodeIntegration: true → 任何 XSS 都是 RCE
```

---

## 八、产出模板

```markdown
## 版本安全分析

### 版本信息

| 组件 | 当前版本 | 最新版本 | 差距 | 风险 |
|:-----|:---------|:---------|:-----|:-----|
| Electron | XX.X.X | YY.Y.Y | Z 个大版本 | 高/中/低 |
| Chromium | XXX | YYY | | |
| Node.js | XX.X.X | YY.Y.Y | | |
| V8 | XX.X | YY.Y | | |

### 支持状态

| 检查项 | 状态 |
|:-------|:-----|
| 是否在支持范围（最新3个大版本） | 是/否 |
| 安全默认值（nodeIntegration 等） | 安全/不安全 |

### 已知 CVE

| CVE | 组件 | 类型 | 影响 | 可利用性 |
|:----|:-----|:-----|:-----|:---------|
| CVE-XXXX-XXXXX | Electron/Chromium | RCE | 严重 | 已验证/理论可行 |

### 修复建议

1. 升级 Electron 到 XX.X.X 或更高版本
2. [具体建议]
```
