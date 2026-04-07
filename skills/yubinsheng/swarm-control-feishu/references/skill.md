# Swarm Control Feishu - 飞书智能体集群管理

**版本：** 2.0.0  
**作者：** OpenClaw User  
**描述：** 一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制

## 📖 功能说明

这个 Skill 可以帮助你：

1. **一键搭建飞书智能体集群** - 自动配置多个 agent（main, xg, xc, xd）
2. **全权限控制** - webchat 和飞书渠道都有最大权限，包括提权和 sudo 免密
3. **语音服务集成** - 自动配置语音转录服务，所有 agent 都能听能说
4. **子 Agent 支持** - 所有 agent 都可以创建子 agent，支持并行任务
5. **多项目并行** - 像"集团"一样管理多个飞书机器人

## 🚀 快速开始

### 前置要求

- 已安装 OpenClaw
- 有飞书开放平台账号
- 准备好飞书机器人的 App ID 和 App Secret（最多 4 个）

### 使用方法

1. **加载 Skill**
   - 在 OpenClaw 中输入：`/skills load swarm-control-feishu`
   - 或者直接解压到 `~/.openclaw/skills/swarm-control-feishu/`

2. **准备配置**
   - 编辑 `files/openclaw-config.json`，填入你的飞书账号信息
   - 必填项：
     - `channels.feishu.accounts.*.appId` - 飞书 App ID
     - `channels.feishu.accounts.*.appSecret` - 飞书 App Secret
     - `models.providers.jmrzw.apiKey` - LLM API Key

3. **应用配置**
   - 运行：`bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh`
   - 或者在 OpenClaw 中执行：`apply-config`

4. **启动语音服务**
   - 运行：`bash ~/.openclaw/skills/swarm-control-feishu/scripts/start-voice-service.sh`

5. **完成！**
   - 所有 agent 已就绪
   - 可以在飞书中测试机器人和语音功能

## 📋 目录结构

```
swarm-control-feishu/
├── SKILL.md              # 本文件
├── files/
│   ├── openclaw-config.json      # OpenClaw 完整配置（带详细注释）
│   ├── AGENTS.md               # Agent 共享配置
│   ├── AGENTS_TEMPLATE.md     # Agent 配置模板
│   └── start-voice-service.sh  # 语音服务启动脚本
├── scripts/
│   ├── deploy.sh               # 一键部署脚本
│   ├── setup-workspaces.sh     # 创建工作空间
│   ├── sync-config.sh          # 同步配置到所有 agent
│   └── check-status.sh         # 检查状态
└── README.md                   # 使用说明
```

## 🔧 配置说明

### OpenClaw 主配置 (openclaw-config.json)

**核心配置项：**

