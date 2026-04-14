/** Collect full agent text output */
export function collectAgentText(agent) {
  let text = "";
  agent.subscribe((event) => {
    if (
      event.type === "message_update" &&
      event.assistantMessageEvent.type === "text_delta"
    ) {
      text += event.assistantMessageEvent.delta;
    }
  });
  return () => text;
}

/** Stream agent text deltas in real time */
export function attachStreamLogger(agent, label, write) {
  let needLabel = true;
  agent.subscribe((event) => {
    if (
      event.type === "message_update" &&
      event.assistantMessageEvent.type === "text_delta"
    ) {
      if (needLabel) {
        write(`\n  [${label}] `);
        needLabel = false;
      }
      write(event.assistantMessageEvent.delta);
    }
    if (event.type === "tool_execution_start") {
      needLabel = true;
    }
  });
}

/** Subscribe to log tool calls */
export function attachToolLogger(agent, write) {
  agent.subscribe((event) => {
    switch (event.type) {
      case "tool_execution_start":
        write(
          `  [tool] ${event.toolName}: ${JSON.stringify(event.args)}\n`
        );
        break;
      case "tool_execution_end":
        if (event.isError) {
          const errMsg = typeof event.result === "string"
            ? event.result
            : event.result?.message || JSON.stringify(event.result);
          write(
            `  [tool error] ${event.toolName}: ${errMsg}\n`
          );
        }
        break;
    }
  });
}

/** Extract JSON from agent text (handles ```json ... ``` wrapper) */
export function extractJson(text) {
  // Find ALL ```json ... ``` blocks and try from last to first,
  // since the prompt instructs the model to put the JSON block last.
  const fencedRe = /```json\s*\n?([\s\S]*?)\n?\s*```/g;
  const blocks = [];
  let m;
  while ((m = fencedRe.exec(text)) !== null) blocks.push(m[1]);

  for (let i = blocks.length - 1; i >= 0; i--) {
    try { return JSON.parse(blocks[i]); } catch {}
  }

  // Fallback: find the last top-level JSON object
  const rawRe = /\{[\s\S]*\}/g;
  const rawBlocks = [];
  while ((m = rawRe.exec(text)) !== null) rawBlocks.push(m[0]);

  for (let i = rawBlocks.length - 1; i >= 0; i--) {
    try { return JSON.parse(rawBlocks[i]); } catch {}
  }

  throw new Error("No JSON found in agent output");
}

/** Format a text report and return as a string */
export function printTextReport(result, { color = process.stdout.isTTY } = {}) {
  const c = color
    ? {
        critical: "\x1b[91m",
        high: "\x1b[31m",
        medium: "\x1b[33m",
        low: "\x1b[36m",
        safe: "\x1b[32m",
        reset: "\x1b[0m",
        bold: "\x1b[1m",
        dim: "\x1b[2m",
      }
    : { critical: "", high: "", medium: "", low: "", safe: "", reset: "", bold: "", dim: "" };

  const colorRisk = (r) =>
    `${c[r] || ""}${c.bold}${(r || "unknown").toUpperCase()}${c.reset}`;

  let buf = "";
  const out = (s) => { buf += s; };

  out(`\n${c.bold}═══════════════════════════════════════════${c.reset}\n`);
  out(`${c.bold}Name: ${result.skill_name || "unknown"}${c.reset}\n`);
  if (result.skill_version) out(`Version: ${result.skill_version}\n`);
  if (result.skill_description)
    out(`Description: ${c.dim}${result.skill_description}${c.reset}\n`);
  out(`Overall Risk: ${colorRisk(result.overall_risk)}\n`);
  out(`${c.bold}═══════════════════════════════════════════${c.reset}\n\n`);

  const layerNames = {
    prompt_injection: "Layer 1 — Prompt Injection",
    malicious_behavior: "Layer 2 — Malicious Behavior",
    dynamic_code: "Layer 3 — Dynamic Code Loading",
    obfuscation_binary: "Layer 4 — Obfuscation & Binary",
    dependencies: "Layer 5 — Dependencies & Supply Chain",
    system_modification: "Layer 6 — System Modification",
    code_quality: "Layer 7 — Code Quality Issues",
  };

  for (const [key, label] of Object.entries(layerNames)) {
    const findings = result.findings?.[key];
    const scores = result.layer_scores?.[key];
    if (!scores) continue;

    const riskScore = Math.min(Math.max(Math.round(scores.score), 0), 10);
    const scoreBar = "★".repeat(riskScore) + "☆".repeat(10 - riskScore);

    const risk = scores.risk || "safe";
    const riskTag = colorRisk(risk) + " ".repeat(8 - risk.length);
    out(`  ${riskTag} ${scoreBar} ${c.dim}${riskScore}/10${c.reset}  ${label}\n`);

    if (findings && findings.length > 0) {
      for (const f of findings.slice(0, 5)) {
        const lineRef = f.line_start ? (f.line_end && f.line_end !== f.line_start ? `${f.line_start}-${f.line_end}` : `${f.line_start}`) : "";
        const loc = f.file ? `${f.file}${lineRef ? ":" + lineRef : ""}` : "";
        const tag = f.type || "";
        const sev = f.severity ? `[${f.severity}]` : "";
        const detail = f.detail || f.snippet || "";
        const detailSuffix = detail ? ` — ${detail}` : "";
        out(`    ${c.dim}→ ${loc} ${tag} ${sev}${detailSuffix}${c.reset}\n`);
      }
      if (findings.length > 5) {
        out(`    ${c.dim}  ... and ${findings.length - 5} more${c.reset}\n`);
      }
    }
  }

  // Undeclared capabilities (from malicious_behavior findings)
  const undeclared = (result.findings?.malicious_behavior || [])
    .filter((f) => f.type && f.type.includes("undeclared"));
  if (undeclared.length) {
    out(`\n  ${c.bold}Undeclared Capabilities:${c.reset}\n`);
    for (const f of undeclared) {
      out(`    ${c.dim}→ ${f.detail || f.snippet || f.type}${c.reset}\n`);
    }
  }

  // Deep analysis
  if (result.deep_analysis) {
    const da = result.deep_analysis;
    out(`\n${c.bold}--- Deep Analysis ---${c.reset}\n`);
    if (da.urls?.length) {
      out(`  ${c.bold}URLs investigated: ${da.urls.length}${c.reset}\n`);
      for (const u of da.urls) {
        out(`    → ${u.url} [${u.status}] risk=${u.risk}\n`);
      }
    }
    if (da.dependencies?.length) {
      out(`  ${c.bold}Dependencies investigated: ${da.dependencies.length}${c.reset}\n`);
      for (const d of da.dependencies) {
        out(`    → ${d.name} [${d.exists ? "exists" : "NOT FOUND"}] risk=${d.risk}\n`);
      }
    }
    if (da.binaries?.length) {
      out(`  ${c.bold}Binaries analyzed: ${da.binaries.length}${c.reset}\n`);
    }
    if (da.decoded_blobs?.length) {
      out(`  ${c.bold}Blobs decoded: ${da.decoded_blobs.length}${c.reset}\n`);
    }
    out(`  Deep Risk: ${colorRisk(da.overall_deep_risk || "safe")}\n`);
    if (da.summary) out(`  ${da.summary}\n`);
  }

  out(`\n  ${c.bold}Summary:${c.reset} ${result.summary || ""}\n`);
  out(`  ${c.bold}Recommendation:${c.reset} ${result.recommendation || ""}\n\n`);

  return buf;
}
