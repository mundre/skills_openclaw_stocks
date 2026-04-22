#!/usr/bin/env node
// OpenClaw Emergency Rollback — restore-if-armed.mjs
// Called by @reboot and per-minute cron entries.
// Checks if watchdog is armed and timer has expired. Fires restore if so.

import { existsSync } from 'fs';
import { execSync } from 'child_process';
import { join } from 'path';
import { ROLLBACK_DIR, WATCHDOG_FILE, RESTORE_LOG, getWatchdog, appendLog } from './utils.mjs';

if (!existsSync(WATCHDOG_FILE)) {
  process.exit(0);
}

const watchdog = getWatchdog();

if (!watchdog.armed) {
  process.exit(0);
}

const now = Math.floor(Date.now() / 1000);
const expiry = watchdog.expiryEpoch || 0;

if (now >= expiry) {
  appendLog(RESTORE_LOG, 'CRON/REBOOT CHECK — watchdog armed and expired, triggering restore');
  // Set env and exec restore
  process.env.CRON_TRIGGERED = '1';
  const restoreScript = join(ROLLBACK_DIR, 'scripts', 'restore.mjs');
  try {
    execSync(`node "${restoreScript}"`, { stdio: 'inherit', env: { ...process.env, CRON_TRIGGERED: '1' } });
  } catch (e) {
    appendLog(RESTORE_LOG, `CRON/REBOOT RESTORE ERROR — exit code: ${e.status || 'unknown'}`);
    process.exit(1);
  }
} else {
  const remaining = expiry - now;
  appendLog(RESTORE_LOG, `CRON/REBOOT CHECK — watchdog armed, ${remaining}s remaining`);
}

process.exit(0);
