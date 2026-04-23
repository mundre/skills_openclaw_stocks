"""火一五流程图 — 数据模型 + YAML/JSON 解析 + Mermaid/PlantUML/DOT 代码生成。

支持的图表类型
==============

| 类型                 | 输出 DSL           | 典型用途 |
|--------------------|-------------------|----------|
| flowchart          | Mermaid flowchart  | 普通流程图（含分组 subgraph）|
| swimlane           | PlantUML activity  | 真·泳道图（按角色分栏）|
| swimlane_mermaid   | Mermaid subgraph   | 泳道风格（不需要 Java 时用）|
| sequence           | Mermaid sequence   | 时序图 |
| state              | Mermaid state v2   | 状态图 |
| gantt              | Mermaid gantt      | 甘特图 |
| er                 | Mermaid erDiagram  | ER 图 |
| class              | Mermaid classDiagram | UML 类图 |
| journey            | Mermaid journey    | 用户旅程 |
| pie                | Mermaid pie        | 饼图 |
| architecture       | Mermaid flowchart  | 系统架构（分层 + 分组） |
| c4_context         | Mermaid C4Context  | C4 上下文图 |
| c4_container       | Mermaid C4Container | C4 容器图 |
| mindmap            | Mermaid mindmap    | 简单思维导图（正经的用 huo15-mind-map）|

用 YAML 描述；具体字段按 type 不同而不同，见 SKILL.md 示例。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ----- 通用数据结构 -----


@dataclass
class Node:
    id: str
    label: str = ""
    shape: str = "rect"     # rect/round/stadium/diamond/hexagon/circle/cylinder/cloud/component
    lane: Optional[str] = None
    style_class: Optional[str] = None
    group: Optional[str] = None   # 分组名，用于 subgraph


@dataclass
class Edge:
    src: str
    dst: str
    label: Optional[str] = None
    kind: str = "solid"    # solid / dashed / thick / dotted / bidir
    style_class: Optional[str] = None


@dataclass
class Group:
    id: str
    label: str = ""
    direction: str = ""     # 可选 override
    children: List[str] = field(default_factory=list)


@dataclass
class FlowChart:
    diagram_type: str = "flowchart"
    title: str = ""
    direction: str = "TB"
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    groups: List[Group] = field(default_factory=list)
    lanes: List[str] = field(default_factory=list)
    raw: Optional[str] = None   # 原样 Mermaid/DOT 代码时用
    extras: Dict[str, Any] = field(default_factory=dict)


# ----- 解析 -----


def parse(text_or_path: str, hint: str = "auto") -> FlowChart:
    """顶层解析。按 hint / 扩展名 / 内容特征分发。"""
    import os
    text = text_or_path
    if os.path.exists(text_or_path):
        with open(text_or_path, encoding="utf-8") as f:
            text = f.read()
        if hint == "auto":
            ext = os.path.splitext(text_or_path)[1].lower()
            hint = {".yaml": "yaml", ".yml": "yaml", ".json": "json",
                    ".mmd": "mermaid", ".mermaid": "mermaid",
                    ".puml": "plantuml", ".plantuml": "plantuml",
                    ".dot": "dot", ".gv": "dot"}.get(ext, "auto")
    if hint == "auto":
        stripped = text.lstrip()
        if stripped.startswith("{"):
            hint = "json"
        elif re.match(r"^(flowchart|graph|sequenceDiagram|stateDiagram|gantt|classDiagram|erDiagram|journey|pie|C4Context|C4Container|mindmap|%%\{init)", stripped):
            hint = "mermaid"
        elif stripped.startswith("@startuml") or stripped.startswith("@startsalt"):
            hint = "plantuml"
        elif stripped.startswith("digraph") or stripped.startswith("graph "):
            hint = "dot"
        else:
            hint = "yaml"

    if hint == "json":
        return parse_spec(json.loads(text))
    if hint == "yaml":
        if not HAS_YAML:
            raise RuntimeError("需要 PyYAML（pip install pyyaml）才能解析 YAML 规格文件")
        return parse_spec(yaml.safe_load(text))
    if hint == "mermaid":
        return FlowChart(diagram_type="mermaid_raw", raw=text)
    if hint == "plantuml":
        return FlowChart(diagram_type="plantuml_raw", raw=text)
    if hint == "dot":
        return FlowChart(diagram_type="dot_raw", raw=text)
    raise ValueError(f"未知输入类型：{hint}")


def parse_spec(spec: Dict[str, Any]) -> FlowChart:
    """从 dict（已解析的 YAML/JSON）构造 FlowChart。"""
    fc = FlowChart()
    fc.diagram_type = str(spec.get("type") or spec.get("diagram") or "flowchart").lower()
    fc.title = spec.get("title", "") or ""
    fc.direction = spec.get("direction", "TB")
    fc.extras = {k: v for k, v in spec.items() if k not in {
        "type", "diagram", "title", "direction", "nodes", "edges",
        "groups", "lanes", "relations"
    }}

    # 节点
    for n in spec.get("nodes", []) or []:
        if isinstance(n, str):
            fc.nodes.append(Node(id=n, label=n))
            continue
        fc.nodes.append(Node(
            id=n["id"],
            label=n.get("label", n["id"]),
            shape=n.get("shape", "rect"),
            lane=n.get("lane"),
            style_class=n.get("class"),
            group=n.get("group"),
        ))

    # 边（兼容 relations 别名）
    for e in (spec.get("edges") or spec.get("relations") or []):
        if isinstance(e, list):
            if len(e) == 2:
                fc.edges.append(Edge(src=e[0], dst=e[1]))
            elif len(e) >= 3:
                fc.edges.append(Edge(src=e[0], dst=e[1], label=e[2]))
            continue
        fc.edges.append(Edge(
            src=e.get("from") or e.get("src") or e["source"],
            dst=e.get("to") or e.get("dst") or e["target"],
            label=e.get("label"),
            kind=e.get("kind", "solid"),
            style_class=e.get("class"),
        ))

    # 分组 / 子图
    for g in spec.get("groups", []) or []:
        if isinstance(g, str):
            fc.groups.append(Group(id=g, label=g))
            continue
        fc.groups.append(Group(
            id=g["id"],
            label=g.get("label", g["id"]),
            direction=g.get("direction", ""),
            children=g.get("children", []) or g.get("nodes", []),
        ))

    # 泳道
    if "lanes" in spec:
        lanes = spec["lanes"]
        if lanes and isinstance(lanes[0], dict):
            for lane in lanes:
                fc.lanes.append(lane.get("name") or lane.get("id") or "")
                for step in lane.get("steps") or lane.get("nodes") or []:
                    if isinstance(step, str):
                        fc.nodes.append(Node(id=step, label=step, lane=lane.get("name")))
                    else:
                        fc.nodes.append(Node(
                            id=step["id"],
                            label=step.get("label", step["id"]),
                            shape=step.get("shape", "rect"),
                            lane=lane.get("name"),
                        ))
        else:
            fc.lanes = [str(l) for l in lanes]

    return fc


# ----- Mermaid 生成 -----


_MM_SHAPE = {
    "rect": ("[", "]"),
    "round": ("(", ")"),
    "stadium": ("([", "])"),
    "subroutine": ("[[", "]]"),
    "cylinder": ("[(", ")]"),
    "circle": ("((", "))"),
    "asymmetric": (">", "]"),
    "diamond": ("{", "}"),
    "hexagon": ("{{", "}}"),
    "parallelogram": ("[/", "/]"),
    "trapezoid": ("[/", "\\]"),
}

_MM_EDGE = {
    "solid":  "-->",
    "dashed": "-.->",
    "dotted": "-.->",
    "thick":  "==>",
    "bidir":  "<-->",
    "none":   "---",
}


def _mm_label(label: str) -> str:
    if not label:
        return ""
    # Mermaid 特殊字符需要用引号包起来
    if any(c in label for c in "()[]{}|<>/\\\"\n"):
        safe = label.replace('"', '\\"').replace("\n", "<br/>")
        return f'"{safe}"'
    return label


def _mm_node(n: Node) -> str:
    open_br, close_br = _MM_SHAPE.get(n.shape, _MM_SHAPE["rect"])
    return f"{n.id}{open_br}{_mm_label(n.label or n.id)}{close_br}"


def _mm_edge(e: Edge) -> str:
    arrow = _MM_EDGE.get(e.kind, _MM_EDGE["solid"])
    if e.label:
        label_part = f"|{_mm_label(e.label).strip('"')}|"
        return f"{e.src} {arrow}{label_part} {e.dst}"
    return f"{e.src} {arrow} {e.dst}"


def to_mermaid(fc: FlowChart, style_directive: str = "") -> str:
    """把 FlowChart 转成 Mermaid 代码。style_directive 是 %%{init:...}%% 那行。"""
    if fc.diagram_type == "mermaid_raw":
        # 原样 Mermaid 代码，只在开头插入 style_directive
        raw = fc.raw or ""
        if style_directive and "%%{init" not in raw:
            return style_directive + "\n" + raw
        return raw

    t = fc.diagram_type
    body: List[str]

    if t in ("flowchart", "architecture", "swimlane_mermaid"):
        body = _mm_flowchart(fc)
    elif t == "sequence":
        body = _mm_sequence(fc)
    elif t == "state":
        body = _mm_state(fc)
    elif t == "gantt":
        body = _mm_gantt(fc)
    elif t == "er":
        body = _mm_er(fc)
    elif t == "class":
        body = _mm_class(fc)
    elif t == "journey":
        body = _mm_journey(fc)
    elif t == "pie":
        body = _mm_pie(fc)
    elif t in ("c4_context", "c4context"):
        body = _mm_c4(fc, "Context")
    elif t in ("c4_container", "c4container"):
        body = _mm_c4(fc, "Container")
    elif t == "mindmap":
        body = _mm_mindmap(fc)
    else:
        body = _mm_flowchart(fc)

    # Mermaid 要求 frontmatter（---title---）必须位于文件最前；init 指令跟在其后。
    if body and body[0].startswith("---"):
        first_block = body[0]  # 例如 "---\ntitle: xxx\n---"
        rest = body[1:]
        if style_directive:
            return "\n".join([first_block, style_directive] + rest)
        return "\n".join([first_block] + rest)

    if style_directive:
        return "\n".join([style_directive] + body)
    return "\n".join(body)


def _mm_flowchart(fc: FlowChart) -> List[str]:
    lines = [f"flowchart {fc.direction}"]
    if fc.title:
        lines.insert(0, f"---\ntitle: {fc.title}\n---")
    # 按 group 归类 / 按 lane 归类（swimlane_mermaid 时）
    groups_by_id: Dict[str, Group] = {g.id: g for g in fc.groups}
    grouped_nodes: Dict[str, List[Node]] = {g.id: [] for g in fc.groups}
    ungrouped: List[Node] = []

    for n in fc.nodes:
        key = n.group
        if fc.diagram_type == "swimlane_mermaid":
            key = n.lane
            if key and key not in groups_by_id:
                groups_by_id[key] = Group(id=key, label=key)
                grouped_nodes.setdefault(key, [])
        if key and key in groups_by_id:
            grouped_nodes[key].append(n)
        else:
            ungrouped.append(n)

    # 先输出顶层节点
    for n in ungrouped:
        lines.append("    " + _mm_node(n))

    # 输出 subgraph
    for gid, g in groups_by_id.items():
        direction = g.direction or fc.direction
        title = g.label or gid
        lines.append(f"    subgraph {gid}[\"{title}\"]")
        if direction:
            lines.append(f"        direction {direction}")
        # children 列表里的 + grouped_nodes 里的
        children_ids = set(g.children)
        seen = set()
        for n in grouped_nodes.get(gid, []):
            lines.append("        " + _mm_node(n))
            seen.add(n.id)
        for cid in g.children:
            if cid in seen:
                continue
            # 这个 id 可能是先前声明过的顶层节点
            lines.append(f"        {cid}")
        lines.append("    end")

    # 边
    for e in fc.edges:
        lines.append("    " + _mm_edge(e))

    # classDef / class
    classes = {n.style_class for n in fc.nodes if n.style_class}
    for cls in sorted(c for c in classes if c):
        lines.append(f"    classDef {cls} fill:#f9f9f9,stroke:#999,stroke-width:1px")
    for n in fc.nodes:
        if n.style_class:
            lines.append(f"    class {n.id} {n.style_class}")

    return lines


def _mm_sequence(fc: FlowChart) -> List[str]:
    lines = ["sequenceDiagram"]
    if fc.title:
        lines.append(f"    title {fc.title}")
    # 节点看作 actor / participant
    for n in fc.nodes:
        role = "actor" if n.shape == "actor" else "participant"
        lines.append(f"    {role} {n.id} as {n.label or n.id}")
    for e in fc.edges:
        arrow = "->>" if e.kind != "dashed" else "-->>"
        lbl = (e.label or "").replace("\n", " ")
        lines.append(f"    {e.src}{arrow}{e.dst}: {lbl}")
    # extras 支持 notes/auto_number
    if fc.extras.get("auto_number"):
        lines.insert(1, "    autonumber")
    for note in fc.extras.get("notes", []) or []:
        pos = note.get("position", "over")
        over = note.get("over") or note.get("participant", "")
        txt = (note.get("text", "") or "").replace("\n", "<br/>")
        lines.append(f"    Note {pos} {over}: {txt}")
    return lines


def _mm_state(fc: FlowChart) -> List[str]:
    lines = ["stateDiagram-v2"]
    if fc.title:
        lines.insert(0, f"---\ntitle: {fc.title}\n---")
    if fc.direction:
        lines.append(f"    direction {fc.direction}")
    for n in fc.nodes:
        if n.label and n.label != n.id:
            lines.append(f"    {n.id} : {n.label}")
    for e in fc.edges:
        lbl = f" : {e.label}" if e.label else ""
        lines.append(f"    {e.src} --> {e.dst}{lbl}")
    return lines


def _mm_gantt(fc: FlowChart) -> List[str]:
    lines = ["gantt"]
    if fc.title:
        lines.append(f"    title {fc.title}")
    lines.append(f"    dateFormat {fc.extras.get('dateFormat', 'YYYY-MM-DD')}")
    if "axisFormat" in fc.extras:
        lines.append(f"    axisFormat {fc.extras['axisFormat']}")
    # sections / tasks
    sections = fc.extras.get("sections") or []
    if sections:
        for sec in sections:
            lines.append(f"    section {sec.get('name', '')}")
            for task in sec.get("tasks", []):
                _gantt_task(lines, task)
    else:
        for task in fc.extras.get("tasks", []) or []:
            _gantt_task(lines, task)
    return lines


def _gantt_task(lines: List[str], task: Dict[str, Any]) -> None:
    def _s(v: Any) -> str:
        if v is None:
            return ""
        if hasattr(v, "strftime"):  # datetime.date / datetime
            return v.strftime("%Y-%m-%d")
        return str(v)
    name = _s(task.get("name", ""))
    tid = _s(task.get("id", ""))
    status = _s(task.get("status", ""))
    start = _s(task.get("start", ""))
    dur = _s(task.get("duration", task.get("end", "")))
    parts = [p for p in [status, tid, start, dur] if p]
    lines.append(f"    {name} :{', '.join(parts)}")


def _mm_er(fc: FlowChart) -> List[str]:
    lines = ["erDiagram"]
    if fc.title:
        lines.insert(0, f"---\ntitle: {fc.title}\n---")
    # 节点 = 实体；label 可附带字段
    for n in fc.nodes:
        fields = n.label.split("\n") if "\n" in n.label else []
        if len(fields) > 1:
            lines.append(f"    {n.id} {{")
            for f in fields[1:]:
                lines.append(f"        {f}")
            lines.append("    }")
    for e in fc.edges:
        relation = e.kind if e.kind != "solid" else "||--o{"
        lbl = e.label or "relates to"
        lines.append(f"    {e.src} {relation} {e.dst} : \"{lbl}\"")
    return lines


def _mm_class(fc: FlowChart) -> List[str]:
    lines = ["classDiagram"]
    if fc.title:
        lines.insert(0, f"---\ntitle: {fc.title}\n---")
    if fc.direction:
        lines.append(f"    direction {fc.direction}")
    for n in fc.nodes:
        if "\n" in n.label:
            parts = n.label.split("\n")
            lines.append(f"    class {n.id} {{")
            for p in parts[1:]:
                lines.append(f"        {p}")
            lines.append("    }")
        else:
            lines.append(f"    class {n.id}")
    for e in fc.edges:
        rel = {
            "extends": "<|--",
            "implements": "<|..",
            "composition": "*--",
            "aggregation": "o--",
            "dependency": "..>",
            "association": "-->",
        }.get(e.kind, "-->")
        lbl = f" : {e.label}" if e.label else ""
        lines.append(f"    {e.src} {rel} {e.dst}{lbl}")
    return lines


def _mm_journey(fc: FlowChart) -> List[str]:
    lines = ["journey"]
    if fc.title:
        lines.append(f"    title {fc.title}")
    for section in fc.extras.get("sections", []) or []:
        lines.append(f"    section {section.get('name', '')}")
        for task in section.get("tasks", []) or []:
            lines.append(f"      {task['name']}: {task.get('score', 3)}: {', '.join(task.get('actors', []))}")
    return lines


def _mm_pie(fc: FlowChart) -> List[str]:
    lines = ["pie" + (" showData" if fc.extras.get("show_data") else "")]
    if fc.title:
        lines.append(f"    title {fc.title}")
    for item in fc.extras.get("items", []) or []:
        lines.append(f"    \"{item['name']}\" : {item['value']}")
    return lines


def _mm_c4(fc: FlowChart, level: str) -> List[str]:
    lines = [f"C4{level}"]
    if fc.title:
        lines.append(f"    title {fc.title}")
    # 节点：shape 用 Person / System / System_Ext / Container / Db / ContainerDb
    shape_to_kind = {
        "person": "Person",
        "person_ext": "Person_Ext",
        "system": "System",
        "system_ext": "System_Ext",
        "container": "Container",
        "container_db": "ContainerDb",
        "component": "Component",
        "db": "ContainerDb",
    }
    for n in fc.nodes:
        kind = shape_to_kind.get(n.shape.lower(), "System")
        desc = ""
        if "\n" in n.label:
            parts = n.label.split("\n", 1)
            lbl, desc = parts[0], parts[1]
        else:
            lbl = n.label or n.id
        desc_part = f', "{desc}"' if desc else ""
        lines.append(f'    {kind}({n.id}, "{lbl}"{desc_part})')
    for e in fc.edges:
        lbl = e.label or ""
        lines.append(f'    Rel({e.src}, {e.dst}, "{lbl}")')
    return lines


def _mm_mindmap(fc: FlowChart) -> List[str]:
    lines = ["mindmap"]
    # 简化：假定第一个 node 是根，其他都是根的 child（不处理多级）
    if not fc.nodes:
        return lines
    root = fc.nodes[0]
    lines.append(f"  root(({root.label or root.id}))")
    # 按 edges 建父子关系
    children: Dict[str, List[str]] = {}
    for e in fc.edges:
        children.setdefault(e.src, []).append(e.dst)
    node_by_id = {n.id: n for n in fc.nodes}

    def _render(nid: str, depth: int) -> None:
        for cid in children.get(nid, []):
            node = node_by_id.get(cid)
            label = node.label if node else cid
            lines.append("  " * (depth + 1) + label)
            _render(cid, depth + 1)

    _render(root.id, 1)
    return lines


# ----- PlantUML 生成（真·泳道图） -----


def to_plantuml(fc: FlowChart, style_skinparam: str = "") -> str:
    if fc.diagram_type == "plantuml_raw":
        return fc.raw or ""

    if fc.diagram_type == "swimlane":
        return _puml_swimlane(fc, style_skinparam)
    if fc.diagram_type == "sequence":
        return _puml_sequence(fc, style_skinparam)
    # fallback：让 Mermaid 干
    raise ValueError(f"PlantUML 当前只支持 swimlane/sequence；请用 type: swimlane_mermaid 等走 Mermaid。")


def _puml_swimlane(fc: FlowChart, skin: str) -> str:
    out = ["@startuml"]
    if skin:
        out.append(skin)
    if fc.title:
        out.append(f"title {fc.title}")

    # 按 lane 分组
    lane_order = fc.lanes or []
    if not lane_order:
        lane_order = list(dict.fromkeys([n.lane for n in fc.nodes if n.lane]))

    lane_nodes: Dict[str, List[Node]] = {l: [] for l in lane_order}
    for n in fc.nodes:
        if n.lane in lane_nodes:
            lane_nodes[n.lane].append(n)

    # 构建 id → node 映射与 children 图
    node_by_id = {n.id: n for n in fc.nodes}
    successors: Dict[str, List[Tuple[str, Optional[str]]]] = {}
    for e in fc.edges:
        successors.setdefault(e.src, []).append((e.dst, e.label))

    out.append("start")
    visited = set()

    def _activity_body(n: Node) -> str:
        if n.shape == "diamond":
            return f"if ({n.label or n.id}?) then"
        return f":{n.label or n.id};"

    # 按 lane 顺序，深度优先走边
    first = fc.nodes[0] if fc.nodes else None
    cursor = first
    cur_lane: Optional[str] = None
    while cursor and cursor.id not in visited:
        visited.add(cursor.id)
        if cursor.lane and cursor.lane != cur_lane:
            out.append(f"|{cursor.lane}|")
            cur_lane = cursor.lane
        out.append(_activity_body(cursor))
        nexts = successors.get(cursor.id, [])
        if not nexts:
            break
        # 只线性前进（复杂分支建议用原生 PlantUML 写）
        nxt_id, lbl = nexts[0]
        if lbl:
            out.append(f"note right: {lbl}")
        cursor = node_by_id.get(nxt_id)

    out.append("stop")
    out.append("@enduml")
    return "\n".join(out)


def _puml_sequence(fc: FlowChart, skin: str) -> str:
    out = ["@startuml"]
    if skin:
        out.append(skin)
    if fc.title:
        out.append(f"title {fc.title}")
    for n in fc.nodes:
        role = "actor" if n.shape == "actor" else "participant"
        out.append(f'{role} "{n.label or n.id}" as {n.id}')
    for e in fc.edges:
        arrow = "-->" if e.kind == "dashed" else "->"
        lbl = f" : {e.label}" if e.label else ""
        out.append(f"{e.src} {arrow} {e.dst}{lbl}")
    out.append("@enduml")
    return "\n".join(out)


# ----- Graphviz DOT 生成（复杂网络拓扑、系统架构备选） -----


def to_dot(fc: FlowChart, style: Optional[Any] = None) -> str:
    """把 FlowChart 转成 Graphviz DOT 代码。用于网络拓扑 / 架构备选。"""
    from styles import Style  # 避免循环

    if fc.diagram_type == "dot_raw":
        return fc.raw or ""

    lines = ["digraph G {"]
    lines.append(f'  rankdir={fc.direction if fc.direction in ("TB","BT","LR","RL") else "TB"};')
    lines.append('  node [shape=box, style="rounded,filled", fontname="PingFang SC"];')
    if style:
        lines.append(f'  bgcolor="{style.background}";')
        lines.append(f'  node [fillcolor="{style.primary_color}", fontcolor="{style.primary_text_color}", color="{style.primary_border_color}"];')
        lines.append(f'  edge [color="{style.line_color}", fontname="PingFang SC"];')
    if fc.title:
        lines.append(f'  label="{fc.title}"; labelloc=t; fontsize=18;')

    # 分组
    for g in fc.groups:
        lines.append(f'  subgraph cluster_{g.id} {{')
        lines.append(f'    label="{g.label}";')
        lines.append('    style="rounded,filled"; fillcolor="#F5F5F5";')
        for cid in g.children:
            lines.append(f"    {cid};")
        lines.append("  }")

    for n in fc.nodes:
        attrs = [f'label="{n.label or n.id}"']
        if n.shape in ("cylinder", "cylinder"):
            attrs.append('shape=cylinder')
        elif n.shape == "diamond":
            attrs.append('shape=diamond')
        elif n.shape == "circle":
            attrs.append('shape=circle')
        lines.append(f"  {n.id} [{', '.join(attrs)}];")
    for e in fc.edges:
        attrs = []
        if e.label:
            attrs.append(f'label="{e.label}"')
        if e.kind == "dashed":
            attrs.append('style=dashed')
        attr_str = f" [{', '.join(attrs)}]" if attrs else ""
        lines.append(f"  {e.src} -> {e.dst}{attr_str};")
    lines.append("}")
    return "\n".join(lines)
