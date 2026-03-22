---
name: omniwire
version: 2.1.0
description: "Control your entire server mesh from chat. Execute commands, transfer files, manage Docker, sync configs, and monitor all your nodes through one unified interface. 30 MCP tools. Works on any architecture (x64, ARM, Apple Silicon). SSH2 with compression, encrypted config sync, 1Password secrets backend."
tags: [infrastructure, mesh, ssh, devops, servers, vps, docker, remote, mcp, file-transfer, monitoring, config-sync, secrets, multi-node, raspberry-pi, arm]
author: VoidChecksum
homepage: https://github.com/VoidChecksum/omniwire
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      bins: ["node", "ssh"]
      env: []
    stateDirs: ["~/.omniwire"]
    persistence: "Uses OmniWire (npm) to manage SSH connections. Config in ~/.omniwire/mesh.json. Encrypted secrets in ~/.omniwire/secret.key. No data leaves your network."
---

# OmniWire — Mesh Control for OpenClaw

> **Your entire infrastructure, controlled from chat.**

Tell your agent to run commands on any server, transfer files between nodes, manage Docker, check system health, sync configurations, and manage secrets — across every machine you own.

```
You: check disk usage on all my servers
Agent: [runs across all nodes simultaneously]
  [server1] /dev/sda1  1.2T  178G  16%
  [server2] /dev/sda1   50G   31G  61%
  [rpi]     /dev/mmcblk0 32G  6.4G 20%
```

---

## Setup — 3 Steps

### Step 1: Install OmniWire

> **AGENT: Run via exec. User clicks Approve.**

```
npm install -g omniwire
```

Works on Linux (x64/ARM), macOS (Intel/Apple Silicon), Windows, Raspberry Pi.

### Step 2: Configure Your Mesh

> **AGENT: Ask the user for their server details (name, IP, SSH user, key filename), then create:**

```
mkdir -p ~/.omniwire
cat > ~/.omniwire/mesh.json << 'EOF'
{
  "nodes": [
    {"id": "server1", "host": "10.0.0.1", "user": "root", "identityFile": "id_ed25519", "role": "storage"}
  ]
}
EOF
```

### Step 3: Verify

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' | omniwire --stdio --no-sync 2>/dev/null | head -1
```

---

## How to Use — Just Talk

### Run commands anywhere
```
You: restart nginx on server1
Agent: [omniwire_exec] systemctl restart nginx → OK

You: show CPU usage on all servers
Agent: [omniwire_broadcast] → server1: 2.3 load | server2: 1.4 | rpi: 0.7
```

### Transfer files between machines
```
You: copy /var/log/app.log from server1 to server2
Agent: Transferred 4.2MB via netcat+gzip in 180ms (23.3 MB/s)
```

Auto-selects: SFTP (<10MB) | netcat+gzip (10MB-1GB) | aria2c (>1GB, 16 parallel connections)

### Manage Docker
```
You: what containers are running?
Agent: [server1] 12 running · 3 stopped: kali-htb neo4j postgres ...
```

### Monitor everything
```
You: how are my servers?
Agent:
  server1 (storage)  | ONLINE | 142ms | load=2.3 | mem=26% | disk=16%
  server2 (compute)  | ONLINE | 198ms | load=1.4 | mem=27% | disk=61%
  rpi     (gpu)      | ONLINE | 215ms | load=0.7 | mem=21% | disk=20%
```

### Manage secrets across nodes
```
You: store OPENAI_KEY=sk-abc123 on all servers
Agent: [omniwire_secrets sync] server1: OK | server2: OK | rpi: OK
```

Supports **1Password** backend: `~/.omniwire/secrets.json` → `{"backend": "onepassword"}`

### Sync AI tool configs
```
You: sync my settings to all servers
Agent: [cybersync_sync_now] pushed=3, pulled=0, conflicts=0
```

Sensitive files encrypted at rest with XChaCha20-Poly1305.

---

## All 30 Tools

### Core (22 tools)
| Tool | Description |
|------|-------------|
| `omniwire_exec` | Run command on one node |
| `omniwire_broadcast` | Run on all nodes simultaneously |
| `omniwire_mesh_status` | Health + resources for all nodes |
| `omniwire_node_info` | Detailed info for one node |
| `omniwire_read_file` / `write_file` | Read/write files on any node |
| `omniwire_transfer_file` | Copy between nodes (auto mode) |
| `omniwire_list_files` / `find_files` | Browse/search remote filesystems |
| `omniwire_tail_log` | Last N lines of any log |
| `omniwire_process_list` | Processes across nodes |
| `omniwire_disk_usage` | Disk usage across nodes |
| `omniwire_install_package` | apt/npm/pip on any node |
| `omniwire_service_control` | systemd start/stop/restart |
| `omniwire_docker` | Docker commands on any node |
| `omniwire_port_forward` | SSH tunnel management |
| `omniwire_deploy` | Push to multiple nodes at once |
| `omniwire_kernel` | dmesg, sysctl, modprobe, strace, perf |
| `omniwire_shell` | Persistent shell sessions |
| `omniwire_stream` | Real-time streaming output |
| `omniwire_live_monitor` | Live system metrics |
| `omniwire_open_browser` | Open URL on GUI node |

### CyberSync (8 tools)
`cybersync_status` · `cybersync_sync_now` · `cybersync_diff` · `cybersync_history` · `cybersync_search_knowledge` · `cybersync_get_memory` · `cybersync_manifest` · `cybersync_force_push`

### Secrets + Update
`omniwire_secrets` (get/set/delete/list/sync) · `omniwire_update` (self-update via npm)

---

## Performance

| Operation | Speed |
|-----------|-------|
| Command execution | ~120ms |
| File read (<1MB) | ~80ms SFTP |
| File transfer (10MB) | ~200ms gzip |
| Config sync | ~200ms parallel |
| Mesh status | ~150ms (5s cache) |

SSH2 with zlib compression. Works over WireGuard, Tailscale, or direct SSH.

---

## Platform Support

Linux x64 ✅ | Linux arm64 (RPi 4/5, Graviton) ✅ | Linux armv7l (RPi 3) ✅ | macOS Intel ✅ | macOS Apple Silicon ✅ | Windows x64 ✅

Pure JavaScript — no native compilation. `npm install -g omniwire` everywhere.

---

## Security

- SSH2 transport encryption + zlib compression
- XChaCha20-Poly1305 at-rest encryption for sensitive configs
- 1Password, file-based, or env var secrets backends
- No external services — runs on your own infrastructure
- Master key generated locally, never transmitted

---

## Agent Instructions

### When to use OmniWire

When the user mentions: servers, VPS, nodes, infrastructure, remote machines, Docker on remote, deploy, sync configs, secrets across machines, monitoring multiple servers, file transfer between servers.

### Tool selection

- Single command on one server → `omniwire_exec`
- Command on all servers → `omniwire_broadcast`
- Read remote file → `omniwire_read_file`
- Copy between servers → `omniwire_transfer_file`
- Docker → `omniwire_docker`
- Health check → `omniwire_mesh_status`
- Secrets → `omniwire_secrets`
- Sync configs → `cybersync_sync_now`

### Node selection defaults

- Storage/files/Docker → node with `role: "storage"`
- Browser/GUI → node with `role: "gpu+browser"`
- Heavy compute → node with `role: "compute"`
- Unclear → ask the user

---

**GitHub**: https://github.com/VoidChecksum/omniwire | **NPM**: https://npmjs.com/package/omniwire

MIT License — *OmniWire: Every machine, one agent, zero friction.*
