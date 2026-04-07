---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022057c97db6bffe199b7c2195ddf225334cbe35fcde7c88682583a12435b1834cee022100f2a07641323be21f88cf9c99c57ce9251d711e22e513c5021f155abc887171fa
    ReservedCode2: 3046022100ef56ce35a902fb024bb1db8edc17f9ccf675d4fce4e5e8f88a8f5309b2cfd7a2022100aa8fb0f37c20580fcda2699cf0f39008e6dad35653ff31cfeb568a19aa789a41
---

# Plant Care Expert - 发布指南

## 概述

本技能「植物识别与养护专家」(plant-care-expert) 是一个专业的植物识别与养护咨询技能，可帮助用户识别植物种类并提供科学的养护方案。

---

## 发布渠道

### 1. ClawHub (OpenClaw 官方市场)

**访问地址**: https://clawhub.com

**发布步骤**:

1. 注册/登录 ClawHub 账号
2. 点击 "Publish Skill" 或 "上传技能"
3. 填写技能信息：
   - **名称**: `plant-care-expert`
   - **描述**: 植物识别与养护专家技能，支持识别植物种类、评估养护难度、提供养护指南
   - **分类**: Plant Care / Gardening
   - **标签**: plant-care, indoor-plants, plant-identification, gardening, plant-diagnosis
   - **作者**: 填写您的名称
   - **版本**: 1.0.0
4. 上传技能文件夹（包含 SKILL.md 和 references/）
5. 添加预览图片（可选）
6. 提交审核

### 2. MiniMax Agent (MiniMax 平台)

**访问地址**: https://agent.minimax.io

**发布步骤**:

1. 登录 MiniMax Agent
2. 访问 Skill Creator: https://agent.minimax.io/skill-creator
3. 选择 "Set up validation and packaging for my existing skill"
4. 导入现有的 SKILL.md 文件
5. 按照指引完善信息并发布

### 3. GitHub (开源分享)

**仓库地址**: https://github.com/yourusername/plant-care-expert

**文件夹结构**:

```
plant-care-expert/
├── SKILL.md                      # 主技能文件
├── README.md                     # 说明文档
├── LICENSE                       # MIT 许可证
├── PUBLISH.md                   # 发布指南
└── references/
    ├── plant_database.md         # 常见植物数据库
    └── troubleshooting.md        # 问题排查手册
```

---

## 安装方式

### 通过 clawhub CLI 安装

```bash
# 安装 clawhub
npm i -g clawhub

# 安装技能
clawhub install plant-care-expert --source /path/to/plant-care-expert
```

### 通过 Git 克隆安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/plant-care-expert.git

# 复制到 skills 目录
cp -r plant-care-expert ~/.openclaw/skills/
```

### 手动安装

1. 下载或克隆技能文件夹
2. 将 `plant-care-expert` 文件夹复制到 OpenClaw 的 `skills/` 目录
3. 重启 OpenClaw 服务

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| 植物识别 | 通过图片识别植物种类 |
| 养护难度评估 | 五级难度体系 |
| 环境匹配判断 | 评估光照/温度/湿度/通风 |
| 养护指南生成 | 光照、浇水、土壤、温度、施肥 |
| 问题诊断 | 叶片发黄、萎蔫、病虫害等 |
| 急救措施 | 缺水、水涝、冻害、肥害 |

### 内置知识库

- **植物数据库**: 30+ 常见室内植物信息
- **问题排查手册**: 常见问题诊断和处理方案

### 支持的植物类型

- 观叶植物（绿萝、吊兰、龟背竹等）
- 多肉植物（仙人掌、芦荟、玉露等）
- 开花植物（蝴蝶兰、长寿花、山茶花等）
- 藤本植物（常春藤、藤本月季等）
- 水培植物（绿萝、吊兰、风信子等）

---

## 使用示例

### 示例 1: 识别植物

**用户**: 帮我看看这是什么植物

**助手**:
```
📷 植物识别结果

**植物名称**：绿萝
**拉丁学名**：Epipremnum aureum
**养护难度**：⭐☆☆☆☆（一级/极易养护）
```

### 示例 2: 养护可行性评估

**用户**: 我想养蝴蝶兰，可以吗？

**助手**:
```
🌱 养护可行性评估

**结论**：可以养护，但需要注意湿度

**当前环境匹配度**：
- 光照：✅ 符合
- 温度：✅ 符合
- 湿度：⚠️ 需改善
```

### 示例 3: 问题诊断

**用户**: 叶子发黄怎么办

**助手**:
```
🔍 问题诊断

**可能原因**：
- 浇水过多或过少
- 光照不足
- 缺肥或土壤问题

**确认方法**：检查土壤湿度和光照条件
```

---

## 版本历史

### v1.0.0 (2024-04-07)
- 初始版本发布
- 支持植物识别功能
- 提供养护难度评估
- 包含 30+ 常见植物数据库
- 问题排查手册覆盖常见问题

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交植物数据

如需添加新的植物数据，请参考 `references/plant_database.md` 的格式。

### 提交问题解决方案

如需补充问题排查内容，请参考 `references/troubleshooting.md` 的格式。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- GitHub Issues: https://github.com/yourusername/plant-care-expert/issues
- 邮箱: your.email@example.com

---

## 致谢

本技能的植物数据参考了以下来源：

- 中国植物志
- 维基百科植物条目
- 各大园艺论坛和资料
- 实际养护经验总结
