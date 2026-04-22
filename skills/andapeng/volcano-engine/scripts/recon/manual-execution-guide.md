# 火山引擎文档安全侦察 - 手动执行指南

## 🎯 概述
由于OpenClaw安全策略限制，无法自动执行Node.js脚本。请按照以下步骤手动执行侦察脚本。

## 📋 前提条件
- Node.js已安装 (v14+)
- Playwright已安装 (`npm install playwright`)
- 命令行工具 (PowerShell或CMD)

## 🔧 验证环境
打开命令行，运行以下命令验证环境：

```bash
node --version
# 应该显示: v24.14.0 或更高

npx playwright --version
# 应该显示: 1.59.1 或更高
```

## 🚀 执行步骤

### 步骤1: 打开命令行
1. 按 `Win + R`，输入 `cmd` 或 `powershell`
2. 或者使用Windows Terminal

### 步骤2: 进入脚本目录
```bash
cd "C:\Users\Andapeng\.openclaw\workspace\skills\volcengine\scripts\recon"
```

### 步骤3: 执行侦察脚本
```bash
node safe-playwright-recon.js
```

### 步骤4: 等待执行完成
脚本将：
- 启动Headless浏览器
- 检查3个关键URL（8-15秒随机延迟）
- 生成结果文件
- 自动关闭浏览器

**预计时间:** 约30-45秒

## 📊 预期输出

### 控制台输出示例
```
=== 火山引擎文档安全侦察开始 ===
严格遵守速率限制: 8000-15000ms 延迟
检查 3 个URL
输出目录: ./safe-results

检查: 目标文档-文本生成
URL: https://www.volcengine.com/docs/82379/1399009?lang=zh
随机延迟 11234ms...
状态码: 200
标题: 文本生成--火山方舟-火山引擎
内容长度: 45210 字符
是否有内容: true
是否有文档元素: true
文本样本: 已提取
...
```

### 生成的文件
```
safe-results/
├── recon.log              # 完整操作日志
├── results.json           # JSON格式侦察结果
├── report.md              # Markdown格式报告
└── results-interim.json   # 中间结果（防中断）
```

## ⚠️ 安全注意事项

### 脚本已实现的安全措施
1. **严格遵守robots.txt** - 避开所有禁止目录
2. **极低请求频率** - 8-15秒随机延迟
3. **最小化目标** - 只检查3个关键URL
4. **反封锁检测** - 遇到403/429立即停止
5. **浏览器仿真** - 完整Chrome UA + 中文环境
6. **内容保护** - 只提取文本样本，不保存完整内容

### 遇到封锁的处理
如果脚本检测到疑似封锁（403/429状态码），会：
1. 立即停止执行
2. 记录错误信息
3. 保存已获取的结果
4. 建议暂停自动化尝试

## 🔍 结果解读

### 成功情况（至少1个URL可访问）
- 检查 `safe-results/results.json`
- 查看 `safe-results/report.md` 获取总结
- 分析页面结构和内容样本

### 失败情况（所有URL不可访问）
- 检查错误代码和原因
- 查看安全日志 `safe-results/recon.log`
- 可能需要调整访问策略或人工验证

## 🛠️ 故障排除

### 常见问题

#### 1. Node.js找不到
```bash
# 如果node命令不可用，尝试完整路径
"C:\Program Files\nodejs\node.exe" safe-playwright-recon.js
# 或
"C:\Users\Andapeng\AppData\Roaming\npm\node.exe" safe-playwright-recon.js
```

#### 2. Playwright未安装
```bash
# 安装Playwright
npm install playwright
# 安装Chromium浏览器
npx playwright install chromium
```

#### 3. 脚本执行错误
- 确保在正确的目录执行
- 检查文件是否存在: `dir safe-playwright-recon.js`
- 查看Node.js错误信息

#### 4. 网络问题
- 确保可以访问 `https://www.volcengine.com`
- 检查防火墙或代理设置
- 尝试手动访问目标URL

### 错误代码参考
- **200**: 成功
- **404**: 页面不存在
- **403**: 禁止访问（可能触发反爬）
- **429**: 请求过多（速率限制）
- **0**: 网络错误或连接失败

## 📞 执行后步骤

### 1. 报告结果
执行完成后，请告知我：
- 是否成功执行
- 发现了哪些URL可访问
- 遇到的任何问题

### 2. 进一步分析
根据结果，我可以：
- 分析页面结构
- 制定内容提取方案
- 调整volcengine技能文档
- 规划下一阶段工作

### 3. 安全记录
- 保持 `safe-results/` 目录备份
- 记录执行时间和结果
- 如有封锁迹象，暂停后续尝试

## 🎛️ 高级选项

### 自定义配置
如果需要调整，可以修改脚本中的配置：

```javascript
// 在 safe-playwright-recon.js 中调整
const config = {
    urls: [ /* 目标URL */ ],
    safety: {
        minDelayMs: 8000,    // 最小延迟
        maxDelayMs: 15000,   // 最大延迟
        // ...
    }
};
```

### 扩展检查
如需检查更多URL，可以在`urls`数组中添加：

```javascript
urls: [
    // 现有URL...
    {
        url: 'https://www.volcengine.com/docs/82379/models?lang=zh',
        name: '模型文档',
        priority: 'medium'
    }
]
```

## ✅ 完成确认

执行完成后，请检查：
- [ ] `safe-results/results.json` 文件已生成
- [ ] `safe-results/report.md` 报告已生成
- [ ] 控制台显示"侦察完成"消息
- [ ] 没有出现错误或警告信息

## ⏱️ 时间安排建议

- **立即执行**: 如果现在有空闲时间
- **稍后执行**: 可以在后台运行，不影响其他工作
- **分批执行**: 如有需要，可以分多次执行不同URL

---

**重要提示**: 如果遇到任何问题或不确定的地方，请随时询问。安全第一，宁可暂停也不要冒险触发封锁。

**执行后请回复我结果，我会继续后续分析工作。**