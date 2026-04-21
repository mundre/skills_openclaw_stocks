# Quality Gates

> AI-Company Agent Factory 质量验证关卡

## 四层质量门禁体系

### Tool Layer (L0)

| 门禁 | 检查项 | 阈值 | 阻断 | 工具 |
|------|--------|------|------|------|
| G0-1 | 无状态验证 | 100%幂等 | ✅ | 单元测试 |
| G0-2 | 接口合规性 | 0缺失字段 | ✅ | JSON Schema |
| G0-3 | 测试覆盖率 | ≥90% | ✅ | pytest + coverage |
| G0-4 | 安全扫描 | Critical/High=0 | ✅ | bandit + safety |
| G0-5 | 性能基准 | P95≤500ms | ❌ | 基准测试 |

---

### Execution Layer (L1)

| 门禁 | 检查项 | 阈值 | 阻断 | 工具 |
|------|--------|------|------|------|
| G1-1 | 单一职责验证 | 职责域数=1 | ✅ | 代码审查 |
| G1-2 | 幂等性验证 | 一致性100% | ✅ | 重复执行测试 |
| G1-3 | 集成测试 | 通过率≥95% | ✅ | 集成测试套件 |
| G1-4 | 幻觉率检测 | ≤3% | ✅ | 黄金测试集 |
| G1-5 | 并发安全 | 0异常 | ✅ | 并发测试 |
| G1-6 | KPI达标 | 全部达标 | ❌ | KPI监控 |

---

### Management Layer (L2)

| 门禁 | 检查项 | 阈值 | 阻断 | 工具 |
|------|--------|------|------|------|
| G2-1 | 状态机完整性 | 100%状态覆盖 | ✅ | 状态机验证 |
| G2-2 | 错误恢复路径 | 每种失败有策略 | ✅ | 故障注入测试 |
| G2-3 | 并发控制 | 无竞态条件 | ✅ | 并发测试 |
| G2-4 | 审计日志 | 100%操作记录 | ✅ | 日志审查 |
| G2-5 | 资源隔离 | Worker间无泄漏 | ✅ | 资源监控 |

---

### Decision Layer (L3)

| 门禁 | 检查项 | 阈值 | 阻断 | 工具 |
|------|--------|------|------|------|
| G3-1 | 数据驱动 | 100%决策有数据 | ✅ | 决策审查 |
| G3-2 | 权威引用 | 引用标准可追溯 | ✅ | 引用检查 |
| G3-3 | 闭环反馈 | 决策后追踪执行 | ✅ | 追踪系统 |
| G3-4 | 审计完整 | 100%决策记录 | ✅ | 审计日志 |
| G3-5 | 人工接管 | 通道可用性100% | ✅ | 可用性测试 |

---

## 自动化验证

### 运行所有门禁

```bash
python scripts/validate_agent.py --agent-dir ./agents/my-agent/
```

### 单独运行某层门禁

```bash
# Tool层
python scripts/validate_agent.py --layer tool --agent-dir ./agents/my-skill/

# Execution层
python scripts/validate_agent.py --layer execution --agent-dir ./agents/my-worker/
```

---

## 门禁报告格式

```json
{
  "agent_name": "content-writer-agent",
  "layer": "execution",
  "timestamp": "2026-04-16T18:48:00Z",
  "gates": [
    {
      "gate_id": "G1-1",
      "name": "单一职责验证",
      "status": "PASS",
      "details": "职责域数=1"
    },
    {
      "gate_id": "G1-2",
      "name": "幂等性验证",
      "status": "PASS",
      "details": "3次执行输出一致性100%"
    },
    {
      "gate_id": "G1-3",
      "name": "集成测试",
      "status": "PASS",
      "details": "通过率97%"
    },
    {
      "gate_id": "G1-4",
      "name": "幻觉率检测",
      "status": "FAIL",
      "details": "幻觉率5.2%，超过阈值3%"
    }
  ],
  "summary": {
    "total": 6,
    "passed": 5,
    "failed": 1,
    "blocking": 1
  }
}
```

---

## 处理失败门禁

### 流程

1. **识别失败门禁** — 查看报告中的FAIL项
2. **分析根因** — 查看details了解具体问题
3. **修复问题** — 修改代码或配置
4. **重新验证** — 再次运行门禁
5. **全部通过** — 进入发布流程

### 常见失败及修复

| 门禁 | 常见失败 | 修复方法 |
|------|----------|----------|
| G0-3 | 测试覆盖率<90% | 补充单元测试 |
| G0-4 | 安全漏洞 | 升级依赖，修复代码 |
| G1-2 | 幂等性失败 | 移除状态依赖 |
| G1-4 | 幻觉率高 | 增强Prompt约束 |
| G2-1 | 状态机不完整 | 补充状态转移 |
| G3-1 | 无数据支撑 | 补充数据引用 |

---

## 参考

- [ISO 25010 Software Quality](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
