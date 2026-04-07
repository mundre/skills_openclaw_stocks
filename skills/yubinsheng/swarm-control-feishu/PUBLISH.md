# ClawHub 发布指南

## 📦 准备工作

Skill 已打包完成：
```
/home/lehua/.openclaw/workspace/skills/swarm-control-feishu-2.0.0.tgz (15KB)
```

## 🚀 发布方法

### 方法 1：本地安装（推荐用于测试）

1. **复制到 skills 目录**

```bash
# 复制 skill 目录
cp -r /home/lehua/.openclaw/workspace/skills/swarm-control-feishu \
      ~/.openclaw/skills/

# 或者解压
mkdir -p ~/.openclaw/skills
tar -xzf /home/lehua/.openclaw/workspace/skills/swarm-control-feishu-2.0.0.tgz \
        -C ~/.openclaw/skills/
```

2. **验证安装**

```bash
# 列出所有 skills
openclaw skills list

# 查看 skill 信息
openclaw skills info swarm-control-feishu

# 检查 skill 状态
openclaw skills check
```

3. **使用 Skill**

```bash
# 部署
bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh

# 启动语音服务
bash ~/.openclaw/skills/swarm-control-feishu/files/start-voice-service.sh
```

---

### 方法 2：通过 ClawHub 发布（推荐用于分享）

**注意：** 当前 OpenClaw CLI 暂不支持直接发布到 ClawHub，需要手动操作。

#### 步骤 1：注册 ClawHub 账号

访问 https://clawhub.ai 并使用 GitHub 登录。

#### 步骤 2：准备发布文件

确保以下文件存在且正确：

```
swarm-control-feishu/
├── package.json          # ✅ 已创建
├── SKILL.md              # ✅ 已创建
├── README.md             # ✅ 已创建
├── files/
│   ├── openclaw-config.json      # ✅ 已创建（带注释）
│   ├── AGENTS.md               # ✅ 已创建
│   ├── AGENTS_TEMPLATE.md     # ✅ 已创建
│   └── start-voice-service.sh  # ✅ 已创建（可执行）
└── scripts/
    ├── deploy.sh               # ✅ 已创建（可执行）
    ├── setup-workspaces.sh     # ✅ 已创建（可执行）
    ├── sync-config.sh          # ✅ 已创建（可执行）
    └── check-status.sh         # ✅ 已创建（可执行）
```

#### 步骤 3：验证 package.json

```bash
cat ~/.openclaw/skills/swarm-control-feishu/package.json
```

应该包含：

```json
{
  "name": "swarm-control-feishu",
  "version": "2.0.0",
  "description": "一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制",
  "author": "OpenClaw User",
  "license": "MIT",
  "keywords": ["feishu", "swarm", "agents", "voice", "multi-agent"]
}
```

#### 步骤 4：发布到 GitHub（推荐）

1. **创建 GitHub 仓库**

```bash
# 初始化 git
cd /home/lehua/.openclaw/workspace/skills/swarm-control-feishu
git init

# 创建 .gitignore
cat > .gitignore << 'EOF'
*.tgz
.DS_Store
EOF

# 添加文件
git add .

# 提交
git commit -m "Initial commit: Swarm Control Feishu v2.0.0"

# 添加远程仓库（替换为你的 GitHub 仓库）
git remote add origin https://github.com/your-username/swarm-control-feishu.git

# 推送
git push -u origin main
```

2. **在 ClawHub 上添加 Skill**

访问 https://clawhub.ai 并：

1. 点击 "Publish" 或 "Upload"
2. 输入 GitHub 仓库 URL
3. 等待审核和索引

---

### 方法 3：通过 API 发布（高级用户）

**前提：** 需要 ClawHub API Token

```bash
# 1. 获取 API Token（在 ClawHub 设置中）
TOKEN="clh_XBP37Ynwplhhqk7ob-3_jkrGkY-AQYU8BEu__nGhym8"

# 2. 上传 skill
curl -X POST https://clawhub.ai/api/v1/skills/publish \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "swarm-control-feishu",
    "version": "2.0.0",
    "repository": "https://github.com/your-username/swarm-control-feishu"
  }'
```

---

## 🔍 验证发布

### 在 ClawHub 上搜索

访问 https://clawhub.ai/skills 并搜索 "swarm-control-feishu"。

### 通过 CLI 搜索

```bash
# 搜索 skill
openclaw skills search swarm-control-feishu

# 安装（如果已发布）
openclaw skills install swarm-control-feishu
```

---

## 📋 发布清单

在发布前，请确认：

- [x] `package.json` 正确配置
- [x] `SKILL.md` 完整且清晰
- [x] `README.md` 包含使用说明
- [x] 所有脚本可执行（`chmod +x`）
- [x] `openclaw-config.json` 带完整注释
- [x] 已在本地测试部署成功
- [ ] 已创建 GitHub 仓库
- [ ] 已更新 `package.json` 中的 `repository.url`
- [ ] 已在 GitHub 上发布 release
- [ ] 已在 ClawHub 上注册并提交审核

---

## ⚠️ 注意事项

1. **API Key 和敏感信息**
   - `openclaw-config.json` 中包含你的真实 API Key
   - 发布前应该将其替换为占位符或示例值
   - 用户安装后需要自己填入

2. **版本管理**
   - 使用语义化版本（SemVer）
   - 主版本.次版本.修订版本（如 2.0.0）

3. **文档**
   - `SKILL.md` 是核心文档，必须详细
   - `README.md` 是快速入门指南
   - 两者内容应该互补

4. **测试**
   - 发布前在干净的环境中测试
   - 确保所有脚本都能正常执行
   - 验证语音服务可以启动

---

## 🎯 快速发布命令

```bash
# 1. 切换到 skill 目录
cd /home/lehua/.openclaw/workspace/skills/swarm-control-feishu

# 2. 打包
tar -czf swarm-control-feishu-2.0.0.tgz \
    SKILL.md README.md package.json files/ scripts/

# 3. 推送到 GitHub
git add .
git commit -m "Release v2.0.0"
git push origin main

# 4. 在 GitHub 上创建 Release
#    - 访问 https://github.com/your-username/swarm-control-feishu/releases/new
#    - 标签：v2.0.0
#    - 上传 swarm-control-feishu-2.0.0.tgz

# 5. 在 ClawHub 上提交审核
#    - 访问 https://clawhub.ai
#    - 输入仓库 URL
#    - 等待审核
```

---

## 📞 需要帮助？

- OpenClaw 文档：https://docs.openclaw.ai
- ClawHub 文档：https://clawhub.ai/about
- 提交 Issue：https://github.com/openclaw/openclaw/issues

---

**祝你发布顺利！** 🎉
