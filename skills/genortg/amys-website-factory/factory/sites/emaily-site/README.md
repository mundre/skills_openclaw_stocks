# Emaily — website

Marketing site for **Emaily**, an email agent that watches your inbox, produces structured summaries, and highlights the next action.

Built with **Next.js (App Router) + TypeScript + Tailwind**.

## Pages

- `/` (home)
- `/how-it-works`
- `/security`

## Local development

```bash
npm install
npm run dev -- --port 3010
```

Then open:
- http://localhost:3010

## Quality gates

```bash
npm run lint
npm run build
npm audit --audit-level=low
```

## Notes

- Server Components by default. Add `'use client'` only when needed.
- Fonts are loaded via `next/font` (swap enabled).
