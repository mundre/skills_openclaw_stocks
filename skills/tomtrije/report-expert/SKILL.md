---
name: report-expert
description: "生成 HTML 报告页面并部署到 Cloudflare Pages 站点。涵盖设计系统、页面结构、索引管理、iframe 内嵌查看、自动部署全流程。触发词：写报告、发布报告、部署报告、生成报告页面、report publisher、报告专家、升级报告专家、更新报告技能、发布技能升级。"
---

# 报告专家

将调研内容生成符合设计规范的 HTML 报告页面，支持两种内容类型：**报告页面**（同站部署）和**外部页面**（独立部署，iframe 内嵌查看）。

---

## 技能版本管理

所有远程地址均从 `manifest.json` 的 `repository` 字段动态获取，**不硬编码任何绝对 URL**。

### 安装方式

技能支持两种安装渠道：

| 渠道 | 安装命令 | 特点 |
|------|---------|------|
| **ClawHub** | `clawhub install report-expert` | 自动管理版本，安全扫描，推荐 | |
| **CF Pages** | 将 manifest.json 地址发送给 Agent | 包含 upgrade.py 自更新脚本 |

### 拉取升级（用户指令触发）

当用户说「升级报告专家」「更新报告技能」「检查技能更新」时，根据安装方式选择升级命令：

**ClawHub 安装的技能：**
```bash
clawhub update report-expert
```

**CF Pages 安装的技能：**
> **安全提示：** 升级会从 `manifest.repository` 指定的远端下载文件并覆盖本地技能文件（含 SHA256 校验）。请确认你信任该远端来源。

```bash
SKILL_DIR="<技能实际目录路径>"
python3 "${SKILL_DIR}/upgrade.py"
```

> **注意：** `upgrade.py` 仅随 CF Pages 渠道分发，ClawHub 渠道通过 `clawhub update` 管理，不包含该文件。
```

### 发布升级（修改技能后触发）

当用户说「发布技能升级」「发布报告专家」「提交技能更新」时，执行发布流程。

> **安全提示：** 发布会将技能文件部署到 Cloudflare Pages，需要 `CLOUDFLARE_API_TOKEN`。请确认 token 权限范围合理（仅需 Pages 编辑权限）。

```bash
SKILL_DIR="<技能实际目录路径>"

SKILL_DIR="$SKILL_DIR" python3 << 'PYEOF'
import json, hashlib, os, sys
from datetime import date

skill_dir = os.environ.get("SKILL_DIR", os.path.dirname(os.path.abspath(__file__)))
manifest_path = os.path.join(skill_dir, "manifest.json")

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# 1. 版本递增
old_ver = manifest.get("version", "0.0.0")
parts = old_ver.lstrip("v").split(".")
parts[-1] = str(int(parts[-1]) + 1)
new_ver = ".".join(parts)
manifest["version"] = new_ver
manifest["updated"] = date.today().isoformat()

# 2. 远程基础地址（从 repository 字段读取）
repo = manifest.get("repository", "").rstrip("/")

