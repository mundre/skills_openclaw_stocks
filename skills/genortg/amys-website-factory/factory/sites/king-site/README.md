# king-site — website

Built with **Next.js (App Router) + TypeScript + Tailwind**.

## Local development


added 6 packages, and audited 367 packages in 1s

146 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities

> king-site@0.1.0 dev
> next dev

▲ Next.js 16.2.4 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://192.168.1.238:3000
✓ Ready in 276ms

[?25h

## Quality gates


> king-site@0.1.0 lint
> eslint


/home/genorbox1/.openclaw/skills/amys-website-factory/factory/sites/king-site/src/app/layout.tsx
  24:9  warning  Custom fonts not added in `pages/_document.js` will only load for a single page. This is discouraged. See: https://nextjs.org/docs/messages/no-page-custom-font  @next/next/no-page-custom-font

/home/genorbox1/.openclaw/skills/amys-website-factory/factory/sites/king-site/src/app/page.tsx
  3:39  warning  'useCallback' is defined but never used  @typescript-eslint/no-unused-vars

✖ 2 problems (0 errors, 2 warnings)


> king-site@0.1.0 build
> next build

▲ Next.js 16.2.4 (Turbopack)

  Creating an optimized production build ...
✓ Compiled successfully in 1428ms
  Running TypeScript ...
  Finished TypeScript in 1418ms ...
  Collecting page data using 5 workers ...
  Generating static pages using 5 workers (0/4) ...
  Generating static pages using 5 workers (1/4) 
  Generating static pages using 5 workers (2/4) 
  Generating static pages using 5 workers (3/4) 
✓ Generating static pages using 5 workers (4/4) in 329ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
└ ○ /_not-found


○  (Static)  prerendered as static content

found 0 vulnerabilities
