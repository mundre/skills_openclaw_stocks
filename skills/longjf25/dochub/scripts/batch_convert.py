"""
DocHub - Document Workbench v4
- init mode: preserve original directory structure, batch convert to _docs_md
- run mode: incremental conversion (new/changed files only)
- process mode: process new docs from update/ folder
- Generate: 工作知识库.md (knowledge base), _convert_log.txt (log), _index.md (index)
- Security: path traversal guard, safe subprocess, temp cleanup, log write safety
"""
import os
import re
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from collections import defaultdict

# ============================================================
# Constants
# ============================================================

MARKITDOWN_CMD = [sys.executable, "-m", "markitdown"]
LOG_FILE = None

# Directory names
RAW_DIR = "RAW"                    # Original documents
DOCS_MD_DIR = "_docs_md"          # Converted Markdown documents
INDEX_FILE = "_index.md"          # Document index
CONVERT_LOG_FILE = "_convert_log.txt"  # Conversion log
UPDATE_DIR = "update"             # New document drop zone
KNOWLEDGE_BASE_FILE = "工作知识库.md"  # Knowledge base

# Skip directories when scanning (RAW is source, don't skip it)
SKIP_DIRS = {DOCS_MD_DIR, "_markdown", UPDATE_DIR, "_sanitized_output",
             "_restored_output", "node_modules", ".git", "__pycache__"}

# Supported extensions
DOC_EXTENSIONS = {".docx", ".xlsx", ".pdf", ".doc"}

# Single text max processing length (10 MB), skip oversized to avoid OOM
MAX_TEXT_LENGTH = 10 * 1024 * 1024

# ============================================================
# Utility Functions
# ============================================================


def normalize_name(name):
    """
    Normalize directory or file name (stem only, no extension).
    Only keeps: Chinese chars, English letters, digits, underscore(_), hyphen(-).
    All other characters are replaced by underscore, consecutive underscores collapsed.
    
    规范化目录名/文件名（不含扩展名）：
    只保留：中文、英文字母、数字、下横线(_)、中横线(-)。
    其他字符统一替换为下横线，连续下横线合并为一个。
    """
    if not name:
        return name
    # Keep: CJK unified ideographs (u4e00-u9fff), common CJK punctuation extensions,
    #       English letters, digits, underscore, hyphen
    # Replace everything else with underscore
    cleaned = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf\w\-]', '_', name)
    # Collapse consecutive underscores into one
    cleaned = re.sub(r'_+', '_', cleaned)
    # Strip leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Fallback: if result is empty (e.g. name was all special chars)
    return cleaned if cleaned else '_unnamed_'


def normalize_path(path_str):
    """
    Normalize all parts of a path string.
    规范化路径的所有部分（目录名和文件名）。
    Returns a Path object with all parts normalized.
    """
    p = Path(path_str)
    parts = list(p.parts)
    # Normalize each part (skip drive letter on Windows, e.g. 'C:\\')
    start = 1 if len(parts) > 1 and parts[0].endswith(':') else 0
    for i in range(start, len(parts)):
        part = parts[i]
        # For the last part, normalize stem and re-attach extension
        if i == len(parts) - 1 and '.' in part:
            stem, ext = part.rsplit('.', 1)
            parts[i] = normalize_name(stem) + '.' + ext
        else:
            parts[i] = normalize_name(part)
    return Path(*parts)


def log(msg):
    """Log output with write safety — never crashes main process / 日志容错"""
    try:
        clean = ''.join(c for c in str(msg) if c.isprintable() or c in '\n\r\t')
        print(clean)
    except Exception:
        pass
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(str(msg) + "\n")
        except Exception:
            pass


def init_log(workspace):
    global LOG_FILE
    LOG_FILE = workspace / CONVERT_LOG_FILE
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"DocHub v4 - {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
    except Exception as e:
        print(f"[WARN] Cannot create log file: {e}")


def validate_workspace(workspace):
    """Validate workspace path — ensure it exists and is a directory / 校验工作区路径"""
    p = Path(workspace)
    if not p.exists():
        log(f"[ERROR] Workspace does not exist: {p}")
        sys.exit(1)
    if not p.is_dir():
        log(f"[ERROR] Workspace is not a directory: {p}")
        sys.exit(1)
    return p.resolve()


