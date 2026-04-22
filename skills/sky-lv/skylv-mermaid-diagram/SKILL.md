---
name: skylv-mermaid-diagram
slug: skylv-mermaid-diagram
version: 1.0.0
description: "Generates Mermaid diagrams from descriptions. Creates flowcharts, sequence diagrams, and architecture diagrams. Triggers: mermaid diagram, architecture diagram, flowchart."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: mermaid-diagram
---

# Mermaid Diagram Generator

## Overview
Generates Mermaid diagrams for documentation.

## When to Use
- User asks to "draw a diagram" or "create architecture diagram"

## Flowchart Template

graph TD
  A[Start] --> B{Decision}
  B -->|Yes| C[Action 1]
  B -->|No| D[Action 2]
  C --> E[End]
  D --> E

## Sequence Diagram Template

sequenceDiagram
  Client->>API: POST /orders
  API->>DB: INSERT order
  DB-->>API: order_id
  API-->>Client: Confirmation

## Architecture Diagram Template

graph TB
  subgraph Frontend
    A[React App]
  end
  subgraph Backend
    B[API Gateway]
    C[Auth Service]
  end
  A --> B
  B --> C

## Tips
- Use LR (left-right) or TD (top-down)
- Use subgraphs to group components
- Add notes for complex decisions
