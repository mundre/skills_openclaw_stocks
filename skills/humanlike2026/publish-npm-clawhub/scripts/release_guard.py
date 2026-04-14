#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from scan_patterns.doc_context_patterns import (
    SAFE_DOC_CONTEXT_PATTERNS,
    SECRET_PATH_PATTERNS,
    UNSAFE_DOC_CONTEXT_PATTERNS,
)
from scan_patterns.env_patterns import ENV_PATTERNS
from scan_patterns.file_patterns import FILE_PATTERNS
from scan_patterns.network_patterns import NETWORK_PATTERNS


FORBIDDEN_DEFAULTS = [
    ".npmrc",
    ".env",
    "*.tgz",
    "*.local.json",
    "*.pyc",
    "__pycache__",
    ".claude/settings.local.json",
    "config/publish.accounts.json",
]

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".py",
    ".sh",
    ".yml",
    ".yaml",
}
CODE_EXTENSIONS = {
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".py",
    ".sh",
}
DOC_EXTENSIONS = {
    ".md",
    ".txt",
}

VERSION_CONST_PATTERNS = [
    re.compile(r"\b(?:SKILL|PLUGIN|PACKAGE|APP)_VERSION\s*=\s*['\"]([^'\"]+)['\"]"),
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_git_ignored(repo: Path, rel_path: str) -> bool:
    result = run(["git", "check-ignore", rel_path], repo)
    return result.returncode == 0


def tracked_files(repo: Path) -> set[str]:
    result = run(["git", "ls-files"], repo)
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"SKILL.md", "README", "README.md"}


def is_code_candidate(path: Path) -> bool:
    return path.suffix.lower() in CODE_EXTENSIONS


def is_doc_candidate(path: Path) -> bool:
    return path.suffix.lower() in DOC_EXTENSIONS or path.name in {"SKILL.md", "README", "README.md"}


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_any(rel_path: str, patterns: list[str]) -> bool:
    parts = rel_path.split("/")
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern) or rel_path == pattern:
            return True
        if "/" not in pattern and "*" not in pattern and any(part == pattern for part in parts):
            return True
    return False


def copy_selected(repo: Path, include_paths: list[str], output_dir: Path, forbidden_patterns: list[str]) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in include_paths:
        src = repo / item
        if not src.exists():
            continue
        if matches_any(item, forbidden_patterns):
            continue
        dst = output_dir / item
        if src.is_dir():
            def ignore(dirpath: str, names: list[str]) -> set[str]:
                ignored: set[str] = set()
                for name in names:
                    candidate = Path(dirpath) / name
                    rel_path = candidate.relative_to(repo).as_posix()
                    if matches_any(rel_path, forbidden_patterns):
                        ignored.add(name)
                return ignored

            shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def scan_file(path: Path) -> dict[str, list[str]]:
    warnings: dict[str, list[str]] = {
        "env_and_network": [],
        "file_and_network": [],
        "secret_paths": [],
        "version_consts": [],
    }
    if not is_text_candidate(path):
        return warnings
    if path.name == "release_guard.py":
        return warnings

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return warnings

    if is_code_candidate(path):
        has_env = any(re.search(pattern, content) for pattern in ENV_PATTERNS)
        has_network = any(re.search(pattern, content) for pattern in NETWORK_PATTERNS)
        has_file = any(re.search(pattern, content) for pattern in FILE_PATTERNS)

        if has_env and has_network:
            warnings["env_and_network"].append(path.as_posix())
        if has_file and has_network:
            warnings["file_and_network"].append(path.as_posix())
        if any(re.search(pattern, content) for pattern in SECRET_PATH_PATTERNS):
            warnings["secret_paths"].append(path.as_posix())

    if is_doc_candidate(path):
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if not any(re.search(pattern, line) for pattern in SECRET_PATH_PATTERNS):
                continue
            context = " ".join(lines[max(0, idx - 3): min(len(lines), idx + 4)]).lower()
            has_safe_context = any(re.search(pattern, context) for pattern in SAFE_DOC_CONTEXT_PATTERNS)
            has_unsafe_context = any(re.search(pattern, context) for pattern in UNSAFE_DOC_CONTEXT_PATTERNS)
            if has_unsafe_context and not has_safe_context:
                warnings["secret_paths"].append(path.as_posix())
                break

    for pattern in VERSION_CONST_PATTERNS:
        for match in pattern.finditer(content):
            warnings["version_consts"].append(f"{path.as_posix()} -> {match.group(1)}")

    return warnings


