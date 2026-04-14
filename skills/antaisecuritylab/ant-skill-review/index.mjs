#!/usr/bin/env node
import { setMaxListeners } from "node:events";
setMaxListeners(0);
import { openSync, readFileSync, writeFileSync, writeSync } from "node:fs";
import { join } from "node:path";
import { Agent } from "@mariozechner/pi-agent-core";
import { parseArgs } from "./src/cli.mjs";
import {
  makeBashTool,
  makeNpmPackageAnalysisTool,
  makePypiPackageAnalysisTool,
  makeUrlAnalysisTool,
  makeBinaryAnalysisTool,
} from "./src/tools.mjs";
import { loadConfig, getConfig, getModelConfig } from "./src/config.mjs";
import {
  getExplorePrompt,
  getDeepAnalysisPrompt,
} from "./src/prompts.mjs";
import { prescan } from "./src/prescan.mjs";
import {
  collectAgentText,
  attachToolLogger,
  attachStreamLogger,
  extractJson,
  printTextReport,
} from "./src/report.mjs";
import { computeScores } from "./src/scoring.mjs";

const { configFile, pre, deep, lang, jsonOutput, outputFile, logFile, verbose, skillDir } = parseArgs();
loadConfig(configFile);

// -- Log writer: routes detailed logs to stderr (-v) and/or file (--log) --
const logWriters = [];
if (verbose) logWriters.push((s) => process.stderr.write(s));
if (logFile) {
  const logFd = openSync(logFile, "w");
  logWriters.push((s) => writeSync(logFd, typeof s === "string" ? s : Buffer.from(s)));
}
const log = logWriters.length > 0
  ? (s) => { for (const w of logWriters) w(s); }
  : null;

// Status messages always go to stderr
const status = (s) => process.stderr.write(s);

status(`Scanning: ${skillDir}\n`);
status(`Mode: ${pre ? "prescan-only" : deep ? "deep" : "standard"}\n\n`);

// -- Pre-scan: collect file info and dangerous patterns --
status(`--- Pre-scan ---\n`);
let prescanResult = prescan(skillDir);

// -- Read _meta.json if present, append to prescan --
try {
  const meta = JSON.parse(
    readFileSync(join(skillDir, "_meta.json"), "utf-8")
  );
  const parts = [];
  if (meta.slug) parts.push(`- slug: ${meta.slug}`);
  if (meta.version) parts.push(`- version: ${meta.version}`);
  if (meta.publishedAt) {
    const date = new Date(meta.publishedAt).toLocaleString();
    parts.push(`- publishedAt: ${date}`);
  }
  if (parts.length) {
    const metaBlock = `\n## Meta Info from ./_meta.json\n${parts.join("\n")}`;
    prescanResult += metaBlock;
  }
} catch {}

if (pre) {
  const out = prescanResult + "\n";
  if (outputFile) {
    writeFileSync(outputFile, out);
    status(`\nReport saved to ${outputFile}\n`);
  } else {
    process.stdout.write(out);
  }
  process.exit(0);
}

if (log) log(prescanResult + "\n");

// -- Phase 1: Explore (surface all potential risks) --
status(`--- Phase 1: Explore ---\n`);

const exploreAgent = new Agent({
  initialState: {
    systemPrompt: getExplorePrompt(lang),
    model: getModelConfig(),
    tools: [makeBashTool(skillDir)],
  },
  getApiKey: async () => getConfig().apiKey,
});

const getExploreText = collectAgentText(exploreAgent);
if (log) {
  attachToolLogger(exploreAgent, log);
  attachStreamLogger(exploreAgent, "ExploreAgent", log);
}

try {
  await exploreAgent.prompt(
    `Explore the skill package. Flag all potential security risks by layer.\n\n# Pre-scan Results\n\n${prescanResult}`
  );
} catch (err) {
  status(`Agent error (explore): ${err.message}\n`);
  process.exit(1);
}

const analysisText = getExploreText();

let result;
try {
  result = extractJson(analysisText);
} catch (err) {
  status(`\nFailed to parse JSON from explore agent output.\n`);
  if (log) log(`Raw output:\n${analysisText}\n`);
  process.exit(1);
}

// Deterministic scoring — overwrite any model-provided scores
computeScores(result);

// -- Phase 2: Deep analysis (if --deep) --
if (deep) {
  status(`\n--- Phase 2: Deep Analysis ---\n`);

  // Check if there are any findings worth deep-analyzing
  const hasDeepWork = ["prompt_injection", "dynamic_code", "obfuscation_binary", "dependencies"]
    .some((key) => (result.findings?.[key] || []).length > 0);

  if (!hasDeepWork) {
    status(`No items to deep-analyze, skipping.\n`);
  } else {

    const deepAgent = new Agent({
      initialState: {
        systemPrompt: getDeepAnalysisPrompt(lang),
        model: getModelConfig(),
        tools: [
          makeNpmPackageAnalysisTool(),
          makePypiPackageAnalysisTool(),
          makeUrlAnalysisTool(),
          makeBinaryAnalysisTool(skillDir),
        ],
      },
      getApiKey: async () => getConfig().apiKey,
    });

    const getDeepText = collectAgentText(deepAgent);
    if (log) {
      attachToolLogger(deepAgent, log);
      attachStreamLogger(deepAgent, "DeepAgent", log);
    }

    try {
      await deepAgent.prompt(
        `Investigate the following ExploreAgent scan results. Identify URLs, dependencies, and binaries that need deep analysis, then use the provided tools to verify them.\n\n${JSON.stringify(result, null, 2)}`
      );
    } catch (err) {
      status(`Agent error (deep): ${err.message}\n`);
      process.exit(1);
    }

    let deepResult;
    try {
      deepResult = extractJson(getDeepText());
    } catch (err) {
      status(`\nFailed to parse deep analysis JSON.\n`);
      if (log) log(`Raw output:\n${getDeepText()}\n`);
      process.exit(1);
    }

    result.deep_analysis = deepResult.deep_analysis;

    // Reconcile deep analysis risk into overall result
    reconcileDeepRisk(result);
  }
}

/**
 * If deep analysis found a higher risk, escalate overall_risk and recommendation.
 */
function reconcileDeepRisk(result) {
  const RISK_ORDER = ["safe", "low", "medium", "high", "critical"];
  const deepRisk = result.deep_analysis?.overall_deep_risk;
  if (!deepRisk) return;

  const currentIdx = RISK_ORDER.indexOf(result.overall_risk);
  const deepIdx = RISK_ORDER.indexOf(deepRisk);

  if (deepIdx > currentIdx) {
    result.overall_risk = deepRisk;
  }

  // Re-derive recommendation from the (possibly escalated) overall_risk
  const finalIdx = RISK_ORDER.indexOf(result.overall_risk);
  if (finalIdx >= 3) {       // high or critical
    result.recommendation = "do_not_install";
  } else if (finalIdx >= 2) { // medium
    result.recommendation = "caution";
  } else {                    // safe or low
    result.recommendation = "install";
  }
}

// -- Output --
if (outputFile) {
  const content = jsonOutput
    ? JSON.stringify(result, null, 2) + "\n"
    : printTextReport(result, { color: false });
  writeFileSync(outputFile, content);
  status(`\nReport saved to ${outputFile}\n`);
  process.exit(0);
} else {
  const content = jsonOutput
    ? JSON.stringify(result, null, 2) + "\n"
    : printTextReport(result);
  process.stdout.write(content, () => process.exit(0));
}