# 3. 重算所有文件哈希
for root, dirs, fnames in os.walk(skill_dir):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
    for fname in fnames:
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, skill_dir)
        if rel == "manifest.json":
            continue
        with open(fpath, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        sz = os.path.getsize(fpath)
        if rel not in manifest.get("files", {}):
            manifest.setdefault("files", {})[rel] = {}
        manifest["files"][rel]["sha256"] = sha
        manifest["files"][rel]["size"] = sz
        # url 保持相对路径
        manifest["files"][rel]["url"] = rel

# 4. 清理已删除的文件
existing = set()
for root, dirs, fnames in os.walk(skill_dir):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
    for fname in fnames:
        rel = os.path.relpath(os.path.join(root, fname), skill_dir)
        if rel != "manifest.json":
            existing.add(rel)
for rel in list(manifest.get("files", {}).keys()):
    if rel not in existing:
        del manifest["files"][rel]

# 5. 写入 manifest
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# 5.5. 同步版本号到技能介绍页面
index_html = os.path.join(skill_dir, "index.html")
if os.path.exists(index_html):
    ih = open(index_html, "r", encoding="utf-8").read()
    # 替换版本号标记（匹配 v数字.数字.数字 格式）
    import re
    ih = re.sub(r'v\d+\.\d+\.\d+', f'v{new_ver}', ih, count=1)
    open(index_html, "w", encoding="utf-8").write(ih)
    print(f"📄 介绍页版本已同步: v{new_ver}")

print(f"✅ 版本: v{old_ver} → v{new_ver}")
print(f"📦 文件: {len(manifest['files'])} 个")
for rel, meta in manifest["files"].items():
    print(f"  {meta['sha256'][:12]}...  {meta['size']:>6}B  {rel}")
PYEOF

# 6. 发布到预览环境（自动升级版本号 + 同步所有文件版本）
SKILL_DIR="$SKILL_DIR"
python3 "${SKILL_DIR}/deploy.py" publish

# 7. 验证预览内容（检查输出的预览地址）
#    - manifest.json 版本号正确
#    - index.html 版本号正确
#    - SKILL.md 版本号正确

# 8. 验证无误后，发布到生产环境
python3 "${SKILL_DIR}/deploy.py" publish-prod
```

### 验证发布

发布后执行以下命令确认：

```bash
SKILL_DIR="<技能实际目录路径>"
REPO=$(python3 -c "import json; print(json.load(open('${SKILL_DIR}/manifest.json'))['repository'])")

# 检查 manifest 可达
curl -sL "${REPO}/manifest.json" | python3 -c "import json,sys; m=json.load(sys.stdin); print(f'v{m[\"version\"]} — {len(m[\"files\"])} files')"

# 检查各文件可达
curl -sI "${REPO}/SKILL.md" | head -1
curl -sI "${REPO}/deploy.py" | head -1
```

---

## 前置配置（使用者必须完成）

### 四组部署目标配置

在 TOOLS.md 中按需配置：

```markdown
### Report Expert 技能配置

**部署模式：** local
- `REPORT_DEPLOY_MODE=local`
- `REPORT_LOCAL_DIR=/path/to/site`  # 本地站点根目录
- `REPORT_LOCAL_URL=https://example.com/claw`  # 站点访问地址
- `REPORT_SITE_NAME=传琪`

# 远程报告部署（可选）
- `REPORT_CF_PROJECT=reports-site`  # 报告站 CF Pages 项目名

# 技能 CF 发布（可选）
- `SKILL_CF_PROJECT=report-expert-skill`  # 技能站 CF Pages 项目名

# 技能 ClawHub 发布（可选）
- `SKILL_CLAWHUB_SLUG=report-expert`
- `SKILL_CLAWHUB_NAME=报告专家`
```

### 共用凭据

- `CLOUDFLARE_API_TOKEN` — 环境变量或 TOOLS.md，一个 token 管所有 CF 操作
  - 建议使用最小权限 token（仅需 Cloudflare Pages 编辑权限）
  - 建议使用环境变量方式配置，不要提交到公共仓库

## 两种内容类型

### 1. 报告页面（同站部署）

完整的调研报告、教程等，部署在报告主站的子目录下。

**流程：**
1. 生成 HTML body 内容（只需 `<style>` + 内容 HTML，不需要完整页面）
2. 运行 `python3 deploy.py deploy <category> <html_file> --title "标题" --desc "描述"`
3. 脚本自动：套模板、注入样式、添加页脚、更新索引
4. 运行 wrangler 部署到 Cloudflare Pages

### 2. 外部页面（独立部署 + iframe 内嵌）

游戏、工具、测试等独立页面，部署到独立的 Cloudflare Pages 项目，同时在报告主站索引中展示。

**流程：**
1. 生成完整的独立 HTML 页面
2. 创建独立的 Cloudflare Pages 项目并部署
3. 运行 `python3 deploy.py add <filename> --title "标题" --desc "描述" --category other --url "https://xxx.pages.dev/"`
4. 更新 dist/index.json 并部署报告主站

**首页行为：**
- 报告页面：正常跳转到报告详情页
- 外部页面：在 iframe 中内嵌打开，保留页头、侧边栏和页脚导航

## 分类体系

### 分类命名规范

1. **双标识格式**：创建报告或新建分类时，必须使用 `英文标识 + 中文名称` 的双标识体系
2. **路径使用英文标识**：文件存储路径、URL 路径、索引过滤字段均使用英文标识（如 `research`、`analysis`）
3. **展示使用中文名称**：索引页面、用户界面展示时使用中文名称（如「深度研究」「数据分析」）
4. **逻辑执行用英文标识**：代码中的分类判断、过滤、路由等逻辑全部基于英文标识

### 现有分类

| key | 名称 | 说明 |
|-----|------|------|
| research | 深度研究 | 系统性调研与分析 |
| analysis | 数据分析 | 数据驱动的分析洞察 |
| summary | 内容摘要 | 信息整理与要点提炼 |
| comparison | 对比评测 | 产品、方案或工具的横向对比 |
| tutorial | 教程指南 | 操作指南与最佳实践 |
| other | 其他 | 游戏、工具、测试等外部页面 |

## CLI 命令

```bash
# 报告部署
python3 deploy.py deploy <category> <file> [--title T] [--desc D]  # 自动选本地/远程
python3 deploy.py local-deploy <category> <file> [--title T] [--desc D]
python3 deploy.py remote-deploy <category> <file> [--title T] [--desc D]

# 技能发布
python3 deploy.py skill-cf-publish          # 发布技能到 CF Pages 预览
python3 deploy.py skill-cf-publish-prod     # 发布技能到 CF Pages 生产
python3 deploy.py skill-clawhub-publish [--changelog "xxx"]  # 发布到 ClawHub

# 索引和备份
python3 deploy.py add <filename> --title T --desc D --category C [--url U]
python3 deploy.py rebuild_index
python3 deploy.py scan [--ai]
python3 deploy.py update
python3 deploy.py backup [list|restore <name>]
```

## 索引管理操作规范

当用户从索引页管理模式生成指令后，执行对应的索引管理操作：

### 移动分类
- **只修改 index.json 中的 category 字段，不要移动实际文件**
- 修改后必须执行 `python3 deploy.py update` 部署更新

```python
# 修改 category 示例
import json
f = 'dist/index.json'
d = json.load(open(f))
for p in d['pages']:
    if p['filename'] == 'xxx.html':
        p['category'] = 'target-category'
json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
```

### 删除页面
- 删除源文件（`REPORT_LOCAL_DIR` 下对应路径）和 dist 中的副本
- 执行 `python3 deploy.py rebuild_index` 重建索引并部署

### 操作后必须部署
- **移动分类** → `python3 deploy.py update`
- **删除页面** → `python3 deploy.py rebuild_index`
- 不部署 = 没生效

---

## 部署前检查清单

每份报告部署前必须逐项确认：

### 🔍 成果物 Review（部署前必须执行）

**生成 HTML 后、部署前，必须对产出物执行自动化 review：**

```bash
# 1. div 闭合校验（必须完全相等）
OPEN=$(grep -c '<div' FILE); CLOSE=$(grep -c '</div>' FILE); echo "div: $OPEN open / $CLOSE close"; [ "$OPEN" = "$CLOSE" ] && echo "✅ PASS" || echo "❌ FAIL"

# 2. 检查重复嵌套 report-wrap
PATTERN=$(grep -c 'class="report-wrap"' FILE); [ "$PATTERN" -le 1 ] && echo "✅ PASS" || echo "❌ FAIL: $PATTERN report-wrap found"

# 3. 检查重复 page-body
PATTERN=$(grep -c 'class="page-body"' FILE); [ "$PATTERN" -le 1 ] && echo "✅ PASS" || echo "❌ FAIL: $PATTERN page-body found"

# 4. 检查重复 scroll-progress / toc-sidebar / toc-toggle
for CLS in scroll-progress toc-sidebar toc-toggle; do PATTERN=$(grep -c "$CLS" FILE); [ "$PATTERN" -le 1 ] && echo "✅ $CLS" || echo "❌ FAIL: $CLS x$PATTERN"; done

# 5. 检查是否有手写 footer
grep -q 'class="page-footer"' FILE && echo "❌ FAIL: 手写 footer detected" || echo "✅ PASS"

# 6. 检查标题是否为中文（标题应在 h1.report-header__title 中）
TITLE=$(grep -o 'report-header__title">[^<]*<' FILE | sed 's/.*>\(.*\)</.*/\1/')
echo "标题: $TITLE"

# 7. 检查深色背景
grep -qP 'background[^;]*#0[0-9a-f]|background[^;]*#1[0-9a-f]' FILE && echo "❌ FAIL: 深色背景" || echo "✅ PASS"

# 8. 检查 page-body 中是否有 script 标签
# （允许 body 底部的 script，但 page-body 内容区不应有）
```

**review 失败时必须修复后再部署，不可跳过此步骤。**

### 部署检查项

- [ ] 使用 base.css + main.js（引用 `../styles/base.css` 和 `../scripts/main.js`）
- [ ] 包含 toc-sidebar + toc-toggle + scroll-progress 元素
- [ ] TOC 标题带 SVG 列表图标，关闭按钮用 SVG X 图标，展开按钮用 SVG 汉堡图标
- [ ] **页头页脚由 main.js 统一注入，HTML 中不要手写 `<footer>` 或面包屑链接**
- [ ] report-header__breadcrumb 只需写结构（a + span），链接和 SVG 图标由 JS 自动填充
- [ ] 分类标签带 SVG 图标，日期带 SVG 日历图标
- [ ] 内容包裹在 report-wrap > report-header + page-body 中
- [ ] h2/h3 有 id 属性供大纲跳转（main.js 会自动补 id，但建议模板中直接写上）
- [ ] **不要手写 `<footer class="page-footer">`**，JS 会自动注入统一页脚（logo + 传琪 + 年份）
- [ ] **没有使用任何 emoji 作为图标或 UI 元素**
- [ ] 配色使用 base.css 变量（`var(--c-xxx)`），没有硬编码颜色
- [ ] **禁止在 body 内联样式中使用深色背景（`#0f`/`#1a`/`#111`/`#222` 等深色值）**
- [ ] **禁止 CSS fallback 使用深色值**，如 `var(--c-bg, #0f0f1e)` 必须改为 `var(--c-bg, #f8fafc)` 等亮色值
- [ ] **禁止深色背景配深色文字**，确保背景和文字的对比度足够
- [ ] 卡片/区块用底色+阴影，没有用线框
- [ ] 表格表头用 `--c-elevated` 深色底
- [ ] 表格主体用 `--c-surface` 白色底，偶数行用 `--c-surface-alt`
- [ ] **🔴 强制校验：`<div>` 和 `</div>` 数量必须完全相等**（`grep -c '<div' file && grep -c '</div>' file`），不等则禁止部署。多余的闭合标签会导致页面白屏、样式错乱、内容消失
- [ ] **🔴 强制校验：只允许一套页面框架**（1个 scroll-progress、1个 toc-sidebar、1个 toc-toggle、1个 report-wrap、1个 page-body），重复会导致布局崩溃
- [ ] **🔴 禁止手写 `<footer>`**（第3次强调，子 agent 最容易犯这个错）
- [ ] **🔴 禁止在 page-body 中间插入 `<script>` 标签**，所有图表初始化脚本必须写在 body 底部、main.js 之后

## 模板文件

- `templates/base.css` — 设计系统样式（v6.1 底色层级）
- `templates/index.html` — 首页模板（含 iframe viewer）
- `scripts/main.js` — 交互系统（TOC、滚动进度、渐入动画、图表放大 Lightbox）
- `deploy.py` — CLI 入口（参数解析与命令分发）
- `lib/config.py` — 配置加载、四组部署目标常量、工具函数
- `lib/page.py` — 页面 HTML 生成与部署
- `lib/index.py` — 索引管理（重建/添加/扫描）
- `lib/backup.py` — 备份恢复与页面模板更新
- `lib/local_deploy.py` — 本地报告部署（写入 dist 目录）
- `lib/remote_deploy.py` — 远程报告部署（Cloudflare Pages via wrangler）
- `lib/skill_cf_publish.py` — 技能发布到 CF Pages（预览/生产）
- `lib/skill_clawhub_publish.py` — 技能发布到 ClawHub registry
- `manifest.json` — 版本信息、文件清单、更新日志
- `upgrade.py` — 独立升级脚本（可选，agent 可直接按 SKILL.md 流程执行）


## 安全说明

### 所需环境变量
- `CLOUDFLARE_API_TOKEN` — Cloudflare API Token，远程报告部署 + 技能 CF 发布共用，local 模式无需配置

### 所需外部工具
- `python3` — 运行部署脚本
- `curl` — 升级流程下载远端文件
- `npx` / `wrangler` — 远程发布到 Cloudflare Pages
- `openclaw` — AI 自动分类功能（`--ai` 模式，可选）
- `clawhub` — ClawHub 发布 CLI（`skill-clawhub-publish` 命令）

### ClawHub 发布注意
- **⚠️ 发布前必须排除 `dist/` 和 `backups/` 目录**，否则超过 20MB 限制会失败
- `skill-clawhub-publish` 已内置自动临时移除逻辑，但需确认生效

### 升级安全
- 升级从 `manifest.json` 的 `repository` 字段指定的远端下载文件
- 所有文件经过 SHA256 校验，校验失败会拒绝写入
- **建议：** 仅在信任远端来源时执行升级

### 凭据管理
- 凭据通过环境变量或 TOOLS.md 配置，**不要将 token 提交到公共仓库**
- 建议使用环境变量方式配置 CLOUDFLARE_API_TOKEN
- 建议使用最小权限 token（仅需 Cloudflare Pages 编辑权限）

## 图表与可视化规范

> **图表放大功能**：main.js 已内置图表放大（Lightbox）功能，支持 chart-box、ECharts div、Mermaid 流程图。手机端按钮始终可见。ECharts 弹层会重新创建实例确保正确渲染。

报告页面内置三种图表引擎，按需选用：

### 1. Mermaid — 流程图/架构图/时序图

适用于：系统架构、流程说明、时序关系、状态机等。

```html
<div class="mermaid-wrap"><pre class="mermaid">
flowchart TD
    A["节点A"] --> B["节点B"]
</pre></div>
```

**禁止事项：**
- ❌ 不要在 `mermaid-wrap` 外再包额外的 `div`（如 `arch-diagram`），否则会导致 `</div>` 闭合错乱
- ❌ 不要在 mermaid 代码块前后加多余的闭合标签

**支持类型：** `flowchart`、`sequence`、`class`、`state`、`er`、`gantt`、`pie`、`mindmap`、`timeline`

### 2. ECharts — 数据可视化（推荐）

适用于：柱状图、折线图、饼图、散点图、雷达图、热力图、地图、桑基图等复杂数据可视化。

**HTML 结构（写在 page-body 内容区）：**
```html
<div class="chart-box">
  <div class="chart-box__title">图表标题</div>
  <div class="chart-box__canvas" id="chart-xxx"></div>
  <div class="chart-box__caption">数据来源说明</div>
</div>
```

**初始化脚本（必须写在 body 底部，mermaid 脚本之后）：**
```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  var chart = echarts.init(document.getElementById('chart-xxx'));
  chart.setOption({ /* ... */ });
  window.addEventListener('resize', function() { chart.resize(); });
});
</script>
```

**配色原则：** 使用报告主题色 `#6366f1`（indigo）为主色，辅以 `#8b5cf6`、`#06b6d4`、`#10b981`、`#f59e0b`、`#ef4444` 等柔和色系。避免使用默认亮色。

**尺寸类：**
- 默认高度 360px：`chart-box__canvas`
- 小图 240px：`chart-box__canvas--sm`
- 大图 480px：`chart-box__canvas--lg`

**注意事项：**
- 每个图表的 `id` 必须唯一（建议用 `chart-` 前缀 + 简短描述）
- 始终监听 `resize` 事件确保响应式
- 多个图表可在同一个 DOMContentLoaded 回调中初始化，统一管理 resize

### 3. Chart.js — 轻量图表

适用于：简单的柱状图、折线图、饼图、环形图、面积图。比 ECharts 更轻量。

**HTML 结构（写在 page-body 内容区）：**
```html
<div class="chart-container">
  <canvas id="chart-xxx" height="300"></canvas>
</div>
<p class="chart-caption">图表说明</p>
```

**初始化脚本（必须写在 body 底部，ECharts 脚本之后）：**
```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  new Chart(document.getElementById('chart-xxx'), {
    type: 'bar',
    data: {
      labels: ['A', 'B', 'C'],
      datasets: [{ label: '数据', data: [10, 20, 15], backgroundColor: '#6366f1' }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
});
</script>
```

### 图表优先原则（必须遵守）

生成报告时，凡是能用图表表达的内容，**必须优先使用图表渲染**，而非纯文字或表格堆砌。

**适用场景：**
- 数据对比 → 柱状图/水平柱状图
- 趋势变化 → 折线图/面积图
- 占比分布 → 饼图/环形图
- 多维评估 → 雷达图
- 流程步骤 → 流程图/甘特图
- 系统关系 → 架构图/ER图
- 转化链路 → 漏斗图
- 状态流转 → 状态机图
- 时序交互 → 时序图
- 项目排期 → 甘特图
- 数据散布 → 散点图

**判断标准：** 如果一段内容包含 3 个以上数据点、多步骤流程、多组件关系，就必须用图表呈现。

---

### 选型指南

| 场景 | 推荐引擎 | 理由 |
|------|----------|------|
| 流程/架构/时序 | Mermaid | 声明式语法，适合关系图 |
| 复杂数据可视化 | ECharts | 交互丰富，图表类型全面 |
| 简单统计图表 | Chart.js | 轻量，上手快 |
| 需要动画效果 | ECharts | 内置丰富动画和交互 |
| 多图表混排 | ECharts | 统一风格，配色一致 |

### ⚠️ 常见错误检查清单（每次生成后必须检查）

| # | 问题 | 正确做法 | 后果 |
|---|------|---------|------|
| 1 | Mermaid 用 `<mermaid>` 标签 | 必须用 `<pre class="mermaid">` | 图表不渲染 |
| 2 | `mermaid.initialize()` 在 CDN 加载前调用 | 必须在 `<script src="mermaid.min.js">` 之后调用 | ReferenceError |
| 3 | Mermaid 外层 div 设置了 background 色 | 外层容器不设背景色，让 Mermaid 自身控制渲染 | 底色污染/白块 |
| 4 | ECharts 容器 div 没设高度 | 必须 `style="width:100%;height:400px"` 或用 CSS 设固定高度 | 图表不渲染（高度为0） |
| 5 | ECharts CDN 放在 body 底部但初始化用 DOMContentLoaded | CDN 放 head 同步加载，初始化用 DOMContentLoaded | 加载时序可能出错 |
| 6 | 多个图表用了相同 id | 每个 ECharts 容器 id 必须唯一 | 只渲染第一个 |
| 7 | 子 agent 输出完整 HTML 页面 | 子 agent 只输出 style + body 内容片段 | report-wrap/page-body 双重嵌套 |
| 8 | style 标签残留到 page-body 内 | style 必须在 head 中，body 中不得有 style | 样式异常/白屏 |

### 脚本加载顺序（严格遵守）

```
<head>
  ├── echarts.min.js        ← 同步加载
  └── chart.umd.min.js      ← 同步加载
<body>
  ├── page-body 内容区       ← 只放 HTML 容器，不放 <script>
  ├── main.js
  ├── mermaid.min.js + init
  ├── ECharts 初始化脚本     ← DOMContentLoaded
  └── Chart.js 初始化脚本    ← DOMContentLoaded
</body>
```

**核心规则：** 图表容器 HTML 写在内容区，初始化 `<script>` 写在 body 底部。绝不在 page-body 中间内联图表初始化脚本，否则库尚未加载会导致渲染失败。

---

## 注意事项

- **本技能不包含任何 Cloudflare 凭据**，所有 token/account/project 信息由使用者自行配置
- 首页由 index.html 模板 + index.json 数据驱动，index.html 不应手动编辑
- 如果报告 HTML 是完整页面（含 `<html>` 标签），deploy.py 会自动提取 body 和 style
- deploy.py 会自动给文件名加日期前缀
- **外部页面**需要额外创建独立 Cloudflare Pages 项目并部署，然后用 `add` 命令加入索引
- 首页的 iframe viewer 会自动识别外部 URL（`url` 字段以 http 开头且域名不同），用 iframe 内嵌打开
- 管理模式下支持拖拽页面到侧边栏分类进行移动、勾选删除，操作完成后生成组合指令
- 管理模式下按 ESC 退出管理模式，取消所有未提交的操作
