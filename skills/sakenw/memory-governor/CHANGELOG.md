# Changelog

## 0.2.4-beta - 2026-03-31

### Fixed

- `check-memory-host.py` and `validate-memory-frontmatter.py` now support Python 3.9 / 3.10 via `tomli` fallback

### Changed

- installation docs now call out Python version compatibility explicitly

## 0.2.3-beta - 2026-03-31

### Added

- migration guide for hosts that already have a messy memory setup
- manifest examples for `reusable_lessons` as `directory` or `pattern`

### Changed

- host checker and manifest contract now support `fallback_paths`
- installation and integration docs now point legacy hosts to the migration path
- integration checklist now calls out non-single `reusable_lessons` modes explicitly

## 0.2.2-beta - 2026-03-31

### Added

- bilingual public-facing intro sections in `README.md`
- bilingual opening guidance in `SKILL.md`

### Changed

- public packaging now reads more clearly for both English and Chinese readers

## 0.2.1-beta - 2026-03-31

### Added

- clearer English public-facing summary in `README.md`
- bilingual skill description in `SKILL.md` for ClawHub-facing metadata

### Changed

- public packaging now explains the `Installed / Integrated / Validated` model more clearly for external readers

## 0.2.0-beta - 2026-03-31

This is the first distributable beta shape of `memory-governor`.

### Added

- generic core + host profiles packaging model
- packaged fallback templates in `assets/fallbacks/`
- installation and integration guide
- host profile reference for `Generic` and `OpenClaw`
- snippets for host-level and skill-level integration
- before / after comparison page
- generic host validation record
- standalone `examples/generic-host/` example directory
- lightweight bootstrap script for generic hosts
- adapter manifest contract via `memory-governor-host.toml`
- manifest-driven host checker flow for generic and OpenClaw hosts

### Changed

- path-centric design language was tightened into `memory type -> target class -> adapter`
- optional skills such as `self-improving` and `proactivity` are now treated as adapters, not core dependencies
- OpenClaw is now framed as a reference host profile rather than the universal default
- OpenClaw host can now declare its adapter map explicitly instead of relying only on reference-profile inference

### Fixed

- machine-local absolute links were removed from package-facing docs
- fallback assets are now packaged inside the skill
- adapter resolution order is documented explicitly
- host checking can now prefer explicit manifest contracts over directory guessing

### Current Scope

`memory-governor` remains a governance kernel.

It does not attempt to become:

- a second-brain platform
- a universal sync bus
- a forced workspace migration tool

### Known Gaps

- no polished public landing page yet
- no richer installer beyond the lightweight bootstrap
- no versioned release automation
