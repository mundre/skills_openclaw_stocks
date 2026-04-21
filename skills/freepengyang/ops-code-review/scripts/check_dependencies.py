#!/usr/bin/env python3
"""
工具依赖检查 - 必须在 skill 加载前运行
"""
import subprocess
import sys
import os
import json
import shlex

REQUIRED_TOOLS = {
    "svn": {
        "help": "SVN 客户端，用于 checkout 和 diff",
        "install": "apt-get install subversion",
    },
    "bandit": {
        "help": "Python 安全扫描",
        "install": "pip install --break-system-packages bandit",
    },
    "pylint": {
        "help": "Python 代码检查",
        "install": "pip install --break-system-packages pylint",
    },
    "npx": {
        "help": "Node.js 包执行器（用于 eslint）",
        "install": "npm install -g npx",
    },
    "phpcs": {
        "help": "PHP 代码规范检查",
        "install": "composer global require squizlabs/php_codesniffer",
        "deps": ["composer"],
    },
    "composer": {
        "help": "PHP 包管理器（用于安装 phpcs）",
        "install": "curl -sS https://getcomposer.org/installer -o /tmp/composer-setup.php && php /tmp/composer-setup.php -- --install-dir=/usr/local/bin --filename=composer",
    },
    "typescript-eslint": {
        "help": "ESLint TypeScript 解析器（前端代码审计必需）",
        "install": "npm install -g @typescript-eslint/parser @typescript-eslint/eslint-plugin typescript-eslint",
    },
}

MISSING_TOOLS_FILE = "/tmp/code_review_missing_tools.json"


def check_tool(name: str) -> bool:
    """检查工具是否存在"""
    # 特殊处理 Node.js 模块（@scope/package-name 形式）
    if name == "typescript-eslint":
        result = subprocess.run(
            ["node", "-e", "require('@typescript-eslint/parser')"],
            capture_output=True,
            text=True,
            env={**os.environ, "NODE_PATH": "/usr/lib/node_modules"},
        )
        return result.returncode == 0

    result = subprocess.run(
        ["which", name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def check_all() -> dict:
    """检查所有工具，返回缺失列表"""
    missing = {}
    for tool, info in REQUIRED_TOOLS.items():
        if not check_tool(tool):
            missing[tool] = info
    return missing


def ensure_tools() -> bool:
    """确保所有工具已安装，返回是否全部就绪"""
    missing = check_all()
    if not missing:
        print("[OK] All required tools are installed")
        if os.path.exists(MISSING_TOOLS_FILE):
            os.remove(MISSING_TOOLS_FILE)
        return True

    print(f"[WARN] Missing tools: {', '.join(missing.keys())}")
    with open(MISSING_TOOLS_FILE, "w") as f:
        json.dump(missing, f, ensure_ascii=False, indent=2)
    return False


def install_tool(name: str) -> bool:
    """安装指定工具"""
    if name not in REQUIRED_TOOLS:
        print(f"[ERROR] Unknown tool: {name}")
        return False

    info = REQUIRED_TOOLS[name]
    install_cmd = info["install"]
    print(f"[INFO] Installing {name}: {install_cmd}")

    deps = info.get("deps", [])
    for dep in deps:
        if not check_tool(dep):
            print(f"[INFO] Installing dependency {dep} first...")
            if not install_tool(dep):
                print(f"[ERROR] Failed to install dependency {dep}")
                return False

    result = subprocess.run(
        shlex.split(install_cmd),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"[OK] {name} installed successfully")
        return True
    else:
        print(f"[ERROR] Failed to install {name}: {result.stderr}")
        return False


def install_all() -> dict:
    """尝试安装所有缺失的工具，返回结果"""
    missing = check_all()
    results = {}
    for tool in missing:
        results[tool] = install_tool(tool)
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        missing = check_all()
        if not missing:
            print("All tools OK")
            sys.exit(0)
        print(f"Missing: {', '.join(missing.keys())}")
        print("\nTrying to install missing tools...")
        results = install_all()
        failed = [t for t, ok in results.items() if not ok]
        if failed:
            print(f"\nFailed to install: {', '.join(failed)}")
            sys.exit(1)
        print("\nAll tools installed successfully")
        sys.exit(0)

    action = sys.argv[1]

    if action == "check":
        missing = check_all()
        if missing:
            for tool, info in missing.items():
                print(f"MISSING: {tool} - {info['help']}")
                print(f"  Install: {info['install']}")
            sys.exit(1)
        print("All tools OK")
        sys.exit(0)

    elif action == "install" and len(sys.argv) >= 3:
        ok = install_tool(sys.argv[2])
        sys.exit(0 if ok else 1)

    elif action == "install-all":
        results = install_all()
        failed = [t for t, ok in results.items() if not ok]
        if failed:
            print(f"Failed: {', '.join(failed)}")
            sys.exit(1)
        print("All installed")
        sys.exit(0)

    elif action == "ensure":
        ok = ensure_tools()
        sys.exit(0 if ok else 1)

    else:
        print(f"Usage: {sys.argv[0]} [check|install|install-all|ensure]")
        sys.exit(1)
