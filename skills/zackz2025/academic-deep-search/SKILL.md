---
name: academic-deep-search
description: Search academic literature and return structured, immediately useful results. Triggers: (1) "what molecules/markers do studies in [topic] detect?", "一般检测哪些分子", "results里一般报道什么"; (2) "show me a typical figure of [topic]", "找个XX的典型figure", "看看XX相关的figure". Two modes: Body Mode organizes results by experiment type; Figure Mode organizes by individual figures with original captions. For biomedical topics, PubMed/PMC is the preferred source.
---

# Academic Deep Search

## Two Modes

| Mode | What It Answers |
|------|---------------|
| **Body Mode** | "What molecules/markers do studies typically detect?" / "What do results sections usually report?" / "What experimental methods are used in field X?" — organized by experiment type |
| **Figure Mode** | "Show me a typical figure of X" / "How are figures of X typically presented?" — organized by Figure, with original captions |

Both modes share the same search workflow; only the organizing and presentation differ.

## Workflow

### Step 1 — Understand the question and translate to search terms

1. Understand what the user is asking
2. Translate to English search terms — all API calls must use English; Chinese is only for comprehension
3. For biomedical topics: use standardized vocabulary (MeSH terms when available), NOT free-text translations
4. Generate 2-3 alternative search phrases (synonyms, broader/narrower terms)

### Step 2 — Construct the search query for the target platform

Different platforms have different syntax. Know the platform before searching.

**PubMed / PMC:**
- MeSH terms: `TERM[MeSH]`
- Field tag: `TERM[Field]` (e.g., `TERM[Title]`)
- Phrase search: `"exact phrase"`
- Boolean: `AND`, `OR`, `NOT` (uppercase)
- Journal field: `TERM[Journal]`
- Date field: `TERM[dp]`

**Example template:**
```
("concept A"[MeSH] OR "concept B"[MeSH])
AND "disease or condition"[MeSH]
AND "intervention"[MeSH]
AND "journal name"[Journal]
```

**For non-PubMed platforms:** adapt the syntax to the target platform's conventions. General principles:
- Use quotes for phrases
- Use AND/OR/NOT for combining terms
- Use field tags if available
- Filter by source type, date, or other faceted search options if supported

**Journal name:** When a user provides a journal name, verify its exact indexed form in the target database before searching. Display names often differ from indexed names (e.g., with or without punctuation, abbreviation variants). Always confirm against the database's journal field.

### Step 3 — Search (respect user-specified scope first)

**Priority rules (highest to lowest):**

1. **User specified journals or sources** — strictly limit to those sources; do not expand to other sources
   - User specifies journal A, B, C → search only A, B, C
   - User specifies PubMed only → do not mix with Google Scholar or other sources
   - User provides a specific URL → read that URL only; do not search for alternatives

2. **User did not specify** — use the best default source for the topic
   - Biomedical: PubMed / PMC (highest quality free full text)
   - Other fields: Google Scholar, arXiv, or field-appropriate databases
   - General discovery: web search (Tavily)

**Tool selection:**
1. `web_fetch` — fetch full text directly when URL is known
2. `web_search` — broad discovery, cross-platform
3. Platform-native search (PubMed, arXiv, etc.) — most reliable for verifying source attribution
4. `medical-research-toolkit` MCP — for PubMed/PMC/ChEMBL and other biomedical databases

Goal: find 5-10 candidate papers, prefer open-access full text.

### Step 4 — Verify source membership before citing

**Critical: before citing any paper, confirm it is actually published in the user-specified source.**

Verification method:
- Check the Journal field in search results
- Read the PubMed (or equivalent) abstract page — it shows the journal name
- For uncertain results: re-search using the exact journal field filter to confirm

**Prohibited:**
- Treating a paper as if it came from a target journal when it did not
- Concluding that findings from one journal apply to another journal without explicit justification

### Step 5 — Read full text (not just abstract)

- **Body Mode:** Methods + Results + Discussion sections
- **Figure Mode:** figure captions and the body text that cites each figure

Abstracts alone are insufficient. Full text is required to answer method or marker questions.

### Step 6 — Select papers (2-5, diverse)

- Source compliance: only include papers from user-specified journals or sources
- Diversity: different first authors, different institutions
- Relevance: match the keywords and research context
- Quality: complete Methods descriptions and clear figure captions

### Step 7 — Present

Output directly in Chat unless the user explicitly asks for a file.

**Body Mode — organize by experiment type, not by paper:**
```
### 1. [Experiment Type, e.g. Western Blot]

| Molecule | Change | Loading Control | Reference |
|---------|--------|----------------|-----------|
| X       | ↑/↓   | β-actin        | PMCID Fig.X |

Source: [PMCID1] · [PMCID2] · [PMCID3]
```

**Figure Mode — organize by Figure, include original caption:**
```
📍 [Paper Title] · [Journal] · [Year] · [PMCID/DOI]
**Fig. X[panel]** — [Figure name]
Caption: [full original caption]
Location in text: [which Results paragraph cites this figure]
```

## Principles

1. **User-specified scope is binding** — never expand beyond it without explicit permission
2. **Use standardized vocabulary for biomedical topics** — MeSH or equivalent, not free-text translations
3. **All API calls use English search terms**
4. **Read full text** — abstracts alone cannot answer method or marker questions
5. **Output directly in Chat** — no file generation unless requested
6. **Inline citations** (PMID, PMCID, or DOI) for traceability
7. **Verify source membership before citing** — no false positives
8. **For biomedical topics, prioritize PubMed / PMC** as the highest-quality free full-text source

## When Nothing Is Found

1. Try different search terms (synonyms, broader terms, MeSH expansion)
2. Try different platforms or databases
3. Report honestly: what was searched, how many papers were read, what was found, why it may be limited, and what alternative approach is suggested
