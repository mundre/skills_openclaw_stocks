# Team Resurrection —— 一键复刻你的团队

> **搬家 · 分身 · 备份，三合一。** 快速复刻你的多 Agent 团队到新环境、新项目、新实验。
>
> **三大场景：**
> - 🚚 **搬家** — 换电脑、重装系统，一键把整个团队迁到新环境
> - 👯 **分身** — 同环境快速复制一支团队，跑实验、做测试、开新项目
> - 📦 **打包** — 备份团队快照，随时可还原
>
> **版本：** v3.0

---

## 零、快速开始

### 场景一：搬家（跨环境迁移）

```
用户（旧环境）：我要搬家
Agent：好的，开始打包...
       [执行 pack.py]
       打包完成：~/一键搬家包/Agent搬家包_YYYYMMDD.zip
       请把搬家包复制到新环境

用户（新环境）：[把搬家包丢给agent] 这是一键搬家包，帮我搬家
Agent：[执行 migrate.py]
       🔒 备份 → 🔧 Main Agent 配置 → 复制身份/成员/skills → 合并配置 → 重启
       ✅ 搬家完成！
```

### 场景二：分身（同环境复制）

```
用户：帮我分身一个团队，后缀用"测试"
Agent：[执行 clone.py]
       检测到 10 人团队 → 备份配置 → 复制 workspace（加后缀）→ 追加配置 → 重启
       
       原团队：毒舌 / 小策 / 老墨 / ...
       分身：  毒舌-测试 / 小策-测试 / 老墨-测试 / ...
       ✅ 分身完成！
```

### 场景三：备份

```
用户：帮我打一个搬家包
Agent：[执行 pack.py]
       ✅ 打包完成：~/一键搬家包/xxx.zip
```

---

## 一、核心概念

### 1.1 团队激活三要素

子代理要正确激活，必须同时满足三个条件：

| 要素 | 参数 | 作用 |
|------|------|------|
| **身份** | `agentId` | 控制读哪个 SOUL.md（人格定义） |
| **隔离** | `cwd` | 控制子代理的 workspace 根目录 |
| **权限** | `allowAgents` | 白名单，允许 spawn 哪些 agentId |

**关键发现：**
- `agentId` 控制人格，不控制 workspace
- `cwd` 才控制 workspace 隔离
- 不设 cwd → 所有子代理读父代理的 workspace

### 1.2 三大功能对比

| | 打包 `pack.py` | 搬家 `migrate.py` | 分身 `clone.py` |
|---|---|---|---|
| **场景** | 备份/跨环境迁移 | 新环境恢复 | 同环境复制 |
| **输入** | 当前环境 | 搬家包 zip | 当前环境 |
| **输出** | zip 文件 | 配置+文件落地 | 配置+文件落地 |
| **重命名** | 不需要 | 不需要 | ✅ ID/路径加后缀 |
| **配置策略** | 收集快照 | deep merge | 追加（不覆盖） |
| **需要传输** | 是（zip） | 否 | 否 |

### 1.3 备份与回滚

**所有操作前自动备份：**
- 目标：`~/.qclaw/backup/`
- 搬家备份：`搬家备份_YYYYMMDD_HHMMSS/`
- 分身备份：`clone备份_YYYYMMDD_HHMMSS/`

**回滚方法：**
```bash
# 搬家回滚
cp -r ~/.qclaw/backup/搬家备份_xxx/* ~/.qclaw/

# 分身回滚（只需还原配置）
cp ~/.qclaw/backup/clone备份_xxx/openclaw.json ~/.qclaw/openclaw.json
openclaw gateway restart
```

### 1.4 配置合并策略

**核心原则：不覆盖现有配置。**

- **搬家（migrate.py）**：deep merge（agents/hooks 字段级合并，其他保留）
- **分身（clone.py）**：追加新 agent（不触碰原有 agent 条目）
- hooks.allowedAgentIds：取并集

---

## 二、脚本说明

### 2.1 脚本清单

| 脚本 | 功能 | 版本 |
|------|------|------|
| `pack.py` | 打包所有资料（生成搬家包） | v2.0 |
| `migrate.py` | 一键搬家执行（从搬家包恢复） | v2.0 |
| `clone.py` | 一键分身（同环境复制团队） | v1.0 🆕 |
| ~~`setup_config.py`~~ | ~~仅更新配置~~ | ❌ 已废弃 |
| ~~`init.sh`~~ | ~~创建 main agent~~ | ❌ 已废弃 |

### 2.2 pack.py（打包脚本）

**功能：** 自动检测当前 workspace，收集所有资料，生成搬家包

**执行方式：**
```bash
cd skills/team-resurrection
python3 pack.py
```

**输出：** `~/一键搬家包/{Agent名称}搬家包_YYYYMMDD_HHMMSS.zip`

**v2.0 改进：**
- ✅ 不再硬编码 workspace 路径，自动检测 active workspace
- ✅ 自动推断 agent 名称（从 SOUL.md/IDENTITY.md）
- ✅ README.md 根据实际内容动态生成

