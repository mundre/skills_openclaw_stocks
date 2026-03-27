#!/usr/bin/env python3
"""
导出服务：接收审核页 POST，将 sentences + baseTrack + mergedTrack 转为服务端格式，
写入 output/export_submit_<ts>.json，并调用 vod_direct_export.py 提交视频导出任务。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from apply_review_to_export import apply_review_to_export


def _project_root() -> Path:
    # 工程根：与 SKILL_DIR 之间固定相隔两级父目录（<工程根>/<任意>/<任意>/<SKILL_DIR名>/）。
    skill_root = Path(__file__).resolve().parents[1]
    try:
        return skill_root.parents[2]
    except IndexError:
        return skill_root.parent


_EXPORT_OUTPUT_DIR: Path | None = None


def _output_dir() -> Path:
    if _EXPORT_OUTPUT_DIR is not None:
        _EXPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return _EXPORT_OUTPUT_DIR
    out = _project_root() / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


class ExportHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/export", "/", "/health"):
            self._send_json(200, {
                "ok": True,
                "message": "导出服务运行中，请使用 POST /export 提交导出任务",
            })
            return
        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/export" and parsed.path != "/":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self.send_error(400, "Empty body")
            return

        body_bytes = self.rfile.read(content_length)
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        try:
            export_req = apply_review_to_export(body)
            ts = int(time.time() * 1000)
            out_path = _output_dir() / f"export_submit_{ts}.json"
            _output_dir().mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(export_req, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            # 调用 vod_direct_export.py 提交视频导出任务（--output-dir 须在 submit 之前，为主解析器参数）
            script_dir = Path(__file__).resolve().parent
            cmd = [sys.executable, str(script_dir / "vod_direct_export.py")]
            if _EXPORT_OUTPUT_DIR is not None:
                cmd.extend(["--output-dir", str(_EXPORT_OUTPUT_DIR)])
            cmd.extend([
                "submit",
                "--edit-param", str(out_path),
                "--wait",
                "--json-output",
            ])
            proc = subprocess.run(
                cmd,
                cwd=script_dir,
                capture_output=True,
                text=True,
                timeout=35 * 60,
            )
            if proc.returncode != 0:
                err = proc.stderr or proc.stdout or "未知错误"
                self._send_json(500, {"error": f"vod_direct_export 失败: {err[:500]}"})
                return
            try:
                lines = [l.strip() for l in proc.stdout.strip().split("\n") if l.strip()]
                for line in reversed(lines):
                    if line.startswith("{"):
                        result = json.loads(line)
                        break
                else:
                    result = {"message": "任务已提交", "path": str(out_path)}
            except (json.JSONDecodeError, IndexError):
                result = {"message": "任务已提交", "path": str(out_path), "stdout": proc.stdout[:500]}
            self._send_json(200, result)
        except subprocess.TimeoutExpired:
            self._send_json(500, {"error": "导出任务超时（35分钟）"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[export] {args[0]}")


def main() -> None:
    global _EXPORT_OUTPUT_DIR
    parser = argparse.ArgumentParser(description="导出服务：接收审核页 POST，写入 export_submit_*.json")
    parser.add_argument("--port", type=int, default=7860, help="端口，默认 7860")
    parser.add_argument("--host", default="127.0.0.1", help="主机，默认 127.0.0.1")
    parser.add_argument("--output-dir", default="", help="输出目录，默认 output；可指定 output/<文件名>")
    args = parser.parse_args()

    if args.output_dir:
        out_str = str(args.output_dir).strip()
        proj_root = _project_root()
        out_base = (proj_root / "output").resolve()
        cand = Path(out_str)
        if cand.is_absolute():
            resolved = cand.resolve()
            try:
                resolved.relative_to(out_base)
            except ValueError:
                raise SystemExit(f"ERROR: --output-dir 必须在 {out_base} 下：{resolved}")
            _EXPORT_OUTPUT_DIR = resolved
        else:
            if not out_str.startswith("output/"):
                raise SystemExit("ERROR: --output-dir 只允许传 `output/<文件名>`（相对路径）")
            resolved = (proj_root / out_str).resolve()
            try:
                resolved.relative_to(out_base)
            except ValueError:
                raise SystemExit(f"ERROR: --output-dir 路径越界：{out_str}")
            _EXPORT_OUTPUT_DIR = resolved
        _EXPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    else:
        _EXPORT_OUTPUT_DIR = None

    server = HTTPServer((args.host, args.port), ExportHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"导出服务已启动: {url}/export")
    out_hint = str(_output_dir()) if _EXPORT_OUTPUT_DIR else "output"
    print(f"审核页点击「提交视频导出任务」后，将保存数据并调用 vod_direct_export 导出视频")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
