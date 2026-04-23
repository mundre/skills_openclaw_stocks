"""把 Mermaid / PlantUML / DOT 代码渲染成 SVG / PNG / PDF。

后端探测顺序（每种 DSL 各自的）：
- Mermaid：`mmdc`（npm @mermaid-js/mermaid-cli） → npx → docker ghcr.io/mermaid-js/mermaid-cli
- PlantUML：`plantuml` → java -jar plantuml.jar → docker plantuml/plantuml
- Graphviz：`dot`

如果所有后端都不可用，会把源码写到 `.mmd/.puml/.dot` 文件里并抛出 RuntimeError，
让用户自己渲染（比如复制到 https://mermaid.live）。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


SUPPORTED_EXTS = {".svg", ".png", ".pdf", ".mmd", ".puml", ".dot", ".md", ".markdown"}


def render(source: str, output_path: str, engine: str = "mermaid",
           width: Optional[int] = None, height: Optional[int] = None,
           background: Optional[str] = None) -> str:
    """核心渲染函数。返回最终产物路径。"""
    out = Path(output_path)
    ext = out.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"不支持的扩展名 {ext}；可选 {sorted(SUPPORTED_EXTS)}")

    out.parent.mkdir(parents=True, exist_ok=True)

    # 仅导出源码
    if ext in (".mmd", ".md", ".markdown"):
        out.write_text(source, encoding="utf-8")
        return str(out)
    if ext == ".puml":
        out.write_text(source, encoding="utf-8")
        return str(out)
    if ext == ".dot":
        out.write_text(source, encoding="utf-8")
        return str(out)

    if engine == "mermaid":
        return _render_mermaid(source, out, width=width, height=height, background=background)
    if engine == "plantuml":
        return _render_plantuml(source, out)
    if engine == "dot":
        return _render_dot(source, out)
    raise ValueError(f"未知 engine：{engine}")


# ----- Mermaid -----


def _find_mmdc() -> Optional[list]:
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        return ["npx", "-y", "@mermaid-js/mermaid-cli"]
    if shutil.which("docker"):
        return [
            "docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{os.getcwd()}:/data",
            "minlag/mermaid-cli", "-"
        ]
    return None


def _render_mermaid(source: str, out: Path, *, width=None, height=None,
                    background=None) -> str:
    cmd_base = _find_mmdc()
    if not cmd_base:
        # 没有 mmdc，把 .mmd 导出
        fallback = out.with_suffix(".mmd")
        fallback.write_text(source, encoding="utf-8")
        raise RuntimeError(
            f"未找到 mmdc / npx / docker，已把 Mermaid 源码保存到 {fallback}。"
            "\n安装任选其一："
            "\n  npm i -g @mermaid-js/mermaid-cli      # 推荐"
            "\n  或用在线编辑器：https://mermaid.live"
        )

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "source.mmd"
        src.write_text(source, encoding="utf-8")
        cmd = list(cmd_base) + ["-i", str(src), "-o", str(out)]
        if width:
            cmd += ["-w", str(width)]
        if height:
            cmd += ["-H", str(height)]
        if background:
            cmd += ["-b", background]
        # 设置 puppeteer 的 no-sandbox 配置（常见 Linux CI 报错）
        pup_cfg = Path(td) / "puppeteer.json"
        pup_cfg.write_text(json.dumps({"args": ["--no-sandbox", "--disable-setuid-sandbox"]}))
        cmd += ["-p", str(pup_cfg)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"mmdc 渲染失败：\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            ) from e
    return str(out)


# ----- PlantUML -----


def _find_plantuml() -> Optional[list]:
    if shutil.which("plantuml"):
        return ["plantuml"]
    # 常见 jar 路径
    for candidate in [
        "/opt/homebrew/opt/plantuml/libexec/plantuml.jar",
        "/usr/local/opt/plantuml/libexec/plantuml.jar",
        "/usr/share/plantuml/plantuml.jar",
    ]:
        if os.path.isfile(candidate) and shutil.which("java"):
            return ["java", "-jar", candidate]
    if shutil.which("docker"):
        return ["docker", "run", "--rm", "-i", "plantuml/plantuml", "-pipe"]
    return None


def _render_plantuml(source: str, out: Path) -> str:
    cmd = _find_plantuml()
    if not cmd:
        fallback = out.with_suffix(".puml")
        fallback.write_text(source, encoding="utf-8")
        raise RuntimeError(
            f"未找到 plantuml / java / docker，已把 PlantUML 源码保存到 {fallback}。"
            "\n安装："
            "\n  brew install plantuml     (macOS)"
            "\n  apt install plantuml      (Ubuntu/Debian)"
        )

    ext = out.suffix.lower()
    fmt = {".svg": "-tsvg", ".png": "-tpng", ".pdf": "-tpdf"}[ext]
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "source.puml"
        src.write_text(source, encoding="utf-8")
        full_cmd = list(cmd) + [fmt, "-o", str(out.parent.absolute()), str(src)]
        try:
            subprocess.run(full_cmd, check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # 保底：把源码落盘，调用方可以复制到在线编辑器
            fallback = out.with_suffix(".puml")
            fallback.write_text(source, encoding="utf-8")
            stdout = getattr(e, "stdout", "") or ""
            stderr = getattr(e, "stderr", "") or ""
            raise RuntimeError(
                f"plantuml 渲染失败（可能是 docker 镜像未拉 / daemon 未启动）。"
                f"已把 PlantUML 源码落到 {fallback}。"
                f"\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            ) from e
    # plantuml 会输出 source.{fmt}，我们移到指定 out
    produced = Path(out.parent) / src.name.replace(".puml", ext)
    if produced.exists() and produced != out:
        produced.rename(out)
    return str(out)


# ----- Graphviz -----


def _render_dot(source: str, out: Path) -> str:
    if not shutil.which("dot"):
        fallback = out.with_suffix(".dot")
        fallback.write_text(source, encoding="utf-8")
        raise RuntimeError(
            f"未找到 dot (Graphviz)，已把 DOT 源码保存到 {fallback}。"
            "\n安装： brew install graphviz"
        )
    ext = out.suffix.lower()
    fmt = {".svg": "svg", ".png": "png", ".pdf": "pdf"}[ext]
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "source.dot"
        src.write_text(source, encoding="utf-8")
        cmd = ["dot", f"-T{fmt}", str(src), "-o", str(out)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"dot 渲染失败：\nSTDERR: {e.stderr}"
            ) from e
    return str(out)