### 2.3 migrate.py（搬家脚本）

**功能：** 完整的一键搬家流程

**执行方式：**
```bash
# 方式A（推荐）：解压后直接运行
unzip 搬家包.zip && cd 搬家包 && python3 migrate.py

# 方式B：zip 在当前目录
python3 migrate.py

# 方式C：传入路径
python3 migrate.py /path/to/搬家包.zip
```

**执行步骤：**

| Step | 内容 | 说明 |
|------|------|------|
| 0 | 备份现有配置 | 自动检测已有配置，备份到 `~/.qclaw/backup/` |
| 0.5 | Main Agent 配置 | **交互选择**（指向/新建/覆盖） |
| 1 | 复制身份文件 | SOUL.md / MEMORY.md / TOOLS.md 等 |
| 2 | 复制团队成员 | 自动检测，有则复制，无则跳过 |
| 3 | 复制 skills | 整个 skills 目录覆盖 |
| 4 | 合并 agent 配置 | deep merge，保护新环境其他配置 |
| 5 | 创建 cron 任务 | 跳过已存在的 |
| 6 | 重启 Gateway | 等待 5 秒让 channel 注册 |

**Main Agent 选项：**

```
选项 1：指向现有 agent → 把当前 agent 指向新 workspace
选项 2：新建 main agent 实例 → 创建新目录 + 配置
选项 3：覆盖现有 main agent → ⚠️ 需二次确认
```

### 2.4 clone.py（分身脚本）🆕

**功能：** 在同一环境下复制整个团队，所有 ID/路径加后缀避免冲突

**执行方式：**
```bash
# 交互式（会询问后缀）
cd skills/team-resurrection
python3 clone.py

# 指定后缀
python3 clone.py --suffix "测试"
```

**执行步骤：**

| Step | 内容 | 说明 |
|------|------|------|
| 1 | 检测当前团队 | 读 openclaw.json，找 main + 成员 |
| 2 | 询问分身后缀 | 默认 `copy`，可自定义 |
| 3 | 备份配置 | → `~/.qclaw/backup/clone备份_xxx/` |
| 4 | 复制 workspace | 所有 workspace 目录名加后缀 |
| 5 | 复制 agentDir | 所有 agentDir 目录名加后缀 |
| 6 | 重命名 agent ID | 所有 ID 加后缀（如 `xiaoce` → `xiaoce-测试`） |
| 7 | 更新 AGENTS.md | 新 workspace 的 AGENTS.md 中 ID 同步更新 |
| 8 | 追加到 openclaw.json | 不覆盖原有 agent，只追加新 agent |
| 9 | 重启 Gateway | 等待 5 秒让 channel 注册 |

**分身命名示例：**

```
后缀: 测试

原团队：                    分身：
  毒舌 (agent-ba01c6a8)       毒舌-测试 (agent-ba01c6a8-测试)
  小策 (xiaoce)               小策-测试 (xiaoce-测试)
  老墨 (laomo)                老墨-测试 (laomo-测试)
  ...

workspace:
  ~/.qclaw/workspace-agent-ba01c6a8/
  → ~/.qclaw/workspace-agent-ba01c6a8-测试/

  ~/.qclaw/workspace-agent-ba01c6a8/xiaoce/
  → ~/.qclaw/workspace-agent-ba01c6a8-测试/xiaoce-测试/
```

**冲突检测：** 执行前自动检查目标路径是否已存在，冲突则中止（不覆盖）。

---

## 三、搬家包结构

```
搬家包/
├── README.md                    ← 动态生成（含团队成员列表）
├── migrate.py                   ← 一键执行脚本
│
├── 身份层/                      ← Main Agent
│   ├── SOUL.md / MEMORY.md / TOOLS.md / AGENTS.md / IDENTITY.md / USER.md
│   └── memory/
│
├── 团队成员层/                  ← 子代理（自动检测，有则包含）
│   ├── 成员A/SOUL.md
│   └── ...
│
├── skills/                      ← Skills
├── openclaw-agents.json         ← Agent 配置片段
├── cron_tasks.json              ← Cron 任务清单
└── 工作目录说明.md             ← git 工作目录提示
```

### 通用化

| 场景 | pack.py | migrate.py | clone.py |
|------|---------|-----------|----------|
| 有团队 | 打包成员 | 复制成员 | 复制+重命名 |
| 无团队 | 跳过 | 跳过 | 只复制 main |
| 有 cron | 打包 | 创建 | 不涉及 |
| 无 cron | 跳过 | 跳过 | 不涉及 |

---

## 四、配置文件说明

### 4.1 openclaw.json 核心配置

