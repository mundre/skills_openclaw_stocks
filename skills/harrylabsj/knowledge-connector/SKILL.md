---
name: Knowledge Connector
description: Turn scattered notes and documents into an actionable knowledge graph. Use when the user wants an import wizard, cross-document answers, relationship maps, and concrete next-step suggestions instead of a passive graph dump.
---

# Knowledge Connector

Knowledge Connector should feel like a product line, not another graph utility.

Its job is not just to extract concepts. Its job is to help the user:
- import notes and documents with low friction
- search across multiple documents from one query
- visualize concept relationships in a way that is easy to inspect
- get actionable graph results such as what to connect, review, or expand next

## What This Skill Optimizes For

Default toward five high-value outcomes:
- fast document import
- guided import onboarding
- cross-document knowledge retrieval
- relationship-aware graph views
- actionable next steps

Avoid drifting into “yet another adjacent knowledge skill”.

## Primary Workflows

### 1. Import Experience

Use `kc import-docs` when the user wants to build a graph from multiple files or a notes directory.
Use `kc import-wizard` when the user wants a preview-first onboarding flow.

Good import behavior means:
- accept files or a directory
- preserve source titles and paths
- show how many documents, concepts, and relations were created
- keep the user oriented after import

### 2. Cross-Document Search

Use `kc search` or `kc query` when the user asks:
- where an idea appears across notes
- which documents mention a concept
- what concepts connect several documents

Results should show:
- matching concepts
- matching source documents
- useful next actions

### 3. Relationship Visualization

Use `kc visualize` for full graph export and `kc map` for a concept-centered actionable subgraph.

Visualization should help the user answer:
- what is central
- what is weakly connected
- what deserves review

### 4. Actionable Results

Do not stop at “here is the graph”.

The output should usually recommend one or more actions such as:
- import more source material
- auto-connect newly imported concepts
- inspect a concept-centered subgraph
- verify weak relationships from source documents
- export a graph view for sharing or review

## Core Commands

### Import

```bash
kc import-wizard --dir notes/
kc import-docs --dir notes/
kc import-docs --files a.md b.md c.txt
```

### Search

```bash
kc search "machine learning"
kc answer "哪些文档把强化学习和规划连在一起？"
kc query "transformer" --sources
kc query --ask "哪些文档同时提到了强化学习和规划？"
```

### Map And Visualize

```bash
kc map --concept "人工智能" --depth 2
kc visualize --format html --output graph.html
kc visualize --concept "机器学习" --depth 2 --output ml-graph.html
```

### Manage

```bash
kc stats
kc export --output backup.json
kc import --file backup.json
```

## Output Standard

When the skill returns results, prefer this structure:

### What Matched
Show concepts and source coverage.

### Why It Matters
Explain the meaningful relationship or pattern.

### Next Step
Tell the user what to do next with the graph.

## Product Positioning

Knowledge Connector is strongest when the user has:
- a growing notes corpus
- repeated concepts spread across files
- a need to move from storage to understanding

It is weaker if it only acts like a raw extractor with no import flow, no source-aware search, and no next-step guidance.
