import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "How Emaily works",
  description: "A practical overview of Emaily’s pipeline and reliability model.",
};

function Step({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
      <div className="flex items-baseline justify-between">
        <div className="font-[var(--font-display)] text-2xl tracking-tight">
          {title}
        </div>
        <div className="font-mono text-xs text-[var(--muted)]">{n}</div>
      </div>
      <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{body}</p>
    </div>
  );
}

export default function HowItWorks() {
  return (
    <div className="grain flex min-h-full flex-col">
      <SiteHeader />
      <main className="flex-1 py-16 sm:py-24">
        <Container>
          <h1 className="font-[var(--font-display)] text-4xl tracking-tight sm:text-5xl">
            How it works
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            Emaily is built to be boringly reliable. It reads email, summarizes
            and classifies, then notifies you with structured output. The goal is
            not “AI vibes”. The goal is: you act faster, with less cognitive
            overhead.
          </p>

          <div className="mt-10 grid gap-5 lg:grid-cols-2">
            <Step
              n="01"
              title="Poll"
              body="A scheduled check runs (cron). It connects to IMAP, searches for new/unread mail, and fetches the minimal content needed for summarization."
            />
            <Step
              n="02"
              title="Deduplicate"
              body="A local state file stores the last processed UID. Only newer messages are handled. This prevents repeat notifications and makes runs idempotent."
            />
            <Step
              n="03"
              title="Summarize"
              body="Each message is distilled into a short synopsis plus explicit action items. Long threads are reduced to decision-ready context."
            />
            <Step
              n="04"
              title="Notify"
              body="Emaily sends a single concise summary to your chosen channel(s). Alerts for failures (like server-down) are throttled to avoid spam." 
            />
          </div>

          <div className="mt-10 rounded-2xl border border-[var(--stroke)] bg-[color:rgba(0,0,0,0.35)] p-6 shadow-[var(--shadow)]">
            <div className="text-xs uppercase tracking-widest text-[var(--muted)]">
              Reliability notes
            </div>
            <ul className="mt-4 space-y-3 text-sm leading-7 text-[var(--muted)]">
              <li>
                <span className="text-[var(--accent)]">•</span> Runs are safe
                to repeat. State makes it idempotent.
              </li>
              <li>
                <span className="text-[var(--accent)]">•</span> “Server down”
                alerts are rate-limited so you do not get pinged every 15
                minutes.
              </li>
              <li>
                <span className="text-[var(--accent)]">•</span> Output stays
                structured. The format is a contract, not a suggestion.
              </li>
            </ul>
          </div>
        </Container>
      </main>
      <SiteFooter />
    </div>
  );
}

