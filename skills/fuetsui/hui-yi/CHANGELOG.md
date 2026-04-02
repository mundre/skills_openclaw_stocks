# Hui Yi Changelog

## 1.0.2 — Cross-platform update and release alignment

**Cross-platform helpers.** Replaced bash-first operational guidance with Python helper scripts intended to work on Linux, macOS, and Windows using a standard `python` command.

**Helper cleanup.** Renamed Python helpers to remove the `hui_yi_` prefix:
- `hui_yi_search.py` → `search.py`
- `hui_yi_rebuild.py` → `rebuild.py`
- `hui_yi_decay.py` → `decay.py`
- `hui_yi_cool.py` → `cool.py`

**Schema alignment.** Standardized the documented archive shape around the current workspace-friendly formats:
- `index.md` uses one Markdown block per note
- `tags.json` uses `{ _meta, notes[] }`
- note sections use bullet-based values that match existing cold-memory notes

**State handling.** Cooling guidance updates the top-level `coldMemory` object inside `memory/heartbeat-state.json` instead of overwriting the whole file. `rebuild.py` now refreshes `coldMemory.lastIndexRefresh`, and `cool.py scan` uses `lastArchive` for incremental detection.

**Automation is optional.** The skill explicitly works in manual mode when helper scripts are unavailable. Scripts are helpers, not hard dependencies.

**Packaging/docs sync.** Added and aligned:
- `manifest.yaml`
- `README.md`
- manifest notes and reference docs
- legacy shell deprecation messages

**Retrieval quality.** Improved semantic-context extraction during rebuild so prose sections are preserved in `tags.json`.

---

## 1.0.1 — Wording and publishing consistency

Patch release.

Changes:
- replaced Chinese trigger examples with English phrasing in `SKILL.md`
- updated the cold-memory schema reference to use the same English trigger wording
- kept recall semantics unchanged; this release is wording and publishing consistency only

---

## 1.0.0 — Original public release (by Fue Tsui)

Original OpenClaw skill release.

Key characteristics of the early public version:
- instruction-heavy `SKILL.md`
- reference-based cold-memory workflow
- published to ClawHub / GitHub as the initial public baseline
- later identified as needing clearer manifest/path declarations for platform review
