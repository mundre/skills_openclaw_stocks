#!/usr/bin/env node
/**
 * Save Markdown to Obsidian vault
 *
 * Usage: node save.mjs <markdown_file> [--path <vault_subpath>]
 *
 * Reads config.json for vault name and default path.
 * Filename is derived from the YAML frontmatter title.
 *
 * Tries obsidian CLI first, falls back to direct file write.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { execSync } from "child_process";
import { dirname, join, resolve } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const configPath = join(__dirname, "..", "config.json");

// --- Args ---
const args = process.argv.slice(2);
const mdFile = args.find(a => !a.startsWith("--"));
let overridePath = null;
const pathIdx = args.indexOf("--path");
if (pathIdx !== -1 && args[pathIdx + 1]) {
  overridePath = args[pathIdx + 1];
}

if (!mdFile) {
  console.error("Usage: node save.mjs <markdown_file> [--path <vault_subpath>]");
  process.exit(1);
}

// --- Config ---
let config = { obsidian_vault: "", default_path: "" };
try {
  config = JSON.parse(readFileSync(configPath, "utf-8"));
} catch {}

if (!config.obsidian_vault) {
  console.error("Error: obsidian_vault not configured in config.json");
  console.error("Run the skill once and let your AI agent set it up, or edit config.json manually.");
  process.exit(1);
}

const vaultName = config.obsidian_vault;
const savePath = overridePath || config.default_path;

if (!savePath) {
  console.error("Error: no save path specified (use --path or set default_path in config.json)");
  process.exit(1);
}

// --- Read markdown and extract title for filename ---
const mdContent = readFileSync(mdFile, "utf-8");
let filename = "untitled.md";

const titleMatch = mdContent.match(/^title:\s*"(.+?)"/m);
if (titleMatch) {
  // Clean title for filename: keep Chinese chars, alphanumeric, spaces→underscores
  filename = titleMatch[1]
    .replace(/[\/\\:*?"<>|]/g, "")
    .trim() + ".md";
}

const targetPath = `${savePath}/${filename}`;

// --- Try obsidian CLI first ---
function tryObsidianCli() {
  try {
    // Check if obsidian CLI exists
    execSync("which obsidian", { stdio: "ignore" });

    // Escape content for shell - write to temp file and read it
    const tmpFile = `/tmp/wx_save_${Date.now()}.md`;
    writeFileSync(tmpFile, mdContent);
    const content = readFileSync(tmpFile, "utf-8");

    execSync(
      `obsidian create path="${targetPath}" content="${content.replace(/"/g, '\\"').replace(/\$/g, '\\$')}" vault=${vaultName}`,
      { stdio: "inherit", timeout: 10000 }
    );

    // Clean up temp file
    try { execSync(`rm ${tmpFile}`, { stdio: "ignore" }); } catch {}
    return true;
  } catch {
    return false;
  }
}

// --- Fallback: direct file write ---
function directWrite() {
  // Try to find vault disk path
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const possiblePaths = [
    join(homeDir, "Library/Mobile Documents/iCloud~md~obsidian/Documents", vaultName),
    join(homeDir, "Documents/obsidian", vaultName),
    join(homeDir, "Obsidian", vaultName),
    join(homeDir, vaultName),
  ];

  let vaultRoot = null;
  for (const p of possiblePaths) {
    if (existsSync(p)) {
      vaultRoot = p;
      break;
    }
  }

  if (!vaultRoot) {
    console.error(`Error: could not find vault "${vaultName}" on disk.`);
    console.error("Searched:", possiblePaths.join(", "));
    console.error("Use obsidian CLI or specify the vault disk path manually.");
    process.exit(1);
  }

  const fullPath = join(vaultRoot, targetPath);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, mdContent, "utf-8");
  console.log(`Saved: ${fullPath}`);
}

// --- Execute ---
console.log(`Saving to vault="${vaultName}" path="${targetPath}"`);

if (!tryObsidianCli()) {
  console.log("obsidian CLI not available, falling back to direct file write...");
  directWrite();
}

console.log("Done.");