def sanitize_path(base, target):
    """Ensure resolved target is within base directory — prevent path traversal / 路径穿越防护"""
    resolved = (base / target).resolve()
    base_resolved = base.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        log(f"[ERROR] Path traversal detected: {target}")
        return None
    return resolved


# ============================================================
# Keyword Analysis
# ============================================================


def extract_keywords(text, top_n=20):
    """Extract keywords from text (simple word frequency) / 从文本中提取关键词"""
    if not text or len(text) > MAX_TEXT_LENGTH:
        return []
    # Remove punctuation and numbers
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', ' ', text.lower())
    words = text.split()
    # Filter stopwords
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                 '自己', '这', '那', '他', '她', '它', '们', '为', '与', '对', '以', '及',
                 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on', 'with',
                 'at', 'by', 'from', 'as', 'into', 'through', 'and', 'or', 'but', 'if'}
    words = [w for w in words if len(w) >= 2 and w not in stopwords]
    freq = defaultdict(int)
    for w in words:
        freq[w] += 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]


def get_doc_keywords(path, tmp_path):
    """Get document keywords via markitdown / 获取文档关键词"""
    try:
        shutil.copy2(path, tmp_path)
        result = subprocess.run(
            MARKITDOWN_CMD + [tmp_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return extract_keywords(result.stdout)
    except subprocess.TimeoutExpired:
        log(f"  [WARN] markitdown timeout for {path.name}")
    except Exception:
        pass
    return []


# ============================================================
# Categorization (Auto Mode)
# ============================================================


def analyze_and_categorize(workspace):
    """
    Dynamically analyze document content, auto-generate category structure
    动态分析文档内容，自动生成分类结构
    Returns: {category_name: [doc_paths]}
    """
    log("\n[STEP 1] Scanning documents...")
    all_docs = []
    raw_base = workspace / RAW_DIR
    if not raw_base.exists():
        raw_base = workspace  # Fallback to workspace root

    for root, dirs, files in os.walk(raw_base):
        root_parts = set(Path(root).parts)
        if any(d in root_parts for d in SKIP_DIRS):
            continue
        for f in files:
            if Path(f).suffix.lower() in DOC_EXTENSIONS:
                all_docs.append(Path(root) / f)

    log(f"  Found {len(all_docs)} documents")
    if not all_docs:
        return {}

    # Sample analysis (max 30 docs)
    sample = all_docs[:30] if len(all_docs) > 30 else all_docs
    doc_signatures = {}

    log("\n[STEP 2] Analyzing document content...")
    for i, doc in enumerate(sample):
        fd, tmp = tempfile.mkstemp(suffix=doc.suffix)
        os.close(fd)
        try:
            kw = get_doc_keywords(doc, tmp)
            doc_signatures[str(doc)] = kw
            if (i + 1) % 5 == 0:
                log(f"  Analyzed {i+1}/{len(sample)}...")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    # Cluster by keyword similarity
    log("\n[STEP 3] Generating category structure...")
    categories = defaultdict(list)
    category_keywords = {}

    for doc in all_docs:
        doc_str = str(doc)
        kw = doc_signatures.get(doc_str, [])
        sig = set([w for w, _ in kw[:5]])

        if not sig:
            categories["Other"].append(doc)
            continue

        matched = False
        best_score = 0
        best_cat = None
        for cat, cat_kw in category_keywords.items():
            cat_set = set([w for w, _ in cat_kw[:10]])
            score = len(sig & cat_set)
            if score > best_score:
                best_score = score
                best_cat = cat

        if best_score >= 1:
            categories[best_cat].append(doc)
        else:
            new_cat = f"_{kw[0][0]}" if kw else "Other"
            base = new_cat
            n = 1
            while new_cat in categories:
                new_cat = f"{base}_{n}"
                n += 1
            categories[new_cat] = [doc]
            category_keywords[new_cat] = kw

    for cat in list(categories.keys()):
        if not categories[cat]:
            del categories[cat]

    final_cats = {}
    for cat, docs in categories.items():
        if cat.startswith("_"):
            kw_list = category_keywords.get(cat, [])
            if kw_list:
                final_cats[f"docs_{kw_list[0][0]}"] = docs
            else:
                final_cats["Uncategorized"] = docs
        else:
            final_cats[cat] = docs

    return final_cats


# ============================================================
# Directory Structure - Preserve Full Path
# ============================================================


def rename_raw_dirs(raw_base):
    """
    Recursively rename directories and files under raw_base to normalized names.
    Only directories and file names (stems) are renamed; file extensions are preserved.
    Returns list of (action, old_path, new_path) for logging.
    
    递归重命名 raw_base 下的目录和文件，使其符合命名规范。
    只重命名目录名和文件名（不含扩展名）。
    返回操作记录列表 [(action, old_path, new_path), ...]
    """
    actions = []

    # --- Phase 1: rename files (bottom-up to avoid path confusion) ---
    for root, dirs, files in os.walk(raw_base):
        for f in files:
            original = Path(root) / f
            stem, ext = original.stem, original.suffix
            new_stem = normalize_name(stem)
            if new_stem != stem:
                target = Path(root) / (new_stem + ext)
                try:
                    original.rename(target)
                    actions.append(("rename_file", str(original), str(target)))
                except Exception as e:
                    log(f"  [WARN] Cannot rename file {f}: {e}")

    # --- Phase 2: rename directories (bottom-up) ---
    for root, dirs, files in os.walk(raw_base, topdown=False):
        for d in sorted(dirs, reverse=True):
            original = Path(root) / d
            new_name = normalize_name(d)
            if new_name != d:
                target = Path(root) / new_name
                # Avoid collision: if target already exists, append suffix
                if target.exists():
                    base = new_name
                    n = 2
                    while target.exists():
                        target = Path(root) / f"{base}_{n}"
                        n += 1
                try:
                    original.rename(target)
                    actions.append(("rename_dir", str(original), str(target)))
                except Exception as e:
                    log(f"  [WARN] Cannot rename dir {d}: {e}")

    return actions


def scan_full_structure(workspace):
    """
    Scan full directory structure preserving all levels.
    RAW directories are expected to already be normalized (via rename_raw_dirs).
    
    扫描完整目录结构，保留所有层级。
    RAW 目录应该在 init 时已经通过 rename_raw_dirs 规范化。
    Returns: [(rel_path, doc_path), ...] where rel_path preserves directory structure
    """
    raw_base = workspace / RAW_DIR
    if not raw_base.exists():
        raw_base = workspace  # Fallback

    docs_with_structure = []

    for root, dirs, files in os.walk(raw_base):
        root_path = Path(root)
        root_parts = set(root_path.parts)

        # Skip output directories
        if any(d in root_parts for d in SKIP_DIRS):
            continue

        for f in files:
            ext = Path(f).suffix.lower()
            if ext in DOC_EXTENSIONS:
                doc_path = root_path / f
                try:
                    rel_path = doc_path.relative_to(raw_base)
                except ValueError:
                    rel_path = doc_path.relative_to(workspace)

                docs_with_structure.append((rel_path, doc_path))

    return docs_with_structure


def create_output_structure(workspace, docs_with_structure):
    """
    Create output directory structure based on document paths.
    Directory and file names are normalized before creating paths.
    
    根据文档路径创建输出目录结构。
    目录名和文件名在创建路径前已规范化。
    Returns: {source_path: dest_path}
    """
    log("\n[STEP 4] Creating directory structure...")
    md_base = workspace / DOCS_MD_DIR
    md_base.mkdir(exist_ok=True)

    move_map = {}

    # Group by top-level directory for display
    top_level_groups = defaultdict(list)
    for rel_path, doc_path in docs_with_structure:
        if rel_path.parts:
            top_level_groups[rel_path.parts[0]].append((rel_path, doc_path))
        else:
            top_level_groups["root"].append((rel_path, doc_path))

    for top_dir, docs in sorted(top_level_groups.items()):
        log(f"  {top_dir}/ ({len(docs)} docs)")

        for rel_path, doc_path in docs:
            # Normalize each path component
            norm_parts = [normalize_name(p) for p in rel_path.parent.parts]
            norm_stem = normalize_name(doc_path.stem)

            # Build normalized destination path
            if norm_parts:
                dst_path = md_base.joinpath(*norm_parts) / norm_stem
            else:
                dst_path = md_base / norm_stem

            # Handle duplicate names
            if dst_path.with_suffix(".md").exists():
                counter = 1
                while dst_path.with_suffix(".md").exists():
                    dst_path = md_base.joinpath(*(norm_parts or [''])) / f"{norm_stem}_{counter}"
                    counter += 1

            move_map[str(doc_path)] = dst_path

    # Create update folder
    update_dir = workspace / UPDATE_DIR
    update_dir.mkdir(exist_ok=True)
    log(f"\n  Created: {UPDATE_DIR}/ (new document drop zone)")

    return move_map


# ============================================================
# Conversion
# ============================================================


def convert_single(src_path, dst_path):
    """Convert a single file to Markdown / 转换单个文件到 MD"""
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=src_path.suffix)
        os.close(fd)
        try:
            shutil.copy2(src_path, tmp)
            result = subprocess.run(
                MARKITDOWN_CMD + [tmp],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0 and result.stdout.strip():
                md_path = dst_path.with_suffix(".md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                return True
            else:
                log(f"    [WARN] markitdown returned empty for {src_path.name}")
        except subprocess.TimeoutExpired:
            log(f"    [WARN] Conversion timeout for {src_path.name}")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    except Exception as e:
        log(f"    [ERROR] {e}")
    return False


# ============================================================
# Incremental Mode
# ============================================================


def run_incremental(workspace):
    """
    Incremental mode: normalize any un-normalized names, then convert new/changed files.
    增量模式：规范化未规范的命名，然后转换新增/变更的文件。
    """
    md_base = workspace / DOCS_MD_DIR
    if not md_base.exists():
        log(f"[WARN] {DOCS_MD_DIR}/ does not exist, please run init first")
        return

    log("\n[INCREMENTAL] Incremental conversion mode")
    log("=" * 50)

    # --- Step 1: Normalize RAW names ---
    raw_base = workspace / RAW_DIR
    if raw_base.exists():
        actions = rename_raw_dirs(raw_base)
        if actions:
            log(f"\n  Normalized {len(actions)} RAW items")

    # --- Step 2: Find new/changed files ---
    md_to_source = {}
    for md_file in md_base.rglob("*.md"):
        rel = md_file.relative_to(md_base)
        # Build normalized relative path to match against RAW
        norm_rel = Path(*(normalize_name(p) for p in rel.parts))
        for ext in [".docx", ".xlsx", ".pdf", ".doc"]:
            # Check RAW first, then workspace root
            src_candidate = workspace / RAW_DIR / str(norm_rel).replace(".md", ext)
            if not src_candidate.exists():
                src_candidate = workspace / str(norm_rel).replace(".md", ext)
            if not src_candidate.exists():
                # Try original (non-normalized) path as fallback
                src_candidate = workspace / RAW_DIR / str(rel).replace(".md", ext)
            if src_candidate.exists():
                md_to_source[str(md_file)] = src_candidate
                break

    total = 0
    success = 0
    for md_path_str, src_path in md_to_source.items():
        md_path = Path(md_path_str)
        if md_path.exists() and src_path.exists() and md_path.stat().st_mtime > src_path.stat().st_mtime:
            continue
        total += 1
        if convert_single(src_path, md_path.with_suffix("")):
            success += 1

    log(f"\nIncremental conversion complete: {success}/{total} files updated")


# ============================================================
# Interactive Mode Selection
# ============================================================


def ask_classify_mode():
    """
    Ask user to select categorization mode
    询问用户选择分类模式
    """
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            choice = sys.argv[idx + 1].strip()
            if choice == "1":
                print("\n[MODE] Parameter: Keep original structure (mode=1)")
                return "keep"
            elif choice == "2":
                print("\n[MODE] Parameter: Auto-analyze & categorize (mode=2)")
                return "auto"

    # Interactive mode
    print("\n" + "=" * 60)
    print("[INIT] DocHub Initialization / 文档工作台初始化")
    print("=" * 60)
    print("\n目录结构规范:")
    print("  RAW/          - 原始文档（不动）")
    print("  _docs_md/     - Markdown转换文档")
    print("  update/       - 新文档入口")
    print("  工作知识库.md - 知识库入口")
    print("\nSelect categorization mode / 请选择分类结构创建方式：\n")
    print("  [1] Keep original structure / 保持原有目录结构")
    print("      - Organize docs into _docs_md/ preserving current folders")
    print()
    print("  [2] Auto-analyze & categorize / 系统自动分析创建分类")
    print("      - Analyze document keywords")
    print("      - Group by content similarity")
    print()
    print("=" * 60)

    while True:
        choice = input("\nEnter [1/2] (default 1) / 请输入选择 [1/2]（默认 1）: ").strip()
        if choice == "" or choice == "1":
            return "keep"
        elif choice == "2":
            return "auto"
        else:
            print("Invalid input / 无效输入，请输入 1 或 2")


# ============================================================
# Scan Existing Structure (Keep Mode)
# ============================================================


def scan_existing_structure(workspace):
    """
    Scan existing directory structure preserving full path
    扫描现有目录结构，保留完整路径
    Returns: [(rel_path, doc_path), ...]
    """
    docs = scan_full_structure(workspace)
    return [(str(rp), dp) for rp, dp in docs]


# ============================================================
# Index Generation
# ============================================================


def generate_index(workspace, docs_with_structure):
    """Generate document index / 生成文档索引"""
    md_base = workspace / DOCS_MD_DIR
    index_file = md_base / INDEX_FILE

    # Group docs by top-level directory
    groups = defaultdict(list)
    for rel_path, doc_path in docs_with_structure:
        top_dir = rel_path.parts[0] if rel_path.parts else "root"
        groups[top_dir].append((rel_path, doc_path))

    lines = [
        "# 文档索引\n",
        f"> 自动生成 | 更新时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n\n",
        "## 目录结构\n\n",
        "```\n",
        f"{DOCS_MD_DIR}/\n",
    ]

    # Generate tree structure
    def add_tree(path_parts, prefix=""):
        if not path_parts:
            return
        if len(path_parts) == 1:
            lines.append(f"{prefix}├── {path_parts[0]}/\n")
        else:
            lines.append(f"{prefix}└── {path_parts[0]}/\n")
        if len(path_parts) > 1:
            add_tree(path_parts[1:], prefix + "    ")

    for top_dir in sorted(groups.keys()):
        lines.append(f"├── {top_dir}/\n")
        subdocs = defaultdict(list)
        for rel_path, _ in groups[top_dir]:
            if len(rel_path.parts) > 2:
                subdocs[rel_path.parts[1]].append(rel_path)
            elif len(rel_path.parts) == 2:
                subdocs[rel_path.parts[1]].append(rel_path)

        for subdir in sorted(subdocs.keys()):
            lines.append(f"│   ├── {subdir}/\n")

    lines.append("```\n\n")

    # Document list
    lines.append("## 文档清单\n\n")
    for top_dir in sorted(groups.keys()):
        lines.append(f"### {top_dir}\n\n")
        for rel_path, doc_path in sorted(groups[top_dir]):
            md_path = md_base / rel_path.with_suffix(".md")
            if md_path.exists():
                lines.append(f"- [{doc_path.stem}]({md_path.relative_to(md_base).as_posix()})\n")
        lines.append("\n")

    try:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        log(f"  Generated: {index_file}")
    except Exception as e:
        log(f"[ERROR] Failed to write index: {e}")


# ============================================================
# Knowledge Base Generation
# ============================================================


def generate_knowledge_base(workspace, docs_with_structure):
    """Generate knowledge base / 生成工作知识库"""
    kb_file = workspace / KNOWLEDGE_BASE_FILE

    # Count docs by category
    groups = defaultdict(list)
    for rel_path, doc_path in docs_with_structure:
        top_dir = rel_path.parts[0] if rel_path.parts else "root"
        groups[top_dir].append((rel_path, doc_path))

    # Category descriptions
    cat_desc = {
        "发货分队": "分单仓管理、工作笔记、队长小结等",
        "工作报告": "年度总结、述职报告、月度汇报等",
        "新进港货站相关": "基建项目、智能货架、ETV测试等",
    }

    total_docs = sum(len(docs) for docs in groups.values())

    lines = [
        "# 工作知识库\n\n",
        f"> 广州白云国际物流有限公司 - 国际货站进港室文档知识库\n",
        f"> 更新时间：{__import__('datetime').datetime.now().strftime('%Y年%m月%d日')}\n\n",
        "---\n\n",
        "## 📋 文档概览\n\n",
        f"本知识库包含国际货站进港室相关工作文档，共 **{total_docs} 篇 Markdown 文档**，涵盖以下领域：\n\n",
        "| 领域 | 说明 | 文档数量 |\n",
        "|------|------|----------|\n",
    ]

    for cat in sorted(groups.keys()):
        desc = cat_desc.get(cat, "")
        lines.append(f"| {cat} | {desc} | ~{len(groups[cat])}篇 |\n")

    lines.append("\n---\n\n")

    # Directory structure
    lines.append("## 🗂️ 文档目录结构\n\n")
    lines.append("```\n")
    lines.append("文档工作台/\n")
    lines.append(f"├── {RAW_DIR}/                    # 原始文档（未转换）\n")
    lines.append(f"├── {DOCS_MD_DIR}/               # Markdown 转换文档\n")
    lines.append(f"│   ├── 发货分队/\n")
    lines.append(f"│   ├── 工作报告/\n")
    lines.append(f"│   └── 新进港货站相关/\n")
    lines.append(f"├── {UPDATE_DIR}/                 # 新文档入口\n")
    lines.append(f"├── {KNOWLEDGE_BASE_FILE}       # 本文件\n")
    lines.append(f"└── {CONVERT_LOG_FILE}        # 转换日志\n")
    lines.append("```\n\n")

    # Quick links
    lines.append("## 📌 常用文档快速链接\n\n")
    lines.append("### 纪检工作\n\n")
    for rel_path, doc_path in docs_with_structure:
        if "党风廉政" in str(rel_path) or "述职报告" in str(rel_path):
            md_path = Path(DOCS_MD_DIR) / rel_path.with_suffix(".md")
            lines.append(f"- [{doc_path.stem}](../{md_path.as_posix()})\n")

    lines.append("\n### 发货分队工作\n\n")
    for rel_path, doc_path in docs_with_structure:
        if "发货" in str(rel_path) and ("总结" in str(rel_path) or "汇报" in str(rel_path)):
            md_path = Path(DOCS_MD_DIR) / rel_path.with_suffix(".md")
            lines.append(f"- [{doc_path.stem}](../{md_path.as_posix()})\n")

    lines.append("\n### 新进港货站项目\n\n")
    for rel_path, doc_path in docs_with_structure:
        if "新进港货站" in str(rel_path) and ("需求" in str(rel_path) or "方案" in str(rel_path)):
            md_path = Path(DOCS_MD_DIR) / rel_path.with_suffix(".md")
            lines.append(f"- [{doc_path.stem}](../{md_path.as_posix()})\n")

    lines.append("\n---\n\n")
    lines.append("*本知识库由 DocHub 文档工作台自动维护*\n")

    try:
        with open(kb_file, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        log(f"  Generated: {kb_file}")
    except Exception as e:
        log(f"[ERROR] Failed to write knowledge base: {e}")


# ============================================================
# Init Mode
# ============================================================


def run_init(workspace):
    """Initialize: normalize RAW dirs, create structure, batch convert / 初始化模式"""

    mode = ask_classify_mode()

    init_log(workspace)

    # --- STEP 0: Normalize RAW directory and file names ---
    log("\n[STEP 0] Normalizing RAW directory/file names...")
    log("  Rule: only Chinese, English, digits, underscore(_), hyphen(-) allowed")
    log("  Rule: spaces and special chars replaced by underscore")
    raw_base = workspace / RAW_DIR
    if raw_base.exists():
        actions = rename_raw_dirs(raw_base)
        if actions:
            log(f"  Renamed {len(actions)} items:")
            for action, old, new in actions:
                short_old = Path(old).name
                short_new = Path(new).name
                log(f"    [{action}] {short_old} -> {short_new}")
        else:
            log("  All names already normalized, no changes needed")
    else:
        log("  [SKIP] RAW/ does not exist")

    if mode == "keep":
        log("\n[MODE] Keep original directory structure / 保持原有目录结构")
        log("=" * 60)
        docs_with_structure = scan_full_structure(workspace)
        if not docs_with_structure:
            log("[WARN] No documents found / 未发现任何文档")
            return

        # Group by top-level for display
        groups = defaultdict(list)
        for rel_path, doc_path in docs_with_structure:
            top = rel_path.parts[0] if rel_path.parts else "root"
            groups[top].append((rel_path, doc_path))

        log(f"Found {len(docs_with_structure)} documents in {len(groups)} directories")
        for cat, docs in sorted(groups.items()):
            log(f"  {cat}/ ({len(docs)} docs)")
    else:
        log("\n[MODE] Auto-analyze & categorize / 系统自动分析创建分类")
        log("=" * 60)
        categories = analyze_and_categorize(workspace)
        if not categories:
            log("[WARN] No documents found / 未发现任何文档")
            return
        docs_with_structure = []
        for cat, docs in categories.items():
            norm_cat = normalize_name(cat)
            for doc in docs:
                docs_with_structure.append((Path(norm_cat) / normalize_name(doc.name), doc))

    # --- STEP 1: Delete old _docs_md and recreate ---
    old_md = workspace / DOCS_MD_DIR
    if old_md.exists():
        try:
            shutil.rmtree(old_md)
            log(f"\n[STEP 1] Removed old {DOCS_MD_DIR}/ directory")
        except Exception as e:
            log(f"\n[WARN] Could not remove old {DOCS_MD_DIR}/: {e}")
    else:
        log(f"\n[STEP 1] Creating fresh {DOCS_MD_DIR}/ directory")

    # --- STEP 2: Create directory structure and get move map ---
    try:
        move_map = create_output_structure(workspace, docs_with_structure)
    except Exception as e:
        log(f"[ERROR] Failed to create directory structure: {e}")
        return

    # --- STEP 3: Batch convert ---
    log("\n[STEP 3] Converting documents to Markdown...")
    total = len(move_map)
    success = 0
    failed = []

    for i, (src_str, dst) in enumerate(move_map.items(), 1):
        src = Path(src_str)
        try:
            rel_path = src.relative_to(workspace / RAW_DIR) if (workspace / RAW_DIR).exists() else src.relative_to(workspace)
        except ValueError:
            rel_path = src.name
        log(f"  [{i}/{total}] {rel_path}")
        try:
            if convert_single(src, dst):
                success += 1
                log(f"    [OK]")
            else:
                failed.append(src_str)
                log(f"    [FAIL]")
        except Exception as e:
            failed.append(src_str)
            log(f"    [ERROR] {e}")

    # --- STEP 4: Generate index and knowledge base ---
    log("\n[STEP 4] Generating index and knowledge base...")
    try:
        doc_pairs = [(Path(k), Path(v.parent) / Path(v).name.replace(".md", "")) for k, v in move_map.items()]
        generate_index(workspace, doc_pairs)
        generate_knowledge_base(workspace, doc_pairs)
    except Exception as e:
        log(f"[ERROR] Failed to generate index/KB: {e}")

    # --- Report ---
    log("\n" + "=" * 60)
    log(f"[RESULT] Conversion complete: {success}/{total} succeeded / 转换完成: {success}/{total} 成功")
    if failed:
        log(f"Failed files / 失败文件数: {len(failed)}")
        for f in failed:
            log(f"  - {f}")
    else:
        log("All succeeded! / 全部成功!")
    log("=" * 60)
    log(f"\n[OUTPUT] Document index: {workspace / DOCS_MD_DIR / INDEX_FILE}")
    log(f"[OUTPUT] Knowledge base: {workspace / KNOWLEDGE_BASE_FILE}")
    log(f"[LOG] Processing log: {LOG_FILE}")


# ============================================================
# Process Update Folder
# ============================================================


def process_update_folder(workspace):
    """
    Process new documents in update/ folder:
    1. Normalize file names (remove spaces/special chars)
    2. Analyze content -> match category
    3. Copy to categorized directory with normalized names
    4. Incremental convert
    5. Clear update/
    
    处理 update/ 文件夹中的新文档：
    1. 规范化文件名（去除空格/特殊字符）
    2. 分析内容 -> 匹配分类
    3. 复制到分类目录（使用规范化文件名）
    4. 增量转换
    5. 清空 update/
    """
    update_dir = workspace / UPDATE_DIR
    md_base = workspace / DOCS_MD_DIR

    if not update_dir.exists() or not any(update_dir.iterdir()):
        log(f"[WARN] {UPDATE_DIR}/ is empty or does not exist")
        return

    safe_update = sanitize_path(workspace, UPDATE_DIR)
    if safe_update is None:
        log(f"[ERROR] Unsafe update directory path")
        return

    log(f"\n[UPDATE] Processing new documents in {UPDATE_DIR}/...")
    log("=" * 50)

    existing_cats = [d.name for d in md_base.iterdir() if d.is_dir() and not d.name.startswith("_")]

    new_docs = list(safe_update.iterdir())
    for doc in new_docs:
        if doc.is_dir():
            continue

        # --- Normalize file name first ---
        stem, ext = doc.stem, doc.suffix
        norm_stem = normalize_name(stem)
        if norm_stem != stem:
            norm_doc = doc.parent / (norm_stem + ext)
            try:
                doc.rename(norm_doc)
                log(f"  [RENAME] {stem}{ext} -> {norm_stem}{ext}")
                doc = norm_doc
            except Exception as e:
                log(f"  [WARN] Cannot normalize filename {doc.name}: {e}")

        # Analyze content for category matching
        fd, tmp = tempfile.mkstemp(suffix=doc.suffix)
        os.close(fd)
        kw = []
        try:
            shutil.copy2(doc, tmp)
            result = subprocess.run(
                MARKITDOWN_CMD + [tmp],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                kw = extract_keywords(result.stdout)
        except subprocess.TimeoutExpired:
            log(f"  [WARN] Timeout analyzing {doc.name}")
        except Exception:
            pass
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

        matched_cat = None
        for cat in existing_cats:
            cat_clean = cat.replace("docs_", "")
            for word, _ in kw[:5]:
                if cat_clean in word or word in cat_clean:
                    matched_cat = cat
                    break
            if matched_cat:
                break

        if not matched_cat and existing_cats:
            matched_cat = existing_cats[0]

        if not matched_cat:
            matched_cat = "Other"

        # Normalize category name as well
        norm_cat = normalize_name(matched_cat)
        safe_cat = sanitize_path(md_base, norm_cat)
        if safe_cat is None:
            log(f"  [SKIP] Unsafe category: {norm_cat} for {doc.name}")
            continue
        safe_cat.mkdir(exist_ok=True)

        dest = sanitize_path(safe_cat, doc.name)
        if dest is None:
            log(f"  [SKIP] Unsafe filename: {doc.name}")
            continue

        shutil.copy2(doc, dest)
        log(f"  {doc.name} -> {norm_cat}/")
        convert_single(dest, dest.with_suffix(""))

    # Clear update folder
    for doc in new_docs:
        if doc.is_file():
            try:
                doc.unlink()
            except Exception:
                pass
    log(f"\n{UPDATE_DIR}/ cleared (folder preserved) / 已清空（保留空文件夹）")


# ============================================================
# Main Entry
# ============================================================


def main():
    if len(sys.argv) < 2:
        print("Usage / 用法:")
        print("  python batch_convert.py init [--mode 1|2] <workspace>")
        print("  python batch_convert.py run <workspace>")
        print("  python batch_convert.py process <workspace>")
        print()
        print("Directory structure / 目录结构:")
        print(f"  {RAW_DIR}/          - Original documents / 原始文档")
        print(f"  {DOCS_MD_DIR}/     - Converted Markdown / Markdown文档")
        print(f"  {UPDATE_DIR}/       - New document drop zone / 新文档入口")
        print(f"  {KNOWLEDGE_BASE_FILE} - Knowledge base / 知识库")
        print(f"  {CONVERT_LOG_FILE} - Conversion log / 转换日志")
        print()
        print("  --mode 1  Keep original structure (default) / 保持原有目录结构（默认）")
        print("  --mode 2  Auto-analyze & categorize / 系统自动分析创建分类")
        sys.exit(1)

    mode = sys.argv[1].lower()
    args = [a for i, a in enumerate(sys.argv[2:], 2)
            if not (a == "--mode" or (i > 2 and sys.argv[i-1] == "--mode"))]
    workspace = Path(args[0]).resolve() if args else Path.cwd()

    workspace = validate_workspace(workspace)

    if mode == "init":
        run_init(workspace)
    elif mode == "run":
        run_incremental(workspace)
    elif mode == "process":
        process_update_folder(workspace)
    else:
        log(f"[ERROR] Unknown mode / 未知模式: {mode}")
        log("  Supported / 支持的模式: init / run / process")
        sys.exit(1)


if __name__ == "__main__":
    main()
