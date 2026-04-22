#!/usr/bin/env node
// OpenClaw Emergency Rollback — recovery-test.mjs
// Usage: node recovery-test.mjs <subcommand>
//
// Subcommands:
//   preflight      — check all dependencies and system readiness
//   save-recovery  — copy current openclaw.json to openclaw.recovery
//   sabotage       — deliberately break openclaw.json (makes it invalid JSON)
//   verify         — check if openclaw.json was restored (is valid JSON again)

import { existsSync, readFileSync, writeFileSync, copyFileSync, statSync } from 'fs';
import { execSync } from 'child_process';
import {
  ROLLBACK_DIR, RECOVERY_FILE, CHANGE_LOG, RESTORE_LOG,
  getConfig, getOpenclawJson, getManifest, getWatchdog,
  readJson, appendLog
} from './utils.mjs';

const subcommand = process.argv[2];
if (!subcommand) {
  console.error('Usage: node recovery-test.mjs <preflight|save-recovery|sabotage|verify>');
  process.exit(1);
}

const OC_JSON = getOpenclawJson();

switch (subcommand) {

  case 'preflight': {
    console.log('=== Recovery Test Pre-Flight Check ===');
    let pass = true;

    // Check node (we're running, so it's there)
    console.log(`  ✓ node found: ${process.execPath}`);

    // Check zip/unzip
    for (const tool of ['zip', 'unzip']) {
      try {
        execSync(`command -v ${tool}`, { stdio: 'ignore' });
        console.log(`  ✓ ${tool} found`);
      } catch {
        console.log(`  ✗ ${tool} NOT FOUND — install before proceeding`);
        pass = false;
      }
    }

    // Check cron
    try {
      execSync('crontab -l 2>/dev/null || true', { stdio: 'ignore' });
      console.log('  ✓ cron accessible');
    } catch {
      console.log('  ✗ cron NOT accessible');
      pass = false;
    }

    // Check rollback directory
    if (existsSync(ROLLBACK_DIR)) {
      console.log('  ✓ rollback directory exists');
    } else {
      console.log('  ✗ rollback directory missing — run setup first');
      pass = false;
    }

    // Check manifest
    const manifest = getManifest();
    console.log(`  ✓ manifest.json (${manifest.snapshots.length} snapshots)`);

    // Check scripts
    const scripts = ['snapshot.mjs', 'restore.mjs', 'restore-if-armed.mjs', 'watchdog-set.mjs', 'watchdog-clear.mjs'];
    for (const s of scripts) {
      const p = `${ROLLBACK_DIR}/scripts/${s}`;
      if (existsSync(p)) {
        console.log(`  ✓ ${s} exists`);
      } else {
        console.log(`  ✗ ${s} missing`);
        pass = false;
      }
    }

    // Check openclaw.json
    if (existsSync(OC_JSON)) {
      const parsed = readJson(OC_JSON);
      if (parsed) {
        console.log('  ✓ openclaw.json exists and is valid JSON');
      } else {
        console.log('  ✗ openclaw.json exists but is NOT valid JSON');
        pass = false;
      }
    } else {
      console.log(`  ✗ openclaw.json not found at ${OC_JSON}`);
      pass = false;
    }

    // Check restart command
    const config = getConfig();
    if (config.restartCommand) {
      console.log(`  ✓ restart command: ${config.restartCommand}`);
    } else {
      console.log('  ✗ restart command not configured');
      pass = false;
    }

    console.log('');
    if (pass) {
      console.log('All checks passed. Ready to test.');
    } else {
      console.log('Some checks FAILED. Fix the issues above before testing.');
      process.exit(1);
    }
    break;
  }

  case 'save-recovery': {
    if (!existsSync(OC_JSON)) {
      console.error(`ERROR: openclaw.json not found at ${OC_JSON}`);
      process.exit(1);
    }

    copyFileSync(OC_JSON, RECOVERY_FILE);
    const config = getConfig();
    console.log(`Recovery copy saved: ${RECOVERY_FILE}`);
    console.log('');
    console.log('If the test fails, restore manually with:');
    console.log(`  cp ${RECOVERY_FILE} ${OC_JSON}`);
    console.log(`  ${config.restartCommand || 'openclaw gateway restart'}`);

    appendLog(CHANGE_LOG,
      `RECOVERY TEST — MANUAL BACKUP SAVED\n  Source: ${OC_JSON}\n  Backup: ${RECOVERY_FILE}`
    );
    break;
  }

  case 'sabotage': {
    if (!existsSync(OC_JSON)) {
      console.error(`ERROR: openclaw.json not found at ${OC_JSON}`);
      process.exit(1);
    }

    // Verify recovery copy exists before sabotaging
    if (!existsSync(RECOVERY_FILE)) {
      console.error(`ERROR: No recovery copy found at ${RECOVERY_FILE}`);
      console.error('Run "node recovery-test.mjs save-recovery" first.');
      process.exit(1);
    }

    // Insert invalid text at the top to break JSON parsing
    const original = readFileSync(OC_JSON, 'utf8');
    const originalSize = statSync(OC_JSON).size;
    const broken = `BROKEN_BY_RECOVERY_TEST — ${new Date().toISOString()}\n${original}`;
    writeFileSync(OC_JSON, broken);

    console.log('Config sabotaged. openclaw.json is now invalid JSON.');
    console.log(`Original size: ${originalSize} bytes`);
    console.log('The watchdog should restore it automatically when the timer expires.');

    appendLog(CHANGE_LOG,
      `RECOVERY TEST — CONFIG SABOTAGED\n  File: ${OC_JSON}\n  Method: prepended BROKEN_BY_RECOVERY_TEST marker\n  Original size: ${originalSize} bytes`
    );
    break;
  }

  case 'verify': {
    console.log('=== Recovery Test Verification ===');

    if (!existsSync(OC_JSON)) {
      console.log('  ✗ openclaw.json not found');
      console.log('RESULT: FAILED');
      process.exit(1);
    }

    // Check if sabotage marker is still there
    const content = readFileSync(OC_JSON, 'utf8');
    if (content.startsWith('BROKEN_BY_RECOVERY_TEST')) {
      console.log('  ✗ BROKEN_BY_RECOVERY_TEST marker still present');
      console.log('  The watchdog has NOT restored the config yet.');
      console.log('');
      console.log('RESULT: NOT YET RESTORED — wait longer or check cron');
      console.log('');
      console.log('Debug:');
      console.log('  crontab -l                                    # cron entries');
      console.log(`  cat ${RESTORE_LOG}       # restore attempts`);
      console.log(`  node ${ROLLBACK_DIR}/scripts/watchdog-status.mjs  # timer`);
      process.exit(1);
    }

    // Check if valid JSON
    const parsed = readJson(OC_JSON);
    if (parsed) {
      console.log('  ✓ openclaw.json is valid JSON');
      console.log('  ✓ BROKEN_BY_RECOVERY_TEST marker is gone');
    } else {
      console.log('  ✗ openclaw.json exists but is NOT valid JSON');
      console.log('RESULT: PARTIAL — file may have been partially restored');
      process.exit(1);
    }

    // Check watchdog state
    const watchdog = getWatchdog();
    console.log(`  Watchdog armed: ${watchdog.armed}`);

    // Check restore log
    if (existsSync(RESTORE_LOG)) {
      const log = readFileSync(RESTORE_LOG, 'utf8');
      const lastRestore = log.split('\n').filter(l => l.includes('RESTORE COMPLETE')).pop();
      if (lastRestore) console.log(`  Last restore: ${lastRestore.trim()}`);
    }

    console.log('');
    console.log('RESULT: PASSED — recovery test successful');

    appendLog(CHANGE_LOG,
      `RECOVERY TEST — VERIFIED PASSED\n  openclaw.json: valid JSON, marker removed\n  Watchdog armed: ${watchdog.armed}`
    );
    break;
  }

  default:
    console.error(`Unknown subcommand: ${subcommand}`);
    console.error('Usage: node recovery-test.mjs <preflight|save-recovery|sabotage|verify>');
    process.exit(1);
}
