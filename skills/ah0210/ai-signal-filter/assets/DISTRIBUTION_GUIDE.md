# AI信号筛选器 - 多智能体分发指南

## 一、Skill 标准合规性

✅ 已符合 OpenClaw AgentSkill 规范：

| 检查项 | 状态 |
|--------|------|
| SKILL.md 存在且有标准 frontmatter | ✅ |
| 触发条件描述完整准确 | ✅ |
| references/ 参考文档独立 | ✅ |
| scripts/ 可执行脚本 | ✅ |
| runtime-templates/ 运行时模板 | ✅ |
| 资产文件隔离 | ✅ |
| 无冗余 README 等文件 | ✅ |
| 渐进式披露设计 | ✅ |

## 二、分发给其他智能体的三种方式

### 方式1：直接复制 Skill 目录（推荐）

```bash
# 1. 复制整个 skill 目录到目标智能体的 skills 目录
cp -r ai-signal-filter/ /path/to/other-agent/skills/

# 2. 目标智能体执行初始化
python3 skills/ai-signal-filter/scripts/run-signal-filter.py --init
```

✅ **优点**：最简单，代码+配置+模板一次性复制
⚠️ **注意**：每个智能体有独立的 `memory/signal/` 运行时目录，数据不共享

---

### 方式2：通过 Cron 任务集成

```bash
# 目标智能体安装定时任务
python3 skills/ai-signal-filter/scripts/install-cron.py 09:00
```

✅ 适合需要每日自动执行的智能体
✅ 可自定义执行时间（参数如：08:30, 18:00）

---

### 方式3：作为子 Skill 跨会话调用

在其他智能体的对话中触发：
> 「执行 ai-signal-filter skill 生成今日信号」

OpenClaw 会自动加载 Skill 并执行流程。

## 三、标准化调用接口

所有智能体统一使用这些接口：

| 命令 | 作用 |
|------|------|
| `run-signal-filter.py --init` | 初始化运行时目录，创建用户画像模板 |
| `run-signal-filter.py` | 执行一次信号筛选，生成报告 |
| `run-signal-filter.py --cron` | cron模式，静默输出 |
| `install-cron.py [HH:MM]` | 安装每日定时任务 |

## 四、运行时目录结构

每个智能体独立的运行时数据位于：
```
memory/signal/
├── profile.md          # 用户画像 + 反馈 + 信息源评分（每个智能体不同）
├── history.md          # 7天去重历史记录
└── YYYY-MM-DD-report.md # 每日生成的报告
```

## 五、跨智能体协作最佳实践

1. **代码共享，数据隔离**：所有智能体共享同一份 Skill 代码，每个智能体有自己的 `memory/signal/` 目录

2. **画像统一模板，按需定制**：每个智能体可以有不同的关注权重和排除项

3. **报告分发**：生成的报告可通过 `sessions_send()` 跨会话推送给其他智能体

4. **反馈闭环**：每个智能体的反馈独立记录，不影响其他智能体的评分系统

5. **信息源评分共享（可选）**：如需共享高质量信息源名单，可定期同步 profile.md 的评分部分
