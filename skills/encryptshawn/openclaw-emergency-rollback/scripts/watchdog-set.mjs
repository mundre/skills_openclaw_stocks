#!/usr/bin/env node
// OpenClaw Emergency Rollback — watchdog-set.mjs
// Usage: node watchdog-set.mjs <minutes>
// Arms the watchdog for the given number of minutes.

import { execSync } from 'child_process';
import {
  ROLLBACK_DIR, WATCHDOG_FILE, CHANGE_LOG,
  writeJson, getManifest, appendLog, timestamp
} from './utils.mjs';

const minutes = parseInt(process.argv[2], 10);
if (!minutes || minutes <= 0) {
  console.error('Usage: node watchdog-set.mjs <minutes>');
  process.exit(1);
}

const now = Math.floor(Date.now() / 1000);
const expiry = now + minutes * 60;
const setAt = timestamp();
const expiryDate = new Date(expiry * 1000);
const expiryHuman = expiryDate.toISOString().replace(/\.\d+Z$/, 'Z');
const expiryDisplay = expiryDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });

// Read target snapshot label
const manifest = getManifest();
const snap1 = manifest.snapshots.find(s => s.slot === 1);
const targetLabel = snap1 ? snap1.label : 'no snapshot saved';

// Write watchdog.json
writeJson(WATCHDOG_FILE, {
  armed: true,
  setAt,
  expiryEpoch: expiry,
  expiryHuman,
  minutesSet: minutes,
  targetSnapshot: 'snapshot-1',
  targetLabel
});

// Install per-minute cron entry calling restore-if-armed.mjs
// Tag with '# openclaw-watchdog' so clear/restore can find and remove only this line
// Preserve @reboot entry (which also calls restore-if-armed.mjs but starts with @reboot)
const cronLine = `* * * * * node ${ROLLBACK_DIR}/scripts/restore-if-armed.mjs # openclaw-watchdog`;
try {
  execSync(
    `(crontab -l 2>/dev/null | grep -v '# openclaw-watchdog' | grep -v '^\\* \\* \\* \\* \\*.*openclaw-rollback/scripts/restore'; echo '${cronLine}') | crontab -`,
    { stdio: 'ignore', shell: '/bin/bash' }
  );
} catch (e) {
  console.error('WARNING: Failed to install cron entry. Watchdog may not fire automatically.');
}

// Log
appendLog(CHANGE_LOG,
  `WATCHDOG ARMED\n  Minutes: ${minutes}\n  Expiry: ${expiryHuman}\n  Target: snapshot-1 — "${targetLabel}"`
);

console.log(`Watchdog armed — ${minutes} minutes. Expires at ${expiryDisplay}. Target: ${targetLabel}`);
