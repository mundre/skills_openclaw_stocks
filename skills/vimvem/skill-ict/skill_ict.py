"""
Skill Auditor v3.0.0 - Claw Skill 质量检验工具
借鉴竞品 yoder-skill-auditor v3.1.0 和 skill-auditor-pro的优秀设计
支持: Python, Shell (bash/sh), JavaScript/TypeScript
"""
import os
import re
import ast
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

# ============ 版本信息 ============
VERSION = "3.0.0"  # skill-ict v3.0.0

# ============ 安全检测模式 (20+项) ============

# Check 1: 凭证关键词 (Python + Shell + JS)
CRED_PATTERNS = {
    'py': [
        r'os\.environ|getenv',
        r'api[_-]?key|secret[_-]?key|password|credential',
        r'private[_-]?key|mnemonic|seed[_-]?phrase',
    ],
    'sh': [
        r'\$API_KEY|\$SECRET|\$TOKEN|\$PASSWORD',
        r'\${[A-Z_]+}',
        r'\.env|\.aws|\.ssh',
    ],
    'js': [
        r'process\.env',
        r'apiKey|api_key|secretKey',
        r'\.env',
    ]
}

# Check 2: 代码执行
EXEC_PATTERNS = {
    'py': [
        r'eval\s*\(|exec\s*\(',
        r'subprocess\.call.*shell\s*=\s*True',
        r'os\.system|os\.popen',
        r'__import__\s*\(',
    ],
    'sh': [
        r'eval\s+',
        r'exec\s+',
        r'`[^`]+`',
        r'\$\([^)]+\)',
        r'bash\s+-c',
    ],
    'js': [
        r'eval\s*\(',
        r'child_process|spawn\(|execSync',
        r'Function\s*\(',
        r'require\s*\(\s*[\'"]child_process',
    ]
}

# Check 3: 数据外泄 URL
EXFIL_PATTERNS = {
    'all': [
        r'webhook\.site|requestbin|ngrok\.io',
        r'pipedream\.net|hookbin|beeceptor',
        r'requestcatcher|postb\.in|httpbin\.org',
        r'myjson\.com|jsonblob\.io',
    ]
}

# Check 4: Base64 混淆
B64_PATTERNS = {
    'py': [r'atob\(|btoa\(|base64\.decode'],
    'sh': [r'base64\s+-d|base64\s+--decode'],
    'js': [r'atob\(|btoa\(|Buffer\.from.*base64'],
}

# Check 5: 敏感文件系统
FS_PATTERNS = {
    'py': [r'/etc/passwd|/etc/shadow', r'~/.ssh|~/.gnupg|~/.aws'],
    'sh': [r'/etc/passwd|/etc/shadow', r'~\/\.ssh|~\/\.gnupg'],
    'js': [r'\/etc\/passwd', r'\.ssh\/|\.gnupg\/'],
}

# Check 6: 加密钱包地址
CRYPTO_PATTERNS = {
    'all': [
        r'0x[a-fA-F0-9]{40}',
        r'bc1[a-zA-HJ-NP-Z0-9]{39,59}',
        r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',
    ]
}

# Check 7: 依赖混淆/拼写抢注
PKG_PATTERNS = {
    'all': [
        r'@internal|@private|@corp|@company',
        r'-internal-|-private-',
        r'requets|reqeusts|lodasg|loadsh|colosr|axois',  # 常见拼写错误
    ]
}

# Check 8: 安装钩子
HOOK_PATTERNS = {
    'all': [
        r'postinstall|preinstall|post_install|pre_install',
        r'setup\.py.*install',
    ]
}

# Check 9: Symlink 攻击
SYMLINK_PATTERNS = {
    'py': [r'os\.symlink|fs\.symlinkSync'],
    'sh': [r'ln\s+-s'],
    'js': [r'fs\.symlink|symlink\('],
}

# Check 10: 时间炸弹
TIMEBOMB_PATTERNS = {
    'py': [r'Date\.now|datetime\.now', r'setTimeout|setInterval'],
    'sh': [r'at\s+|crontab'],
    'js': [r'setTimeout|setInterval|Date\.now'],
}

# Check 11: 远程脚本执行
REMOTE_EXEC_PATTERNS = {
    'all': [
        r'curl\s+.*\|\s*bash|wget\s+.*\|\s*bash',
        r'curl\s+.*sh\b|wget\s+.*sh\b',
    ]
}

