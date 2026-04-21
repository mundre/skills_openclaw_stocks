# paper-deep-reading-openclaw-source-aware-skill v1.2.2

A formula-first, source-aware paper deep-reading skill for OpenClaw / ClawHub style packaging.

## What changed in 1.2.2

- restored a stronger **formula-preservation** requirement
- supports a **single Markdown report** as the default final reading surface
- allows all evidence locators to be grouped in a **final appendix**
- requires each core equation to be explained at four levels:
  - what the symbols mean
  - what the equation is doing
  - why the authors likely chose this form
  - what the weaknesses / alternatives are

## Default outputs

- `report.md`
- `traceability_manifest.json`
- `latex_paragraphs.json`
- `artifact_index.json`

## Preferred use

Use this skill when the user wants:

- a traceable deep-reading report
- no webpage reader
- equation-level explanation that does not collapse into short prose
- a final appendix for claim-to-evidence verification
