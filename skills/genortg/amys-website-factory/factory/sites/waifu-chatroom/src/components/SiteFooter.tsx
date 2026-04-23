import Link from "next/link";
import { Container } from "@/components/Container";

export function SiteFooter() {
  return (
    <footer className="border-t border-[var(--stroke)]">
      <Container>
        <div className="flex flex-col gap-6 py-10 text-sm sm:flex-row sm:items-center sm:justify-between">
          <div className="text-[var(--muted)]">
            AMY is a workflow machine. The vibe is optional.
          </div>
          <div className="flex flex-wrap gap-5">
            <Link className="text-[var(--muted)] hover:text-[var(--fg)]" href="/principles">
              Principles
            </Link>
            <Link className="text-[var(--muted)] hover:text-[var(--fg)]" href="/workflows">
              Workflows
            </Link>
          </div>
        </div>
      </Container>
    </footer>
  );
}