# Check 12: 遥测/追踪
TELEMETRY_PATTERNS = {
    'all': [
        r'google-analytics|gtag|ga\(',
        r'segment\.|mixpanel|amplitude|hotjar',
    ]
}

# Check 13: 不寻常端口
PORT_PATTERNS = {
    'all': [
        r':\d{4,5}[/"\']',  # 端口号
    ]
}

# Check 14: 提示词注入 (文档)
PROMPT_INJECTION = {
    'all': [
        r'ignore.*previous instructions',
        r'disregard.*previous|forget your rules',
        r'you are now |act as |pretend to be',
        r'override.*(safety|security|rules)',
    ]
}

# Check 15: 隐蔽数据外发
STEALTH_EXFIL = {
    'all': [
        r'send.*(data|files?|secrets?|tokens?) to',
        r'POST.*(data|files?|secrets?)',
    ]
}

# Check 16: C2 服务器
C2_PATTERNS = {
    'all': [
        r'91\.92\.242\.30',
    ]
}

# Check 17: 容器逃逸
CONTAINER_ESCAPE = {
    'all': [
        r'docker.*socket|\.docker\.sock',
        r'cgroup\.escape|\.namespace',
    ]
}

# Check 18: SSH 远程连接
SSH_PATTERNS = {
    'all': [
        r'ssh\s+-|scp\s+',
        r'paramiko|netmiko',
        r'fabric\.operations',
    ]
}

# 所有检测类别
SECURITY_CHECKS = [
    ("credential-harvest", "凭证收集", CRED_PATTERNS, "critical"),
    ("code-execution", "代码执行", EXEC_PATTERNS, "critical"),
    ("exfiltration-url", "数据外泄URL", EXFIL_PATTERNS, "critical"),
    ("base64-obfuscation", "Base64混淆", B64_PATTERNS, "medium"),
    ("sensitive-fs", "敏感文件系统", FS_PATTERNS, "critical"),
    ("crypto-wallet", "加密钱包地址", CRYPTO_PATTERNS, "critical"),
    ("dependency-confusion", "依赖混淆", PKG_PATTERNS, "high"),
    ("install-hook", "安装钩子", HOOK_PATTERNS, "medium"),
    ("symlink-attack", "Symlink攻击", SYMLINK_PATTERNS, "critical"),
    ("time-bomb", "时间炸弹", TIMEBOMB_PATTERNS, "medium"),
    ("remote-exec", "远程脚本执行", REMOTE_EXEC_PATTERNS, "critical"),
    ("telemetry", "遥测追踪", TELEMETRY_PATTERNS, "medium"),
    ("prompt-injection", "提示词注入", PROMPT_INJECTION, "critical"),
    ("stealth-exfil", "隐蔽数据外发", STEALTH_EXFIL, "critical"),
    ("c2-server", "C2服务器", C2_PATTERNS, "critical"),
    ("container-escape", "容器逃逸", CONTAINER_ESCAPE, "critical"),
    ("ssh-remote", "SSH远程连接", SSH_PATTERNS, "medium"),
]

# 文档必要章节
REQUIRED_SKILL_SECTIONS = ['描述', '使用方法', '功能']


# ============ 工具函数 ============
def is_comment_line(line: str, ext: str) -> bool:
    """检查是否是注释行"""
    stripped = line.strip()
    if ext == 'py':
        return stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''")
    elif ext in ('sh', 'bash'):
        return stripped.startswith('#')
    elif ext in ('js', 'ts'):
        return stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*')
    return False

