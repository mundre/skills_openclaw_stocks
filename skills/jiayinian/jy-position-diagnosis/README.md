# jy-position-diagnosis-skill

证券投顾持仓诊断技能 - 基于恒生聚源 (gildata) MCP 金融数据库

## 快速开始

### 1. 安装依赖

```bash
npm install -g mcporter
```

### 2. 配置 MCP 服务

```bash
# 获取 JY_API_KEY 后配置
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

### 3. 验证配置

```bash
mcporter list
```

### 4. 使用技能

在对话中触发：
- "请帮我诊断持仓：贵州茅台 100 股 成本 1600 元"
- "持仓诊断：宁德时代 200 股 成本 180 元"
- "分析我的持仓"

## 目录结构

```
jy-position-diagnosis/
├── SKILL.md              # 技能定义和使用说明
├── README.md             # 本文件
├── references/
│   ├── template.md       # 报告模板
│   └── data_sources.md   # MCP 工具使用说明
└── examples/
    └── sample_diagnosis.md  # 示例诊断报告
```

## 五维度诊断

1. **持仓分析** - 持仓结构、资产配置、盈亏情况
2. **风险舆情** - 近 7 天风险舆情监控
3. **持仓优化** - 减仓/增配建议
4. **产品推荐** - 同类替代产品筛选
5. **用户画像** - 投资偏好与风险承受能力

## JY_API_KEY 申请

向恒生聚源官方邮箱发送邮件申请：
- **邮箱：** datamap@gildata.com
- **标题：** 数据地图 KEY 申请 -XX 公司 - 申请人姓名

详见 `SKILL.md` 中的"环境检查与配置"章节。

## 免责声明

本报告仅供研究参考，**NOT investment advice**。市场有风险，投资需谨慎。
