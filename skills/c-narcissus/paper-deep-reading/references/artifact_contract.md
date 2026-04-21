# Artifact Contract

## `artifact_index.json`
Top-level index for all outputs that belong to one paper reading bundle.

Required keys:

- `schema_version`
- `paper_id`
- `report`
- `traceability_manifest`
- `latex_paragraphs`

Optional keys:

- `source_package`
- `pdfs`
- `notes`

## `traceability_manifest.json`
Maps report claims to source evidence.

Each claim entry should include:

- `claim_id`
- `section_id`
- `report_anchor`
- `statement`
- `interpretation_type`
- `confidence`
- `evidences`

Recommended extra field:

- `human_locators`

Each evidence entry may include:

- `evidence_id`
- `source_kind`
- `source_file`
- `paragraph_id`
- `page`
- `line_start`
- `line_end`
- `locator_method`
- `synctex`
- `quote_text`
- `notes`

## `latex_paragraphs.json`
Stable anchor list extracted from LaTeX.

Each paragraph entry should include:

- `paragraph_id`
- `source_path`
- `line_start`
- `line_end`
- `section_path`
- `kind`
- `text`

## Report requirement

In `report.md`, every claim bullet must be followed by one or more nested `原文定位` bullets that tell the reader:

- which source file to open
- which section / subsection to inspect
- which line span to inspect
- roughly from which excerpt to which excerpt the relevant paragraph runs

## Claim typing
Allowed interpretation labels:

- `evidence-backed interpretation`
- `plausible inference`
- `speculation`
