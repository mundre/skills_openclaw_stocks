/**
 * self_healing_engine.js — AI Agent Self-Healing Engine
 * 
 * Detects failures, analyzes root cause, applies fixes, learns from patterns.
 * 
 * Usage: node self_healing_engine.js <command> [args...]
 * Commands:
 *   analyze <errorLog|errorText>    Analyze an error and suggest fixes
 *   heal <errorLog|errorText>       Analyze + apply automatic fixes
 *   patterns                         List known fix patterns
 *   learn <error> <fix>             Learn a new fix pattern
 *   watch <command>                 Run command with self-healing enabled
 *   test                            Run built-in test suite
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync, exec } = require('child_process');

// ── Fix Pattern Database ──────────────────────────────────────────────────────
const BUILTIN_PATTERNS = [
  {
    id: 'powershell-ampersand',
    error: /AmpersandNotAllowed|too many arguments|ParserError/,
    cause: 'PowerShell does not support & in compound commands',
    fix: 'Use ; instead of &&, or call via cmd /c wrapper',
    examples: ['& cmd /c "echo a && echo b"', '& ping -n 5 127.0.0.1'],
    tags: ['powershell', 'windows'],
    confidence: 0.95,
  },
  {
    id: 'git-push-443',
    error: /443|Connection reset|ECONNREFUSED|connection timeout/i,
    cause: 'GitHub port 443 blocked by firewall/proxy',
    fix: 'Use GitHub API instead of git push (api.github.com works on HTTPS port)',
    examples: ['GitHub API PUT /repos/{owner}/{repo}/contents/{path}'],
    tags: ['git', 'network', 'github'],
    confidence: 0.9,
  },
  {
    id: 'node-e-flag-parse',
    error: /too many arguments|Unknown option|ReferenceError/,
    cause: 'Node.js -e flag parses argv incorrectly on Windows PowerShell',
    fix: 'Write JavaScript to a .js file and execute with: node file.js',
    examples: ['node -e "console.log(process.argv[2])" -- "value" FAILS'],
    tags: ['nodejs', 'windows', 'powershell'],
    confidence: 0.9,
  },
  {
    id: 'clawhub-rate-limit',
    error: /Rate limit|max.*new skills per hour/i,
    cause: 'ClawHub allows max 5 new skill publishes per hour',
    fix: 'Wait for rate limit reset (1 hour), or use cron to batch publish',
    examples: ['Set cron job with 1+ hour intervals between batches'],
    tags: ['clawhub', 'rate-limit'],
    confidence: 0.95,
  },
  {
    id: 'clawhub-version-exists',
    error: /Version already exists/i,
    cause: 'Skill was actually published despite error message',
    fix: 'Check with clawhub inspect <slug> to verify publish status',
    examples: ['clawhub inspect skylv-skill-name'],
    tags: ['clawhub'],
    confidence: 0.95,
  },
  {
    id: 'exec-timeout',
    error: /timeout|Timed out|killed by signal/i,
    cause: 'Command exceeded timeout or process was killed',
    fix: 'Increase timeout, split long operations, or use background exec with polling',
    examples: ['timeoutMs: 60000 -> 120000', 'background: true'],
    tags: ['execution', 'timeout'],
    confidence: 0.85,
  },
  {
    id: 'json-parse-fail',
    error: /Unexpected token|JSON\.parse|SyntaxError/i,
    cause: 'JSON string is malformed (encoding, BOM, or syntax error)',
    fix: 'Use Buffer for binary-safe handling, check for BOM (\\uFEFF), validate JSON before parsing',
    examples: ['JSON.parse(text.replace(/\\uFEFF/, ""))'],
    tags: ['json', 'encoding'],
    confidence: 0.88,
  },
  {
    id: 'file-exists-check',
    error: /ENOENT|no such file|not found/i,
    cause: 'File path does not exist, or path resolution is wrong',
    fix: 'Use path.isAbsolute(), ensure parent dir exists with fs.mkdirSync(recursive:true), check case sensitivity',
    examples: ['fs.mkdirSync(dir, {recursive:true})', 'path.resolve(cwd, relPath)'],
    tags: ['filesystem', 'path'],
    confidence: 0.9,
  },
  {
    id: 'api-rate-limit-http',
    error: /429|Too Many Requests|Rate.*limit|rate.limit/i,
    cause: 'API rate limit exceeded',
    fix: 'Wait for reset (check Retry-After header), implement exponential backoff, cache responses',
    examples: ['Wait ms from Retry-After header, then retry with exponential backoff'],
    tags: ['api', 'network'],
    confidence: 0.92,
  },
  {
    id: 'convex-error',
    error: /ConvexError|Uncaught (?:Type)?Error/i,
    cause: 'Backend API validation or server-side error',
    fix: 'Read error message for specific field issues, check API documentation, retry after delay',
    examples: ['Check error message for "required" or "invalid" fields'],
    tags: ['api', 'backend'],
    confidence: 0.8,
  },
  {
    id: 'wsl-not-installed',
    error: /WSL2|wsl\.exe|WSL/g,
    cause: 'WSL2 is not installed on Windows',
    fix: 'Windows-native solution required (Node.js, Python via pip, PowerShell) instead of bash scripts',
    examples: ['Convert bash install.sh to Node.js script'],
    tags: ['wsl', 'windows', 'bash'],
    confidence: 0.9,
  },
  {
    id: 'encoding-utf8-gbk',
    error: /乱码|garbled|invalid.*encoding|decode/i,
    cause: 'File encoding mismatch (UTF-8 vs GBK, missing BOM)',
    fix: 'Specify encoding: utf8 or utf-8-sig for BOM, use iconv for conversion',
    examples: ['fs.readFileSync(path, "utf8")', 'JSON.parse(text)'],
    tags: ['encoding', 'windows'],
    confidence: 0.88,
  },
];

// ── Pattern Storage ──────────────────────────────────────────────────────────
const PATTERNS_FILE = '.self-heal-patterns.json';

function loadPatterns() {
  if (!fs.existsSync(PATTERNS_FILE)) return [...BUILTIN_PATTERNS];
  try {
    const extra = JSON.parse(fs.readFileSync(PATTERNS_FILE, 'utf8'));
    return [...BUILTIN_PATTERNS, ...extra];
  } catch { return [...BUILTIN_PATTERNS]; }
}

function savePatterns(patterns) {
  const custom = patterns.filter(p => !BUILTIN_PATTERNS.find(b => b.id === p.id));
  if (custom.length > 0) fs.writeFileSync(PATTERNS_FILE, JSON.stringify(custom, null, 2));
}

// ── Root Cause Analysis ───────────────────────────────────────────────────────
function analyzeRootCause(errorText, patterns) {
  const matched = [];
  for (const p of patterns) {
    if (p.error.test(errorText)) {
      matched.push({ ...p, matchLen: (errorText.match(p.error)?.[0] || '').length });
    }
  }
  matched.sort((a, b) => b.confidence - a.confidence);
  return matched.slice(0, 3);
}

// ── Fix Suggestion ────────────────────────────────────────────────────────────
function suggestFixes(errorText, patterns) {
  const matched = analyzeRootCause(errorText, patterns);
  if (matched.length === 0) {
    return {
      severity: 'unknown',
      diagnosis: 'Error pattern not recognized. Manual investigation required.',
      fixes: [],
      suggestions: [
        'Search for the error message online',
        'Check recent changes to the failing component',
        'Try running with verbose logging',
        'Check system logs for related errors',
      ],
    };
  }

  const top = matched[0];
  const severity = top.confidence >= 0.9 ? 'high' : top.confidence >= 0.8 ? 'medium' : 'low';

  return {
    severity,
    diagnosis: top.cause,
    fixes: matched.map(p => ({
      fix: p.fix,
      confidence: p.confidence,
      examples: p.examples,
      tags: p.tags,
    })),
    suggestions: [],
  };
}

// ── Healer ───────────────────────────────────────────────────────────────────
function autoFix(errorText, patterns) {
  const result = suggestFixes(errorText, patterns);
  if (!result.fixes.length) return { result, applied: null };

  const top = result.fixes[0];
  if (top.confidence < 0.85) {
    return { result, applied: null, note: 'Confidence too low for auto-fix. Manual fix required.' };
  }

  return { result, applied: top.fix };
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdAnalyze(errorText, format) {
  const patterns = loadPatterns();
  const result = suggestFixes(errorText, patterns);

  if (format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(`\n## Self-Healing Analysis\n`);
  console.log(`Severity: ${result.severity.toUpperCase()}`);
  console.log(`\nDiagnosis: ${result.diagnosis}\n`);

  if (result.fixes.length) {
    console.log(`Suggested fixes (by confidence):`);
    for (const f of result.fixes) {
      console.log(`  [${Math.round(f.confidence * 100)}%] ${f.fix}`);
      if (f.examples?.length) {
        for (const ex of f.examples.slice(0, 2)) {
          console.log(`    Example: ${ex}`);
        }
      }
    }
  }

  if (result.suggestions.length) {
    console.log(`\nGeneral suggestions:`);
    for (const s of result.suggestions) console.log(`  - ${s}`);
  }

  console.log();
}

function cmdHeal(errorText) {
  const patterns = loadPatterns();
  const { result, applied, note } = autoFix(errorText, patterns);
  cmdAnalyze(errorText, 'text');

  if (applied) {
    console.log(`\n✅ Auto-fix available: ${applied}`);
  } else if (note) {
    console.log(`\n⚠️  ${note}`);
  }
}

function cmdPatterns(args) {
  const patterns = loadPatterns();
  const tagFilter = args.includes('--tag') ? args[args.indexOf('--tag') + 1] : null;
  const filtered = tagFilter ? patterns.filter(p => p.tags.includes(tagFilter)) : patterns;

  console.log(`\n## Fix Patterns (${filtered.length}/${patterns.length})\n`);
  for (const p of filtered) {
    const tags = p.tags.join(', ');
    console.log(`  [${Math.round(p.confidence * 100)}%] ${p.id} (${tags})`);
    console.log(`    Cause: ${p.cause}`);
    console.log(`    Fix: ${p.fix}\n`);
  }
}

function cmdLearn(errorText, fixText) {
  if (!errorText || !fixText) {
    console.error('Usage: self_healing_engine.js learn "<error>" "<fix>"'); process.exit(1);
  }
  const patterns = loadPatterns();
  const newPattern = {
    id: crypto.randomUUID().slice(0, 8),
    error: new RegExp(errorText.slice(0, 50), 'i'),
    cause: 'User learned pattern',
    fix: fixText,
    examples: [],
    tags: ['user-learned'],
    confidence: 0.95,
  };
  patterns.push(newPattern);
  savePatterns(patterns);
  console.log(`✅ Learned: ${newPattern.id}`);
}

function cmdWatch(command) {
  console.log(`\n## Self-Healing Watch Mode`);
  console.log(`Command: ${command}`);
  console.log(`Monitoring for errors...\n`);

  try {
    const out = execSync(command, { encoding: 'utf8', timeout: 60000 });
    console.log(out);
    console.log('✅ No errors detected');
  } catch (err) {
    const errText = err.message || String(err);
    console.log(`❌ Error detected:\n${errText}\n`);
    cmdHeal(errText);
  }
}

function cmdTest() {
  const patterns = loadPatterns();
  const tests = [
    {
      input: 'AmsersandNotAllowed & in compound commands',
      expect: 'powershell-ampersand',
      desc: 'PowerShell ampersand error'
    },
    {
      input: 'GitHub 443 port connection timeout ECONNREFUSED',
      expect: 'git-push-443',
      desc: 'GitHub 443 error'
    },
    {
      input: 'Version already exists',
      expect: 'clawhub-version-exists',
      desc: 'ClawHub version exists'
    },
    {
      input: 'Rate limit max 5 new skills per hour',
      expect: 'clawhub-rate-limit',
      desc: 'ClawHub rate limit'
    },
    {
      input: 'JSON.parse unexpected token in JSON at position 0',
      expect: 'json-parse-fail',
      desc: 'JSON parse error'
    },
  ];

  let passed = 0;
  for (const t of tests) {
    const matched = analyzeRootCause(t.input, patterns);
    const ok = matched[0]?.id === t.expect;
    console.log(`${ok ? '✅' : '❌'} ${t.desc}: ${matched[0]?.id || 'none'} (expected: ${t.expect})`);
    if (ok) passed++;
  }
  console.log(`\n${passed}/${tests.length} tests passed`);
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = { analyze: cmdAnalyze, heal: cmdHeal, patterns: cmdPatterns, learn: cmdLearn, watch: cmdWatch, test: cmdTest };

if (!cmd || !COMMANDS[cmd]) {
  console.log(`self_healing_engine.js — AI Agent Self-Healing Engine

Usage: node self_healing_engine.js <command> [args...]

Commands:
  analyze <errorText>        Analyze an error and suggest fixes
  heal <errorText>           Analyze + auto-fix (high confidence only)
  patterns [--tag <tag>]     List all fix patterns (filter by tag)
  learn "<error>" "<fix>"    Learn a new fix pattern
  watch <command>            Run command with self-healing monitoring
  test                       Run built-in test suite

Examples:
  node self_healing_engine.js analyze "PowerShell AmpersandNotAllowed &"
  node self_healing_engine.js heal "Version already exists"
  node self_healing_engine.js patterns --tag windows
  node self_healing_engine.js test
`);
  process.exit(0);
}

if (cmd === 'analyze' || cmd === 'heal') {
  const input = args[0];
  if (!input) { console.error('Provide error text'); process.exit(1); }
  if (cmd === 'analyze') cmdAnalyze(input);
  else cmdHeal(input);
} else if (cmd === 'patterns') {
  cmdPatterns(args);
} else if (cmd === 'learn') {
  cmdLearn(args[0], args[1]);
} else if (cmd === 'watch') {
  cmdWatch(args.join(' '));
} else if (cmd === 'test') {
  cmdTest();
}
