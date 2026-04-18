# yaf-php-audit

用于 **PHP / Yaf 老项目代码审计** 的 OpenClaw skill，重点适配 **PHP 7.3 + Yaf** 风格项目。

它适合这几类场景：

- 对单个 PHP/Yaf 项目做首轮代码审计
- 对一批结构相似的老项目做批量初筛
- 在支付、回调、任务、Redis、SQL、权限等高风险区域快速定位热点
- 为人工深度审计提供统一的清单、脚本和报告输出

---

## 目录结构

```text
yaf-php-audit/
├── SKILL.md
├── README.md
├── references/
│   └── checklist.md
└── scripts/
    ├── scan_project.sh
    └── scan_workspace.sh
```

---

## 功能说明

### 1. 单项目审计

脚本：`scripts/scan_project.sh`

能力：

- 检查项目结构是否符合常见 Yaf 风格
- 扫描入口文件
- 扫描危险函数
- 扫描原始输入使用
- 扫描 SQL 拼接嫌疑
- 扫描回调 / 支付 / 任务关键词
- 扫描 PHP 7.4+ / 8.x 语法嫌疑
- 输出文本报告

### 2. 批量项目审计

脚本：`scripts/scan_workspace.sh`

能力：

- 扫描工作区下所有一级项目目录
- 为每个项目生成一份文本报告
- 生成 `summary.csv` 汇总表
- 生成 `summary.md` 人读版汇总
- 生成 `high-risk.txt` 高风险项目清单

### 3. 审计标准

参考文件：`references/checklist.md`

用于统一：

- 结构检查维度
- 安全检查维度
- 性能检查维度
- 可靠性检查维度
- 风险分级标准
- 报告模板

---

## 部署方式

### 方式一：目录方式部署

将整个目录放到 OpenClaw workspace skills 目录中：

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r yaf-php-audit ~/.openclaw/workspace/skills/
```

目录最终应类似：

```text
~/.openclaw/workspace/skills/yaf-php-audit/
```

### 方式二：打包后分发

如果你已经拿到了 `.skill` 包，可以按你的 OpenClaw 安装方式导入或分发。

当前包名示例：

```text
yaf-php-audit.skill
```

### 方式三：发布到 ClawHub

如果你要共享给其他 OpenClaw 用户，推荐发布到 ClawHub。

先登录：

```bash
clawhub login
clawhub whoami
```

再发布：

```bash
clawhub publish /path/to/yaf-php-audit \
  --slug yaf-php-audit \
  --name "Yaf PHP Audit" \
  --version 1.1.0 \
  --changelog "Initial public release: single-project audit reports, batch workspace scan, summary outputs, high-risk list, checklist, and README."
```

---

## 使用方式

### 单项目扫描

会输出一份“项目审计报告”格式的文本。

直接输出到终端：

```bash
bash scripts/scan_project.sh /path/to/project
```

输出到文本文件：

```bash
bash scripts/scan_project.sh /path/to/project /path/to/output/project-report.txt
```

示例：

```bash
bash scripts/scan_project.sh /mnt/d/Users/Public/php20250819/2026www/51dm /mnt/d/Users/Public/php20250819/2026www/audit-output/51dm.txt
```

### 批量扫描整个工作区

```bash
bash scripts/scan_workspace.sh /path/to/workspace /path/to/audit-output
```

示例：

```bash
bash scripts/scan_workspace.sh /mnt/d/Users/Public/php20250819/2026www /mnt/d/Users/Public/php20250819/2026www/audit-output
```

---

## 输出结果说明

批量扫描默认输出目录类似：

```text
audit-output/
├── summary.csv
├── summary.md
├── high-risk.txt
└── projects/
    ├── 51dm.txt
    ├── project-a.txt
    └── project-b.txt
```

### `projects/*.txt`

每个项目一份首轮扫描文本报告，包含：

- 项目名 / 路径 / 生成时间
- 目录结构检查
- 入口文件列表
- 危险函数命中
- 原始输入命中
- SQL 拼接嫌疑
- Redis 高耗时命令
- 外部调用线索
- 回调 / 支付 / 任务关键词
- PHP 新语法嫌疑

### `summary.csv`

适合排序、筛选和导入表格工具。

字段：

- `project`
- `risk_level`
- `dangerous_hits`
- `raw_input_hits`
- `callback_hits`
- `payment_hits`
- `task_hits`
- `php_new_syntax_hits`
- `notes`

### `summary.md`

适合人工快速浏览。

### `high-risk.txt`

列出被粗分级为 `high` 的项目，方便优先人工复核。

---

## 风险等级说明

这是一个 **首轮粗筛分级**，不是最终审计结论。

- `high`：高复杂度 / 高敏感业务 / 多个高风险特征叠加
- `medium`：存在明显风险面，建议人工复核
- `low`：首轮命中较少，但不代表绝对安全

建议流程：

1. 先看 `summary.csv` 或 `summary.md`
2. 优先处理 `high-risk.txt`
3. 再对高风险项目做人工深审

---

## 适用范围

更适合：

- PHP 7.3 老项目
- Yaf 风格项目
- 传统 PHP 项目首轮静态审计
- 多项目复制型业务代码
- 以支付、回调、任务、内容分发为核心的业务系统

不适合直接替代：

- 渗透测试
- 真正的静态分析器
- 完整的数据流安全分析
- 最终人工审计结论

---

## 注意事项

- 本 skill 的脚本输出是 **首轮扫描结果**，不是最终漏洞结论。
- 命中项需要结合代码上下文人工确认。
- 对支付、回调、登录态、任务系统命中较多的项目，应优先深审。
- 批量项目场景下，不建议一开始就为所有项目写长篇报告，应先做风险排序。

---

## 推荐使用流程

### 单项目

1. 跑 `scan_project.sh`
2. 看文本报告
3. 根据命中点人工深读关键文件
4. 输出正式审计结论

### 多项目

1. 跑 `scan_workspace.sh`
2. 看 `summary.csv`
3. 按高风险项目排序
4. 对前几名项目人工深审
5. 最后再输出正式汇总报告

---

## 二次开发建议

后续可继续增强：

- 输出 Markdown 格式项目报告
- 自动提取支付/回调相关文件清单
- 增加回调验签专项扫描
- 增加事务/幂等关键词专项扫描
- 增加 SQL/Redis 热点统计
- 增加针对特定项目框架的规则集
