# Agent workflow: how AMY should build a site

1) Intake (brief)
  - Parse WEBSITE_BRIEF_TEMPLATE.md, extract colors and tech choices. Validate minimal fields (name, slug, goal).

2) Scaffold
  - Run `new-site.sh --slug <slug>` to scaffold Next.js + Tailwind + TS. Commit scaffold.
  - Inject CSS variables and Tailwind config from DESIGN_GUIDE.md.

3) Components & UI pack
  - If brief requests a pack, install (shadcn/radix/headless/Tailwind UI) or copy components into /components.

4) Content & copy
  - Use COPYWRITING.md templates to generate hero copy, meta tags, feature bullets, and CTAs.

5) Interactivity & features
  - Optional features: auth (NextAuth), SaaS billing (Stripe), API routes, webhooks. Add toggles in brief.

6) Verify
  - Run `check-site.sh --site sites/<slug> --port 3000` (wrapped verify) to run Playwright + accessibility checks and produce artifacts.

7) Iterate
  - Apply design or copy changes, re-run verify until green.

8) Publish (manual approval)
  - Use `publish-site.sh` or `deploy-site.sh` with user-provided credentials. Require explicit approval for production deploys.

