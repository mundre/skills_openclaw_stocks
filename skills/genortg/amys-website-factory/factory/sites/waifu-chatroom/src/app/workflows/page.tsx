import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Workflows",
  description: "Reusable workflows: scaffold, iterate, verify, ship.",
};

export default function Workflows() {
  return (
    <div className="atmo flex min-h-full flex-col">
      <SiteHeader />
      <main className="flex-1 py-16 sm:py-24">
        <Container>
          <h1 className="font-[var(--font-display)] text-4xl tracking-tight sm:text-5xl">
            Workflows
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            These are patterns AMY uses to build sites and keep systems stable.
          </p>

          <div className="mt-10 overflow-hidden rounded-2xl border border-[var(--stroke)] bg-black/20 shadow-[var(--shadow)]">
            <div className="border-b border-[var(--stroke)] px-4 py-3 text-xs text-[var(--muted)]">
              website.ship.loop
            </div>
            <pre className="overflow-x-auto p-5 text-xs leading-6 text-[var(--fg)]">
{`1) Scaffold (Next.js + TS + Tailwind)
2) Pick one bold design direction
3) Implement layout + components
4) Write real copy (no lorem)
5) Add 1–2 subpages
6) npm run lint && npm run build
7) Commit meaningful increments
8) Document the workflow for reuse`}
            </pre>
          </div>

          <div className="mt-8 rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
            <div className="text-xs uppercase tracking-widest text-[var(--muted)]">
              Tip
            </div>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">
              Client components are expensive. Keep them small, isolated, and
              justified. Server components do the heavy lifting.
            </p>
          </div>
        </Container>
      </main>
      <SiteFooter />
    </div>
  );
}

