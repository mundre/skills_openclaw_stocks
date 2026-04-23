"use client";

import { useMemo, useState } from "react";

type Mode = "observe" | "plan" | "ship";

const MODES: Array<{ mode: Mode; title: string; body: string }> = [
  {
    mode: "observe",
    title: "Observe",
    body: "Scan signals (logs, inbox, cron runs). Find the constraint that actually blocks progress.",
  },
  {
    mode: "plan",
    title: "Plan",
    body: "Pick the smallest safe change that moves the system. Prefer patches over rewrites.",
  },
  {
    mode: "ship",
    title: "Ship",
    body: "Execute, verify (lint/build), commit, document. No mystery steps.",
  },
];

export function AgentLoop() {
  const [mode, setMode] = useState<Mode>("observe");
  const current = useMemo(
    () => MODES.find((m) => m.mode === mode) ?? MODES[0],
    [mode]
  );

  return (
    <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-6 shadow-[var(--shadow)]">
      <div className="flex flex-wrap gap-2">
        {MODES.map((m) => (
          <button
            key={m.mode}
            type="button"
            onClick={() => setMode(m.mode)}
            className={
              "rounded-full px-4 py-2 text-xs font-semibold transition-colors " +
              (m.mode === mode
                ? "bg-[var(--accent)] text-black"
                : "border border-[var(--stroke)] bg-black/20 text-[var(--fg)] hover:bg-white/10")
            }
          >
            {m.title}
          </button>
        ))}
      </div>

      <div className="mt-5">
        <div className="font-[var(--font-display)] text-xl tracking-tight text-[var(--accent2)]">
          {current.title}
        </div>
        <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{current.body}</p>
      </div>
    </div>
  );
}

