import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Security",
  description: "How Emaily keeps secrets and data exposure under control.",
};

function Card({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
      <div className="font-[var(--font-display)] text-xl tracking-tight">
        {title}
      </div>
      <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{body}</p>
    </div>
  );
}

export default function Security() {
  return (
    <div className="grain flex min-h-full flex-col">
      <SiteHeader />
      <main className="flex-1 py-16 sm:py-24">
        <Container>
          <h1 className="font-[var(--font-display)] text-4xl tracking-tight sm:text-5xl">
            Security
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            Emaily is designed around one idea: keep sensitive data close.
            Reliability matters, but not at the cost of spraying secrets into the
            world.
          </p>

          <div className="mt-10 grid gap-5 lg:grid-cols-3">
            <Card
              title="Local-first"
              body="Runs inside your OpenClaw environment. Prefer loopback services and on-box storage over external dashboards."
            />
            <Card
              title="Explicit boundaries"
              body="Only env vars prefixed with NEXT_PUBLIC_ are allowed into the browser bundle. Everything else stays server-side."
            />
            <Card
              title="Least noise"
              body="Summaries are compact and actionable. You can tune what gets posted so private details do not leak into chat history." 
            />
          </div>

          <div className="mt-10 rounded-2xl border border-[var(--stroke)] bg-[color:rgba(0,0,0,0.35)] p-6 shadow-[var(--shadow)]">
            <div className="text-xs uppercase tracking-widest text-[var(--muted)]">
              Practical checklist
            </div>
            <ul className="mt-4 space-y-3 text-sm leading-7 text-[var(--muted)]">
              <li>
                <span className="text-[var(--accent)]">•</span> Put secrets in
                <code className="mx-1 rounded bg-black/35 px-1.5 py-0.5 font-mono text-xs text-[var(--fg)]">
                  .env.local
                </code>
                (never commit).
              </li>
              <li>
                <span className="text-[var(--accent)]">•</span> Avoid storing
                full raw emails long-term unless required.
              </li>
              <li>
                <span className="text-[var(--accent)]">•</span> Prefer sending
                “what changed + what to do” over forwarding entire threads.
              </li>
            </ul>
          </div>
        </Container>
      </main>
      <SiteFooter />
    </div>
  );
}

