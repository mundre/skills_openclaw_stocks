#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIDSO GEO 品牌诊断轮询脚本

用途：
- 轮询品牌诊断结果
- 下载诊断报告文件
- 若结果为 Markdown，则转成 PDF
- 以 OpenClaw 常见输出格式返回结果：
  - 成功文件：stdout 输出 `MEDIA:/path/to/file`
  - 文字结果：stdout 输出普通文本

用法：
    python diagnosis_poll.py "露露"
    python diagnosis_poll.py "露露" --api-key your_key
    python diagnosis_poll.py "露露" --interval 60 --max-attempts 30

环境变量：
    AIDSO_GEO_API_KEY   可选，若未传 --api-key，则从环境变量读取
"""

import sys
import os
import json
import time
import uuid
import mimetypes
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
import markdown
from weasyprint import HTML


API_URL = "https://api.aidso.com/openapi/skills/band_report/md"
API_KEY_URL = "https://geo.aidso.com/setting?type=apiKey&platform=GEO"
COMPLETE_ANALYSIS_URL = "https://geo.aidso.com/completeAnalysis"
PURCHASE_POINTS_URL = "https://geo.aidso.com"

DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_MAX_ATTEMPTS = 30

PDF_CSS = """
body {
  font-family: Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  line-height: 1.7;
  color: #222;
  padding: 24px;
}
h1, h2, h3, h4 {
  color: #111;
  margin-top: 20px;
  margin-bottom: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px 0;
  font-size: 11px;
}
th, td {
  border: 1px solid #d9d9d9;
  padding: 8px 10px;
  vertical-align: top;
  text-align: left;
}
th {
  background: #f5f5f5;
}
code {
  background: #f6f8fa;
  padding: 2px 4px;
  border-radius: 4px;
}
pre {
  background: #f6f8fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}
blockquote {
  border-left: 4px solid #ddd;
  margin: 12px 0;
  padding: 8px 12px;
  color: #555;
  background: #fafafa;
}
"""


def out_text(msg: str) -> None:
    print(msg, flush=True)


def out_media(path: str) -> None:
    print(f"MEDIA:{path}", flush=True)
    sys.exit(0)


def out_debug(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def build_auth_headers(api_key: str) -> dict:
    return {"x-api-key": api_key}


def normalize_code(code):
    if code is None:
        return None
    try:
        return int(code)
    except Exception:
        return code


def get_backend_msg(data: dict) -> str:
    if not isinstance(data, dict):
        return ""
    msg = data.get("msg")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    message = data.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return ""


def format_backend_error_message(msg: str) -> str:
    if not msg:
        return "接口返回错误"
    if "积分不足" in msg:
        return f"{msg}\n请前往{PURCHASE_POINTS_URL} 购买积分"
    return msg


def is_invalid_token_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return code == 401 or "invalid token" in msg or "鉴权失败" in msg


def is_processing_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return code == 200 and (
        "处理中" in msg or
        "processing" in msg or
        "请稍后" in msg
    )


def is_success_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    return code in (None, 0, 200, "0", "200")


def raise_backend_error_if_any(data: dict) -> None:
    if not isinstance(data, dict):
        return
    if is_invalid_token_response(data) or is_processing_response(data) or is_success_response(data):
        return
    msg = get_backend_msg(data)
    if msg:
        raise ValueError(format_backend_error_message(msg))
    raise ValueError(f"API 返回错误：{json.dumps(data, ensure_ascii=False)}")


def parse_json_utf8(resp: requests.Response) -> dict:
    raw = resp.content
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        pass
    try:
        return resp.json()
    except Exception:
        pass
    return json.loads(resp.text)


def safe_report_filename(ext: str) -> str:
    if not ext:
        ext = ".dat"
    if not ext.startswith("."):
        ext = "." + ext
    return f"geo_report_{uuid.uuid4().hex}{ext}"


def save_bytes_to_temp(content: bytes, filename: str) -> str:
    out_path = Path("/tmp") / filename
    out_path.write_bytes(content)
    return str(out_path)


def guess_ext_from_content_type(content_type: str) -> str:
    content_type = (content_type or "").split(";")[0].strip().lower()
    mapping = {
        "application/pdf": ".pdf",
        "text/markdown": ".md",
        "text/plain": ".txt",
        "application/json": ".json",
        "text/html": ".html",
        "application/octet-stream": ".bin",
    }
    if content_type in mapping:
        return mapping[content_type]
    return mimetypes.guess_extension(content_type) or ""


def infer_ext_from_url(url: str) -> str:
    try:
        path = unquote(urlparse(url).path)
        suffix = Path(path).suffix
        return suffix.lower() if suffix else ""
    except Exception:
        return ""


def looks_like_md_link(url: str) -> bool:
    return infer_ext_from_url(url) == ".md"


def looks_like_pdf_link(url: str) -> bool:
    return infer_ext_from_url(url) == ".pdf"


def extract_file_url_from_json(data: dict):
    if not isinstance(data, dict):
        return None

    data_field = data.get("data")
    if isinstance(data_field, str):
        value = data_field.strip()
        if value.startswith("http://") or value.startswith("https://"):
            return value

    if isinstance(data_field, dict):
        for key in ("url", "fileUrl", "downloadUrl", "mdUrl", "pdfUrl", "reportUrl"):
            v = data_field.get(key)
            if isinstance(v, str):
                value = v.strip()
                if value.startswith("http://") or value.startswith("https://"):
                    return value

    return None


def fetch_url_response(url: str, auth_headers: dict | None = None) -> requests.Response:
    attempts = []
    if auth_headers:
        attempts.append(auth_headers)
    attempts.append({})

    last_error = None
    for headers in attempts:
        try:
            resp = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
            if resp.status_code == 200:
                return resp
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = str(e)

    raise ValueError(f"获取文件失败：{last_error or '未知错误'}")


def assert_not_invalid_file_response(resp: requests.Response) -> None:
    content_type = (resp.headers.get("Content-Type") or "").lower()
    text_sample = ""
    if "text" in content_type or "json" in content_type or "xml" in content_type:
        try:
            text_sample = resp.text[:1000]
        except Exception:
            text_sample = ""

    invalid_markers = [
        "NoSuchKey",
        "The specified key does not exist",
        '"Code":"NoSuchKey"',
        "'Code': 'NoSuchKey'",
    ]
    if any(marker in text_sample for marker in invalid_markers):
        raise ValueError("下载报告文件失败：NoSuchKey")


def download_remote_file(url: str, auth_headers: dict | None = None) -> str:
    resp = fetch_url_response(url, auth_headers=auth_headers)
    assert_not_invalid_file_response(resp)

    ext = guess_ext_from_content_type(resp.headers.get("Content-Type") or "") or infer_ext_from_url(url) or ".dat"
    filename = safe_report_filename(ext)
    local_path = save_bytes_to_temp(resp.content, filename)
    out_debug(f"[DEBUG] downloaded file path={local_path}")
    return local_path


def fetch_markdown_text(url: str, auth_headers: dict | None = None) -> str:
    resp = fetch_url_response(url, auth_headers=auth_headers)
    assert_not_invalid_file_response(resp)

    text = resp.text.strip()
    if not text:
        raise ValueError("md 文件内容为空")
    return text


def render_markdown_to_pdf(md_text: str) -> str:
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>GEO诊断报告</title>
<style>{PDF_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    out_path = str(Path("/tmp") / safe_report_filename(".pdf"))
    HTML(string=html).write_pdf(out_path)
    out_debug(f"[DEBUG] rendered pdf path={out_path}")
    return out_path


def request_report(brand: str, api_key: str) -> dict:
    resp = requests.get(
        API_URL,
        params={"brandName": brand},
        headers=build_auth_headers(api_key),
        timeout=180,
    )
    resp.raise_for_status()

    content_type = (resp.headers.get("Content-Type") or "").lower()
    if "application/json" not in content_type:
        return {
            "kind": "raw",
            "content_type": content_type,
            "bytes": resp.content,
        }

    return {
        "kind": "json",
        "data": parse_json_utf8(resp),
    }


def build_success_file(payload: dict, api_key: str) -> str:
    headers = build_auth_headers(api_key)

    if payload.get("kind") == "raw":
        ext = guess_ext_from_content_type(payload.get("content_type") or "") or ".dat"
        return save_bytes_to_temp(payload["bytes"], safe_report_filename(ext))

    data = payload["data"]
    file_url = extract_file_url_from_json(data)
    if not file_url:
        backend_msg = get_backend_msg(data)
        if backend_msg:
            raise ValueError(format_backend_error_message(backend_msg))
        raise ValueError(f"接口未返回有效文件链接：{json.dumps(data, ensure_ascii=False)}")

    if looks_like_pdf_link(file_url):
        return download_remote_file(file_url, auth_headers=headers)

    if looks_like_md_link(file_url):
        md_text = fetch_markdown_text(file_url, auth_headers=headers)
        return render_markdown_to_pdf(md_text)

    remote_resp = fetch_url_response(file_url, auth_headers=headers)
    assert_not_invalid_file_response(remote_resp)

    remote_ct = (remote_resp.headers.get("Content-Type") or "").lower()
    if "markdown" in remote_ct or "text/plain" in remote_ct or infer_ext_from_url(file_url) == ".md":
        md_text = remote_resp.text.strip()
        if not md_text:
            raise ValueError("md 文件内容为空")
        return render_markdown_to_pdf(md_text)

    ext = guess_ext_from_content_type(remote_ct) or infer_ext_from_url(file_url) or ".dat"
    return save_bytes_to_temp(remote_resp.content, safe_report_filename(ext))


def poll_report(brand: str, api_key: str, interval_seconds: int, max_attempts: int):
    for attempt in range(1, max_attempts + 1):
        out_debug(f"[DEBUG] polling attempt={attempt}/{max_attempts}, brand={brand}")

        result = request_report(brand, api_key)

        if result["kind"] == "json":
            data = result["data"]

            if is_invalid_token_response(data):
                return (
                    "text",
                    f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                    f"获取地址：{API_KEY_URL}"
                )

            if is_processing_response(data):
                if attempt < max_attempts:
                    time.sleep(interval_seconds)
                    continue
                return (
                    "text",
                    "诊断结果暂未生成完成，请稍后重试。\n\n"
                    f"也可以前往官网查看：{COMPLETE_ANALYSIS_URL}"
                )

            raise_backend_error_if_any(data)

        # raw file or json with valid file url
        local_file = build_success_file(result, api_key)
        return ("media", local_file)

    return (
        "text",
        "诊断结果暂未生成完成，请稍后重试。\n\n"
        f"也可以前往官网查看：{COMPLETE_ANALYSIS_URL}"
    )


def parse_args(argv: list[str]) -> tuple[str, str, int, int]:
    if len(argv) < 2:
        raise ValueError(
            "用法：python diagnosis_poll.py <brandName> [--api-key KEY] [--interval 60] [--max-attempts 30]"
        )

    brand = argv[1].strip()
    if not brand:
        raise ValueError("brandName 不能为空")

    api_key = None
    interval_seconds = DEFAULT_INTERVAL_SECONDS
    max_attempts = DEFAULT_MAX_ATTEMPTS

    i = 2
    while i < len(argv):
        token = argv[i]
        if token == "--api-key":
            i += 1
            if i >= len(argv):
                raise ValueError("--api-key 缺少参数")
            api_key = argv[i].strip()
        elif token == "--interval":
            i += 1
            if i >= len(argv):
                raise ValueError("--interval 缺少参数")
            interval_seconds = int(argv[i])
        elif token == "--max-attempts":
            i += 1
            if i >= len(argv):
                raise ValueError("--max-attempts 缺少参数")
            max_attempts = int(argv[i])
        else:
            raise ValueError(f"无法识别的参数：{token}")
        i += 1

    if not api_key:
        api_key = os.environ.get("AIDSO_GEO_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            f"未检测到 API key，请通过 --api-key 传入，或设置环境变量 AIDSO_GEO_API_KEY。\n"
            f"获取地址：{API_KEY_URL}"
        )

    if interval_seconds <= 0:
        raise ValueError("--interval 必须大于 0")
    if max_attempts <= 0:
        raise ValueError("--max-attempts 必须大于 0")

    return brand, api_key, interval_seconds, max_attempts


def main():
    try:
        brand, api_key, interval_seconds, max_attempts = parse_args(sys.argv)
        kind, payload = poll_report(brand, api_key, interval_seconds, max_attempts)

        if kind == "media":
            out_media(payload)
        else:
            out_text(payload)

    except ValueError as e:
        out_text(str(e))
        sys.exit(0)
    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            out_text(
                f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                f"获取地址：{API_KEY_URL}"
            )
            sys.exit(0)

        out_text(f"请求失败：HTTP {status or '未知状态码'}")
        sys.exit(0)
    except Exception as e:
        out_debug(f"[ERROR] diagnosis_poll failed: {e}")
        out_text(f"诊断处理失败：{e}")
        sys.exit(0)


if __name__ == "__main__":
    main()