```json
{
  // ========== AGENTS 配置 ==========
  "agents": {
    "defaults": {
      // 工作空间路径（主 agent）
      "workspace": "/home/lehua/.openclaw/workspace",
      
      // 模型配置（示例 2 个，可扩展）
      "models": {
        "jmrzw/glm-4.7": { "alias": "GLM" },
        "jmrzw/deepseek-v3.2": { "alias": "DeepSeek" }
      },
      
      // 默认模型（必填）
      "model": { "primary": "jmrzw/glm-4.7" },
      
      // 沙箱模式（关闭 = 全权限）
      "sandbox": { "mode": "off" },
      
      // 子 Agent 配置（允许创建子 agent）
      "subagents": {
        "maxConcurrent": 10,           // 最大并发数
        "maxSpawnDepth": 5,            // 最大嵌套深度
        "maxChildrenPerAgent": 10,     // 每个 agent 最多子 agent
        "archiveAfterMinutes": 60,      // 归档时间
        "runTimeoutSeconds": 600        // 运行超时
      }
    },
    
    // Agent 列表（必填）
    "list": [
      {
        "id": "main",                      // Agent ID（必填）
        "workspace": "/home/lehua/.openclaw/workspace",  // 工作空间（必填）
        "model": { "primary": "jmrzw/glm-4.7" },  // 模型（必填）
        "sandbox": { "mode": "off" }      // 沙箱模式
      },
      // ... 其他 agent
    ]
  },
  
  // ========== 渠道绑定（必填）==========
  "bindings": [
    { "agentId": "main", "match": { "channel": "feishu", "accountId": "default" } },
    // ... 其他绑定
  ],
  
  // ========== 网关配置 ==========
  "gateway": {
    "mode": "local",                    // 运行模式
    "auth": { 
      "mode": "token", 
      "token": "自动生成或填写"        // 认证令牌
    },
    "port": 18789,                     // 端口号
    "bind": "lan"                      // 绑定地址
  },
  
  // ========== 工具权限配置（核心）==========
  "tools": {
    "profile": "full",                 // 工具配置文件（full = 最大权限）
    
    "exec": { 
      "host": "auto",                 // 执行主机
      "security": "full",              // 安全模式（full = 无限制）
      "ask": "off"                    // 询问确认（off = 不询问）
    },
    
    "fs": { 
      "workspaceOnly": false           // 文件系统权限（false = 全部）
    },
    
    "elevated": { 
      "enabled": true,                // 启用提权
      "allowFrom": {                   // 允许提权的渠道
        "webchat": ["*"],             // webchat 全部用户
        "feishu": ["*"]              // 飞书全部用户
      }
    },
    
    "sessions": { 
      "visibility": "all"             // session 可见性（all = 全部）
    },
    
    "agentToAgent": { 
      "enabled": true                  // 允许 agent 间通信
    }
  },
  
  // ========== 模型配置（必填）==========
  "models": {
    "providers": {
      "jmrwz": {                     // 提供商 ID（可自定义）
        "baseUrl": "https://jmrai.net/v1",  // API 地址
        "apiKey": "sk-xxxxx",          // API Key（必填）
        "api": "openai-completions",    // API 类型
        "models": [                    // 模型列表
          {
            "id": "glm-4.7",          // 模型 ID
            "name": "GLM 4.7",        // 模型名称
            "input": ["text"],         // 输入类型
            "contextWindow": 128000,   // 上下文窗口
            "maxTokens": 8192,        // 最大 token
            "cost": {                 // 成本（可选）
              "input": 0.0028,
              "output": 0.0028
            }
          },
          // ... 其他模型
        ]
      }
    }
  },
  
  // ========== 飞书渠道配置（必填）==========
  "channels": {
    "feishu": {
      "enabled": true,                 // 启用飞书
      "connectionMode": "websocket",   // 连接模式
      "domain": "feishu",            // 域名
      "groupPolicy": "open",          // 群组策略
      "subagentSecurity": "full",      // 子 agent 安全策略
      "accounts": {                   // 飞书账号（必填）
        "default": {
          "appId": "cli_xxxxx",       // 飞书 App ID（必填）
          "appSecret": "xxxxx"        // 飞书 App Secret（必填）
        },
        // ... 其他账号
      }
    }
  },
  
  // ========== Session 配置 ==========
  "session": {
    "dmScope": "per-channel-peer"     // DM session 范围
  }
}
```

### 语音服务配置

语音服务基于 Python + FastAPI，使用 SenseVoice 模型进行语音识别。

**启动脚本：** `start-voice-service.sh`

**依赖：**
- Python 3.8+
- FastAPI
- uvicorn
- funasr（sensevoice）

**服务地址：** http://localhost:8080

**API 端点：**
- `GET /health` - 健康检查
- `POST /transcribe` - 语音转录

## 🤖 Agent 说明

### 集群架构

这个配置创建了一个"集团式"的智能体集群：

```
用户 → main (小华)
     ├─→ xg (小古) - 项目 A
     ├─→ xc (小程) - 项目 B
     └─→ xd (小鼎) - 项目 C
```

### Agent 职责

| Agent | 名称 | 职责 | 用户 |
|-------|------|------|------|
| main | 小华 | 总控，分配任务 | 管理员 |
| xg | 小古 | 项目 A 专家 | 项目 A 成员 |
| xc | 小程 | 项目 B 专家 | 项目 B 成员 |
| xd | 小鼎 | 项目 C 专家 | 项目 C 成员 |

