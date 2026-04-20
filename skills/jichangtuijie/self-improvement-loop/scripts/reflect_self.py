#!/usr/bin/env python3
"""reflect_self: distill 反射自检与自修复 — v4.2"""
import os, re, sys, subprocess
from datetime import datetime, timezone

import os
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
LEARNINGS_DIR = os.path.join(WORKSPACE, ".learnings")
DISTILL_SELF = os.path.join(LEARNINGS_DIR, "DISTILL-SELF.md")

HEADER = """# DISTILL-SELF.md — distill 自我改进暂存区
> 本文件由 distill.sh v4.2 自动维护。手动编辑请保持格式完整。
"""

def ts():
    return datetime.now(timezone.utc).isoformat()

def get_next_id():
    seq = 1
    if os.path.exists(DISTILL_SELF):
        with open(DISTILL_SELF) as f:
            for line in f:
                m = re.search(r'SELF-FIX-(\d+)', line)
                if m:
                    seq = max(seq, int(m.group(1)) + 1)
    return f"{seq:03d}"

def can_auto_fix(proposal):
    markers = ["sed ", "grep ", "阈值", "阈值调整", "阈值修改", "awk",
               "THRESHOLD", "count ", "count>", "count>=", "count <",
               "count <=", "count==", "排序", "limit"]
    return any(m in proposal for m in markers)

def ensure_file():
    if not os.path.exists(DISTILL_SELF):
        with open(DISTILL_SELF, "w") as f:
            f.write(HEADER + "\n")

def scan_distill_patterns():
    """Scan learnings for distill.* patterns, write new SELF-FIX entries."""
    ensure_file()
    existing = set()
    with open(DISTILL_SELF) as f:
        for line in f:
            m = re.search(r'\*\*Pattern\*\*:\s*([^\n]+)', line)
            if m:
                existing.add(m.group(1).strip())

    new_entries = []
    files = [
        os.path.join(LEARNINGS_DIR, "LEARNINGS.md"),
        os.path.join(LEARNINGS_DIR, "ERRORS.md"),
        os.path.join(LEARNINGS_DIR, "FEATURE_REQUESTS.md"),
    ]
    for fpath in files:
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            content = f.read()

        # Extract pending entries with distill.* Pattern-Key
        for entry in re.finditer(r'(## \[LRN-[^\]]+\].*?)(?=## \[LRN-|^# |\Z)', content, re.DOTALL):
            block = entry.group(1)
            pk_m = re.search(r'Pattern-Key:\s*([^\n]+)', block)
            status_m = re.search(r'\*\*Status\*\*:\s*([^\n]+)', block)
            pk = pk_m.group(1).strip() if pk_m else ""
            status = status_m.group(1).strip().lower() if status_m else ""
            if pk.startswith("distill.") and status in ("", "pending", "active", "in_progress"):
                if pk not in existing:
                    raw_snippet = " ".join(block.splitlines()[:3])[:200]
                    nid = get_next_id()
                    needs_human = "false" if can_auto_fix(block) else "true"
                    entry_text = (
                        f"## [SELF-FIX-{nid}]\n"
                        f"**Detected**: {ts()}\n"
                        f"**Pattern**: {pk}\n"
                        f"**Source**: distill reflect check\n"
                        f"**Severity**: medium\n"
                        f"**Proposal**: distill 发现自身存在问题，建议检查相关代码。原文：{raw_snippet}\n"
                        f"**Status**: pending\n"
                        f"**Needs-Human**: {needs_human}\n"
                        f"**Applied-At**:\n\n"
                    )
                    new_entries.append(entry_text)
                    existing.add(pk)

    if new_entries:
        with open(DISTILL_SELF, "a") as f:
            f.write("\n".join(new_entries) + "\n")
        print(f"[distill reflect] Generated {len(new_entries)} new self-fix proposal(s)", file=sys.stderr)

def collect_needs_human():
    """Return list of SELF-FIX IDs that need human intervention."""
    ensure_file()
    needs_human = []
    with open(DISTILL_SELF) as f:
        in_entry = False
        eid = ""
        pending = False
        for line in f:
            if re.match(r'^## \[SELF-FIX-', line.strip()):
                in_entry = True
                m = re.search(r'SELF-FIX-(\S+)', line)
                eid = m.group(1) if m else ""
                pending = False
            elif in_entry:
                if re.search(r'Status.*pending', line, re.I):
                    pending = True
                elif re.search(r'Needs-Human.*true', line, re.I) and pending:
                    needs_human.append(f"SELF-FIX-{eid}")
                    in_entry = False
    return needs_human

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "detect"
    if step == "detect":
        scan_distill_patterns()
    elif step == "apply":
        # Step 4: apply auto-fixes (currently a no-op; complex fixes -> needs_human)
        needs = collect_needs_human()
        print(f"[distill reflect] {len(needs)} self-fix(es) need human intervention", file=sys.stderr)
    elif step == "check":
        needs = collect_needs_human()
        for nid in needs:
            print(nid)
