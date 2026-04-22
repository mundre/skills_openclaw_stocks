/**
 * smart_renamer.js — Intelligent Batch File Renamer
 * 
 * Rename files by patterns, dates, sequences, or custom rules.
 * Preview before applying. Undo capability.
 * 
 * Usage: node smart_renamer.js <command> [args...]
 * Commands:
 *   preview <dir> <rule>    Preview renames
 *   apply <dir> <rule>      Apply renames
 *   undo <dir>              Undo last batch
 *   rules                   List rename rules
 */

const fs = require('fs');
const path = require('path');

const HISTORY_FILE = '.rename-history.json';

// ── Rename Rules ─────────────────────────────────────────────────────────────
const RULES = {
  lowercase: (name) => name.toLowerCase(),
  uppercase: (name) => name.toUpperCase(),
  trim: (name) => name.trim(),
  spaces_to_underscores: (name) => name.replace(/\s+/g, '_'),
  underscores_to_spaces: (name) => name.replace(/_/g, ' '),
  remove_special: (name) => name.replace(/[^a-zA-Z0-9._-]/g, ''),
  prefix: (name, prefix) => prefix + name,
  suffix: (name, suffix) => {
    const ext = path.extname(name);
    const base = path.basename(name, ext);
    return base + suffix + ext;
  },
  replace: (name, find, replace) => name.replace(new RegExp(find, 'g'), replace),
  sequence: (name, start, step) => {
    const ext = path.extname(name);
    return `${String(start).padStart(4, '0')}${ext}`;
  },
  date_prefix: (name) => {
    const d = new Date();
    const date = `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;
    const ext = path.extname(name);
    const base = path.basename(name, ext);
    return `${date}_${base}${ext}`;
  },
  extension: (name, newExt) => {
    const base = path.basename(name, path.extname(name));
    return base + (newExt.startsWith('.') ? newExt : '.' + newExt);
  },
};

// ── History ──────────────────────────────────────────────────────────────────
function loadHistory(dir) {
  const file = path.join(dir, HISTORY_FILE);
  if (!fs.existsSync(file)) return [];
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); }
  catch { return []; }
}

function saveHistory(dir, history) {
  fs.writeFileSync(path.join(dir, HISTORY_FILE), JSON.stringify(history.slice(-10), null, 2));
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdPreview(dir, ruleName, ...args) {
  if (!dir || !ruleName) {
    console.error('Usage: smart_renamer.js preview <dir> <rule> [args...]');
    process.exit(1);
  }
  if (!fs.existsSync(dir)) { console.error(`Directory not found: ${dir}`); process.exit(1); }
  
  const rule = RULES[ruleName];
  if (!rule) { console.error(`Unknown rule: ${ruleName}`); process.exit(1); }
  
  const files = fs.readdirSync(dir).filter(f => fs.statSync(path.join(dir, f)).isFile());
  
  console.log(`\n## Preview: ${files.length} files\n`);
  console.log('Old Name'.padEnd(40) + ' →  ' + 'New Name');
  console.log('─'.repeat(80));
  
  let count = 0;
  for (const file of files.slice(0, 20)) {
    const newName = rule(file, ...args);
    if (newName !== file) {
      console.log(file.padEnd(40) + ' →  ' + newName);
      count++;
    }
  }
  if (files.length > 20) console.log(`... and ${files.length - 20} more files`);
  console.log(`\n${count} files would be renamed.\n`);
}

function cmdApply(dir, ruleName, ...args) {
  if (!dir || !ruleName) {
    console.error('Usage: smart_renamer.js apply <dir> <rule> [args...]');
    process.exit(1);
  }
  if (!fs.existsSync(dir)) { console.error(`Directory not found: ${dir}`); process.exit(1); }
  
  const rule = RULES[ruleName];
  if (!rule) { console.error(`Unknown rule: ${ruleName}`); process.exit(1); }
  
  const files = fs.readdirSync(dir).filter(f => fs.statSync(path.join(dir, f)).isFile());
  const renames = [];
  let count = 0;
  
  for (const file of files) {
    const newName = rule(file, ...args);
    if (newName !== file) {
      try {
        fs.renameSync(path.join(dir, file), path.join(dir, newName));
        renames.push({ old: file, new: newName });
        count++;
      } catch (e) {
        console.log(`Error: ${file} → ${newName}: ${e.message}`);
      }
    }
  }
  
  // Save to history
  const history = loadHistory(dir);
  history.push({ timestamp: new Date().toISOString(), rule: ruleName, args, renames });
  saveHistory(dir, history);
  
  console.log(`\n✅ Renamed ${count} files.\n`);
}

function cmdUndo(dir) {
  if (!dir) { console.error('Usage: smart_renamer.js undo <dir>'); process.exit(1); }
  
  const history = loadHistory(dir);
  const last = history[history.length - 1];
  if (!last) { console.log('No history to undo.'); return; }
  
  let count = 0;
  for (const r of last.renames) {
    try {
      fs.renameSync(path.join(dir, r.new), path.join(dir, r.old));
      count++;
    } catch (e) {
      console.log(`Error undoing ${r.new}: ${e.message}`);
    }
  }
  
  history.pop();
  saveHistory(dir, history);
  console.log(`\n✅ Undone ${count} renames.\n`);
}

function cmdRules() {
  console.log(`\n## Available Rename Rules\n`);
  console.log('Rule                    Description');
  console.log('────────────────────────────────────────────');
  console.log('lowercase               Convert to lowercase');
  console.log('uppercase               Convert to uppercase');
  console.log('trim                    Remove leading/trailing spaces');
  console.log('spaces_to_underscores   Replace spaces with _');
  console.log('underscores_to_spaces   Replace _ with spaces');
  console.log('remove_special          Remove special characters');
  console.log('prefix <text>           Add prefix');
  console.log('suffix <text>           Add suffix before extension');
  console.log('replace <find> <repl>   Replace text');
  console.log('sequence <start>        Number files (0001.ext)');
  console.log('date_prefix             Add date prefix (YYYYMMDD_)');
  console.log('extension <ext>         Change extension');
  console.log();
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  preview: cmdPreview,
  apply: cmdApply,
  undo: cmdUndo,
  rules: cmdRules,
};

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`smart_renamer.js — Intelligent Batch File Renamer

Usage: node smart_renamer.js <command> [args...]

Commands:
  preview <dir> <rule> [args]  Preview renames
  apply <dir> <rule> [args]    Apply renames
  undo <dir>                   Undo last batch
  rules                        List rename rules

Examples:
  node smart_renamer.js preview ./photos lowercase
  node smart_renamer.js apply ./photos date_prefix
  node smart_renamer.js apply ./docs prefix "2026_"
  node smart_renamer.js undo ./photos
`);
  process.exit(0);
}

COMMANDS[cmd](...args);
