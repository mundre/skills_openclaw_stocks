import Link from "next/link";
import { Container } from "@/components/Container";
import { Mark } from "@/components/Mark";

const links = [
  { href: "/how-it-works", label: "How it works" },
  { href: "/security", label: "Security" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--stroke)] bg-[color:rgba(11,10,8,0.55)] backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="group flex items-center gap-3">
            <span className="text-[var(--accent)]">
              <Mark className="transition-transform duration-300 group-hover:rotate-[-4deg]" />
            </span>
            <div className="leading-tight">
              <div className="font-[var(--font-display)] text-lg tracking-tight">
                Emaily
              </div>
              <div className="text-xs text-[var(--muted)]">
                inbox triage, done quietly
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
              href="#demo"
              className="rounded-full border border-[var(--stroke)] bg-[var(--panel)] px-4 py-2 text-[var(--fg)] shadow-[var(--shadow)] hover:bg-[var(--panel-strong)]"
            >
              See output
            </a>
          </nav>

          <a
            href="#start"
            className="inline-flex items-center rounded-full bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-black shadow-[var(--shadow)] transition-transform hover:translate-y-[-1px]"
          >
            Get the workflow
          </a>
        </div>
      </Container>
    </header>
  );
}

