import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Principles",
  description: "Operating principles for a reliable personal ops agent.",
};

function Item({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
      <div className="font-[var(--font-display)] text-xl tracking-tight text-[var(--accent2)]">
        {title}
      </div>
      <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{body}</p>
    </div>
  );
}

export default function Principles() {
  return (
    <div className="atmo flex min-h-full flex-col">
      <SiteHeader />
      <main className="flex-1 py-16 sm:py-24">
        <Container>
          <h1 className="font-[var(--font-display)] text-4xl tracking-tight sm:text-5xl">
            Principles
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            AMY is not magic. It is disciplined execution with sharp boundaries.
          </p>

          <div className="mt-10 grid gap-5 lg:grid-cols-3">
            <Item
              title="Local-first"
              body="Prefer on-box services, files as state, and explicit configs. Data stays close by default."
            />
            <Item
              title="Minimal surprises"
              body="Tools are used directly. If something needs approval, it is asked plainly."
            />
            <Item
              title="Quality gates"
              body="No hand-wavy ‘done’. Lint, build, and basic verification are non-negotiable."
            />
          </div>
        </Container>
      </main>
      <SiteFooter />
    </div>
  );
}

