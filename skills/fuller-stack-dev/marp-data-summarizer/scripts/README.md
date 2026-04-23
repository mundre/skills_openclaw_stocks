# Marp Render Helper

Use the bundled helper to render Marp decks instead of re-assembling CLI flags by hand.

## Usage

```bash
node {baseDir}/scripts/render-marp.js deck.slides.md
node {baseDir}/scripts/render-marp.js deck.slides.md deck.slides.pdf --format pdf
node {baseDir}/scripts/render-marp.js deck.slides.md ./slide-images --format pngs
```

## Default behavior

- default output format: `.html`
- keeps `*.slides.md` as the source deck
- prefers local `marp` if installed
- falls back to `npx`, `pnpm dlx`, `bunx`, or `yarn dlx`

## Verification

The helper verifies that the expected artifact exists and is non-empty before returning success.
