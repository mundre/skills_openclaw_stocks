# Security Compliance

> AI-Company Agent Factory 安全合规规范

## VirusTotal 合规

### 禁止模式 (Forbidden Patterns)

以下模式在Skill中**禁止出现**：

| 模式 | 风险 | 检测方法 |
|------|------|----------|
| `eval(` | 代码注入 | 正则匹配 |
| `exec(` | 任意代码执行 | 正则匹配 |
| `__import__('os').system` | 系统命令执行 | AST分析 |
| `subprocess.call` | 子进程执行 | 正则匹配 |
| Hardcoded API keys | 凭证泄露 | 熵值检测 |
| `requests.post` to unknown hosts | 数据外泄 | URL白名单 |
| `pickle.loads` | 反序列化漏洞 | 正则匹配 |
| `yaml.load` without SafeLoader | YAML注入 | 正则匹配 |

### 允许模式 (Allowed Patterns)

以下模式**允许使用**：

| 模式 | 用途 | 约束 |
|------|------|------|
| 标准库调用 | 文件读写、数据处理 | 在permissions中声明 |
| 已声明的依赖 | 功能实现 | 在dependencies中列出 |
| `subprocess.run` with whitelist | 必要的系统调用 | 命令白名单 |
| `requests.get` to known hosts | API调用 | URL白名单 |
| `json.loads` | JSON解析 | 输入验证后使用 |
| `yaml.safe_load` | YAML解析 | 必须使用safe_load |

### 自动检测规则

```python
# 伪代码 - VirusTotal检测逻辑
FORBIDDEN_PATTERNS = [
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__.*system',
    r'subprocess\.(call|run|Popen)',
    r'[A-Za-z0-9]{32,}',  # 潜在API key
    r'pickle\.loads',
    r'yaml\.load\s*\(',
]

ALLOWED_PATTERNS = [
    r'json\.loads',
    r'yaml\.safe_load',
    r'subprocess\.run\s*\(\s*\[\s*["\']whitelisted_cmd',
]

def scan_skill(skill_path):
    content = read_file(skill_path)
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, content):
            flag_suspicious(pattern, skill_path)
    
    return scan_report
```

---

## ClawHub 代码审查

### SKILL.md 结构合规 (8项)

| 检查项 | 要求 | 验证方法 |
|--------|------|----------|
| Frontmatter完整 | name, slug, version, description必填 | YAML解析 |
| When to Use存在 | 至少3个触发场景 | 文本匹配 |
| Core Rules存在 | 3-7条规则 | 文本匹配 |
| 行数限制 | ≤80行 | wc -l |
| 描述长度 | ≤200字符 | len() |
| 版本格式 | semver (X.Y.Z) | 正则匹配 |
| Slug格式 | kebab-case | 正则匹配 |
| Metadata声明 | standardized: true | YAML解析 |

### 权限声明完整性 (6项)

| 检查项 | 要求 | 验证方法 |
|--------|------|----------|
| file_read声明 | 如读取文件 | permissions检查 |
| file_write声明 | 如写入文件 | permissions检查 |
| network声明 | 如网络调用 | permissions检查 |
| execute_scripts声明 | 如执行脚本 | permissions检查 |
| 权限最小化 | 仅声明必要权限 | 人工审查 |
| 权限与功能匹配 | 声明权限与实际使用一致 | 代码审查 |

### 依赖安全检查 (7项)

| 检查项 | 要求 | 验证方法 |
|--------|------|----------|
| 依赖锁定 | package-lock.json / requirements.txt | 文件存在性 |
| 无已知CVE | 依赖无Critical/High漏洞 | safety扫描 |
| 版本固定 | 精确版本号，无通配符 | 正则匹配 |
| 许可证合规 | 依赖许可证兼容 | license扫描 |
| 依赖数量合理 | 不过度依赖 | 数量阈值 |
| 依赖来源可信 | PyPI/npm官方源 | 源验证 |
| 废弃依赖检查 | 无已废弃依赖 | 版本检查 |

---

## 四层安全门禁

### Tool Layer

| 门禁 | 要求 | 验证 |
|------|------|------|
| 最小权限 | 仅请求必要权限 | 权限审查 |
| 无副作用 | 不修改外部状态 | 代码审查 |
| 输入验证 | 严格校验所有参数 | 测试覆盖 |
| 输出脱敏 | 不包含敏感信息 | 输出审查 |
| 无硬编码密钥 | 从环境变量读取 | 密钥扫描 |
| 安全依赖 | 无已知CVE | 依赖扫描 |

### Execution Layer

| 门禁 | 要求 | 验证 |
|------|------|------|
| 输入验证 | 严格校验任务参数 | Schema验证 |
| 输出脱敏 | 不包含PII/敏感数据 | 输出审查 |
| 工具调用限制 | 仅使用授权Skills | 调用链分析 |
| 错误信息泛化 | 不暴露内部细节 | 错误消息审查 |
| 资源限制 | 内存/CPU/超时限制 | 资源监控 |
| 审计日志 | 关键操作记录 | 日志审查 |

### Management Layer

| 门禁 | 要求 | 验证 |
|------|------|------|
| 状态隔离 | Worker状态不互相影响 | 隔离测试 |
| 权限边界 | Orchestrator不越权 | 权限审查 |
| 审计追踪 | 所有操作记录 | 日志审查 |
| 故障隔离 | Worker故障不扩散 | 故障注入 |
| 并发安全 | 无竞态条件 | 并发测试 |
| 资源公平 | 无饥饿/死锁 | 资源监控 |
| 回滚能力 | 可回滚到上一致状态 | 回滚测试 |

### Decision Layer

| 门禁 | 要求 | 验证 |
|------|------|------|
| 审计日志 | 100%决策记录 | 日志审查 |
| 人工接管 | 紧急情况下可人工介入 | 接管测试 |
| 数据溯源 | 决策数据来源可追溯 | 数据血缘 |
| 合规审查 | 符合监管要求 | 合规检查 |
| 偏见检测 | 决策公平性 | 偏见测试 |
| 可解释性 | 决策依据可解释 | 解释性审查 |
| 授权验证 | 决策权限验证 | 权限审查 |
| 冲突解决 | 冲突指令仲裁机制 | 冲突测试 |

---

## 审查流程

### 三态结果

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| **PASS** | 全部检查通过 | 进入发布流程 |
| **FAIL** | 有阻断性失败 | 修复后重新审查 |
| **CONDITIONAL PASS** | 有条件通过 | 满足附加约束后通过 |

### 审查类型

#### 自动审查 (11项)

- Schema验证
- Lint检查
- 单元测试
- 安全扫描
- 依赖扫描
- 性能基准
- 覆盖率检查
- 代码复杂度
- 重复代码检测
- 文档完整性
- 许可证检查

#### 人工审查 (9项)

- 架构合理性
- 设计模式适用性
- 安全边界清晰性
- 权限最小化
- 错误处理完整性
- 可维护性评估
- 可扩展性评估
- 业务逻辑正确性
- 用户体验

#### 条件通过 (8项)

- 测试覆盖率略低但核心路径覆盖
- 有低风险依赖CVE但有修复计划
- 新功能缺少文档但有文档计划
- 性能略低于基准但有优化计划
- 代码复杂度略高但有重构计划
- 使用实验性功能但有回滚方案
- 缺少部分测试但有测试计划
- 文档不完整但有完善计划

---

## 合规声明

本Skill遵循以下安全标准：

- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

---

## 参考

- [VirusTotal API](https://developers.virustotal.com/)
- [ClawHub Security Guidelines](https://clawhub.ai/security)
- [SLSA Framework](https://slsa.dev/)
