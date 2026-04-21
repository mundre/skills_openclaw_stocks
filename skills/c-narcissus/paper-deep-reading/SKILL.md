---
name: paper-deep-reading-source-aware
description: Produce a traceable deep-reading report for a research paper, with inline paragraph locators after every claim, plus report.md, traceability_manifest.json, latex_paragraphs.json, and artifact_index.json.
version: 1.2.2
metadata: {"openclaw":{"emoji":"📘"}}
---

# Paper Deep Reading — Source-Aware + Formula-First Single-File Report Pipeline

Use this skill when the user wants a **deep, paper-grounded, auditable reading report** for one computer-science paper or a small paper batch.

The input may be:

- a user-provided PDF
- a user-provided LaTeX source tree or `.tex` files
- only the paper title or citation-like paper name

The default output is **text-first and audit-first**.  
This version intentionally **does not rely on a webpage reader**.

## 1) Core deliverables

1. **Human-readable report**
   - `report.md`

2. **Machine-readable trace artifacts**
   - `traceability_manifest.json`
   - `latex_paragraphs.json`
   - `artifact_index.json`

## 2) Key change in 1.2.1

The report itself is now the primary verification surface.

Every important claim in `report.md` must:

- have a stable claim id such as `C5.2`
- have an interpretation label:
  - `evidence-backed interpretation`
  - `plausible inference`
  - `speculation`
- be followed immediately by one or more **inline original-paragraph locators**

### Required inline locator format

After each claim bullet, add nested bullets such as:

- `[C5.2][evidence-backed interpretation] <claim text>`
  - `原文定位 1：main.tex → Methodology > Neighborhood Pseudo-Labeling，行 343–349；从“<start excerpt>”到“<end excerpt>”。`
  - `原文定位 2：supplementary.tex → Experimental Setup，行 262–266；从“<start excerpt>”到“<end excerpt>”。`

The inline locator must make it easy for a human reader to verify the claim directly from LaTeX or PDF.



## 2.1) Formula-first strengthening in 1.2.2

This version restores the formula-preservation bar expected by the original deep-reading skill.

When the paper contains key formulas, the report must **not** compress them into prose-only summaries.

For each central equation or objective, the report must explicitly include:

1. the equation itself in readable math form
2. symbol-by-symbol explanation
3. what optimization / estimation / filtering role it plays
4. why the authors likely wrote it in this form instead of a nearby alternative
5. how it connects to the previous and next module
6. what may be brittle, heuristic, under-justified, or computationally expensive about it

If the user requests a **single Markdown file**, the preferred format is:

- main report in the front
- a consolidated **claim → evidence index** at the end

Do not weaken equation detail for the sake of shorter presentation.

## 2.2) Single-file report mode

When the user explicitly says:

- no webpage
- one markdown file only
- evidence can go at the end

then produce one authoritative `.md` file whose body is easy to read continuously, and whose final appendix contains the locator index for all major claim ids.


## 3) Source acquisition policy

Always assemble the **best available evidence package** before writing.

Preferred reading order:

1. **arXiv LaTeX/source package**
2. **user-provided LaTeX**
3. **best available PDF**
4. **supplementary material**
5. **OpenReview thread / rebuttal / meta-review when relevant**

### 3.1 When LaTeX is available

Treat LaTeX as the primary structural source.

Use PDF only as a visual and pagination aid for:

- figure interpretation
- table reading
- page-local narrative flow
- page anchors

### 3.2 When only PDF is available

Do not stop at PDF summarization immediately.

First check whether the same paper has a matching arXiv LaTeX/source package.  
If it exists and matches the same paper, switch to **LaTeX-primary + PDF-assisted** reading.

If not, continue with the PDF and say explicitly that the reading is **PDF-primary**.

### 3.3 When only title is available

Search for the paper and collect:

1. arXiv source package if available
2. the best PDF
3. supplementary PDF or appendix if available
4. OpenReview forum if venue is ICLR or otherwise OpenReview-hosted

Never silently analyze the wrong paper. Disambiguate by title, authors, abstract, year, and method keywords.

## 4) Mandatory artifacts

### 4.1 `report.md`

The report must cover, whenever the evidence supports it:

1. paper identification and source package used
2. title interpretation
3. what problem the paper really solves
4. scientific problem ladder
5. related-work gap audit
6. main idea
7. likely author reasoning path
8. symbols, assumptions, and notation
9. key formulas and equation-by-equation explanation (formula preserved, term-by-term explained, critiqued, and linked to adjacent modules)
10. theory / proof / practice mapping
11. algorithm or module walkthrough with concrete example
12. figure explanation
13. experimental design
14. table / chart / claim alignment audit
15. reviewer-lens audit
16. innovation points and claim-by-claim support audit
17. weaknesses and limitations
18. innovation type and scientific-boundary judgment
19. future directions
20. vivid plain-language story summary
21. exact sources used

### 4.2 `traceability_manifest.json`

This is the claim-to-evidence map.

Rules:

- every claim id in the report must appear in the manifest
- one bullet must not hide multiple independent claims under one id
- if a claim depends on multiple paragraphs / equations / tables / appendix passages, list them separately
- each claim entry should also include a human-friendly locator summary when possible

### 4.3 `latex_paragraphs.json`

This is the stable LaTeX anchor index.

Each entry must keep:

- `paragraph_id`
- `source_path`
- `line_start`
- `line_end`
- `section_path`
- `kind`
- `text`

### 4.4 `artifact_index.json`

A compact index for the generated text-first bundle.

It should list the locations of:

- `report.md`
- `traceability_manifest.json`
- `latex_paragraphs.json`
- main PDF if any
- supplementary PDF if any
- source package path if known

## 5) Claim discipline

### 5.1 Claim ids

Use stable section-local ids such as:

- `C3.1`
- `C5.2`
- `C14.4`

### 5.2 Claim splitting rule

Do not hide multiple judgments in one claim bullet.

### 5.3 Evidence completeness rule

List all materially relevant evidence for a claim, not just one convenient paragraph.

### 5.4 Interpretation labels

Each claim must declare exactly one of:

- `evidence-backed interpretation`
- `plausible inference`
- `speculation`

## 6) Writing style for verification

Prefer a report that is pleasant to read **and** easy to audit.

For every claim, the user should be able to answer three questions immediately:

1. Which source file supports this?
2. Which section or subsection is it in?
3. From which paragraph span or line span should I start checking?

This skill is successful only if the user can verify the report without needing a separate webpage reader.
