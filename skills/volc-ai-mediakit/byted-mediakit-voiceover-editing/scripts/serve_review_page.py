#!/usr/bin/env python3
"""
审核页静态服务：托管 templates/review-page/，提供 GET /api/review-data 返回 review_import_data.json，
POST /export 代理到导出服务（避免 501）。
是否自动打开浏览器由环境变量 TALKING_VIDEO_AUTO_EDIT_REVIEW_AUTO_OPEN 决定：默认不打开；1/true/yes 时打开。
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import threading
import urllib.request
import urllib.error
from urllib.parse import urlparse
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 加载 skill .env（override=True 确保 .env 覆盖 shell 已有变量）
try:
    from dotenv import load_dotenv
    skill_dir = Path(__file__).resolve().parents[1]
    env_path = skill_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass


def _should_auto_open_browser() -> bool:
    """默认不打开；仅当 TALKING_VIDEO_AUTO_EDIT_REVIEW_AUTO_OPEN=1/true/yes 时打开"""
    v = (os.getenv("TALKING_VIDEO_AUTO_EDIT_REVIEW_AUTO_OPEN") or "").strip().lower()
    return v in ("1", "true", "yes")


def _project_root() -> Path:
    # 工程根：与 SKILL_DIR 之间固定相隔两级父目录（<工程根>/<任意>/<任意>/<SKILL_DIR名>/）。
    skill_root = Path(__file__).resolve().parents[1]
    try:
        return skill_root.parents[2]
    except IndexError:
        return skill_root.parent


def _output_dir(output_dir_override: str = "") -> Path:
    if not output_dir_override:
        return _project_root() / "output"

    out_str = str(output_dir_override).strip()
    proj_root = _project_root()
    out_base = (proj_root / "output").resolve()

    cand = Path(out_str)
    if cand.is_absolute():
        resolved = cand.resolve()
        try:
            resolved.relative_to(out_base)
        except ValueError:
            raise SystemExit(f"ERROR: --output-dir 必须在 {out_base} 下：{resolved}")
        return resolved

    # 约束：只允许 output/<文件名>（相对路径）
    if not out_str.startswith("output/"):
        raise SystemExit("ERROR: --output-dir 只允许传 `output/<文件名>`（相对路径）")

    resolved = (proj_root / out_str).resolve()
    try:
        resolved.relative_to(out_base)
    except ValueError:
        raise SystemExit(f"ERROR: --output-dir 路径越界：{out_str}")
    return resolved


def _review_data_path(output_dir_override: str = "") -> Path:
    return _output_dir(output_dir_override) / "review_import_data.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="审核页静态服务")
    parser.add_argument("--port", type=int, default=5173, help="端口，默认 5173")
    parser.add_argument("--host", default="127.0.0.1", help="主机，默认 127.0.0.1")
    parser.add_argument("--output-dir", default="", help="输出目录，默认 output；可指定 output/<文件名>")
    parser.add_argument(
        "--export-server",
        default="http://127.0.0.1:7860",
        help="导出服务地址，POST /export 将代理到此地址",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="不自动打开浏览器（覆盖环境变量 TALKING_VIDEO_AUTO_EDIT_REVIEW_AUTO_OPEN）",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    template_dir = skill_dir / "templates" / "review-page"
    if not template_dir.exists():
        raise FileNotFoundError(f"审核页目录不存在: {template_dir}")

    export_server_url = args.export_server.rstrip("/")

    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(template_dir), **kwargs)

        @staticmethod
        def _request_path(path: str) -> str:
            """self.path 可能带查询串或片段，仅取 path 段做路由。"""
            p = urlparse(path).path or "/"
            if len(p) > 1 and p.endswith("/"):
                p = p.rstrip("/")
            return p

        def do_OPTIONS(self):
            req_path = self._request_path(self.path)
            if req_path == "/export":
                self._proxy_export("OPTIONS")
                return
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.end_headers()

        def do_GET(self):
            req_path = self._request_path(self.path)
            if req_path == "/api/review-data":
                self._serve_review_data()
                return
            if req_path == "/export":
                self._send_json(200, {
                    "ok": True,
                    "message": "导出接口需使用 POST 提交。请在审核页点击「提交视频导出任务」按钮。",
                })
                return
            super().do_GET()

        def do_POST(self):
            if self._request_path(self.path) == "/export":
                self._proxy_export("POST")
                return
            self.send_error(501, "Unsupported method (%r)" % self.command)

        def _proxy_export(self, method: str):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            req = urllib.request.Request(
                f"{export_server_url}/export",
                data=body,
                method=method,
                headers={"Content-Type": self.headers.get("Content-Type", "application/json")},
            )
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        if k.lower() not in ("transfer-encoding",):
                            self.send_header(k, v)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(e.read() if e.fp else b"{}")
            except Exception as e:
                self.send_error(502, f"导出服务不可用: {e}")

        def _send_json(self, status: int, data: dict):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_review_data(self):
            path = _review_data_path(args.output_dir)
            if not path.exists():
                self.send_error(404, "review_import_data.json 未生成，请先运行 prepare_export_data.py")
                return
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_error(500, str(e))

        def log_message(self, format, *args):
            print(f"[serve] {args[0]}")

    port = args.port
    for attempt in range(20):
        try:
            server = HTTPServer((args.host, port), CustomHandler)
            break
        except OSError as e:
            if getattr(e, "errno", None) == errno.EADDRINUSE or "Address already in use" in str(e):
                port = args.port + attempt + 1
                if attempt < 19:
                    continue
            raise
    url = f"http://{args.host}:{port}"
    if port != args.port:
        print(f"[提示] 端口 {args.port} 已被占用，已使用 {port}")
    print(f"审核页服务已启动: {url}")
    print(f"  - 审核页: {url}/")
    print(f"  - 数据 API: {url}/api/review-data")
    print(f"  - 导出代理: {url}/export -> {export_server_url}/export")

    if not args.no_open and _should_auto_open_browser():
        def _open_later():
            import time
            time.sleep(1.2)
            webbrowser.open(url)
            print("[提示] 已自动打开审核页")
        threading.Thread(target=_open_later, daemon=True).start()
    else:
        print("[提示] 未自动打开（TALKING_VIDEO_AUTO_EDIT_REVIEW_AUTO_OPEN=0 或 --no-open），请手动访问上述 URL")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