def is_pattern_def_line(line: str, ext: str) -> bool:
    """检查是否是检测规则定义行（防误报）"""
    stripped = line.strip()
    
    # Python: 匹配变量赋值
    if ext == 'py':
        if re.search(r'[A-Z_][A-Z_]*=\s*(\[|r[\'"])', line):
            return True
        if re.search(r'^\s*\(["\']', line) and re.search(r'["\'].*["\'].*\[', line):
            return True
        if re.search(r'^\s+(\(["\']|\[)', line) and 'PATTERNS' in line:
            return True
        if re.search(r'^\s*["\'][\w-]+["\']:\s*\[', line):
            return True
        if re.search(r'result\s*=\s*\{', line):
            return True
        if re.match(r'\s*r[\'"]', line):
            return True
    
    # Shell: 排除变量定义和 echo 语句
    if ext == 'sh':
        # 排除变量赋值: VAR='...' 或 VAR="..."
        if re.match(r'^[A-Z_][A-Z_]*=', stripped):
            return True
        # 排除 echo 语句
        if stripped.startswith('echo '):
            return True
        # 排除 if/fi, for/done, while/done 等结构
        if stripped.startswith(('if ', 'then', 'else', 'fi', 'for ', 'done', 'while ', 'case ', 'esac')):
            return True
        # 排除函数定义
        if re.match(r'^[_a-zA-Z][_a-zA-Z0-9*\(\)\s]+\(\)', stripped):
            return True
        # 排除日志级别
        if re.search(r'log_(critical|warning|info|pass)', line):
            return True
        # 排除 CRED_PATTERNS= 这种检测规则定义
        if re.match(r'^[A-Z_]+_PATTERNS=', stripped):
            return True
        # 排除 local VAR= 定义
        if re.match(r'^local\s+[A-Z_][A-Z_]*=', stripped):
            return True
    
    # JS: 排除 export/const/let 定义的常量
    if ext in ('js', 'ts'):
        if re.match(r'^(export\s+)?(const|let)\s+[A-Z_]', stripped):
            return True
        if stripped.startswith('//'):
            return True
    
    return False

def should_skip_line(line: str, ext: str) -> bool:
    """判断是否应该跳过此行"""
    return is_comment_line(line, ext) or is_pattern_def_line(line, ext)


# ============ 文件类型检测 ============
def get_file_language(file_path: str) -> str:
    """根据文件扩展名判断语言"""
    ext = os.path.splitext(file_path)[1].lower()
    mapping = {
        '.py': 'py',
        '.sh': 'sh',
        '.bash': 'sh',
        '.js': 'js',
        '.mjs': 'js',
        '.cjs': 'js',
        '.ts': 'ts',
        '.tsx': 'ts',
        '.jsx': 'ts',
    }
    return mapping.get(ext, 'unknown')


def get_all_files(folder_path: str) -> List[Tuple[str, str]]:
    """获取所有需要扫描的代码文件"""
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        # 排除测试和缓存目录
        if any(x in root for x in ['test_samples', 'tests', '__pycache__', '.git', 'node_modules']):
            continue
        for f in filenames:
            lang = get_file_language(f)
            if lang != 'unknown':
                files.append((os.path.join(root, f), lang))
    return files


# 审计工具自身的文件名（排除扫描）
AUDITOR_FILES = ['skill_ict.py', 'skill_auditor.py', 'audit.sh', 'inspect.sh', 'trust_score.py']


# ============ AST 解析 (Python) ============
class FunctionExtractor(ast.NodeVisitor):
    def __init__(self):
        self.functions: Set[str] = set()
        self.classes: Set[str] = set()
    
    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)


def extract_functions_ast(file_path: str) -> Set[str]:
    """使用 AST 提取函数名"""
    if not file_path.endswith('.py'):
        return set()
    functions = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        extractor = FunctionExtractor()
        extractor.visit(tree)
        functions = extractor.functions
    except:
        pass
    return functions


