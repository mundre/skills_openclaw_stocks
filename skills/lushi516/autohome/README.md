# 🚗 Autohome - 汽车资讯获取技能

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)
![Version](https://img.shields.io/badge/version-1.2.1-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**Autohome** 是一个用于获取汽车之家最新资讯的OpenClaw技能，支持定时推送和格式化输出。

## ✨ 功能特性

- 📰 **获取最新汽车资讯** - 从汽车之家获取最新的10条资讯
- 🎨 **格式化输出** - 美观的Markdown格式，包含标题、链接、摘要
- ⏰ **定时任务支持** - 可配置每日定时推送（默认每天9:00）
- 🔗 **询价入口** - 每条资讯附带"立即询价"链接
- 📱 **多平台支持** - 支持Feishu、Telegram等消息平台
- 🔧 **易于配置** - 简单的命令行配置

## 🚀 快速开始

### 安装技能
```bash
clawhub install autohome
```

### 获取今日资讯
```
获取汽车之家最新10条资讯
```

### 配置定时任务
```bash
openclaw cron add --name "daily-car-news" \
  --cron "0 9 * * *" \
  --message "获取汽车之家最新10条资讯" \
  --to "user:你的用户ID" \
  --channel feishu \
  --announce
```

## 📋 输出示例

**2026 年 3 月 16 日汽车之家最新 10 条资讯汇总**

（1）[预计25-35万元 深蓝Z7以及深蓝Z7T将于3月23日正式并开启预售](https://www.autohome.com.cn/news/202603/1312959.html) | [立即询价](https://www.autohome.com.cn)


摘要：深蓝品牌全新大型轿车深蓝Z7以及深蓝Z7T将于3月23日正式发布并开启预售，新车定位高端市场。

（2）[约25万元起 捷途M6将于3月23日开启预售 搭载第二代鲲鹏动力系统](https://www.autohome.com.cn/news/202603/1312958.html) | [立即询价](https://www.autohome.com.cn)


摘要：捷途M6将于3月23日正式开启预售，定位大型SUV，预计售价约25万元起，搭载第二代鲲鹏动力系统。

## 🛠️ 技术架构

### 工具依赖
- `web_fetch` - 网页内容获取
- `exec` - 命令执行
- `openclaw cron` - 定时任务管理

### 数据源
- 汽车之家新闻：https://www.autohome.com.cn/news/

## 📁 文件结构

```
autohome/
├── SKILL.md              # 技能主文档
├── README.md             # 使用说明
├── package.json          # 技能元数据
├── reference.md          # 详细参考文档
├── cron-config.json      # 定时任务配置模板
└── scripts/
    └── get-car-news.sh   # 资讯获取示例脚本
```

## 🔧 配置选项

### 定时任务时间
- 每天9:00：`0 9 * * *`
- 每天12:00：`0 12 * * *`
- 工作日9:00：`0 9 * * 1-5`

### 输出平台
- Feishu（默认）
- Telegram
- WhatsApp
- Discord

## 🐛 故障排除

### 常见问题
1. **无法获取资讯** - 检查网络连接和汽车之家可访问性
2. **定时任务不执行** - 运行 `openclaw cron status`
3. **格式问题** - 检查输出格式配置

### 调试命令
```bash
# 查看任务状态
openclaw cron list

# 手动运行测试
openclaw cron run daily-car-news

# 检查技能配置
openclaw skills info autohome
```

## 📈 使用场景

### 🏢 企业用户
- 汽车经销商：获取最新车型信息
- 汽车媒体：跟踪行业动态
- 投资机构：监控汽车市场变化

### 👤 个人用户
- 汽车爱好者：每日汽车资讯推送
- 购车者：了解最新车型和价格
- 行业从业者：跟踪技术发展

## 🔄 更新日志

### v1.0.1 (2026-03-16)
- 🔧 修复脚本中的品牌名称不一致问题
- 📝 完善package.json文件配置
- 📋 添加完整的技能发布元数据

### v1.0.0 (2026-03-16)
- 🎉 初始版本发布
- ✅ 支持汽车之家资讯获取
- ✅ 完整的格式化输出
- ✅ 定时任务配置
- ✅ 询价入口功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👏 致谢

- 感谢 [汽车之家](https://www.autohome.com.cn) 提供资讯数据
- 感谢 OpenClaw 社区的支持
- 感谢所有贡献者和使用者

---

**让汽车资讯获取变得简单高效！** 🚀