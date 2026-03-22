# skill-ict

- **描述**: 自动化检查 Claw Skill 质量的工具，支持代码风格、安全漏洞、文档完整性和代码文档一致性检查
- **触发词**: 质检, audit, 检查skill, skill质量, ICT
- **分类**: devtools
- **版本**: 3.0.1

> ⚠️ **安全说明**：本工具包含恶意代码模式检测规则，用于静态分析审计目标代码。检测规则本身包含 exec、eval、C2 等敏感关键字，这是正常的审计功能，不会执行任何恶意操作。

## 使用方法

### CLI
```bash
python skill_ict.py <skill_folder_path>
python skill_ict.py <skill_folder_path> --json
python skill_ict.py <skill_folder_path> --allowlist allowlist.json
```

### API
```python
from skill_ict import audit_skill
result = audit_skill("/path/to/skill-folder")
```

## 功能

### 安全检查 (17项)
- 凭证收集 + 网络调用（组合检测）
- 代码执行 (eval/exec/spawn)
- 数据外泄 URL
- Base64 混淆 payloads
- 敏感文件系统访问
- 加密钱包地址检测
- 依赖混淆/拼写抢注
- 安装钩子 (pre/post install)
- Symlink 攻击
- 时间炸弹 (延迟触发)
- 远程脚本执行 (curl|bash)
- 遥测/追踪代码
- 提示词注入检测
- 隐蔽数据外发指令
- C2 服务器检测
- 容器逃逸检测
- SSH 远程连接检测

### 支持语言
- Python (.py)
- Shell (.sh, .bash)
- JavaScript/TypeScript (.js, .ts)

### 质量检查
- SKILL.md 完整性
- 代码风格 (行长度、语法)
- 代码文档一致性
- 文件结构

### 防误报机制
- PATTERN_DEF_FILTER - 自动过滤检测规则定义
- 注释行过滤
- 白名单支持

## 限制
- 部分检测基于正则，可能存在误报
- LLM 分析需外部工具
