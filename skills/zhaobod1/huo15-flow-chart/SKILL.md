---
name: huo15-flow-chart
displayName: 火一五流程图技能
description: 规范 + 时尚的流程图、泳道图、系统架构图、C4 架构图、时序图、状态图、ER 图、甘特图生成。输入 YAML/JSON 规格或直接 Mermaid/PlantUML/DOT 源码，输出 SVG/PNG/PDF；内置 10 种风格（modern / classic / dark / xiaohongshu / ocean / forest / sunset / minimal / pastel / github）。触发词：流程图、泳道图、时序图、状态图、ER 图、系统架构图、C4 图、画流程图、生成流程图。
version: 1.1.0
aliases:
  - 火一五流程图
  - 火一五流程图技能
  - 流程图
  - 流程图生成
  - 画流程图
  - 泳道图
  - 时序图
  - 状态图
  - 甘特图
  - ER图
  - 架构图
  - 系统架构图
  - C4 架构图
  - flowchart
  - flow-chart
  - diagram
  - mermaid
dependencies:
  python-packages:
    - pyyaml
  external:
    - name: "@mermaid-js/mermaid-cli"
      install: "npm i -g @mermaid-js/mermaid-cli"
      notes: "渲染 Mermaid 时用"
    - name: plantuml
      install: "brew install plantuml"
      notes: "只在 type=swimlane 真·泳道图时用"
    - name: graphviz
      install: "brew install graphviz"
      notes: "复杂网络拓扑可选"
---

# 火一五流程图技能 v1.0

> 规范 + 时尚的流程图 / 架构图 / 泳道图 / 时序图 / 状态图生成器 — 青岛火一五信息科技有限公司

---

## 一、核心能力

1. **十三种图表** —
   | type                 | 用途                               | 渲染引擎 |
   |---------------------|-----------------------------------|---------|
   | `flowchart`          | 普通流程图                         | Mermaid |
   | `architecture`       | 系统架构图（分层 + 分组）           | Mermaid |
   | `swimlane`           | 真·泳道图（PlantUML `\|lane\|`）    | PlantUML |
   | `swimlane_mermaid`   | 泳道风格（不需要 Java）             | Mermaid |
   | `sequence`           | 时序图                             | Mermaid / PlantUML |
   | `state`              | 状态图                             | Mermaid |
   | `gantt`              | 甘特图                             | Mermaid |
   | `er`                 | ER 图                              | Mermaid |
   | `class`              | UML 类图                           | Mermaid |
   | `journey`            | 用户旅程                           | Mermaid |
   | `pie`                | 饼图                               | Mermaid |
   | `c4_context`         | C4 上下文图（L1）                   | Mermaid |
   | `c4_container`       | C4 容器图（L2）                     | Mermaid |

2. **十种风格** —
   | key | 名称 | 色调 | 适用场景 | 中文别名 |
   |------|-----|------|---------|---------|
   | `modern`      | 现代商务   | 深蓝灰 + 橙 | 日常文档、PPT | 现代、商务 |
   | `classic`     | 经典稳重   | 蓝紫 + 杏黄 | 正式汇报、咨询 | 经典、稳重 |
   | `dark`        | 暗色霓虹   | 深底 + 青粉 | 演示大屏、技术分享 | 暗色、黑色、霓虹 |
   | `xiaohongshu` | 小红书暖奶油 | 红 + 米白   | 小红书封面、种草图 | 小红书、奶油、xhs |
   | `ocean`       | 海洋蓝     | 天蓝 + 橙 | SaaS 产品、技术架构 | 海洋、蓝、蓝色 |
   | `forest`      | 森林绿     | 墨绿 + 琥珀 | 环保、农业、健康 | 森林、绿、自然 |
   | `sunset`      | 夕阳暖橙   | 赤橙 + 青 | 运营活动、温暖叙事 | 夕阳、暖橙、橙 |
   | `minimal`     | 极简素雅   | 纯黑白灰 | 学术论文、出版物 | 极简、素雅、学术、论文、黑白 |
   | `pastel`      | 马卡龙粉嫩 | 粉蓝紫 | 儿童教育、女性向 | 马卡龙、粉嫩、粉、儿童 |
   | `github`      | 极客 GitHub | 黑白 + 强调蓝绿 | 开源文档、README | 极客、程序员、gh |

3. **三种输入** —
   - **YAML/JSON 规格**（推荐，可读性好）
   - **Mermaid 源码**（`.mmd`）直接传入，加 style 注入
   - **PlantUML 源码**（`.puml`）直接传入

