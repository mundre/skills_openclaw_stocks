# Manifest 优化建议（1.0.3）

## 问题

ClawHub 安全扫描可能标记 "Suspicious"，原因是 skill 会读写冷记忆文件，但如果 manifest 未声明路径与脚本，平台无法提前知道访问范围。

## 建议的 manifest 修改

```yaml
required_paths:
  - path: memory/cold/
    access: read_write
    description: Cold memory archive — notes, index, metadata, retrieval log
  - path: memory/heartbeat-state.json
    access: read_write
    description: Heartbeat state with coldMemory maintenance metadata

creates_files: true
modifies_files: true
has_scripts: true

scripts:
  - path: scripts/search.py
    description: Search cold memory index and tags metadata
  - path: scripts/rebuild.py
    description: Rebuild index.md and tags.json from note files
  - path: scripts/decay.py
    description: Decay confidence levels based on last_verified age
  - path: scripts/cool.py
    description: Scan daily notes and update coldMemory heartbeat state
```

## 效果

1. 明确声明会访问的路径与脚本
2. 让安装前的权限范围更清楚
3. 降低被平台误判为可疑 skill 的概率
4. 与 Linux / macOS / Windows 通用的 Python helper 方案保持一致