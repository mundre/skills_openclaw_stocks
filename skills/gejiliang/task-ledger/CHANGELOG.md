# Changelog

## 0.2.3

- Added reporting schema fields for `short-first`, `normal`, and `detailed` reporting modes.
- Added short-format export in `task-export.py` for chat-friendly updates.
- Added file-backed long report output via `task-export.py --write-report`.
- Stored generated long report paths in task state.
- Synced the published skill package to include reporting-aware workflow support.

## 0.2.2

- Added readiness helper `task-ready.py`.
- Added `task-start-if-ready.py` for readiness-gated task starts.
- Added relation/dependency graph export in Markdown, DOT, and JSON (`task-graph-export.py`).
- Added readiness column to open-task listing.
- Strengthened `task-doctor.py` with scheduling-specific diagnostics.
- Synced the published skill package to include all local control-plane and scheduling enhancements.

## 0.2.1

- Added parent/child task relation fields and task tree view (`task-ls-tree.py`).
- Strengthened dependency and relation checks in `task-doctor.py`.
- Added human-friendly task export (`task-export.py`).
- Added Markdown output mode to `task-resume-summary.py`.
- Improved `task-bind-process.py` with `process.bound` event naming and optional process state.
- Added `--json` and `--strict` support to `task-doctor.py`.
- Added migration helper `migrate-task-020.py` for bringing legacy task files to the 0.2 baseline.

## 0.2.0

- Added richer task schema with lifecycle, blocking, rollback, and notification fields.
- Added recovery helpers:
  - `task-verify.py`
  - `task-resume-summary.py`
  - `task-bind-subtask.py`
  - `task-bind-cron.py`
- Improved `task-events.py` filtering and JSON output.
- Added specialized templates:
  - `restart-openclaw-gateway.example.json`
  - `deploy-service.example.json`
- Added `task.schema.json`.
- Synchronized the published ClawHub skill package with the local toolkit.
- Published `task-ledger@0.2.0`.

## 0.1.1

- Improved discoverability wording.
- Added better search tags for ClawHub.

## 0.1.0

- Initial public release of the task-ledger toolkit.
