# 助学星 — 功能详解与架构文档

## 一、应用架构

### 技术栈
- **单文件 SPA**：所有 HTML/CSS/JS 集成在一个 `.html` 文件中，零依赖
- **数据持久化**：全部使用 `localStorage`，支持离线运行
- **运行环境**：微信小程序 WebView，支持 `window.parent.handleGoto()` 父页面导航
- **UI 框架**：纯 CSS 手写组件，无第三方框架

### 页面结构（Tab 导航）
底部 Tab 栏切换四个视图：
1. **首页 (home)** — 统计概览 + 今日任务 + AI 建议
2. **任务 (tasks)** — 任务列表 + 备忘录列表
3. **目标 (goals)** — 目标管理 + 偏差分析
4. **添加 (add)** — 快速添加表单（任务/备忘录/目标）

---

## 二、功能模块详解

### 2.1 任务管理

**数据模型 (`Task`)**：
```javascript
{
  id: string,          // 唯一标识（时间戳+随机字符串）
  title: string,       // 任务标题
  desc: string,        // 任务描述（支持换行）
  date: string,        // 截止日期 (YYYY-MM-DD)
  time: string,        // 截止时间 (HH:MM)，可选
  priority: string,    // 优先级: high / med / low
  tag: string,         // 分类标签
  done: boolean,       // 完成状态
  doneAt: number|null, // 完成时间戳
  img: string|null,    // 附件图片（Base64）
  createdAt: number    // 创建时间戳
}
```

**核心功能**：
- 任务 CRUD（增删改查）
- 优先级三级标记（高/中/低），左侧色条区分
- 倒计时徽章：紧急（<24h）/ 正常 / 已逾期 / 已过期
- 任务完成后半透明 + 删除线样式
- 图片附件支持

### 2.2 备忘录管理

**数据模型 (`Memo`)**：
```javascript
{
  id: string,
  title: string,
  content: string,     // 支持换行的文本内容
  tag: string,
  img: string|null,
  createdAt: number
}
```

**核心功能**：
- 独立备忘录列表，按标签筛选
- 支持图片附件
- 与任务共用"添加"表单，通过类型切换

### 2.3 目标规划

**数据模型 (`Goal`)**：
```javascript
{
  id: string,
  title: string,
  direction: string,   // 考公/考编/考研/留学/创业/就业/综合素养
  period: string,      // 大学/高中/初中/小学
  status: string,      // not_started/in_progress/deviated/completed/abandoned
  subGoals: [{         // 子目标列表
    id: string,
    text: string,
    done: boolean
  }],
  createdAt: number,
  updatedAt: number
}
```

**预设方向与模板**：
- 7 个发展方向，每个方向在 4 个教育阶段都有预设子目标
- 用户可从模板一键生成目标，也可手动创建
- 目标模板包括月度任务、年度规划、特殊事件三类

**偏差分析**：
- 计算公式：实际进度 - 期望进度
- 期望进度基于时间流逝比例（已过天数/总天数）
- 偏差 > 20% 触发红色预警

### 2.4 统计面板

**统计指标**：
| 指标 | 计算方式 |
|------|---------|
| 完成率 | 已完成/总数 × 100% |
| 趋势对比 | 今日完成率 vs 昨日（箭头指示） |
| 优先级分布 | 高/中/低各占比例 |
| 标签分布 | 各标签完成数/总数 |
| 7日日历热力图 | 每日完成率 0-100%，颜色深浅 |

**等级系统**：
| 等级 | 积分范围 | 称号 |
|------|---------|------|
| Lv.1 | 0-99 | 学徒 |
| Lv.2 | 100-299 | 新手 |
| Lv.3 | 300-599 | 入门 |
| Lv.4 | 600-999 | 熟练 |
| Lv.5 | 1000-1499 | 精通 |
| Lv.6 | 1500-2499 | 专家 |
| Lv.7 | 2500-3499 | 大师 |
| Lv.8 | 3500-4499 | 宗师 |
| Lv.9 | 4500-5000 | 传奇 |
| Lv.10 | 5000+ | 传说 |

**积分规则**：
- 完成普通任务：+10 分
- 连续完成 3 天：额外 +5 分
- 连续完成 7 天：额外 +10 分

### 2.5 滚动标题栏

- **位置**：页面顶部 header 下方
- **内容**：用户自定义条目 + 固定推广条目
- **交互**：点击打开编辑弹窗，可增删自定义条目
- **固定条目**：不可删除，点击调用 `window.parent.handleGoto(TICKER_FIXED_URL)` 跳转
- **数据格式**：`[{text: string, url: string}]`，纯字符串自动转为 `{text, url:''}`

### 2.6 数据管理

**备份**：
- 导出所有 localStorage 数据为 JSON 文件
- 包含 12 个数据键的完整备份

**恢复**：
- 上传 JSON 文件恢复数据
- 恢复前自动备份当前数据到 `_autoBackup_beforeRestore`

**重置**：
- 一键清除所有应用数据
- 重置前同样自动备份

---

## 三、扩展指南

### 常用自定义常量

```javascript
// 应用标题（HTML <title>）
// 修改位置：第 6 行

// 主题色
:root{--primary:#6C63FF;...}  // CSS 变量，第 8 行

// 目标方向
const GOAL_DIRECTIONS=['考公','考编','考研','留学','创业','就业','综合素养'];

// 教育阶段
const GOAL_PERIODS=[{key:'大学',...},{key:'高中',...},{key:'初中',...},{key:'小学',...}];

// 等级配置
const LEVELS=[{name:'学徒',min:0},...{name:'传说',min:5000}];

// 固定条目
const TICKER_FIXED_ITEM='自定义文字';
const TICKER_FIXED_URL='自定义链接';
```

### 添加新功能模块

1. **新增 Tab 页面**：
   - 在 `.tab-bar` 中添加新的 `.tab-item`
   - 在 `.views` 中添加新的 `.view` 容器
   - 在 `switchView()` 函数中添加对应的切换逻辑

2. **新增数据类型**：
   - 定义新的 `STORAGE_KEY` 常量
   - 实现 `load*/save*` 函数
   - 在 `BACKUP_KEYS` 数组中注册新键

3. **修改统计图表**：
   - `renderStats()` 函数包含所有图表渲染逻辑
   - 图表使用纯 HTML/CSS 实现，无第三方图表库