4. **四种输出** — `.svg` / `.png` / `.pdf`（调渲染器）；`.mmd` / `.puml` / `.dot`（只导出源码，自己复制到在线编辑器）。

5. **中文友好** — 内置 PingFang SC / Microsoft YaHei / Noto Sans CJK 字体栈。

---

## 二、快速开始

### 2.1 准备渲染器（任选）

```bash
# 方案 A：Mermaid（推荐，覆盖 90% 场景）
npm i -g @mermaid-js/mermaid-cli

# 方案 B：PlantUML（泳道图必须）
brew install plantuml        # macOS
# apt install plantuml       # Debian/Ubuntu

# 方案 C：Graphviz（网络拓扑可选）
brew install graphviz

# Python 依赖
pip install pyyaml
```

### 2.2 最短上手

```bash
# 从 YAML 规格生成系统架构图 PNG
python3 scripts/create-flow-chart.py \
  -i examples/architecture.yaml \
  -o /tmp/arch.png \
  --style modern

# 泳道图（真·PlantUML）
python3 scripts/create-flow-chart.py \
  -i examples/swimlane.yaml \
  -o /tmp/lane.svg

# Mermaid 源码直接渲染
python3 scripts/create-flow-chart.py \
  -i flow.mmd \
  -o /tmp/flow.pdf \
  --style xiaohongshu

# 同时导出多种格式
python3 scripts/create-flow-chart.py \
  -i examples/gantt.yaml \
  -o /tmp/gantt.png \
  --also svg,pdf,mmd

# 只看生成的源码（不渲染，用于在线编辑器）
python3 scripts/create-flow-chart.py \
  -i examples/c4_context.yaml \
  -o /dev/null --dump-source
```

---

## 三、YAML 规格速查

### 3.1 流程图 `flowchart`

```yaml
type: flowchart
title: 用户下单流程
direction: TB          # TB | LR | BT | RL

nodes:
  - { id: start, label: 开始, shape: stadium }
  - { id: check, label: 是否有商品?, shape: diamond }
  - { id: pay,   label: 结算付款 }

edges:
  - { from: start, to: check }
  - { from: check, to: pay, label: 是 }
```

**形状一览**：`rect`（默认）/ `round` / `stadium` / `diamond`（菱形判断）/ `hexagon` / `circle` / `cylinder`（数据库）/ `subroutine` / `parallelogram` / `trapezoid`。

**边类型（`kind`）**：`solid`（默认实线）/ `dashed` / `thick` / `dotted` / `bidir`（双向）。

### 3.2 系统架构图 `architecture`

用 `groups` 分层 + `nodes.group` 归组：

```yaml
type: architecture
title: 火一五 SaaS 系统架构
groups:
  - { id: frontend, label: 前端层,  children: [web, mobile] }
  - { id: backend,  label: 业务层,  children: [svc_user, svc_order] }
  - { id: data,     label: 数据层,  children: [pg, redis] }
nodes:
  - { id: web, label: Web 门户 }
  - { id: pg,  label: PostgreSQL, shape: cylinder }
  # ...
edges:
  - [web, svc_user]
  - [svc_user, pg]
```

### 3.3 泳道图 `swimlane`（真·PlantUML）

```yaml
type: swimlane
title: 采购审批流程
lanes:
  - name: 申请人
    steps:
      - { id: A1, label: 填写采购申请 }
      - { id: A2, label: 提交审批 }
  - name: 部门经理
    steps:
      - { id: B1, label: 初审 }
edges:
  - [A1, A2]
  - [A2, B1]
```

> 需要 `plantuml` 命令；如无 Java 环境可用 `type: swimlane_mermaid` 替代。

### 3.4 时序图 `sequence`

```yaml
type: sequence
title: 用户登录
auto_number: true
nodes:
  - { id: U,  label: 用户,   shape: actor }
  - { id: FE, label: 前端 }
  - { id: BE, label: 后端 }
edges:
  - { from: U,  to: FE, label: 点击登录 }
  - { from: FE, to: BE, label: POST /login }
  - { from: BE, to: FE, label: JWT token, kind: dashed }
notes:
  - { position: over, over: BE, text: "首次登录自动建账" }
```

### 3.5 状态图 `state`

```yaml
type: state
title: 订单状态机
direction: LR
nodes:
  - { id: Pending, label: 待付款 }
  - { id: Paid,    label: 已付款 }
edges:
  - { from: "[*]", to: Pending, label: 下单 }
  - { from: Pending, to: Paid, label: 付款 }
```

### 3.6 甘特图 `gantt`

