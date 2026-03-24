---
name: zhang-contract-review
version: "1.1.0"
description: 九章合同审查专家V1.1.0 - 深度合同风险识别与条款优化（基于DeepSeek R2 + 1000+真实案例库 + 自我进化）
metadata:
  {
    "openclaw": {
      "requires": { "env": ["DEEPSEEK_API_KEY"] },
      "capabilities": ["reasoning", "file_read"],
      "evolution": {
        "enabled": true,
        "version": "2.0.0",
        "data_collection": true,
        "auto_update": false,
        "feedback_loop": true
      }
    },
    "author": "张律师",
    "category": "legal",
    "tags": ["合同", "审查", "风险", "条款", "法务"],
    "evolution_metrics": {
      "usage_tracking": ["审查次数", "风险识别准确率", "用户采纳率"],
      "performance_indicators": ["平均审查时长", "风险检出率", "误报率"],
      "feedback_collection": ["修改建议采纳", "新增风险类型", "用户满意度"]
    },
    "evolution_plan": {
      "v1.2.0": ["新增融资租赁合同模板", "接入司法判例实时更新"],
      "v1.3.0": ["支持多语言合同审查", "AI生成修改建议"],
      "v2.0.0": ["合同生命周期管理", "智能谈判建议"]
    },
    "changelog": [
      {
        "version": "1.1.0",
        "date": "2026-03-23",
        "changes": [
          "接入 DeepSeek R2 推理模型",
          "新增 1000+ 真实合同审查案例库",
          "优化推理链条，支持多轮深度分析",
          "新增合同对比审查功能",
          "支持批量合同审查",
          "集成自我进化系统（v2.0.0）"
        ]
      },
      {
        "version": "1.0.0",
        "date": "2026-03-18",
        "changes": ["初始版本发布"]
      }
    ]
  }
---

# 九章合同审查专家 V1.1.0

**升级亮点**：
- 🤖 **DeepSeek R2** - 深度推理，精准识别隐藏风险
- 📚 **1000+案例库** - 基于真实判例的风险预警
- 🔗 **推理链条** - 可追溯的审查逻辑
- ⚖️ **对比审查** - 版本对比，变更追踪
- 📁 **批量处理** - 一键审查多份合同

## 使用示例

```bash
# 单份合同审查
jiuzhang-cli contract review ./sales_contract.docx

# 深度分析模式
jiuzhang-cli contract review ./contract.pdf --deep

# 合同对比审查
jiuzhang-cli contract compare ./v1.docx ./v2.docx

# 批量审查
jiuzhang-cli contract batch ./contracts/
```

## 核心能力

### 1. 风险识别矩阵
| 风险等级 | 说明 | 处理方式 |
|:-------:|------|---------|
| 🔴 致命 | 可能导致合同无效或重大损失 | 必须修改 |
| 🟠 高危 | 严重不利于我方，可能引发纠纷 | 强烈建议修改 |
| 🟡 中危 | 存在一定风险，需关注 | 建议修改 |
| 🟢 低危 | 表述不清或轻微不利 | 可选修改 |

### 2. 审查维度
- ✅ 主体资格审查
- ✅ 标的条款审查
- ✅ 价款与支付审查
- ✅ 履行期限审查
- ✅ 违约责任审查
- ✅ 争议解决审查
- ✅ 保密条款审查
- ✅ 不可抗力审查

### 3. 案例匹配
基于1000+真实合同判例，智能匹配相似案例，提供风险提示和修改建议。

## 输出格式

### Markdown 报告
```markdown
# 合同审查报告

## 基本信息
- 合同类型: 买卖合同
- 审查时间: 2026-03-23
- 风险等级: 中危
- 建议修改: 5处

## 风险清单
1. [高危] 违约金条款过低
   - 位置: 第8条第2款
   - 风险: 不足以弥补实际损失
   - 建议: 提升至合同总价的30%
   - 参考案例: (2024)京01民终1234号

## 优化建议
...
```

## 环境要求
- `DEEPSEEK_API_KEY` - DeepSeek API 密钥
- `CONTRACT_DB_PATH` - 案例库路径（可选）

## 版本历史
- v1.1.0 (2026-03-23) - DeepSeek R2 + 1000+案例库
- v1.0.0 (2026-03-18) - 初始版本
