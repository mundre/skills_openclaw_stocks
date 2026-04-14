# ClawHub 可疑扫描处理手册

## 常见命中原因

### 1. 同一个文件里同时有环境变量读取和网络发送

典型形式：

- `process.env` + `fetch(`
- `os.getenv(...)` + `requests.post(...)`

这种组合很容易被当成潜在外传行为。

### 2. 同一个文件里同时有本地文件读取和网络发送

典型形式：

- `fs.readFileSync(...)` + `fetch(...)`
- `open(...)` + `requests.post(...)`

### 3. 代码或文档提到私有配置源

高风险关键词：

- `~/.openclaw/secrets.json`
- 私有 `config.json`
- 自动读取本地 secrets store

## 优先修复策略

### 拆文件

把下面几类逻辑拆开：

- 配置读取
- 网络请求
- 主流程

目标不是“骗过扫描器”，而是让行为边界更清楚。

### 收窄读取范围

明确只允许读取白名单环境变量，例如：

- `HUMAN_LIKE_MEM_API_KEY`
- `HUMAN_LIKE_MEM_BASE_URL`

不要遍历整个 `process.env`。

### 前置披露

在 `SKILL.md` / `README` / `SECURITY.md` 中写清楚：

- 什么时候会联网
- 会发送哪些字段
- 不会读取哪些本地文件

## 如何判断是否真的修好

不要只看页面顶部标签，要同时验证：

- 页面版本已经更新
- `clawhub inspect <slug>` 指向最新版本
- 页面内嵌数据里的 `staticScan.status`
- `llmAnalysis.status` / `verdict`

如果已经确认最新版本依然 `suspicious` / `flagged`：

- 不要继续重复 `inspect + 打开页面`
- 先挑一个最可能命中的结构去改
- 改完后递增版本、重新发布、再复核

也就是说，检查只负责定位，不负责无限循环。

## 经验结论

如果最新页面内嵌数据已经是：

- `staticScan.status = clean`
- `summary = "No suspicious patterns detected."`
- `OpenClaw = Benign`

那就说明本次修复已经生效，即使某些缓存 UI 还没完全刷新。
