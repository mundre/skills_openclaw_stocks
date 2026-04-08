---
name: diagram-cog
description: "Create diagrams from text descriptions. Flowcharts, system architecture, mind maps, org charts, ER diagrams, sequence diagrams, Gantt charts, network diagrams. Interactive or printable. Also works well for general interactive visualizations. Use for technical diagrams or process documentation. Outputs: HTML app, PDF. Powered by CellCog."
metadata:
  openclaw:
    emoji: "🔀"
    os: [darwin, linux, windows]
    requires:
      bins: [python3]
      env: [CELLCOG_API_KEY]
author: CellCog
homepage: https://cellcog.ai
dependencies: [cellcog]
---

# Diagram Cog - Describe It in Words, Get It as a Diagram

CellCog turns text descriptions into professional, interactive diagrams. Flowcharts, system architectures, mind maps, org charts, ER diagrams, sequence diagrams — rendered as shareable interactive web pages or print-ready PDFs.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**OpenClaw agents (fire-and-forget — recommended for long tasks):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    notify_session_key="agent:main:main",  # OpenClaw only
    task_label="my-task",
    chat_mode="agent",  # See cellcog skill for all modes
)
```

**All other agents (blocks until done):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    task_label="my-task",
    chat_mode="agent",
)
```

See the **cellcog** mothership skill for complete SDK API reference — delivery modes, timeouts, file handling, and more.

---

## What CellCog Has Internally

CellCog generates diagrams using its internal tools and rendering capabilities:

1. **Mermaid.js Rendering** — Supports flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, Gantt charts, pie charts, mind maps, and more. The agent generates Mermaid syntax and embeds it in an interactive HTML page.
2. **D3.js Rendering** — For custom visualizations that go beyond standard diagram types: force-directed graphs, tree layouts, hierarchical visualizations, network topologies.
3. **Custom SVG/HTML** — For highly tailored diagrams with specific styling, animations, or interactivity (org charts with photos, clickable architecture diagrams).
4. **PDF Generation** — Converts any diagram to a print-ready PDF via CellCog's HTML-to-PDF pipeline.
5. **Highcharts** — For diagrams that blend data visualization with diagramming (Gantt charts with progress bars, organizational heatmaps).

The agent orchestrates: **understand the structure → generate diagram code (Mermaid/D3/SVG) → render as interactive HTML app or PDF**.

---

## What Diagrams You Can Create

- **Flowcharts & Process Flows** — Business processes, decision trees, user flows, approval workflows, troubleshooting guides
- **System Architecture** — Microservices, cloud infrastructure, data pipelines, API architectures, CI/CD pipelines
- **Mind Maps & Concept Maps** — Brainstorming, topic exploration, study aids, content planning, strategy mapping
- **Org Charts** — Company hierarchy, team structures, reporting lines, matrix organizations
- **UML Diagrams** — Sequence, class, state, activity, component diagrams
- **ER Diagrams** — Database schema, data models, entity relationships
- **Network Diagrams** — IT infrastructure, network topology, security zones
- **Gantt Charts & Timelines** — Project timelines, sprint planning, roadmaps
- **Swimlane Diagrams** — Cross-functional process flows, RACI charts
- **User Journey Maps** — Customer experience flows across touchpoints

---

## Output Formats

| Format | Features | Best For |
|--------|----------|----------|
| **Interactive HTML** | Zoom, pan, click, hover, responsive, shareable via URL | Presentations, team sharing, exploration |
| **PDF** | Print-ready, static, professional | Documents, email attachments, printing |

CellCog defaults to interactive HTML. Request PDF explicitly for static output.

---

## Chat Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Individual diagrams, flowcharts, org charts, ER diagrams | `"agent"` |
| Complex multi-diagram documentation, full system design docs | `"agent team"` |
