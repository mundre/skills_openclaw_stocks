#!/usr/bin/env node
// OpenClaw Emergency Rollback — restore.mjs
// Usage: node restore.mjs [slot]
// Restores a snapshot and restarts OpenClaw.
// Must work with zero AI, zero network, zero user interaction.

import { existsSync } from 'fs';
import { execSync } from 'child_process';
import { join } from 'path';
import {
  ROLLBACK_DIR, SNAPSHOTS_DIR, WATCHDOG_FILE, RESTORE_LOG,
  readJson, writeJson, getConfig, getManifest, getWatchdog,
  appendLog, timestampHuman
} from './utils.mjs';

const SLOT = parseInt(process.argv[2] || '1', 10);
const config = getConfig();
const manifest = getManifest();
const RESTART_CMD = config.restartCommand || 'openclaw gateway restart';

// Find snapshot info
const snapInfo = manifest.snapshots.find(s => s.slot === SLOT);
const snapFile = snapInfo ? snapInfo.file : `snapshot-${SLOT}.zip`;
const snapLabel = snapInfo ? snapInfo.label : 'unknown';
const snapTs = snapInfo ? snapInfo.timestamp : 'unknown';
const zipPath = join(SNAPSHOTS_DIR, snapFile);

if (!existsSync(zipPath)) {
  const msg = `RESTORE FAILED — zip not found: ${zipPath}`;
  appendLog(RESTORE_LOG, msg);
  console.error(`ERROR: ${msg}`);
  process.exit(1);
}

// Determine trigger method
const trigger = process.env.CRON_TRIGGERED === '1'
  ? 'cron watchdog (timer expired)'
  : 'manual';

// Log restore start
appendLog(RESTORE_LOG,
  `RESTORE TRIGGERED\n  Method: ${trigger}\n  Target: snapshot-${SLOT} — "${snapLabel}"\n  Snapshot timestamp: ${snapTs}\n  Zip: ${zipPath}`
);

// Restore files — unzip with full path overwrite to /
let unzipExit = 0;
try {
  execSync(`unzip -o "${zipPath}" -d /`, { stdio: 'ignore' });
} catch (e) {
  unzipExit = e.status || 1;
  appendLog(RESTORE_LOG, `RESTORE WARNING — unzip exit code: ${unzipExit}`);
}

// Disarm watchdog
const watchdog = getWatchdog();
watchdog.armed = false;
writeJson(WATCHDOG_FILE, watchdog);

// Remove the per-minute watchdog cron entry (preserve @reboot entry)
try {
  execSync(
    `(crontab -l 2>/dev/null | grep -v '# openclaw-watchdog' | grep -v '^\\* \\* \\* \\* \\*.*openclaw-rollback/scripts/restore') | crontab - 2>/dev/null`,
    { stdio: 'ignore', shell: '/bin/bash' }
  );
} catch {}

// Run restart command
let restartExit = 0;
try {
  execSync(RESTART_CMD, { stdio: 'inherit', shell: '/bin/bash' });
} catch (e) {
  restartExit = e.status || 1;
}

// Log restore complete
appendLog(RESTORE_LOG,
  `RESTORE COMPLETE\n  Restart command: ${RESTART_CMD}\n  Restart exit: ${restartExit}\n  Unzip exit: ${unzipExit}`
);

process.exit(0);