def collect_versions(repo: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    for rel_path in ["package.json", "skill.json", "openclaw.plugin.json"]:
        path = repo / rel_path
        if not path.exists():
            continue
        try:
            data = load_json(path)
        except Exception:
            continue
        version = data.get("version")
        if isinstance(version, str):
            versions[rel_path] = version
    return versions


def main() -> int:
    parser = argparse.ArgumentParser(description="Release guard for npm/ClawHub publishing")
    parser.add_argument("repo", nargs="?", default=".", help="repository path")
    parser.add_argument("--config", default="config/publish.accounts.local.json", help="local config path")
    parser.add_argument("--prepare-release-dir", help="optional sanitized release dir output path")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    config_path = repo / args.config
    failures: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []

    if not config_path.exists():
        failures.append(f"missing local config: {config_path}")
        config = {}
    else:
        try:
            config = load_json(config_path)
            passes.append(f"loaded local config: {relative(config_path, repo)}")
        except Exception as exc:
            failures.append(f"failed to parse local config: {exc}")
            config = {}

    tracked = tracked_files(repo)
    config_rel = relative(config_path, repo) if config_path.exists() else args.config
    if config_rel in tracked:
        failures.append(f"local config is tracked by git: {config_rel}")
    elif config_path.exists() and is_git_ignored(repo, config_rel):
        passes.append(f"local config is gitignored: {config_rel}")
    elif config_path.exists():
        failures.append(f"local config is not gitignored: {config_rel}")

    versions = collect_versions(repo)
    if versions:
        unique_versions = set(versions.values())
        if len(unique_versions) == 1:
            passes.append(f"manifest versions aligned: {next(iter(unique_versions))}")
        else:
            failures.append(f"manifest versions mismatch: {versions}")
    else:
        warnings.append("no manifest version files found")

    publish_cfg = config.get("publish", {})
    forbidden_patterns = list(dict.fromkeys(FORBIDDEN_DEFAULTS + publish_cfg.get("forbidden_patterns", [])))

    repo_files = iter_files(repo)
    forbidden_hits = [
        relative(path, repo)
        for path in repo_files
        if matches_any(relative(path, repo), forbidden_patterns) and relative(path, repo) != config_rel
    ]
    if forbidden_hits:
        warnings.append(f"forbidden-pattern files present in repo root: {', '.join(forbidden_hits[:12])}")
    else:
        passes.append("no forbidden-pattern files found in tracked workspace")

    env_network_hits: list[str] = []
    file_network_hits: list[str] = []
    secret_path_hits: list[str] = []
    version_const_hits: list[str] = []

    for path in repo_files:
        found = scan_file(path)
        env_network_hits.extend(found["env_and_network"])
        file_network_hits.extend(found["file_and_network"])
        secret_path_hits.extend(found["secret_paths"])
        version_const_hits.extend(found["version_consts"])

    if env_network_hits:
        failures.append("same-file env read + network send hits: " + ", ".join(sorted(set(relative(Path(p), repo) for p in env_network_hits))))
    else:
        passes.append("no same-file env read + network send hits")

    if file_network_hits:
        failures.append("same-file file read + network send hits: " + ", ".join(sorted(set(relative(Path(p), repo) for p in file_network_hits))))
    else:
        passes.append("no same-file file read + network send hits")

    if secret_path_hits:
        failures.append("references to secrets/config files found without safe context: " + ", ".join(sorted(set(relative(Path(p), repo) for p in secret_path_hits))))
    else:
        passes.append("no secrets.json/config.json references found")

    if version_const_hits and versions:
        manifest_version = next(iter(set(versions.values()))) if len(set(versions.values())) == 1 else None
        mismatched = [item for item in version_const_hits if manifest_version and not item.endswith(f"-> {manifest_version}")]
        if mismatched:
            failures.append("code version constants mismatch manifest: " + ", ".join(mismatched))
        else:
            passes.append("code version constants match manifest")

    include_paths = publish_cfg.get("include_paths", [])
    if args.prepare_release_dir:
        if not include_paths:
            failures.append("publish.include_paths missing in local config, cannot prepare release dir safely")
        else:
            output_dir = Path(args.prepare_release_dir).resolve()
            copy_selected(repo, include_paths, output_dir, forbidden_patterns)
            output_files = [relative(path, output_dir) for path in iter_files(output_dir)]
            bad_output = [path for path in output_files if matches_any(path, forbidden_patterns)]
            if bad_output:
                failures.append(f"forbidden files copied into release dir: {', '.join(bad_output)}")
            else:
                passes.append(f"prepared sanitized release dir: {output_dir}")

    print("== PASS ==")
    for item in passes:
        print(f"- {item}")
    print("\n== WARN ==")
    for item in warnings or ["-"]:
        print(f"- {item}" if item != "-" else item)
    print("\n== FAIL ==")
    for item in failures or ["-"]:
        print(f"- {item}" if item != "-" else item)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