### Agent 通信

- **Agent 间通信** - 启用 `agentToAgent`，可互相发送消息
- **跨 Session 访问** - `sessions.visibility: all`，可查看所有 session
- **子 Agent 创建** - 所有 agent 都可以创建子 agent 处理并行任务

## 🎤 语音功能

所有 agent 都支持语音输入和输出：

**处理流程：**
1. 用户在飞书中发送语音
2. OpenClaw 接收语音文件
3. 调用语音服务：`POST http://localhost:8080/transcribe`
4. 返回转录文本
5. Agent 根据文本回复

**自动检测：**
- Agent 启动时自动检测语音服务
- 调用：`curl -s http://localhost:8080/health`
- 如果返回 `{"status":"ok"}`，自动启用语音

## 🔐 权限说明

### OpenClaw 权限

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `tools.profile` | `full` | 最大工具权限 |
| `tools.exec.security` | `full` | 命令执行无限制 |
| `tools.exec.ask` | `off` | 不询问确认 |
| `tools.fs.workspaceOnly` | `false` | 可访问所有文件 |
| `tools.sessions.visibility` | `all` | 可见所有 session |
| `tools.agentToAgent.enabled` | `true` | 允许 agent 间通信 |
| `tools.elevated.enabled` | `true` | 允许提权 |
| `sandbox.mode` | `off` | 无沙箱限制 |

### 系统权限

| 配置项 | 值 | 说明 |
|--------|-----|------|
| sudo 免密 | 是 | `lehua ALL=(ALL) NOPASSWD: ALL` |
| elevated 提权 | 是 | webchat 和 feishu 都可用 |

### 飞书权限

- 126 个权限（需要在飞书开放平台后台申请）
- 核心权限：消息读写、文档操作、云盘、通讯录

## 📝 使用示例

### 示例 1：启动集群

```bash
# 应用配置
bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh

# 启动语音服务
bash ~/.openclaw/skillsswarm-control-feishu/scripts/start-voice-service.sh

# 检查状态
bash ~/.openclaw/skills/swarm-control-feishu/scripts/check-status.sh
```

### 示例 2：添加新 Agent

编辑 `files/openclaw-config.json`，在 `agents.list` 中添加：

```json
{
  "id": "xe",
  "workspace": "/home/lehua/.openclaw/workspace-xe",
  "model": { "primary": "jmrzw/glm-4.7" },
  "sandbox": { "mode": "off" }
}
```

然后在 `bindings` 中添加：

```json
{
  "agentId": "xe",
  "match": { "channel": "feishu", "accountId": "xe" }
}
```

在 `channels.feishu.accounts` 中添加账号信息。

### 示例 3：在飞书中使用

1. 打开飞书，找到对应的机器人
2. 发送消息测试
3. 发送语音测试（需要启动语音服务）
4. 机器人会自动回复

## 🛠️ 故障排查

### 问题 1：Agent 无法响应

**检查：**
```bash
# 检查网关状态
openclaw status

# 检查 session 列表
openclaw sessions list

# 查看日志
tail -f ~/.openclaw/logs/gateway.log
```

### 问题 2：语音服务无法工作

**检查：**
```bash
# 检查语音服务状态
curl http://localhost:8080/health

# 查看语音服务日志
tail -f /tmp/sensevoice.log
```

**重启语音服务：**
```bash
bash ~/.openclaw/skills/swarm-control-feishu/scripts/start-voice-service.sh
```

### 问题 3：权限不足

**检查：**
```bash
# 检查 sudo 配置
sudo whoami

# 检查 OpenClaw 配置
openclaw config get
```

## 📚 扩展阅读

- OpenClaw 文档：https://docs.openclaw.ai
- 飞书开放平台：https://open.feishu.cn
- ClawHub：https://clawhub.ai

## 🤝 贡献

欢迎提 Issue 和 PR！

## 📄 许可证

MIT License

---

**有问题？** 查看故障排查章节或访问 OpenClaw 文档。

**准备好了吗？** 运行 `deploy.sh` 开始部署你的飞书智能体集群！🚀
