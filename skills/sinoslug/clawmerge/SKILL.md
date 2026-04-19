---
name: clawmerge
version: 3.0.9
description: |
  OpenClaw workspace 备份/恢复/合并工具。
  支持：完整备份、合并恢复（不覆盖已有）、Cron 任务备份、会话记录备份、配置导出。
  触发词：「备份」「恢复」「迁移」「换电脑」「导出配置」「合并记忆」。
  当 workspace 需要迁移、定期备份、或从另一台设备恢复时使用。
---

# Clawmerge - Workspace 备份/恢复工具

> 换电脑不丢记忆，备份不覆盖重要文件。

## 核心能力

| 功能 | 说明 |
|-----|------|
| **完整备份** | 打包整个 workspace（可排除敏感文件） |
| **合并恢复** | 解压时不覆盖已有文件，适合从另一台设备增量恢复 |
| `--merge-auth` | 备份里有但本地没有 gateway token 时，自动填充（additive only）|
| **Cron 备份** | 自动备份 cron 任务配置 |
| **会话备份** | 可选包含会话记录（.jsonl） |
| **配置导出** | 导出脱敏后的公开配置 |

---

## 使用场景

### 场景 1：定期备份（手动）
```bash
cd ~/.openclaw/workspace
./skills/clawmerge/scripts/one-click-backup.sh /tmp/backup-$(date +%Y%m%d).tar.gz
```

### 场景 2：换电脑后恢复（合并模式）
```bash
# 从备份文件恢复，不覆盖已有文件
./skills/clawmerge/scripts/one-click-restore.sh /path/to/backup.tar.gz --merge
```

### 场景 3：查看备份内容（不解压）
```bash
tar -tzf backup.tar.gz | head -50
```

### 场景 4：只备份 Cron 任务
```bash
./skills/clawmerge/scripts/backup-cron-tasks.sh
```

---

## 脚本清单

| 脚本 | 用途 |
|-----|------|
| `one-click-backup.sh` | 一键备份 workspace |
| `one-click-restore.sh` | 解压恢复（支持 --merge 合并模式） |
| `backup-cron-tasks.sh` | 单独备份 cron 配置 |
| `restore-cron-tasks.sh` | 恢复 cron 配置 |
| `discover-scripts.py` | 扫描 workspace 中的自定义脚本 |
| `gen-requirements.py` | 生成 requirements.txt |
| `post-restore-check.sh` | 恢复后检查完整性 |
| `workspace-manager.sh` | workspace 空间管理（查看大小/清理） |

---

## 备份排除规则

以下文件默认排除（不备份）：

| 排除 | 原因 |
|-----|------|
| `*.pyc` | 编译缓存 |
| `__pycache__/` | Python 缓存 |
| `.session/` | 临时会话 |
| `node_modules/` | npm 包（可从 package.json 恢复） |
| `secrets.json` | 密钥文件 |
| `openclaw.json` | 包含 bot token 等敏感信息 |

**配置备份**：敏感配置用 `configs/public-config.json` 代替（含股票列表、推送目标等公开部分，密钥用占位符）。

---

## 合并恢复逻辑（--merge）

```bash
# 合并模式：遇到同名文件
# - 若原文件与备份不同 → 保留原文件（不覆盖）
# - 若原文件不存在 → 从备份解压
# - 备份中有、原文件没有 → 恢复
```

**使用 --merge 的场景**：
- 从另一台设备的备份恢复（避免覆盖本机已有的配置）
- 合并两台设备的工作成果

**不使用 --merge 的场景**：
- 全新环境直接恢复 → 直接解压覆盖

---

## Dry Run 预览

```bash
# 先看会备份哪些文件，不实际执行
./one-click-backup.sh --dry-run /tmp/test.tar.gz
```

---

## 输出物

备份成功后生成：
- `backup.tar.gz`：主备份文件
- `backup-manifest.txt`：备份文件清单
- `backup-cron-config.json`：Cron 任务配置（JSON格式）

恢复后生成：
- `restore-report.txt`：恢复报告（含跳过/覆盖/新增文件列表）

---

## 故障处理

| 问题 | 解决方案 |
|-----|---------|
| 备份文件过大 | 使用 `--exclude` 排除大文件/目录 |
| 恢复失败 | 检查 `.tar.gz` 是否损坏；尝试 `tar -tzf` 验证 |
| Cron 未恢复 | 手动运行 `restore-cron-tasks.sh` |
| 会话记录丢失 | 下次启动 agent 时会自动重建空会话 |

---

## 依赖

- `bash`
- `tar`
- `python3`（用于 discover-scripts.py 和 gen-requirements.py）

---

*备份不是为了恢复，是为了放心地往前走。* 📦
