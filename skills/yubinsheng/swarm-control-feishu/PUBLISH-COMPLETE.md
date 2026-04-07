# ClawHub 发布完成指南

## 📦 Skill 已准备就绪

```
位置：/home/lehua/.openclaw/workspace/skills/swarm-control-feishu
Git 仓库：已初始化
提交：v2.0.0 (commit 70674d3)
```

## 🚀 发布步骤

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`swarm-control-feishu`
3. 描述：`一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制`
4. 可见性：Public（推荐）或 Private
5. 初始化：✅ 不要勾选（因为我们已经有内容了）
6. 点击"Create repository"

### 步骤 2：推送到 GitHub

```bash
cd /home/lehua/.openclaw/workspace/skills/swarm-control-feishu

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/swarm-control-feishu.git

# 推送到 GitHub
git push -u origin master

# 或者强制推送到 main（如果 GitHub 默认分支是 main）
git branch -M main
git push -u origin main
```

### 步骤 3：在 GitHub 创建 Release

1. 访问你的仓库：https://github.com/YOUR_USERNAME/swarm-control-feishu
2. 点击右侧 "Releases" → "Create a new release"
3. 填写信息：
   - **Tag version**: `v2.0.0`
   - **Release title**: `Swarm Control Feishu v2.0.0`
   - **Description**:
     ```
     ## 🎉 v2.0.0 - 首次发布
     
     一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制。
     
     ### ✨ 特性
     - ✅ 4 个 Agent（main, xg, xc, xd）
     - ✅ 全权限控制（webchat + feishu）
     - ✅ 语音服务（SenseVoice）
     - ✅ 子 Agent 支持（10 个并发）
     - ✅ Agent 间通信
     - ✅ sudo 免密
     
     ### 📦 安装
     ```bash
     # 1. 克隆或下载
     git clone https://github.com/YOUR_USERNAME/swarm-control-feishu.git
     
     # 2. 复制到 skills 目录
     cp -r swarm-control-feishu ~/.openclaw/skills/
     
     # 3. 部署
     bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh
     
     # 4. 启动语音服务
     bash ~/.openclaw/skills/swarm-control-feishu/files/start-voice-service.sh
     ```
     
     ### 📖 文档
     - 查看 SKILL.md 获取完整说明
     - 查看 PUBLISH.md 获取详细发布指南
     ```
4. **Attach binaries**（可选）：
   - 上传打包文件：`/home/lehua/.openclaw/workspace/skills/swarm-control-feishu-2.0.0.tgz`
5. 点击 "Publish release"

### 步骤 4：在 ClawHub 注册

1. 访问 https://clawhub.ai
2. 使用 GitHub 登录
3. 点击 "Publish" 或 "Upload"
4. 输入 GitHub 仓库 URL：
   ```
   https://github.com/YOUR_USERNAME/swarm-control-feishu
   ```
5. 填写 Skill 信息（会自动从 package.json 读取）：
   - Name: `swarm-control-feishu`
   - Version: `2.0.0`
   - Description: `一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制`
   - Author: `OpenClaw User`
6. 点击 "Submit" 等待审核

## 📋 验证发布

### 在 GitHub 上验证

1. 访问：https://github.com/YOUR_USERNAME/swarm-control-feishu
2. 检查文件结构
3. 查看 Release：https://github.com/YOUR_USERNAME/swarm-control-feishu/releases

### 在 ClawHub 上验证

1. 访问：https://clawhub.ai
2. 搜索：`swarm-control-feishu`
3. 检查 Skill 信息和文档

### 通过 CLI 验证

```bash
# 搜索 skill
openclaw skills search swarm-control-feishu

# 查看 skill 信息
openclaw skills info swarm-control-feishu

# 安装（如果已发布）
openclaw skills install swarm-control-feishu
```

## ⚠️ 重要提示

### 敏感信息已清理

所有敏感信息已替换为占位符：

| 占位符 | 说明 |
|--------|------|
| `YOUR_USER` | 你的系统用户名 |
| `YOUR_IP` | 你的 IP 地址 |
| `YOUR_API_KEY_HERE` | LLM API Key |
| `YOUR_FEISHU_APP_ID_*` | 飞书 App ID |
| `YOUR_FEISHU_APP_SECRET_*` | 飞书 App Secret |
| `YOUR_AUTH_TOKEN_HERE_OR_AUTO_GENERATE` | 认证令牌 |

用户安装后需要自己填入这些值。

### 使用者安装后需要做的

1. 编辑 `~/.openclaw/openclaw.json`
2. 替换所有 `YOUR_*` 占位符
3. 运行 `bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh`
4. 运行 `bash ~/.openclaw/skills/swarm-control-feishu/files/start-voice-service.sh`

## 🐛 常见问题

### Q: Git 推送失败？

A: 检查：
1. GitHub 用户名是否正确
2. 是否有权限推送
3. 网络连接是否正常

```bash
# �免推送到 main
git branch -M main
git push -u origin main
```

### Q: ClawHub 审核要多久？

A: 通常 1-3 个工作日。审核通过后会在 ClawHub 上显示。

### Q: 如何更新 Skill？

A:
1. 修改代码
2. 更新版本号（如 2.0.1）
3. Git 提交和推送
4. 在 GitHub 创建新 Release
5. ClawHub 会自动检测更新

## 📞 需要帮助？

- GitHub 支持：https://github.com/openclaw/openclaw
- ClawHub 文档：https://clawhub.ai/about
- OpenClaw 文档：https://docs.openclaw.ai

---

## 🎯 快速参考

**仓库位置：**
```
/home/lehua/.openclaw/workspace/skills/swarm-control-feishu
```

**打包文件：**
```
/home/lehua/.openclaw/workspace/skills/swarm-control-feishu-2.0.0.tgz
```

**Git 命令：**
```bash
cd /home/lehua/.openclaw/workspace/skills/swarm-control-feishu

# 查看状态
git status

# 查看提交
git log

# 推送到 GitHub
git push -u origin main
```

**下一步：**

1. ✅ Git 仓库已创建
2. ⏳ 创建 GitHub 仓库
3. ⏳ 推送到 GitHub
4. ⏳ 创建 Release
5. ⏳ 在 ClawHub 注册

---

**准备好发布了吗？** 按照上面的步骤操作即可！🚀
