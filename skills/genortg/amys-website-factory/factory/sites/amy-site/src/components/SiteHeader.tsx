import Link from "next/link";
import { Container } from "@/components/Container";

const links = [
  { href: "/principles", label: "Principles" },
  { href: "/workflows", label: "Workflows" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--stroke)] bg-[color:rgba(7,8,20,0.6)] backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl border border-[var(--stroke)] bg-[var(--panel)] shadow-[var(--shadow)]">
              <span className="font-[var(--font-display)] text-[11px] tracking-tight text-[var(--accent)]">
                AMY
              </span>
            </span>
            <div className="leading-tight">
              <div className="text-sm font-semibold">Agent ops</div>
              <div className="text-xs text-[var(--muted)]">
                proactive, local-first
              </div>
            </div>
          </Link>

          <nav className="hidden items-center gap-6 text-sm sm:flex">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="text-[var(--muted)] hover:text-[var(--fg)]"
              >
                {l.label}
              </Link>
            ))}
            <a
              href="#loop"
              className="rounded-full border border-[var(--stroke)] bg-[var(--panel)] px-4 py-2 text-[var(--fg)] hover:bg-white/10"
            >
              See the loop
            </a>
          </nav>

          <a
            href="#start"
            className="inline-flex items-center rounded-full bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-black shadow-[var(--shadow)] transition-transform hover:translate-y-[-1px]"
          >
            Build with AMY
          </a>
        </div>
      </Container>
    </header>
  );
}