```json
{
  "agents": {
    "list": [
      { "id": "main", "name": "Main Agent" },
      {
        "id": "member-a",
        "name": "成员A",
        "workspace": "/Users/xxx/.qclaw/workspace-xxx/member-a",
        "agentDir": "/Users/xxx/.qclaw/agents/member-a/agent"
      }
    ],
    "defaults": {
      "model": { "primary": "qclaw/modelroute" },
      "maxConcurrent": 10,
      "subagents": { "allowAgents": ["*"] }
    }
  },
  "hooks": { "allowedAgentIds": ["member-a", "member-b"] }
}
```

### 4.2 关键配置项

| 配置项 | 说明 |
|--------|------|
| `agents.list[].id` | Agent 标识 |
| `agents.list[].name` | 显示名 |
| `agents.list[].workspace` | Agent workspace 绝对路径 |
| `agents.list[].agentDir` | Agent 独立目录（含 models.json） |
| `agents.defaults.subagents.allowAgents` | Spawn 白名单，`["*"]` 允许所有 |
| `hooks.allowedAgentIds` | hooks 触发白名单 |

---

## 五、常见问题排查

### 问题1：`agentId is not allowed`

**原因：** openclaw.json 缺少 `allowAgents` 白名单

**解决：** migrate.py / clone.py 执行时自动补上 `["*"]`

### 问题2：子代理读错 SOUL.md

**原因：** spawn 时没传 `cwd` 参数

**解决：** 必须同时传 `agentId` + `cwd`：
```javascript
sessions_spawn({
  agentId: "member-a",
  cwd: "/Users/xxx/.qclaw/workspace-xxx/member-a",
  mode: "run",
  task: "..."
})
```

### 问题3：Gateway 重启后 spawn 报错 `unknown channel`

**原因：** Gateway 重启时 channel 注册需要几秒

**解决：** 重启后等 5-10 秒再 spawn

### 问题4：分身后 ID 冲突

**现象：** clone.py 报"目标 workspace 已存在"

**解决：** 换一个后缀，或手动删除旧分身：
```bash
rm -rf ~/.qclaw/workspace-xxx-旧后缀
# 然后从 openclaw.json 中删除对应 agent 条目
```

### 问题5：搬家后配置丢失

**原因：** v1.0 用 config replace

**解决：** v2.0+ 已修复（deep merge）。回滚：`cp -r ~/.qclaw/backup/搬家备份_xxx/* ~/.qclaw/`

---

## 六、验证清单

### 搬家验证

- [ ] `openclaw gateway status` 显示 running
- [ ] `ls ~/.qclaw/workspace-*/SOUL.md` 找到 SOUL.md
- [ ] openclaw.json 包含所有 agent 配置
- [ ] `agents.defaults.subagents.allowAgents: ["*"]` 已设置
- [ ] 测试 spawn 至少 2 个 agent，确认人格正确

### 分身验证

- [ ] openclaw.json 中同时存在原团队和分身团队
- [ ] 分身 workspace 路径带后缀
- [ ] 分身 agent ID 带后缀
- [ ] 用分身 ID spawn，确认读的是分身 workspace 的 SOUL.md
- [ ] 原团队 spawn 不受影响

---

## 七、维护建议

1. **定期打包**：重大变更后重新 `pack.py`
2. **备份保留**：至少保留最近 3 次备份
3. **分身清理**：实验完成后删除分身 workspace + 从 openclaw.json 移除条目
4. **日志记录**：所有配置变更记录到 `memory/YYYY-MM-DD.md`

---

## 八、相关文档

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Sessions 文档：https://docs.openclaw.ai/automation/sessions
- Cron 文档：https://docs.openclaw.ai/automation/cron
- Agent 配置：https://docs.openclaw.ai/config/agents
- **材料打包记录：** `MATERIAL_PACKING.md`

---

## 附录：版本变更记录

### v3.0（2026-04-23）

**新增：**
- ✅ `clone.py` 一键分身脚本——同环境复制整个团队，ID/路径自动加后缀
- ✅ SKILL.md 全面升级：介绍改为"搬家·分身·备份三合一"，新增分身场景文档
- ✅ 分身命名策略：后缀式（`agent-xxx-后缀`），交互式或 `--suffix` 参数指定
- ✅ 冲突检测：目标路径已存在则中止，不覆盖
- ✅ AGENTS.md 自动更新：分身 workspace 内的 agent ID 同步加后缀

### v2.0（2026-04-22）

**P0 修复：**
- ✅ pack.py 不再硬编码 workspace-xxx，改为自动检测 active workspace
- ✅ migrate.py 执行前自动备份，现有配置不再丢失
- ✅ config 改为 deep merge，保护新环境其他配置
- ✅ create_main_agent() 三个选项逻辑补全

**P1 修复/优化：**
- ✅ 删除了 init.sh/setup_config.py 的误导文档
- ✅ migrate.py 找包逻辑优化，兼容多种运行方式
- ✅ backup_existing() 自动检测需备份的目标
- ✅ cron 创建区分已存在/失败

### v1.0（2026-04-21）

- 初始版本：pack.py + migrate.py + setup_config.py + init.sh
- 支持有/无团队的通用化检测
- 三个 main agent 选项（选项1/2 执行逻辑残缺）