# ============ 安全检查 ============
def check_security_in_file(file_path: str, lang: str) -> List[Dict[str, Any]]:
    """检查单个文件的安全问题"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return issues
    
    # 获取文件名，用于过滤
    filename = os.path.basename(file_path)
    
    for check_name, desc, patterns, severity in SECURITY_CHECKS:
        # 获取当前语言的模式
        lang_patterns = patterns.get(lang, []) + patterns.get('all', [])
        if not lang_patterns:
            continue
        
        combined = '|'.join(lang_patterns)
        
        for i, line in enumerate(lines, 1):
            if should_skip_line(line, lang):
                continue
            
            # 额外过滤：Shell 脚本中的特殊模式
            if lang == 'sh':
                # 跳过 echo 颜色变量
                if re.search(r'echo.*\$\{[^}]+\}', line):
                    continue
                # 跳过 if/while 条件中的 $()
                if re.search(r'^\s*if\s+.*\$\(', line):
                    continue
                # 跳过赋值语句中的 $()
                if re.search(r'^[A-Z_][A-Z_]*=.*\$\(', line):
                    continue
                # 跳过数组索引 []
                if re.search(r'\$\{?[A-Z_]+\}?\[[^\]]+\]', line):
                    continue
                # 跳过算术表达式 $((...))
                if re.search(r'\$\(\([^\)]+\)\)', line):
                    continue
                # 跳过 grep/awk/sed/xargs 中的管道
                if re.search(r'\|\s*(grep|awk|sed|xargs|head|tail|wc)', line):
                    continue
                # 跳过 basename/dirname/date 等常见命令
                if re.search(r'\$\(basename|dirname|date|readlink', line):
                    continue
            
            # Python: 跳过 datetime.now() 这种时间戳用法和检测代码
            if lang == 'py' and 'datetime.now()' in line:
                # 跳过时间戳用法
                if 'timestamp' in line.lower() or 'isoformat' in line.lower():
                    continue
                # 跳过检测代码本身 (用于判断的 if 语句)
                if "in line" in line or "in content" in line:
                    continue
            
            # 跳过审计工具自身的代码 (包含 audit/inspect/trust-score 等)
            if any(x in filename.lower() for x in ['audit', 'inspect', 'trust-score', 'benchmark', 'test']):
                # 但如果是真正的恶意特征还是要报
                if check_name in ['code-execution', 'remote-exec', 'c2-server', 'container-escape']:
                    pass  # 这些还是要报
                else:
                    continue
            
            if re.search(combined, line, re.IGNORECASE):
                rel_path = os.path.basename(file_path)
                issues.append({
                    'line': i,
                    'type': 'security',
                    'severity': severity,
                    'file': rel_path,
                    'lang': lang,
                    'message': f'{desc}: {line.strip()[:50]}'
                })
    
    return issues


def check_combo_threats(folder_path: str) -> List[Dict[str, Any]]:
    """检查组合威胁：凭证收集 + 网络调用"""
    issues = []
    
    NET_PATTERNS = {
        'py': [r'urllib|requests\.|http\.|https\.', r'os\.system.*curl|wget'],
        'sh': [r'curl |wget |fetch ', r'http|https'],
        'js': [r'axios|fetch|request|got\('],
    }
    
    files = get_all_files(folder_path)
    
    cred_files = set()
    net_files = set()
    
    for fp, lang in files:
        # 排除审计工具自身
        if any(auditor in fp for auditor in AUDITOR_FILES):
            continue
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            
            cred_pat = '|'.join(CRED_PATTERNS.get(lang, []) + CRED_PATTERNS.get('all', []))
            net_pat = '|'.join(NET_PATTERNS.get(lang, []) + NET_PATTERNS.get('all', []))
            
            if cred_pat and re.search(cred_pat, content, re.IGNORECASE):
                cred_files.add(fp)
            if net_pat and re.search(net_pat, content, re.IGNORECASE):
                net_files.add(fp)
        except:
            pass
    
    dangerous = cred_files & net_files
    for f in dangerous:
        issues.append({
            'line': 0,
            'type': 'security',
            'severity': 'critical',
            'file': os.path.basename(f),
            'message': f'组合威胁: 既收集凭证又发起网络调用'
        })
    
    return issues


# ============ 文档检查 ============
def check_doc_security(folder_path: str) -> List[Dict[str, Any]]:
    """检查文档中的安全问题"""
    issues = []
    doc_patterns = PROMPT_INJECTION.get('all', []) + STEALTH_EXFIL.get('all', [])
    combined = '|'.join(doc_patterns)
    
    for root, dirs, files in os.walk(folder_path):
        if any(x in root for x in ['test', 'tests', '__pycache__']):
            continue
        for f in files:
            if f.endswith(('.md', '.txt')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    matches = re.finditer(combined, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            'line': line_num,
                            'type': 'security',
                            'severity': 'critical',
                            'file': os.path.basename(fp),
                            'message': f'文档中发现提示词注入模式'
                        })
                except:
                    pass
    
    return issues


def check_file_structure(folder_path: str) -> List[Dict[str, Any]]:
    """检查文件结构"""
    issues = []
    files = get_all_files(folder_path)
    
    if not files:
        issues.append({
            'line': 0, 'type': 'structure', 'severity': 'medium',
            'message': '未找到代码文件'
        })
    
    # 统计各语言文件
    lang_count = {}
    for fp, lang in files:
        lang_count[lang] = lang_count.get(lang, 0) + 1
    
    if lang_count:
        info = ', '.join(f'{k}: {v}' for k, v in lang_count.items())
        issues.append({
            'line': 0, 'type': 'structure', 'severity': 'info',
            'message': f'代码文件: {info}'
        })
    
    return issues


def check_doc_completeness(folder_path: str) -> List[Dict[str, Any]]:
    """检查文档完整性"""
    issues = []
    skill_path = os.path.join(folder_path, 'SKILL.md')
    
    if not os.path.exists(skill_path):
        issues.append({
            'line': 0, 'type': 'doc', 'severity': 'high',
            'message': '缺少 SKILL.md'
        })
    else:
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            for section in REQUIRED_SKILL_SECTIONS:
                if section not in content:
                    issues.append({
                        'line': 0, 'type': 'doc', 'severity': 'medium',
                        'message': f'SKILL.md 缺少: {section}'
                    })
            if '触发词' not in content and 'triggers' not in content.lower():
                issues.append({
                    'line': 0, 'type': 'doc', 'severity': 'low',
                    'message': '建议添加触发词'
                })
        except Exception as e:
            issues.append({
                'line': 0, 'type': 'error', 'severity': 'high',
                'message': f'文档检查失败: {e}'
            })
    
    return issues


def check_consistency(folder_path: str) -> List[Dict[str, Any]]:
    """检查代码文档一致性"""
    issues = []
    code_functions = set()
    files = get_all_files(folder_path)
    
    for fp, lang in files:
        if lang == 'py':
            code_functions.update(extract_functions_ast(fp))
    
    doc_functions = set()
    for doc in ['README.md', 'SKILL.md']:
        path = os.path.join(folder_path, doc)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                matches = re.findall(r'`(\w+)`|def\s+(\w+)\s*\(', content)
                for m in matches:
                    doc_functions.update([x for x in m if x])
            except:
                pass
    
    # 返回字段名（JSON 返回值的 key），不需要在代码中有对应函数
    return_fields = {
        'line', 'type', 'severity', 'message', 'overall_score', 'summary',
        'skill_path', 'version', 'checks_count', 'error', 'security_issues',
        'structure_issues', 'doc_issues', 'consistency_issues', 'allowlisted',
        'critical', 'high', 'medium', 'low', 'total_issues', 'languages',
        'file', 'lang',
    }
    
    for df in doc_functions:
        # 跳过返回字段名
        if df in return_fields or df.lower() in {x.lower() for x in return_fields}:
            continue
        # 跳过内部函数
        if df.lower() in {'audit_skill', 'main', 'print_report', 'load_allowlist',
                          'functionextractor', 'get_all_files', 'get_file_language'}:
            continue
        if df.lower() not in {cf.lower() for cf in code_functions}:
            issues.append({
                'line': 0, 'type': 'consistency', 'severity': 'low',
                'message': f'文档中的 "{df}" 在代码中未找到'
            })
    
    return issues


# ============ 主审计函数 ============
def audit_skill(skill_path: str, allowlist: List[str] = None) -> Dict[str, Any]:
    """审计 Skill 文件夹"""
    result = {
        'skill_path': skill_path,
        'version': VERSION,
        'security_issues': [],
        'structure_issues': [],
        'doc_issues': [],
        'consistency_issues': [],
        'overall_score': 100,
        'summary': {},
        'checks_count': len(SECURITY_CHECKS),
        'languages': set(),
    }
    
    if not os.path.isdir(skill_path):
        result['error'] = f'路径不存在: {skill_path}'
        result['overall_score'] = 0
        return result
    
    allowlist = allowlist or []
    skill_name = os.path.basename(skill_path)
    is_allowlisted = skill_name in allowlist
    
    # 1. 结构检查
    result['structure_issues'].extend(check_file_structure(skill_path))
    
    # 2. 获取所有文件
    files = get_all_files(skill_path)
    for fp, lang in files:
        result['languages'].add(lang)
    
    # 3. 安全检查 - 所有文件
    for fp, lang in files:
        result['security_issues'].extend(check_security_in_file(fp, lang))
    
    # 4. 文档安全检查
    result['security_issues'].extend(check_doc_security(skill_path))
    
    # 5. 组合威胁检测
    result['security_issues'].extend(check_combo_threats(skill_path))
    
    # 6. 文档检查
    result['doc_issues'].extend(check_doc_completeness(skill_path))
    
    # 7. 一致性检查
    result['consistency_issues'].extend(check_consistency(skill_path))
    
    # 应用白名单
    if is_allowlisted:
        for issue in result['security_issues']:
            if issue.get('severity') == 'critical':
                issue['severity'] = 'info'
                issue['message'] = f'[ALLOWLISTED] {issue["message"]}'
    
    # 计算总分
    severity_weights = {
        'critical': 15, 'high': 10, 'medium': 5, 'low': 2, 'info': 0
    }
    all_issues = (
        result['security_issues'] + 
        result['structure_issues'] + 
        result['doc_issues'] + 
        result['consistency_issues']
    )
    
    deduction = sum(severity_weights.get(i.get('severity', 'low'), 2) for i in all_issues)
    result['overall_score'] = max(0, 100 - deduction)
    
    # 摘要
    result['summary'] = {
        'total_issues': len(all_issues),
        'critical': sum(1 for i in all_issues if i.get('severity') == 'critical'),
        'high': sum(1 for i in all_issues if i.get('severity') == 'high'),
        'medium': sum(1 for i in all_issues if i.get('severity') == 'medium'),
        'low': sum(1 for i in all_issues if i.get('severity') == 'low'),
        'allowlisted': is_allowlisted,
        'languages': list(result['languages']),
    }
    del result['languages']  # 不需要暴露给用户
    
    return result


def print_report(result: Dict[str, Any]):
    """打印报告"""
    print(f"\n{'='*55}")
    print(f"📊 Skill Auditor v{VERSION}")
    print(f"{'='*55}")
    print(f"路径: {result['skill_path']}")
    print(f"检测项: {result['checks_count']} 项")
    langs = result.get('summary', {}).get('languages', [])
    if langs:
        print(f"支持语言: {', '.join(langs)}")
    print(f"总体评分: {result['overall_score']}/100")
    
    s = result.get('summary', {})
    print(f"\n问题统计:")
    print(f"  🔴 Critical: {s.get('critical', 0)}")
    print(f"  🔴 High: {s.get('high', 0)}")
    print(f"  🟡 Medium: {s.get('medium', 0)}")
    print(f"  🟢 Low: {s.get('low', 0)}")
    if s.get('allowlisted'):
        print(f"  ⚪ 已白名单")
    
    categories = [
        ('security_issues', '🔒 安全问题'),
        ('structure_issues', '📁 结构问题'),
        ('doc_issues', '📝 文档问题'),
        ('consistency_issues', '🔄 一致性'),
    ]
    
    for key, title in categories:
        issues = result.get(key, [])
        if issues:
            print(f"\n{title} ({len(issues)} 项):")
            for issue in issues[:6]:
                line = f"L{issue.get('line', 0)}: " if issue.get('line') else ""
                sev = issue.get('severity', 'info')
                icon = {'critical': '🔴', 'high': '🔴', 'medium': '🟡', 'low': '🟢', 'info': '⚪'}.get(sev, '⚪')
                lang = f"[{issue.get('lang', '')}] " if issue.get('lang') else ""
                print(f"  {icon} {lang}{line}{issue['message'][:55]}")
            if len(issues) > 6:
                print(f"  ... 还有 {len(issues) - 6} 项")
    
    print(f"\n{'='*55}")
    verdict = "✅ 优秀" if result['overall_score'] >= 90 else "⚠️ 需改进" if result['overall_score'] >= 70 else "❌ 风险高"
    print(f"判定: {verdict}")
    print(f"{'='*55}\n")


def load_allowlist(path: str) -> List[str]:
    """加载白名单"""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return [s.get('name', '') for s in data.get('skills', [])]
    except:
        return []


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description=f'Skill Auditor v{VERSION} - 多语言安全检测')
    parser.add_argument('folder', help='Skill 文件夹路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--allowlist', help='白名单文件')
    args = parser.parse_args()
    
    allowlist = load_allowlist(args.allowlist) if args.allowlist else []
    result = audit_skill(args.folder, allowlist)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)


if __name__ == '__main__':
    main()
