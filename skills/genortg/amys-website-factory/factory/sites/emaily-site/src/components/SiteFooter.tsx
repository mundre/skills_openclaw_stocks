import Link from "next/link";
import { Container } from "@/components/Container";

export function SiteFooter() {
  return (
    <footer className="border-t border-[var(--stroke)]">
      <Container>
        <div className="flex flex-col gap-6 py-10 text-sm sm:flex-row sm:items-center sm:justify-between">
          <div className="text-[var(--muted)]">
            Emaily runs as an agent, not a SaaS. Keep your data close.
          </div>
          <div className="flex flex-wrap gap-5">
            <Link className="text-[var(--muted)] hover:text-[var(--fg)]" href="/how-it-works">
              How it works
            </Link>
            <Link className="text-[var(--muted)] hover:text-[var(--fg)]" href="/security">
              Security
            </Link>
            <a
              className="text-[var(--muted)] hover:text-[var(--fg)]"
              href="https://docs.openclaw.ai"
              target="_blank"
              rel="noopener noreferrer"
            >
              OpenClaw docs
            </a>
          </div>
        </div>
      </Container>
    </footer>
  );
}

