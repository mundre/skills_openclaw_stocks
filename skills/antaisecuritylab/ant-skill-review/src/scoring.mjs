/**
 * Deterministic scoring for skill security analysis results.
 *
 * Each finding has an enumerated `type` (with base severity) and a
 * model-assigned `severity` (low/medium/high/critical).
 * Per-finding score = max(type base score, severity score).
 * Layer score = max across all findings.
 *
 * Risk level: safe(0), low(1-3), medium(4-6), high(7-8), critical(9-10).
 * overall_risk = worst across layers 1-6 (layer 7 excluded).
 * recommendation = install (safe/low), caution (medium), do_not_install (high/critical).
 */

// Type → base severity (minimum score for this type)
const TYPE_SEVERITY = {
  prompt_injection: {
    direct_injection: 8,
    malicious_instruction: 7,
    remote_prompt: 8,
    jailbreak: 8,
    other: 5,
  },
  dynamic_code: {
    remote_execution: 8,
    other: 8,
  },
  obfuscation_binary: {
    obfuscated_script: 5,
    binary: 5,
    other: 4,
  },
  system_modification: {
    global_install: 3,
    profile_modification: 5,
    cron_job: 5,
    file_write_outside: 4,
    other: 3,
  },
  dependencies: {
    npm: 0,
    pypi: 0,
    homebrew: 0,
    apt: 0,
    go: 0,
    cargo: 0,
    cli_tool: 0,
    other: 0,
  },
  malicious_behavior: {
    credential_theft: 9,
    data_exfiltration: 9,
    sandbox_escape: 8,
    undeclared_capability: 5,
    other: 5,
  },
  code_quality: {
    hardcoded_secret: 4,
    internal_api: 2,
    insecure_config: 3,
    broad_credential_access: 4,
    vulnerable_code: 3,
    phantom_dependency: 2,
    other: 2,
  },
};

// Model-assigned severity → score
const SEVERITY_SCORE = {
  low: 2,
  medium: 5,
  high: 8,
  critical: 10,
};

function scoreToRisk(score) {
  if (score <= 0) return "safe";
  if (score <= 3) return "low";
  if (score <= 6) return "medium";
  if (score <= 8) return "high";
  return "critical";
}

// Per-layer score caps (prevents over-escalation without deep verification)
const LAYER_SCORE_CAP = {
  // dependencies cap removed: three-tier severity (low/medium/high) provides
  // sufficient granularity — unknown packages get medium, only confirmed
  // suspicious names reach high/critical.
};

function scoreFindings(layerKey, findings) {
  if (!findings || findings.length === 0) return 0;

  const typeMap = TYPE_SEVERITY[layerKey] || {};
  const cap = LAYER_SCORE_CAP[layerKey] ?? 10;
  let maxScore = 0;

  for (const f of findings) {
    const typeBase = typeMap[f.type] ?? typeMap.other ?? 0;
    const sevScore = SEVERITY_SCORE[f.severity] ?? 0;
    maxScore = Math.max(maxScore, typeBase, sevScore);
  }

  return Math.min(maxScore, cap);
}

const LAYER_KEYS = [
  "prompt_injection",
  "malicious_behavior",
  "dynamic_code",
  "obfuscation_binary",
  "dependencies",
  "system_modification",
  "code_quality",
];

// Layers 1-6 contribute to overall risk (not layer 7 = code_quality)
const OVERALL_LAYERS = new Set(LAYER_KEYS.slice(0, 6));

/**
 * Mutates `result` in-place, adding layer_scores and
 * overall_risk/recommendation at top level.
 */
export function computeScores(result) {
  if (!result.findings) return;

  result.layer_scores = {};
  let worstOverallScore = 0;

  for (const key of LAYER_KEYS) {
    const findings = result.findings[key];
    if (!findings) continue;

    const score = scoreFindings(key, findings);
    const risk = scoreToRisk(score);
    result.layer_scores[key] = { score, risk };

    if (OVERALL_LAYERS.has(key)) {
      worstOverallScore = Math.max(worstOverallScore, score);
    }
  }

  result.overall_risk = scoreToRisk(worstOverallScore);

  if (worstOverallScore >= 7) {
    result.recommendation = "do_not_install";
  } else if (worstOverallScore >= 4) {
    result.recommendation = "caution";
  } else {
    result.recommendation = "install";
  }
}
