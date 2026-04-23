# AMY — website

Marketing site for **AMY**, a personal ops agent focused on reliable workflows and local-first automation.

Built with **Next.js (App Router) + TypeScript + Tailwind**.

## Pages

- `/` (home)
- `/principles`
- `/workflows`

## Local development

```bash
npm install
npm run dev -- --port 3011
```

Then open:
- http://localhost:3011

## Quality gates

```bash
npm run lint
npm run build
npm audit --audit-level=low
```

## Notes

- Keep client components small and justified.
- `src/components/AgentLoop.tsx` is client-side by design.
