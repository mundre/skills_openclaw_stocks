import Link from "next/link";
import { Container } from "@/components/Container";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-[var(--stroke)] bg-[var(--panel)] px-3 py-1 text-xs text-[var(--muted)]">
      {children}
    </span>
  );
}

function Feature({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
      <div className="font-[var(--font-display)] text-xl tracking-tight">
        {title}
      </div>
      <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{body}</p>
    </div>
  );
}

export default function Home() {
  return (
    <div className="grain flex min-h-full flex-col">
      <SiteHeader />

      <main className="flex-1">
        <section className="py-16 sm:py-24">
          <Container>
            <div className="grid gap-10 lg:grid-cols-[1.3fr_0.7fr] lg:items-start">
              <div>
                <div className="flex flex-wrap gap-2">
                  <Pill>local-first</Pill>
                  <Pill>structured summaries</Pill>
                  <Pill>action-first</Pill>
                  <Pill>no noisy spam</Pill>
                </div>

                <h1 className="mt-6 font-[var(--font-display)] text-4xl leading-[1.05] tracking-tight sm:text-6xl">
                  Your inbox is a queue.
                  <br />
                  Emaily is the calm worker.
                </h1>

                <p className="mt-6 max-w-2xl text-base leading-7 text-[var(--muted)] sm:text-lg">
                  Emaily watches for new mail, turns long threads into a
                  decision-ready brief, and surfaces the next action. It is
                  designed for humans who want to stay in control, but stop
                  drowning.
                </p>

                <div id="start" className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
                  <a
                    className="inline-flex items-center justify-center rounded-full bg-[var(--accent)] px-6 py-3 text-sm font-semibold text-black shadow-[var(--shadow)] transition-transform hover:translate-y-[-1px]"
                    href="#demo"
                  >
                    See a real summary
                  </a>
                  <Link
                    className="inline-flex items-center justify-center rounded-full border border-[var(--stroke)] bg-[var(--panel)] px-6 py-3 text-sm font-semibold text-[var(--fg)] hover:bg-[var(--panel-strong)]"
                    href="/how-it-works"
                  >
                    How it works
                  </Link>
                </div>
              </div>

              <aside className="rounded-2xl border border-[var(--stroke)] bg-[color:rgba(0,0,0,0.35)] p-6 shadow-[var(--shadow)]">
                <div className="text-xs uppercase tracking-widest text-[var(--muted)]">
                  What you get
                </div>
                <ul className="mt-4 space-y-3 text-sm">
                  <li>
                    <span className="text-[var(--accent)]">•</span> From/Subject
                    + 2–3 line synopsis
                  </li>
                  <li>
                    <span className="text-[var(--accent)]">•</span> Requested
                    action (if any)
                  </li>
                  <li>
                    <span className="text-[var(--accent)]">•</span> Recommended
                    next steps
                  </li>
                  <li>
                    <span className="text-[var(--accent)]">•</span> Urgency
                    rating and why
                  </li>
                </ul>
                <div className="mt-6 rounded-xl border border-[var(--stroke)] bg-[var(--panel)] p-4 text-xs text-[var(--muted)]">
                  Designed to be readable in Discord, WhatsApp, or a terminal.
                  No dashboards required.
                </div>
              </aside>
            </div>
          </Container>
        </section>

        <section className="py-14">
          <Container>
            <div className="grid gap-5 md:grid-cols-3">
              <Feature
                title="Signal, not noise"
                body="Stateful UID tracking avoids repeats. Server-down alerts are throttled. You only get what changed."
              />
              <Feature
                title="Tells you what to do"
                body="Every summary ends in an actionable recommendation, with urgency and context."
              />
              <Feature
                title="Local-first by design"
                body="Runs inside your OpenClaw environment. Secrets stay on your box."
              />
            </div>
          </Container>
        </section>

        <section id="demo" className="py-16">
          <Container>
            <div className="flex items-end justify-between gap-6">
              <div>
                <h2 className="font-[var(--font-display)] text-3xl tracking-tight">
                  Example output
                </h2>
                <p className="mt-2 text-sm text-[var(--muted)]">
                  This is the shape Emaily aims to produce, consistently.
                </p>
              </div>
              <Link
                className="hidden text-sm text-[var(--muted)] hover:text-[var(--fg)] sm:inline"
                href="/security"
              >
                Why this is safe →
              </Link>
            </div>

            <div className="mt-6 overflow-hidden rounded-2xl border border-[var(--stroke)] bg-[color:rgba(0,0,0,0.45)] shadow-[var(--shadow)]">
              <div className="flex items-center justify-between border-b border-[var(--stroke)] px-4 py-3">
                <div className="text-xs text-[var(--muted)]">emaily.summary</div>
                <div className="flex gap-2">
                  <span className="h-2 w-2 rounded-full bg-[var(--accent)] opacity-80" />
                  <span className="h-2 w-2 rounded-full bg-white/30" />
                  <span className="h-2 w-2 rounded-full bg-white/20" />
                </div>
              </div>
              <pre className="overflow-x-auto p-5 text-xs leading-6 text-[var(--fg)]">
{`From: billing@vendor.com
Subject: Invoice overdue — action required

Synopsis:
  Vendor says invoice #1841 is 14 days overdue.
  Payment link included. Mentions service interruption risk.

Requested Action:
  Confirm payment date or pay immediately.

Recommended Actions:
  1) Verify invoice in accounting system.
  2) If valid, pay today and reply with confirmation.
  3) If already paid, reply with transaction reference.

Urgency: HIGH (payment escalation + service interruption risk)`}
              </pre>
            </div>
          </Container>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

