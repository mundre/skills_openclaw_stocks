export type SkillCard = {
  title: string;
  summary: string;
  impact: string;
};

export type TechItem = {
  label: string;
  category: "foundation" | "modeling" | "delivery" | "quality";
};

export type WorkflowStep = {
  title: string;
  details: string;
};

export type Principle = {
  title: string;
  details: string;
};

export const heroStats = [
  { label: "Prompt iterations/week", value: "320+" },
  { label: "Automations maintained", value: "24" },
  { label: "Mean response latency", value: "1.2s" },
] as const;

export const llmSkills: SkillCard[] = [
  {
    title: "Code Synthesis",
    summary: "Generate production-ready TypeScript and React patterns from intent.",
    impact: "Faster delivery with strict typing and maintainable architecture.",
  },
  {
    title: "Tool Orchestration",
    summary: "Coordinate multi-step CLI and API workflows with deterministic checks.",
    impact: "Reduced manual toil and fewer deployment mistakes.",
  },
  {
    title: "Debug Intelligence",
    summary: "Trace regressions from stack traces to root causes across boundaries.",
    impact: "Shorter incident windows and reliable fixes.",
  },
  {
    title: "Test Authoring",
    summary: "Create robust test suites that capture edge cases and user journeys.",
    impact: "Higher confidence for refactors and releases.",
  },
  {
    title: "Architecture Guidance",
    summary: "Decompose features into composable modules with explicit contracts.",
    impact: "Cleaner scaling as complexity grows.",
  },
  {
    title: "UX & Copy Tuning",
    summary: "Refine messaging and interface affordances to improve clarity.",
    impact: "Better user trust and stronger product signal.",
  },
];

export const technologies: TechItem[] = [
  { label: "Next.js 16", category: "foundation" },
  { label: "React 19", category: "foundation" },
  { label: "TypeScript 5", category: "foundation" },
  { label: "Tailwind CSS 4", category: "foundation" },
  { label: "Framer Motion", category: "modeling" },
  { label: "Three.js + R3F", category: "modeling" },
  { label: "Lucide", category: "delivery" },
  { label: "OpenRouter", category: "delivery" },
  { label: "Vitest", category: "quality" },
  { label: "Testing Library", category: "quality" },
  { label: "ESLint", category: "quality" },
];

export const principles: Principle[] = [
  {
    title: "Typed boundaries first",
    details: "Every module has explicit input and output contracts before implementation.",
  },
  {
    title: "Automate verification",
    details: "Lint, tests, and builds run as standard gates instead of optional checks.",
  },
  {
    title: "Separation of concerns",
    details: "Presentation, data, and behavior are isolated to simplify maintenance.",
  },
  {
    title: "Performance as a feature",
    details: "Client code is minimized and rendering cost is measured continuously.",
  },
];

export const workflows: WorkflowStep[] = [
  {
    title: "Scope and model",
    details: "Capture goals, define types, and map dependencies before coding begins.",
  },
  {
    title: "Implement core path",
    details: "Build the smallest end-to-end slice with reusable and typed components.",
  },
  {
    title: "Instrument quality",
    details: "Add unit tests, accessibility checks, and lint rules to guard behavior.",
  },
  {
    title: "Polish and ship",
    details: "Tune performance, refine motion, and validate production build output.",
  },
];
