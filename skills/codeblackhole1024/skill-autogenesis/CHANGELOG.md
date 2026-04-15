# Changelog

## 1.2.1

- Refined positioning to emphasize verification-gated skill creation rather than unconditional autonomous writes.
- Clarified that skill creation happens only when recurrence, stability, and environment policy permit it.
- Tightened README wording to better communicate lifecycle controls and safety boundaries.
- Kept local fallback reference behavior for GitHub sources.

## 1.2.0

- Added explicit source resolution policy: GitHub first, local fallback second, `[UNVERIFIED]` last.
- Added local fallback reference files under `references/fallback/`.
- Added `skill_manage`-style lifecycle handling for create, patch, edit, write_file, remove_file, and guarded delete.
- Added reusable template file for generated skills.

## 1.1.0

- Added lifecycle-oriented behavior modeled after `skill_manage`.
- Added support for supporting-file management and duplicate-skill avoidance.

## 1.0.0

- Initial release.
- Added automatic workflow distillation, recurrence detection, and skill generation guidance.
