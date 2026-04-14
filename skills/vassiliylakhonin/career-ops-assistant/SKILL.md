---
name: career-ops-assistant
description: Operate Career-Ops (santifer/career-ops) end-to-end with safe, command-first workflows. Use for setup, evaluate/scan/pdf/batch/tracker/pipeline/apply/deep/contact/training/project/patterns/followup modes, profile personalization, multilingual mode switching, and strict tracker/data-contract integrity.
---

# Career-Ops Assistant

Run Career-Ops with reproducible commands, strong data hygiene, and human-in-the-loop application control.

## Best for

- Installing and bootstrapping Career-Ops correctly
- Running evaluation/pipeline flows reliably
- Maintaining tracker quality at scale (batch + dedup + verify)
- Personalizing output without breaking shared system defaults

## Not for

- Auto-submitting applications without human review
- Editing shared defaults for user-specific preferences
- Bypassing verify/normalize/merge safety steps

## 1) Onboarding gate (mandatory)

Before any evaluation/scan flow, ensure these exist:

- `cv.md`
- `config/profile.yml`
- `modes/_profile.md` (create from `modes/_profile.template.md` if missing)
- `portals.yml`

If missing, complete onboarding first.

## 2) Setup

Preferred bootstrap:

```bash
bash scripts/bootstrap-career-ops.sh /path/to/career-ops
```

Manual fallback:

```bash
npm install
npx playwright install chromium
cp config/profile.example.yml config/profile.yml
cp templates/portals.example.yml portals.yml
[ -f modes/_profile.md ] || cp modes/_profile.template.md modes/_profile.md
[ -f cv.md ] || cat > cv.md <<'EOF'
# CV
Paste CV in markdown.
EOF
npm run doctor
```

## 3) 30-second daily runbook

```bash
npm run doctor
npm run sync-check
npm run verify
```

If running batch or status-heavy flows, also run:

```bash
npm run normalize
npm run dedup
npm run merge
npm run verify
```

## 4) Update lifecycle

Run silently at session start:

```bash
node update-system.mjs check
```

If update exists, ask before applying:

```bash
node update-system.mjs apply
node update-system.mjs dismiss
node update-system.mjs rollback
```

## 5) Mode coverage map

Use one published skill (`career-ops-assistant`) for all intents.

Recognize and route:
- `/career-ops ...`
- `/career-ops-pipeline`
- `/career-ops-evaluate`
- `/career-ops-compare`
- `/career-ops-contact`
- `/career-ops-deep`
- `/career-ops-pdf`
- `/career-ops-training`
- `/career-ops-project`
- `/career-ops-tracker`
- `/career-ops-apply`
- `/career-ops-scan`
- `/career-ops-batch`
- `/career-ops-patterns`
- `/career-ops-followup`

Claude-style shortcuts:
- `/career-ops` (menu/auto)
- `/career-ops {jd-url-or-text}`
- `/career-ops scan|pdf|batch|tracker|apply|pipeline|contacto|deep|training|project|patterns|followup`

## 6) Data contract (critical)

### User layer (safe personalization)

- `cv.md`
- `config/profile.yml`
- `modes/_profile.md`
- `article-digest.md`
- `portals.yml`
- `data/*`, `reports/*`, `output/*`, `interview-prep/*`

### System layer (do not personalize)

- `modes/_shared.md`, base mode files
- scripts `*.mjs`
- `dashboard/*`, `templates/*`, `batch/*`, `CLAUDE.md`

Rule: user-specific narrative, weights, and targeting go to `config/profile.yml` and/or `modes/_profile.md`.

## 7) FPCE decision policy

For each opportunity:

1. Decompose role into the real business problem.
2. Map hard constraints (level/scope/geography/comp/stack/domain).
3. Estimate expected value vs time cost.
4. Output one label:
   - `Apply now`
   - `Position then apply`
   - `Skip`
5. Add concise `Why now / Why not now`.

Default policy:
- Usually reject below `4.0/5` unless asymmetric upside is clear.
- Prefer opportunities with strong proof-point fit and compounding value.

## 8) Personalization workflow

- Collect role targets, constraints, compensation floor, proof points.
- Update `portals.yml` filters and tracked companies.
- Keep `cv.md` as factual source of truth.
- Keep long proof points in `article-digest.md`.
- After user correction, immediately update profile-layer files.

## 9) Multilingual switching

- English: `modes/`
- German: `modes/de`
- French: `modes/fr`
- Japanese: `modes/ja`

Support persistent setting via `config/profile.yml` (`language.modes_dir`).

## 10) Pipeline integrity (strict)

- Never append tracker rows directly in batch flow.
- Write additions to `batch/tracker-additions/*.tsv`.
- After batch always run:

```bash
npm run merge && npm run verify
```

Canonical states only:
`Evaluated`, `Applied`, `Responded`, `Interview`, `Offer`, `Rejected`, `Discarded`, `SKIP`.

Use `npm run normalize` for state cleanup and `npm run dedup` for duplicates.

## 11) Batch/report formatting

- Report pattern: `{###}-{company-slug}-{YYYY-MM-DD}.md`
- TSV additions require 9 columns in order:
  1. `num`
  2. `date`
  3. `company`
  4. `role`
  5. `status`
  6. `score` (`X.X/5`)
  7. `pdf` (`✅/❌`)
  8. `report` markdown link
  9. `notes`

## 12) Offer verification

Prefer browser navigation + snapshot proof for listing validation.
If unavailable, mark verification as unconfirmed.

## 13) Ethics and safety

- Never auto-submit applications.
- Keep human-in-the-loop before final send.
- Discourage low-fit mass apply behavior.
- Prefer quality over volume.

## 14) Dashboard TUI (optional)

```bash
cd dashboard
go build -o career-dashboard .
./career-dashboard --path ..
```

## 15) Troubleshooting ladder

1. `doctor` fails -> fix missing config/CV/templates.
2. PDF fails -> reinstall Playwright Chromium.
3. Broken statuses -> normalize -> verify.
4. Duplicates -> dedup -> verify.
5. Batch merge issues -> validate TSV order -> merge -> verify.
6. Inconsistent state -> verify -> targeted fix -> verify again.
