# Clawmerge 更新记录

## v3.0.9（2026-04-17）

### 安全性修复

**问题1：restore 会覆盖机器级凭证（🔴 严重）**
- **现象**：restore 解压时不加区分地覆盖所有文件，导致 `auth-profiles.json`（API keys）、`openclaw.json`（gateway token）等机器级凭证被旧备份覆盖
- **影响**：换电脑恢复场景下，新机器的凭证被旧备份覆盖，OpenClaw 失联
- **修复**：在 `one-click-restore.sh` 解压后、写入 workspace 前，新增 SECURITY 保护段：
  - 将 `agents/main/agent/auth-profiles.json`、`agents/main/agent/models.json`、`openclaw.json`、`exec-approvals.json` 重命名为 `.bak-日期`，绝不覆盖当前机器凭证
  - 用户始终保留本机 credentials

**问题2：旧版本 backup 覆盖新版本脚本**
- **现象**：旧备份中的 clawmerge 脚本可能在恢复时覆盖新版本脚本
- **修复**：新增版本检查机制
  - backup 脚本输出 `.backup-version` 文件记录版本号
  - restore 脚本读取版本号，版本不一致时弹窗确认，防止意外降级

**问题3：cron jobs 备份包含运行时状态字段**
- **现象**：cron jobs 备份包含 `lastRunAtMs`、`consecutiveErrors` 等机器运行时状态，恢复后状态错乱
- **修复**：备份时剥离所有 state 相关字段（`lastRunAtMs`、`lastRunStatus`、`consecutiveErrors` 等），只保存可移植的 job 定义

### 功能修复

**问题4：backup 路径双斜杠 bug**
- **现象**：`./backup-cron-tasks.sh /tmp/` 时，输出路径变成 `/tmp//cron-tasks-*.json`（双斜杠），且 `$exported_count` 变量在 bash heredoc 内 undefined
- **修复**：`OUTPUT_DIR="${OUTPUT_DIR%/}"` 末尾去 `/`；移除 bash 变量直接引用，改用 Python 输出

**问题5：cron jobs 恢复需手动操作**
- **现象**：`one-click-restore.sh` 检测到 cron 备份后只打印 Manual 引导，实际不恢复
- **修复**：Step 5 改为自动调用 `restore-cron-tasks.sh --dry-run` 预览，确认后执行 merge

**问题6：gateway token 无法 merge**
- **现象**：新机器没有 gateway token（从备份恢复时），只能靠手动复制
- **修复**：新增 `--merge-auth` 参数：
  - `backup-cron-tasks.sh` 同时导出 `auth_token` 字段（从 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 读取）
  - `restore-cron-tasks.sh --merge-auth`：当前 token 为空 + 备份有 → 自动填充；当前已有 token → 跳过（保护）

### 文件变更

| 文件 | 变更 |
|------|------|
| `one-click-backup.sh` | 新增 Step 5 `.backup-version` 标签；Step 编号对齐（4→6） |
| `one-click-restore.sh` | SECURITY 保护段；VERSION CHECK；cron merge 自动引导 |
| `backup-cron-tasks.sh` | 去双斜杠；导出 `auth_token` |
| `restore-cron-tasks.sh` | 重写为纯 Python；新增 `--merge-auth` |
| `_meta.json` | changelog 更新 |
| `SKILL.md` | 新增 `--merge-auth` 说明 |

---

## v3.0.8（2026-03-26）

**修复**：`--with-sessions` 排除 bug
- 原因：tar 的 `--exclude=.backup-sessions` 对所有路径生效，导致会话记录未实际打包
- 修复：通过条件 `EXCLUDE_ITEMS` 解决，`--with-sessions=true` 时不加入排除列表

---

## v3.0.7（2026-03-26）

**修复**：`--with-sessions` 文字提示 bug
- 现象：显示"✓ Session records will be included"，但实际未打包
- 修复：显式添加 `.backup-sessions` 到 tar 命令

---

## v3.0.0（2026-03-18）

**首发 ClawHub**：workspace 备份/恢复/合并工具
- 完整备份、合并恢复、Cron 任务备份、会话记录备份、配置导出