```yaml
type: gantt
title: Q2 路线图
dateFormat: YYYY-MM-DD
axisFormat: "%m-%d"
sections:
  - name: 基建
    tasks:
      - { name: 服务器扩容, id: i1, status: done,   start: 2026-04-01, duration: 5d }
      - { name: 监控升级,   id: i2, status: active, start: 2026-04-06, duration: 10d }
```

状态值：`done` / `active` / `crit`（关键路径红）/ `milestone`（里程碑）/ 留空即未开始。

### 3.7 C4 架构图 `c4_context` / `c4_container`

```yaml
type: c4_context
title: 火一五 SaaS 上下文图
nodes:
  - { id: customer, label: 企业客户\n使用 SaaS 的企业,  shape: person }
  - { id: huo15,    label: 火一五 SaaS\n企业数字化平台,  shape: system }
  - { id: wecom,    label: 企业微信\nIM,               shape: system_ext }
edges:
  - { from: customer, to: huo15, label: 使用 }
  - { from: huo15,    to: wecom, label: OAuth }
```

C4 shape：`person` / `person_ext` / `system` / `system_ext` / `container` / `container_db`（数据库）/ `component`。

### 3.8 其他

- `er` — ER 图，label 用 `\n` 分隔字段
- `class` — UML 类图，edge kind 支持 `extends` / `implements` / `composition` / `aggregation` / `dependency` / `association`
- `journey` — 用户旅程，用 `sections[].tasks[]`，每个 task 有 score (1-5) 和 actors
- `pie` — 饼图，用 `items` 数组

---

## 四、Python API

```python
import sys; sys.path.insert(0, 'scripts')

from flowchart_core import parse, to_mermaid, to_plantuml
from flowchart_render import render
from styles import get_style, to_mermaid_init_directive

fc = parse('spec.yaml')
style = get_style('xiaohongshu')
code = to_mermaid(fc, to_mermaid_init_directive(style))
render(code, '/tmp/out.svg', engine='mermaid')
```

主要接口：

| 函数                              | 说明 |
|---------------------------------|------|
| `parse(path_or_text, hint='auto')` | YAML/JSON/Mermaid/PlantUML/DOT → FlowChart |
| `to_mermaid(fc, init_directive)`   | → Mermaid 源码 |
| `to_plantuml(fc, skin)`            | → PlantUML 源码（只支持 swimlane/sequence）|
| `to_dot(fc, style)`                | → Graphviz DOT |
| `render(source, out, engine)`      | 调用 mmdc/plantuml/dot 渲染 |
| `get_style(key)`                   | 获取 Style 对象（中文别名也能识别）|
| `to_mermaid_init_directive(style)` | 返回 `%%{init: ...}%%` 行 |
| `to_plantuml_skinparam(style)`     | 返回 PlantUML skinparam |

---

## 五、与其他技能的边界

| 需求 | 用哪个技能 |
|------|----------|
| 自由层级的思维导图，要导出 XMind | **huo15-mind-map** |
| 流程图 / 架构图 / 泳道图 / 时序图 | **huo15-flow-chart**（本技能）|
| 工程制图 / 原型图 | 不在范围内，建议 drawio / Figma |
| 数据仪表盘 | 用图表库（Chart.js / ECharts / matplotlib） |

---

## 六、触发词

- 流程图 / 画流程图 / 生成流程图 / 做一张流程图
- 泳道图 / 跨职能流程图 / swim lane
- 系统架构图 / 架构图 / C4 图 / C4 上下文 / C4 容器
- 时序图 / 序列图 / sequence diagram
- 状态图 / 状态机 / state diagram
- ER 图 / 实体关系图
- 甘特图 / gantt
- Mermaid / PlantUML

---

## 七、版本历史

- **v1.1.0（当前）** — 扩展 6 种风格。
  - 新增：`ocean`（海洋蓝）/ `forest`（森林绿）/ `sunset`（夕阳暖橙）/ `minimal`（极简素雅）/ `pastel`（马卡龙粉嫩）/ `github`（极客 GitHub）
  - 更完善的中文别名映射：海洋/森林/夕阳/极简/马卡龙/极客 等均可识别

- **v1.0.0** — 首版。
  - 支持 13 种图表（flowchart / architecture / swimlane / swimlane_mermaid / sequence / state / gantt / er / class / journey / pie / c4_context / c4_container）
  - 3 种输入（YAML/JSON、Mermaid、PlantUML）、6 种输出（svg/png/pdf/mmd/puml/dot）
  - 4 种风格：modern / classic / dark / xiaohongshu（带中文别名）
  - 渲染器自动探测：mmdc > npx > docker（Mermaid）；plantuml > java+jar > docker（PlantUML）；dot（Graphviz）

---

**技术支持：** 青岛火一五信息科技有限公司
