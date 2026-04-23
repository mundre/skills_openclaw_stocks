#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, 'factory');
const SITES = path.join(ROOT, 'sites');

function listSites() {
  return fs.readdirSync(SITES, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}

function createSite(name, briefPath) {
  const out = path.join(SITES, name);
  if (fs.existsSync(out)) throw new Error('site exists: ' + name);
  fs.mkdirSync(out);
  // copy brief if provided
  if (briefPath && fs.existsSync(briefPath)) {
    fs.copyFileSync(briefPath, path.join(out, 'brief.md'));
  }
  return out;
}

function runScript(script, args=[]) {
  const scriptPath = path.join(ROOT, 'scripts', script);
  if (!fs.existsSync(scriptPath)) throw new Error('script not found: ' + script);
  const r = spawnSync('bash', [scriptPath, ...args], { stdio: 'inherit' });
  if (r.error) throw r.error;
  return r.status;
}

function help() {
  console.log('amys-website-factory skill wrapper');
  console.log('commands: list | create <name> [brief] | check <name> | deploy <name> [--prod]');
}

async function main(argv) {
  const cmd = argv[2];
  try {
    if (!cmd) return help();
    if (cmd === 'list') {
      console.log(listSites().join('\n'));
      return;
    }
    if (cmd === 'create') {
      const name = argv[3];
      if (!name) throw new Error('missing name');
      // scaffold with bundled new-site script
      if (fs.existsSync(path.join(ROOT,'scripts','new-site.sh'))) {
        runScript('new-site.sh', ['--slug', name]);
        console.log('created', path.join('sites', name));
        return;
      }
      const out = createSite(name, null);
      console.log('created', out);
      return;
    }
    if (cmd === 'clone') {
      const repo = argv[3];
      const name = argv[4] || path.basename(repo, '.git');
      if (!repo) throw new Error('missing repo URL');
      const dest = path.join(SITES, name);
      if (fs.existsSync(dest)) throw new Error('target exists: '+name);
      // clone using git (requires git installed)
      console.log('cloning', repo, 'to', dest);
      const r = spawnSync('git', ['clone', repo, dest], { stdio: 'inherit' });
      if (r.error) throw r.error;
      console.log('cloned into', dest);
      return;
    }
    if (cmd === 'check') {
      const name = argv[3];
      if (!name) throw new Error('missing name');
      runScript('verify-site.sh', ['--site', path.join('sites', name), '--name', name, '--port', '3000', '--routes', path.join('sites', name, 'routes.json')]);
      return;
    }
    if (cmd === 'deploy') {
      const name = argv[3];
      if (!name) throw new Error('missing name');
      const prod = argv.includes('--prod') ? '--prod' : '';
      runScript('deploy-site.sh', ['--site', path.join('sites', name), prod].filter(Boolean));
      return;
    }
    help();
  } catch (err) {
    console.error('error:', err.message);
    process.exit(2);
  }
}



