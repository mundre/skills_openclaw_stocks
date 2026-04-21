/**
 * diff_engine.js — Professional diff viewer with syntax highlighting
 * 
 * Usage: node diff_engine.js <command> [args...]
 * Commands:
 *   diff <f1> <f2>            Compare two files (unified view)
 *   sbs <f1> <f2>            Side-by-side view
 *   words <f1> <f2>          Word-level diff
 *   git <dir> [args]         Run git diff, pretty-print
 *   html <f1> <f2> [title]   Export diff as standalone HTML
 *   dir <d1> <d2>            Compare two directories
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── Diff Engine ───────────────────────────────────────────────────────────────
function lcs(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = a[i-1] === b[j-1] ? dp[i-1][j-1] + 1 : Math.max(dp[i][j-1], dp[i-1][j]);
  const result = [];
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i-1] === b[j-1]) { result.unshift({ type: 'same', a: a[i-1], b: b[j-1] }); i--; j--; }
    else if (j > 0 && (i === 0 || dp[i][j-1] >= dp[i-1][j])) { result.unshift({ type: 'add', b: b[j-1] }); j--; }
    else { result.unshift({ type: 'del', a: a[i-1] }); i--; }
  }
  return result;
}

function wordLevelDiff(oldLine, newLine) {
  const ow = oldLine.split(/(\s+)/), nw = newLine.split(/(\s+)/);
  const diff = lcs(ow, nw);
  return diff.map(d => {
    if (d.type === 'same') return { type: 'same', text: d.a };
    if (d.type === 'del') return { type: 'del', text: d.a };
    return { type: 'add', text: d.b };
  });
}

// ── Syntax Highlighting ───────────────────────────────────────────────────────
const HL = {
  keyword: c => `\x1b[36m${c}\x1b[0m`,     // cyan
  string: c => `\x1b[33m${c}\x1b[0m`,      // yellow
  comment: c => `\x1b[90m${c}\x1b[0m`,    // dim
  number: c => `\x1b[35m${c}\x1b[0m`,     // magenta
  func: c => `\x1b[32m${c}\x1b[0m`,       // green
  prop: c => `\x1b[34m${c}\x1b[0m`,       // blue
  add: c => `\x1b[32m${c}\x1b[0m`,        // green
  del: c => `\x1b[31m${c}\x1b[0m`,        // red
  same: c => c,
};

function getHL(lang) {
  const kw = ['if','else','for','while','return','function','const','let','var','class','import','export','from','default','async','await','try','catch','throw','new','this','extends','static','public','private','try','except','finally','with','as','lambda','def','pass','yield','raise','in','is','not','and','or','None','True','False','void','int','string','bool','float','null','true','false'];
  const kwSet = new Set(kw);
  return (line) => {
    return line.replace(/(\/\/.*$|\/\*[\s\S]*?\*\/|#.*$)/, c => HL.comment(c))
      .replace(/"([^"\\]|\\.)*"|'([^'\\]|\\.)*'|`([^`\\]|\\.)*`/g, c => HL.string(c))
      .replace(/\b(\d+\.?\d*)\b/g, c => HL.number(c))
      .replace(/\b([\w$]+)\s*\(/g, (m, f) => kwSet.has(f.split('(')[0]) ? HL.keyword(m) : HL.func(m))
      .replace(/\b([\w$]+)\s*:/g, (m, p) => kwSet.has(p.split(':')[0]) ? HL.keyword(m) : HL.prop(m));
  };
}

function detectLang(file) {
  const ext = path.extname(file).toLowerCase();
  const map = { '.js': 'js', '.ts': 'ts', '.py': 'py', '.go': 'go', '.rs': 'rs', '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.cs': 'cs', '.rb': 'rb', '.php': 'php', '.sh': 'sh', '.bash': 'sh', '.ps1': 'ps1', '.md': 'md', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml', '.html': 'html', '.css': 'css', '.sql': 'sql' };
  return map[ext] || 'text';
}

// ── Unified Diff Renderer ─────────────────────────────────────────────────────
function renderUnified(diffResult, oldLabel, newLabel) {
  const oldLines = [], newLines = [];
  let i = 0, j = 0;
  for (const d of diffResult) {
    if (d.type === 'same') { i++; j++; }
    else if (d.type === 'del') { i++; }
    else { j++; }
  }

  const ctxLines = 3;
  const changes = diffResult.map((d, idx) => ({ ...d, idx }));
  const changeIdxs = new Set(changes.filter(d => d.type !== 'same').map(d => d.idx));

  const showIdxs = new Set();
  for (const idx of changeIdxs) {
    for (let k = Math.max(0, idx - ctxLines); k <= Math.min(changes.length - 1, idx + ctxLines); k++) showIdxs.add(k);
  }

  let out = `--- ${oldLabel}\n+++ ${newLabel}\n`;
  let lastShown = -1;
  const shown = [...showIdxs].sort((a, b) => a - b);

  // Group into hunks
  const hunks = [];
  let hunk = null;
  for (const idx of shown) {
    if (!hunk) hunk = { start: idx, lines: [] };
    if (idx > lastShown + 1 && hunk.lines.length > 0) { hunks.push(hunk); hunk = { start: idx, lines: [] }; }
    hunk.lines.push(changes[idx]);
    lastShown = idx;
  }
  if (hunk) hunks.push(hunk);

  const lang = detectLang(oldLabel || 'text');
  const hl = getHL(lang);

  for (const hunk of hunks) {
    const oldStart = hunk.lines.filter(l => l.type !== 'add').length > 0
      ? Math.max(1, hunk.lines[0].idx - hunk.lines.filter(l => l.type === 'add').length - ctxLines + 1)
      : 1;
    const newStart = Math.max(1, hunk.lines[0].idx - ctxLines + 1);
    out += `@@ -${oldStart},${hunk.lines.length + hunk.lines.filter(l => l.type === 'add').length} +${newStart},${hunk.lines.length} @@\n`;

    for (const d of hunk.lines) {
      if (d.type === 'same') {
        out += ` ${hl(d.a || d.b)}\n`;
      } else if (d.type === 'del') {
        out += `\x1b[31m-${d.a}\x1b[0m\n`;
      } else {
        out += `\x1b[32m+${d.b}\x1b[0m\n`;
      }
    }
  }
  return out;
}

// ── Side-by-Side Renderer ────────────────────────────────────────────────────
function renderSBS(diffResult, width = 60) {
  const lang = detectLang('file');
  const hl = getHL(lang);
  const half = Math.floor(width / 2) - 5;
  let out = `\n${'OLD'.padEnd(half)}|${'NEW'.padEnd(half)}\n${'─'.repeat(width)}\n`;

  const oldParts = [], newParts = [];
  for (const d of diffResult) {
    if (d.type === 'same') { oldParts.push({ type: 'same', text: d.a }); newParts.push({ type: 'same', text: d.b }); }
    else if (d.type === 'del') { oldParts.push({ type: 'del', text: d.a }); }
    else { newParts.push({ type: 'add', text: d.b }); }
  }

  // Pad to same length
  while (oldParts.length < newParts.length) oldParts.push({ type: 'pad', text: '' });
  while (newParts.length < oldParts.length) newParts.push({ type: 'pad', text: '' });

  const total = Math.max(oldParts.length, newParts.length);
  for (let i = 0; i < total; i++) {
    const ol = oldParts[i] || { type: 'pad', text: '' };
    const nl = newParts[i] || { type: 'pad', text: '' };
    const prefix = ol.type === 'del' ? '\x1b[31m- ' : ol.type === 'pad' ? '  ' : '  ';
    const nprefix = nl.type === 'add' ? '\x1b[32m+ ' : nl.type === 'pad' ? '  ' : '  ';
    const reset = '\x1b[0m';
    const oldText = ol.type === 'same' ? hl(ol.text) : (ol.type === 'del' ? ol.text : '');
    const newText = nl.type === 'same' ? hl(nl.text) : (nl.type === 'add' ? nl.text : '');
    const oldLine = `${prefix}${oldText}${reset}`.slice(0, half + 8).padEnd(half + 8);
    const newLine = `${nprefix}${newText}${reset}`;
    out += `${oldLine}|${newLine}\n`;
  }
  return out;
}

// ── Word-Level Diff Renderer ──────────────────────────────────────────────────
function renderWords(oldLines, newLines, diffResult) {
  const lang = detectLang('file');
  const hl = getHL(lang);
  let out = '\n';
  let oi = 0, ni = 0;
  for (const d of diffResult) {
    if (d.type === 'same') {
      out += `  ${hl(d.a)}\n`;
      oi++; ni++;
    } else if (d.type === 'del') {
      out += `\x1b[31m-${d.a}\x1b[0m\n`;
      oi++;
    } else {
      out += `\x1b[32m+${d.b}\x1b[0m\n`;
      ni++;
    }
  }
  return out;
}

// ── HTML Export ───────────────────────────────────────────────────────────────
function renderHTML(oldLines, newLines, diffResult, title = 'Diff') {
  const oldLabel = title.split(' vs ')[0] || 'old';
  const newLabel = title.split(' vs ')[1] || 'new';

  const lang = detectLang(title);
  const hl = getHL(lang);

  let oldHtml = '', newHtml = '';
  for (const d of diffResult) {
    if (d.type === 'same') {
      const escaped = hl(d.a || d.b).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\x1b\[[0-9;]*m/g,'');
      oldHtml += `<div class="same">${escaped}</div>`;
      newHtml += `<div class="same">${escaped}</div>`;
    } else if (d.type === 'del') {
      const escaped = (d.a||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      oldHtml += `<div class="del">- ${escaped}</div>`;
      newHtml += `<div class="pad"></div>`;
    } else {
      const escaped = (d.b||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      oldHtml += `<div class="pad"></div>`;
      newHtml += `<div class="add">+ ${escaped}</div>`;
    }
  }

  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${title}</title>
<style>
  body { font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 13px; margin: 0; background: #1e1e1e; color: #d4d4d4; }
  .header { display: flex; background: #252526; border-bottom: 1px solid #3c3c3c; padding: 0; }
  .header div { padding: 12px 20px; flex: 1; font-weight: bold; color: #cccccc; }
  .container { display: flex; }
  .pane { flex: 1; overflow-x: auto; }
  .pane .old { background: #3c1e1e; }
  .pane .new { background: #1e3c1e; }
  .same { padding: 1px 20px; border-left: 3px solid transparent; }
  .del { padding: 1px 20px; border-left: 3px solid #f48771; background: #5c1e1e; }
  .add { padding: 1px 20px; border-left: 3px solid #4ec9b0; background: #1e3c25; }
  .pad { padding: 1px 20px; background: #252526; }
  .stats { background: #333; padding: 8px 20px; color: #888; font-size: 12px; border-bottom: 1px solid #3c3c3c; }
  .add-count { color: #4ec9b0; } .del-count { color: #f48771; }
</style></head><body>
<div class="header"><div>📄 ${oldLabel}</div><div>📄 ${newLabel}</div></div>
<div class="stats">
  <span class="del-count">- ${diffResult.filter(d=>d.type==='del').length} deletions</span> &nbsp;|&nbsp;
  <span class="add-count">+ ${diffResult.filter(d=>d.type==='add').length} additions</span> &nbsp;|&nbsp;
  = ${diffResult.filter(d=>d.type==='same').length} unchanged
</div>
<div class="container">
  <div class="pane old">${oldHtml}</div>
  <div class="pane new">${newHtml}</div>
</div></body></html>`;
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdDiff(file1, file2) {
  if (!file1 || !file2) { console.error('Usage: diff_engine.js diff <file1> <file2>'); process.exit(1); }
  if (!fs.existsSync(file1)) { console.error(`Not found: ${file1}`); process.exit(1); }
  if (!fs.existsSync(file2)) { console.error(`Not found: ${file2}`); process.exit(1); }

  const o = fs.readFileSync(file1, 'utf8').split('\n');
  const n = fs.readFileSync(file2, 'utf8').split('\n');
  const result = lcs(o, n);

  const out = renderUnified(result, path.basename(file1), path.basename(file2));
  console.log(out.replace(/\x1b\[[0-9;]*m/g, '')); // plain text for console
}

function cmdSBS(file1, file2) {
  if (!file1 || !file2) { console.error('Usage: diff_engine.js sbs <file1> <file2>'); process.exit(1); }
  if (!fs.existsSync(file1) || !fs.existsSync(file2)) { console.error('File not found'); process.exit(1); }
  const o = fs.readFileSync(file1, 'utf8').split('\n');
  const n = fs.readFileSync(file2, 'utf8').split('\n');
  const result = lcs(o, n);
  console.log(renderSBS(result));
}

function cmdWords(file1, file2) {
  if (!file1 || !file2) { console.error('Usage: diff_engine.js words <file1> <file2>'); process.exit(1); }
  if (!fs.existsSync(file1) || !fs.existsSync(file2)) { console.error('File not found'); process.exit(1); }
  const o = fs.readFileSync(file1, 'utf8').split('\n');
  const n = fs.readFileSync(file2, 'utf8').split('\n');
  const result = lcs(o, n);
  const out = renderWords(o, n, result);
  console.log(out.replace(/\x1b\[[0-9;]*m/g, ''));
}

function cmdHtml(file1, file2, title) {
  if (!file1 || !file2) { console.error('Usage: diff_engine.js html <file1> <file2> [title]'); process.exit(1); }
  if (!fs.existsSync(file1) || !fs.existsSync(file2)) { console.error('File not found'); process.exit(1); }
  const o = fs.readFileSync(file1, 'utf8').split('\n');
  const n = fs.readFileSync(file2, 'utf8').split('\n');
  const result = lcs(o, n);
  const t = title || `${path.basename(file1)} vs ${path.basename(file2)}`;
  const html = renderHTML(o, n, result, t);
  const outPath = 'diff.html';
  fs.writeFileSync(outPath, html);
  console.log(`✅ HTML diff written: ${outPath}`);
  console.log(`   Open in browser: file://${path.resolve(outPath)}`);
}

function cmdGit(dir, gitArgs) {
  if (!dir) { console.error('Usage: diff_engine.js git <dir> [git args]'); process.exit(1); }
  if (!fs.existsSync(path.join(dir, '.git'))) { console.error('Not a git repository'); process.exit(1); }
  const { execSync } = require('child_process');
  try {
    const args = gitArgs ? gitArgs.join(' ') : '--stat';
    const out = execSync(`git ${args}`, { cwd: dir, encoding: 'utf8', timeout: 10000 });
    console.log(out);
  } catch (e) {
    console.log(e.message);
  }
}

function cmdDir(d1, d2) {
  if (!d1 || !d2) { console.error('Usage: diff_engine.js dir <dir1> <dir2>'); process.exit(1); }
  if (!fs.existsSync(d1) || !fs.existsSync(d2)) { console.error('Directory not found'); process.exit(1); }

  function listDir(d, base = '') {
    const files = [];
    const entries = fs.readdirSync(d, { withFileTypes: true });
    for (const e of entries) {
      if (e.name === '.git' || e.name === 'node_modules') continue;
      const rel = base ? `${base}/${e.name}` : e.name;
      if (e.isDirectory()) files.push(...listDir(path.join(d, e.name), rel));
      else files.push(rel);
    }
    return files.sort();
  }

  const f1 = listDir(d1), f2 = listDir(d2);
  const s1 = new Set(f1), s2 = new Set(f2);

  console.log('\n## Directory Diff\n');
  const only1 = f1.filter(f => !s2.has(f));
  const only2 = f2.filter(f => !s1.has(f));
  const both = f1.filter(f => s2.has(f));

  console.log(`Only in ${path.basename(d1)}: ${only1.length} files`);
  for (const f of only1) console.log(`  - ${f}`);
  console.log(`\nOnly in ${path.basename(d2)}: ${only2.length} files`);
  for (const f of only2) console.log(`  + ${f}`);

  // Compare common files
  const changed = [];
  for (const f of both) {
    try {
      const h1 = crypto.createHash('md5').update(fs.readFileSync(path.join(d1, f))).digest('hex');
      const h2 = crypto.createHash('md5').update(fs.readFileSync(path.join(d2, f))).digest('hex');
      if (h1 !== h2) changed.push(f);
    } catch {}
  }
  console.log(`\nChanged (${both.length} common): ${changed.length} files`);
  for (const f of changed.slice(0, 20)) console.log(`  ~ ${f}`);
  if (changed.length > 20) console.log(`  ... and ${changed.length - 20} more`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = { diff: cmdDiff, sbs: cmdSBS, words: cmdWords, html: cmdHtml, git: cmdGit, dir: cmdDir };

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`diff_engine.js — Professional diff viewer with syntax highlighting

Usage: node diff_engine.js <command> [args...]

Commands:
  diff <f1> <f2>    Unified diff view (default)
  sbs <f1> <f2>     Side-by-side view
  words <f1> <f2>   Word-level diff (inline)
  html <f1> <f2> [t] Export diff as standalone HTML file
  git <dir> [args]  Run git diff with pretty output
  dir <d1> <d2>     Compare two directories

Examples:
  node diff_engine.js diff old.js new.js
  node diff_engine.js sbs config.json config-new.json
  node diff_engine.js html a.txt b.txt "old vs new"
`);
  process.exit(0);
}

if (cmd === 'diff') cmdDiff(args[0], args[1]);
else if (cmd === 'sbs') cmdSBS(args[0], args[1]);
else if (cmd === 'words') cmdWords(args[0], args[1]);
else if (cmd === 'html') cmdHtml(args[0], args[1], args[2]);
else if (cmd === 'git') cmdGit(args[0], args.slice(1));
else if (cmd === 'dir') cmdDir(args[0], args[1]);
