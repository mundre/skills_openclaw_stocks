export default function Principles() {
  const principles = [
    {
      title: "Local-first",
      body: "Prefer on-box services, files as state, and explicit configs. Data stays close by default.",
    },
    {
      title: "Minimal surprises",
      body: "Tools are used directly. If something needs approval, it is asked plainly.",
    },
    {
      title: "Quality gates",
      body: "No hand-wavy 'done'. Lint, build, and basic verification are non-negotiable.",
    },
  ];

  return (
    <section id="principles" className="atmo flex min-h-full flex-col">
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
            {principles.map((principle) => (
              <div
                key={principle.title}
                className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)] scroll-reveal"
              >
                <div className="font-[var(--font-display)] text-xl tracking-tight text-[var(--accent2)]">
                  {principle.title}
                </div>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
                  {principle.body}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </main>
      <SiteFooter />
    </section>
  );
}

const Container = ({ children }: { children: React.ReactNode }) => (
  <div className="container mx-auto px-4">{children}</div>
);
const SiteHeader = () => (
  <header className="bg-black/60 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
    <div className="container mx-auto flex items-center justify-between py-3">
      <a href="/" className="text-xl font-bold gradient-text">AMY</a>
      <div className="flex gap-4">
        <a href="/" className="hover:text-accent">Home</a>
        <a href="#principles" className="hover:text-accent">Principles</a>
        <a href="#workflows" className="hover:text-accent">Workflows</a>
        <a href="#contact" className="hover:text-accent">Contact</a>
      </div>
    </div>
  </header>
);
const SiteFooter = () => (
  <footer className="border-t border-white/10 py-6 text-center text-muted">
    © {new Date().getFullYear()} AMY – Personal Ops Agent
  </footer>
);