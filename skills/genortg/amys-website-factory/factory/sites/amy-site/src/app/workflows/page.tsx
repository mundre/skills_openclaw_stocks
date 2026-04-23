export default function Workflows() {
  const steps = [
    {
      title: "Scaffold",
      body: "Create a new Next.js project with TypeScript, Tailwind, and ESLint.",
    },
    {
      title: "Pick a bold design direction",
      body: "Choose one aesthetic tone and commit fully—no timid gradients.",
    },
    {
      title: "Implement layout + components",
      body: "Build the layout, nav, and reusable UI using shadcn/ui.",
    },
    {
      title: "Write real copy",
      body: "Avoid lorem ipsum. Use actual messaging about AMY.",
    },
    {
      title: "Add subpages",
      body: "Create at least 2–3 subpages (e.g., Principles, Workflows, Contact).",
    },
    {
      title: "Lint & build",
      body: "Run npm run lint and npm run build to ensure quality.",
    },
    {
      title: "Commit meaningful increments",
      body: "Small, focused commits with clear messages.",
    },
    {
      title: "Document for reuse",
      body: "Write a README with instructions for future iterations.",
    },
  ];

  return (
    <section id="workflows" className="atmo flex min-h-full flex-col">
      <SiteHeader />
      <main className="flex-1 py-16 sm:py-24">
        <Container>
          <h1 className="font-[var(--font-display)] text-4xl tracking-tight sm:text-5xl">
            Workflows
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
            These are patterns AMY uses to build sites and keep systems stable.
          </p>

          <div className="mt-10 space-y-6">
            {steps.map((step, index) => (
              <div
                key={step.title}
                className={`rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)] scroll-reveal ${
                  index % 2 === 0 ? "" : ""
                }`}
              >
                <div className="font-[var(--font-display)] text-xl tracking-tight text-[var(--accent2)]">
                  {step.title}
                </div>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
                  {step.body}
                </p>
              </div>
            ))}
          </div>

          {/* Tip */}
          <section className="mt-16">
            <h2 className="font-[var(--font-display)] text-3xl tracking-tight sm:text-4xl mb-8 text-center">
              Tip
            </h2>
            <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)] relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-accent/5 rounded-full -mr-8 -mt-8 blur-3xl"></div>
              <div className="text-xs uppercase tracking-widest text-[var(--muted)]">
                Workflow
              </div>
              <pre className="mt-3 overflow-x-auto p-2 text-xs leading-6 text-[var(--fg)]">
{`1) Scaffold (Next.js + TS + Tailwind)
2) Pick one bold design direction
3) Implement layout + components
4) Write real copy (no lorem)
5) Add 1–2 subpages
6) npm run lint && npm run build
7) Commit meaningful increments
8) Document the workflow for reuse`}
              </pre>
              <div className="mt-6 rounded-2xl border border-[var(--stroke)] bg-black/20 p-4">
                <p className="text-sm leading-7 text-[var(--muted)]">
                  Client components are expensive. Keep them small, isolated, and justified. Server components do the heavy lifting.
                </p>
              </div>
            </div>
          </section>
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