/**
 * version_engine.js — Git-style version control for any file
 * No git required. Pure Node.js.
 * 
 * Usage: node version_engine.js <command> <file> [args...]
 * Commands: snap | history | diff | tag | tags | restore | compare | watch
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── Config ──────────────────────────────────────────────────────────────────
const SNAP_DIR = '.fvsnap';
const LOG_EXT = '.log';
const TAGS_FILE = 'tags.json';
const MAX_SNAPSHOT_SIZE = 10 * 1024 * 1024; // 10MB limit for content storage

// ── Helpers ──────────────────────────────────────────────────────────────────
function hashFile(filePath) {
  const content = fs.readFileSync(filePath);
  return crypto.createHash('sha256').update(content).digest('hex');
}

function isTextFile(buf) {
  // Check for null bytes (binary file indicator)
  for (let i = 0; i < Math.min(buf.length, 8192); i++) {
    if (buf[i] === 0) return false;
  }
  return true;
}

function getSnapDir(filePath) {
  return path.join(path.dirname(filePath), SNAP_DIR);
}

function getSnapFile(filePath) {
  const snapDir = getSnapDir(filePath);
  const base = path.basename(filePath).replace(/[<>:"/\\|?*]/g, '_');
  return path.join(snapDir, base + '.json');
}

function getLogFile(filePath) {
  const snapDir = getSnapDir(filePath);
  const base = path.basename(filePath).replace(/[<>:"/\\|?*]/g, '_');
  return path.join(snapDir, base + LOG_EXT);
}

function getTagsFile(filePath) {
  return path.join(getSnapDir(filePath), TAGS_FILE);
}

function ensureSnapDir(filePath) {
  const dir = getSnapDir(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function loadHistory(filePath) {
  const logFile = getLogFile(filePath);
  if (!fs.existsSync(logFile)) return [];
  try { return JSON.parse(fs.readFileSync(logFile, 'utf8')); }
  catch { return []; }
}

function saveHistory(filePath, history) {
  fs.writeFileSync(getLogFile(filePath), JSON.stringify(history, null, 2));
}

function loadTags(filePath) {
  const f = getTagsFile(filePath);
  if (!fs.existsSync(f)) return {};
  try { return JSON.parse(fs.readFileSync(f, 'utf8')); }
  catch { return {}; }
}

function saveTags(filePath, tags) {
  fs.writeFileSync(getTagsFile(filePath), JSON.stringify(tags, null, 2));
}

function parseVersion(history, v) {
  if (!v) return null;
  if (v === 'HEAD') return history[history.length - 1];
  if (v.startsWith('HEAD~')) {
    const n = parseInt(v.slice(5));
    if (isNaN(n)) return null;
    return history[history.length - 1 - n] || null;
  }
  // Check if it's a tag
  if (!v.match(/^\d+$/)) return null;
  const idx = parseInt(v) - 1;
  return history[idx] || null;
}

function formatDate(ts) {
  const d = new Date(ts);
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

// ── LCS Diff ─────────────────────────────────────────────────────────────────
function lcsDiff(oldLines, newLines) {
  const m = oldLines.length, n = newLines.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = oldLines[i-1] === newLines[j-1] ? dp[i-1][j-1] + 1 : Math.max(dp[i-1][j], dp[i][j-1]);

  const result = [];
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && oldLines[i-1] === newLines[j-1]) {
      result.unshift({ type: 'same', oldLine: i, newLine: j, content: oldLines[i-1] });
      i--; j--;
    } else if (j > 0 && (i === 0 || dp[i][j-1] >= dp[i-1][j])) {
      result.unshift({ type: 'add', newLine: j, content: newLines[j-1] });
      j--;
    } else {
      result.unshift({ type: 'del', oldLine: i, content: oldLines[i-1] });
      i--;
    }
  }
  return result;
}

function renderDiff(diffResult) {
  let out = '';
  let oldLine = 1, newLine = 1;
  let inChunk = false;
  let contextLines = [];

  for (const d of diffResult) {
    if (d.type === 'same') {
      contextLines.push(d);
      if (contextLines.length > 4) contextLines.shift();
      oldLine = d.oldLine + 1;
      newLine = d.newLine + 1;
    } else {
      if (!inChunk && contextLines.length > 0) {
        out += `  @@ -${oldLine - contextLines.length} +${newLine - contextLines.length} @@\n`;
        for (const c of contextLines) out += `   ${c.content}\n`;
      }
      contextLines = [];
      inChunk = true;
      if (d.type === 'del') {
        out += `\x1b[31m-${d.oldLine}: ${d.content}\x1b[0m\n`;
        oldLine++;
      } else {
        out += `\x1b[32m+${d.newLine}: ${d.content}\x1b[0m\n`;
        newLine++;
      }
    }
  }
  return out || 'No differences found.';
}

// ── Commands ─────────────────────────────────────────────────────────────────

function cmdSnap(filePath, message) {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found: ${filePath}`); process.exit(1);
  }
  const hash = hashFile(filePath);
  const stat = fs.statSync(filePath);
  const content = fs.readFileSync(filePath);
  const isText = isTextFile(content);

  ensureSnapDir(filePath);

  const history = loadHistory(filePath);
  const latest = history[history.length - 1];

  // Skip if content hasn't changed
  if (latest && latest.hash === hash) {
    console.log(`No changes detected (hash: ${hash.slice(0, 8)}). Already at latest version.`);
    return;
  }

  const version = history.length + 1;
  const snapshot = {
    version,
    hash,
    message: message || `Snapshot ${version}`,
    timestamp: new Date().toISOString(),
    size: stat.size,
    isText,
  };

  // Store content inline for small text files
  if (isText && stat.size < MAX_SNAPSHOT_SIZE) {
    snapshot.content = content.toString('utf8');
  } else {
    snapshot.note = isText ? 'File too large — hash only' : 'Binary file — hash only';
  }

  history.push(snapshot);
  saveHistory(filePath, history);

  console.log(`✅ Snapshot ${version} created: ${path.basename(filePath)}`);
  console.log(`   Hash: ${hash.slice(0, 12)}`);
  console.log(`   Message: ${snapshot.message}`);
  console.log(`   Size: ${stat.size} bytes`);
}

function cmdHistory(filePath, limit) {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found: ${filePath}`); process.exit(1);
  }
  const history = loadHistory(filePath);
  if (history.length === 0) {
    console.log('No snapshots yet. Run: node version_engine.js snap <file> [message]'); return;
  }
  const tags = loadTags(filePath);
  const tagMap = {};
  for (const [tag, v] of Object.entries(tags)) tagMap[v] = tag;

  const display = limit ? history.slice(-limit) : history;
  const start = limit ? Math.max(0, history.length - limit) : 0;

  console.log(`\n## Version History: ${path.basename(filePath)}`);
  console.log(`Total snapshots: ${history.length}\n`);
  console.log('  Ver  Date                  Hash         Size    Message');
  console.log('  ─── ──────────────────── ──────────── ─────── ─────────────────────────────');

  for (let i = start; i < history.length; i++) {
    const s = history[i];
    const tag = tagMap[s.version] ? ` [${tagMap[s.version]}]` : '';
    const ver = String(s.version).padStart(4);
    const date = formatDate(s.timestamp).padEnd(20);
    const h = s.hash.slice(0, 11).padEnd(12);
    const size = String(s.size).padStart(6);
    const msg = (s.message || '').padEnd(30).slice(0, 30);
    console.log(`  ${ver} ${date} ${h} ${size} ${msg}${tag}`);
  }
  console.log();
}

function cmdDiff(filePath, v1Spec, v2Spec) {
  const history = loadHistory(filePath);
  if (history.length < 2) {
    console.error('Need at least 2 snapshots to diff. Run snap twice first.'); process.exit(1);
  }

  // Default: diff HEAD~1 and HEAD
  if (!v2Spec) {
    v2Spec = 'HEAD';
    v1Spec = v1Spec || 'HEAD~1';
  }
  if (!v1Spec) v1Spec = 'HEAD~1';

  const snap1 = parseVersion(history, v1Spec);
  const snap2 = parseVersion(history, v2Spec);
  if (!snap1) { console.error(`Version not found: ${v1Spec}`); process.exit(1); }
  if (!snap2) { console.error(`Version not found: ${v2Spec}`); process.exit(1); }
  if (snap1.version === snap2.version) { console.log('Same version — no diff.'); return; }

  // Ensure both are text
  if (!snap1.isText || !snap2.isText) {
    console.log(`Binary file — showing hash comparison only:`);
    console.log(`  v${snap1.version}: ${snap1.hash}`);
    console.log(`  v${snap2.version}: ${snap2.hash}`);
    return;
  }

  const oldLines = (snap1.content || '').split('\n');
  const newLines = (snap2.content || '').split('\n');
  const diff = lcsDiff(oldLines, newLines);

  console.log(`\n## Diff: v${snap1.version} → v${snap2.version} (${path.basename(filePath)})`);
  console.log(`  From: ${snap1.hash.slice(0, 12)} (${snap1.message})`);
  console.log(`  To:   ${snap2.hash.slice(0, 12)} (${snap2.message})\n`);

  const rendered = renderDiff(diff);
  // Strip ANSI codes for plain text output
  const plain = rendered.replace(/\x1b\[[0-9;]*m/g, '');
  console.log(plain);
}

function cmdTag(filePath, versionSpec, tagName) {
  const history = loadHistory(filePath);
  if (!tagName) {
    console.error('Usage: version_engine.js tag <file> <version> <tag-name>'); process.exit(1);
  }
  const snap = parseVersion(history, versionSpec);
  if (!snap) { console.error(`Version not found: ${versionSpec}`); process.exit(1); }

  const tags = loadTags(filePath);
  const oldTag = Object.entries(tags).find(([, v]) => v === snap.version);
  if (oldTag) {
    console.log(`Replacing tag '${oldTag[0]}' → v${snap.version} (${tagName})`);
    delete tags[oldTag[0]];
  }
  tags[tagName] = snap.version;
  saveTags(filePath, tags);
  console.log(`✅ Tagged v${snap.version} as '${tagName}'`);
}

function cmdTags(filePath) {
  const history = loadHistory(filePath);
  const tags = loadTags(filePath);
  const entries = Object.entries(tags).sort((a, b) => a[1] - b[1]);

  if (entries.length === 0) {
    console.log('No tags yet. Usage: version_engine.js tag <file> <version> <tag-name>'); return;
  }

  console.log('\n## Tags\n');
  for (const [tag, ver] of entries) {
    const snap = history[ver - 1];
    const date = snap ? formatDate(snap.timestamp) : '?';
    console.log(`  ${String(ver).padStart(4)}. ${tag.padEnd(25)} ${date}  ${snap?.message || ''}`);
  }
  console.log();
}

function cmdRestore(filePath, versionSpec) {
  const history = loadHistory(filePath);
  if (history.length === 0) {
    console.error('No snapshots to restore.'); process.exit(1);
  }

  // Default: restore to previous
  const target = versionSpec
    ? parseVersion(history, versionSpec)
    : history[history.length - 2] || history[history.length - 1];

  if (!target) { console.error(`Version not found: ${versionSpec}`); process.exit(1); }

  // Backup current
  const hash = hashFile(filePath);
  const backupMsg = `Auto-backup before restore to v${target.version}`;
  cmdSnap(filePath, backupMsg);

  if (!target.isText || !target.content) {
    console.error(`Cannot restore: v${target.version} is binary or too large.`);
    console.error(`Hash: ${target.hash}`);
    process.exit(1);
  }

  fs.writeFileSync(filePath, target.content, 'utf8');
  console.log(`✅ Restored ${path.basename(filePath)} to v${target.version}`);
  console.log(`   Message: ${target.message}`);
  console.log(`   New hash: ${hashFile(filePath).slice(0, 12)}`);
}

function cmdCompare(file1, file2) {
  if (!fs.existsSync(file1)) { console.error(`Not found: ${file1}`); process.exit(1); }
  if (!fs.existsSync(file2)) { console.error(`Not found: ${file2}`); process.exit(1); }

  const buf1 = fs.readFileSync(file1);
  const buf2 = fs.readFileSync(file2);
  const h1 = crypto.createHash('sha256').update(buf1).digest('hex');
  const h2 = crypto.createHash('sha256').update(buf2).digest('hex');

  console.log(`\n## Compare: ${path.basename(file1)} vs ${path.basename(file2)}`);
  console.log(`  ${path.basename(file1)}: ${h1.slice(0, 12)} (${buf1.length} bytes)`);
  console.log(`  ${path.basename(file2)}: ${h2.slice(0, 12)} (${buf2.length} bytes)`);

  if (h1 === h2) { console.log('  Identical — no differences.'); return; }

  const isText1 = isTextFile(buf1), isText2 = isTextFile(buf2);
  if (isText1 && isText2) {
    const oldLines = buf1.toString('utf8').split('\n');
    const newLines = buf2.toString('utf8').split('\n');
    const diff = lcsDiff(oldLines, newLines);
    const rendered = renderDiff(diff);
    const plain = rendered.replace(/\x1b\[[0-9;]*m/g, '');
    console.log(plain);
  } else {
    console.log('  (binary files — hashes differ)');
  }
}

function cmdWatch(filePath, interval) {
  if (!fs.existsSync(filePath)) { console.error(`Not found: ${filePath}`); process.exit(1); }
  const ms = interval || 5000;
  let lastHash = null;
  let count = 0;

  console.log(`Watching: ${filePath}`);
  console.log(`Interval: ${ms}ms | Press Ctrl+C to stop\n`);

  // Initial snap
  cmdSnap(filePath, 'Initial (watch mode)');
  lastHash = hashFile(filePath);

  const watcher = fs.watch(filePath, { persistent: false }, (eventType) => {
    if (eventType !== 'change') return;
    setTimeout(() => {
      try {
        const h = hashFile(filePath);
        if (h !== lastHash) {
          count++;
          cmdSnap(filePath, `Auto-snapshot #${count}`);
          lastHash = h;
        }
      } catch {}
    }, 500);
  });

  // Also use polling for safety
  const poll = setInterval(() => {
    try {
      const h = hashFile(filePath);
      if (h !== lastHash) {
        count++;
        cmdSnap(filePath, `Auto-snapshot #${count}`);
        lastHash = h;
      }
    } catch {}
  }, ms);

  process.on('SIGINT', () => {
    watcher.close();
    clearInterval(poll);
    console.log('\nStopped.');
    process.exit(0);
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

if (!cmd || cmd === 'help' || cmd === '--help') {
  console.log(`version_engine.js — Git-style version control for any file

Usage: node version_engine.js <command> <file> [args...]

Commands:
  snap <file> [msg]     Create a snapshot of a file
  history <file>        Show all snapshots (--limit N for last N)
  diff <file> [v1] [v2] Diff between two versions (default: HEAD~1 → HEAD)
  tag <file> <v> <tag>  Tag a version (e.g., v1.0.0, production)
  tags <file>           List all tags
  restore <file> [v]    Restore to a version (default: previous)
  compare <f1> <f2>     Compare any two files
  watch <file> [ms]     Auto-snapshot on file changes

Version specs: HEAD (latest), HEAD~N (N back), or number (1, 2, 3...)
Tags: Named versions like v1.0.0, production, before-refactor

Examples:
  node version_engine.js snap config.json "update DB"
  node version_engine.js diff config.json HEAD~1 HEAD
  node version_engine.js tag config.json 3 v1.0.0
  node version_engine.js restore config.json v1.0.0
  node version_engine.js watch settings.json --interval 3000
`);
  process.exit(0);
}

const COMMANDS = { snap: cmdSnap, history: cmdHistory, diff: cmdDiff, tag: cmdTag, tags: cmdTags, restore: cmdRestore, compare: cmdCompare, watch: cmdWatch };
if (!COMMANDS[cmd]) {
  console.error(`Unknown command: ${cmd}`); process.exit(1);
}

// Handle --limit for history
if (cmd === 'history') {
  const fileIdx = args.findIndex(a => !a.startsWith('--'));
  const limitIdx = args.indexOf('--limit');
  const limit = limitIdx >= 0 ? parseInt(args[limitIdx + 1]) : null;
  const filePath = args[fileIdx >= 0 ? fileIdx : 0];
  if (!filePath) { console.error('Usage: version_engine.js history <file> [--limit N]'); process.exit(1); }
  const absPath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  cmdHistory(absPath, limit);
} else if (cmd === 'snap') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  cmdSnap(filePath, args[1]);
} else if (cmd === 'diff') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  cmdDiff(filePath, args[1], args[2]);
} else if (cmd === 'tag') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  cmdTag(filePath, args[1], args[2]);
} else if (cmd === 'tags') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  cmdTags(filePath);
} else if (cmd === 'restore') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  cmdRestore(filePath, args[1]);
} else if (cmd === 'compare') {
  const f1 = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  const f2 = path.isAbsolute(args[1]) ? args[1] : path.resolve(process.cwd(), args[1]);
  cmdCompare(f1, f2);
} else if (cmd === 'watch') {
  const filePath = path.isAbsolute(args[0]) ? args[0] : path.resolve(process.cwd(), args[0]);
  const intervalIdx = args.indexOf('--interval');
  const interval = intervalIdx >= 0 ? parseInt(args[intervalIdx + 1]) : 5000;
  cmdWatch(filePath, interval);
}
