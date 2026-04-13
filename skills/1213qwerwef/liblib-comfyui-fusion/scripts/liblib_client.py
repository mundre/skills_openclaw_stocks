#!/usr/bin/env python3
"""LiblibAI ComfyUI app client for product background fusion generation."""

import argparse
import base64
import hmac
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE_URL = "https://openapi.liblibai.cloud"
SUBMIT_URI = "/api/generate/comfyui/app"
STATUS_URI = "/api/generate/comfy/status"

# Template/workflow defaults (replace with your own IDs if needed)
DEFAULT_TEMPLATE_UUID = "YOUR_TEMPLATE_UUID"
DEFAULT_WORKFLOW_UUID = "YOUR_WORKFLOW_UUID"
DEFAULT_LORA_NAME = "YOUR_LORA_NAME"

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None


# -----------------------------
# R2 configuration defaults
# -----------------------------
# Note: These defaults can be overridden by env vars.
R2_ENDPOINT_DEFAULT = "https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com/YOUR_BUCKET"
R2_ACCESS_KEY_DEFAULT = "YOUR_R2_ACCESS_KEY"
R2_SECRET_KEY_DEFAULT = "YOUR_R2_SECRET_KEY"
R2_BUCKET_DEFAULT = "your-r2-bucket-name"
PUBLIC_URL_BASE_DEFAULT = "https://your-public-domain.example.com"


def workspace_root() -> Path:
    """.../workspace (parent of skills/)."""
    return Path(__file__).resolve().parent.parent.parent.parent


def default_output_dir() -> Path:
    return workspace_root() / "outputs" / "images"


def make_sign(uri_path: str, secret_key: str) -> dict:
    """Generate auth query params according to Liblib 2.4.2 signature spec."""
    timestamp = str(int(time.time() * 1000))
    signature_nonce = uuid.uuid4().hex
    content = "&".join((uri_path, timestamp, signature_nonce))
    digest = hmac.new(secret_key.encode(), content.encode(), sha1).digest()
    signature = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return {
        "Signature": signature,
        "Timestamp": timestamp,
        "SignatureNonce": signature_nonce,
    }


def extract_first_url(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"https?://[^\s\"']+", text)
    return m.group(0) if m else ""


def file_to_data_uri(path: Path) -> str:
    """Encode local file as data URI (for APIs that accept reference images this way)."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Local image not found: {path}")
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png"
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def r2_upload_local_image(
    local_path: Path,
    *,
    r2_endpoint: str,
    r2_access_key: str,
    r2_secret_key: str,
    bucket_name: str,
    public_url_base: str,
    user_id: str,
    object_prefix: str = "image",
) -> str:
    """
    Upload a local image to Cloudflare R2 (S3-compatible) and return a public URL.
    Mirrors the flow in /Users/wzl/.openclaw/test2.py.
    """
    if boto3 is None:
        raise RuntimeError("boto3 is required for R2 upload. Install boto3 or use --local-image-mode data-uri.")

    local_path = local_path.expanduser().resolve()
    if not local_path.is_file():
        raise FileNotFoundError(f"Local image not found: {local_path}")

    ext = local_path.suffix.lower() or ".png"
    unique_id = uuid.uuid4().hex[:8]
    object_key = f"{object_prefix}/{user_id}_{unique_id}{ext}"

    s3 = boto3.client(
        "s3",
        endpoint_url=r2_endpoint,
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
    )

    s3.upload_file(str(local_path), bucket_name, object_key)
    return f"{public_url_base.rstrip('/')}/{bucket_name}/{object_key}"


def resolve_image_input(
    local_image: str,
    image_url: str,
    feishu_text: str,
    *,
    local_image_mode: str,
    r2_endpoint: str,
    r2_access_key: str,
    r2_secret_key: str,
    r2_bucket: str,
    public_url_base: str,
    r2_user_id: str,
    r2_object_prefix: str,
) -> str:
    """Resolve fusion input: local file (upload to R2 or data URI), URL, or URL extracted from Feishu text."""
    if local_image and local_image.strip():
        local_path = Path(local_image.strip())
        if local_image_mode == "data-uri":
            return file_to_data_uri(local_path)
        if local_image_mode == "r2":
            return r2_upload_local_image(
                local_path,
                r2_endpoint=r2_endpoint,
                r2_access_key=r2_access_key,
                r2_secret_key=r2_secret_key,
                bucket_name=r2_bucket,
                public_url_base=public_url_base,
                user_id=r2_user_id,
                object_prefix=r2_object_prefix,
            )
        raise ValueError(f"Unknown --local-image-mode: {local_image_mode}")
    u = (image_url or "").strip()
    if u:
        return u
    u = extract_first_url(feishu_text or "")
    if u:
        return u
    u = extract_first_url(os.environ.get("FEISHU_TEXT", ""))
    if u:
        return u
    raise ValueError(
        "No image input. Use --local-image <path>, or --image-url, or put a URL in --feishu-text / FEISHU_TEXT."
    )


def api_post(uri: str, body: dict, ak: str, sk: str) -> dict:
    sign = make_sign(uri, sk)
    params = {
        "AccessKey": ak,
        **sign,
    }
    url = f"{BASE_URL}{uri}"
    resp = requests.post(url, params=params, json=body, headers={"Content-Type": "application/json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") not in (None, 0):
        raise RuntimeError(f"API error: {data}")
    return data.get("data", data)


def submit_task(image_url: str, ak: str, sk: str, guidance: float, lora_name: str, strength_model: float) -> dict:
    body = {
        "templateUuid": DEFAULT_TEMPLATE_UUID,
        "generateParams": {
            "213": {
                "class_type": "FluxGuidance",
                "inputs": {
                    "guidance": guidance
                }
            },
            "217": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": strength_model
                }
            },
            "237": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": image_url
                }
            },
            "workflowUuid": DEFAULT_WORKFLOW_UUID
        }
    }
    return api_post(SUBMIT_URI, body, ak, sk)


def query_status(generate_uuid: str, ak: str, sk: str) -> dict:
    body = {"generateUuid": generate_uuid}
    return api_post(STATUS_URI, body, ak, sk)


def poll_result(generate_uuid: str, ak: str, sk: str, interval: int = 3, timeout: int = 300) -> dict:
    start = time.time()
    result = {}
    while time.time() - start < timeout:
        result = query_status(generate_uuid, ak, sk)
        status = result.get("generateStatus", 0)
        pct = result.get("percentCompleted", 0)
        print(f"progress={pct:.0%} status={status}", flush=True, file=sys.stderr)
        if status in (5, 6):
            return result
        time.sleep(interval)
    return result


def extract_image_urls(result: dict) -> list[str]:
    urls = []
    for img in result.get("images") or []:
        if isinstance(img, dict):
            u = img.get("imageUrl") or img.get("url")
            if u:
                urls.append(u)
        elif isinstance(img, str) and img.startswith("http"):
            urls.append(img)
    return urls


def _guess_ext_from_url(url: str) -> str:
    path = urlparse(url).path
    lower = path.lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        if lower.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".png"


def download_result_images(
    urls: list[str],
    output_dir: Path,
    basename_prefix: str,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    day_dir = output_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for i, url in enumerate(urls):
        ext = _guess_ext_from_url(url)
        name = f"{basename_prefix}-{i}{ext}" if i else f"{basename_prefix}{ext}"
        dest = day_dir / name
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        dest.write_bytes(r.content)
        saved.append(dest.resolve())
    return saved


def media_line_for_workspace(saved: Path) -> str:
    """Relative path from workspace root for OpenClaw / Feishu MEDIA convention."""
    try:
        rel = saved.resolve().relative_to(workspace_root())
    except ValueError:
        return f"MEDIA:{saved}"
    return f"MEDIA:./{rel.as_posix()}"


def main():
    parser = argparse.ArgumentParser(description="Liblib Comfy Fusion Generation")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Submit fusion generation task")
    run_p.add_argument("--image-url", default="", help="Public image URL (Liblib server must fetch it)")
    run_p.add_argument(
        "--local-image",
        default="",
        help="Local image path (e.g. Feishu attachment saved under workspace).",
    )
    run_p.add_argument(
        "--local-image-mode",
        default="r2",
        choices=["r2", "data-uri"],
        help="How to turn a local image into Liblib input. Default r2: upload to R2 and use public URL; data-uri: embed as data URI.",
    )
    run_p.add_argument("--r2-endpoint", default=os.environ.get("R2_ENDPOINT", R2_ENDPOINT_DEFAULT))
    run_p.add_argument("--r2-access-key", default=os.environ.get("R2_ACCESS_KEY", R2_ACCESS_KEY_DEFAULT))
    run_p.add_argument("--r2-secret-key", default=os.environ.get("R2_SECRET_KEY", R2_SECRET_KEY_DEFAULT))
    run_p.add_argument("--r2-bucket", default=os.environ.get("R2_BUCKET", R2_BUCKET_DEFAULT))
    run_p.add_argument("--public-url-base", default=os.environ.get("PUBLIC_URL_BASE", PUBLIC_URL_BASE_DEFAULT))
    run_p.add_argument("--r2-user-id", default=os.environ.get("R2_USER_ID", "example-user"))
    run_p.add_argument("--r2-object-prefix", default=os.environ.get("R2_OBJECT_PREFIX", "images"))
    run_p.add_argument("--feishu-text", default="", help="Feishu message text, auto extract first URL")
    run_p.add_argument("--guidance", type=float, default=2.5)
    run_p.add_argument("--lora-name", default=DEFAULT_LORA_NAME)
    run_p.add_argument("--strength-model", type=float, default=1.0)
    run_p.add_argument("--no-poll", action="store_true")
    run_p.add_argument("--interval", type=int, default=3)
    run_p.add_argument("--timeout", type=int, default=300)
    run_p.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Directory for downloaded results (default: <workspace>/outputs/images).",
    )
    run_p.add_argument(
        "--basename",
        type=str,
        default="liblib-fusion",
        help="Output filename stem under outputs/images/YYYY-MM-DD/.",
    )
    run_p.add_argument(
        "--no-download",
        action="store_true",
        help="Do not download result images after success (only print JSON).",
    )
    run_p.add_argument(
        "--print-media",
        dest="print_media",
        action="store_true",
        default=True,
        help="Print MEDIA:./... line for Feishu / channel (default: on).",
    )
    run_p.add_argument(
        "--no-print-media",
        dest="print_media",
        action="store_false",
        help="Suppress MEDIA line.",
    )

    status_p = sub.add_parser("status", help="Query status by generateUuid")
    status_p.add_argument("uuid")

    args = parser.parse_args()

    ak = os.environ.get("LIB_ACCESS_KEY")
    sk = os.environ.get("LIB_SECRET_KEY")
    if not ak or not sk:
        raise RuntimeError("Please set LIB_ACCESS_KEY and LIB_SECRET_KEY environment variables.")

    if args.command == "run":
        image_ref = resolve_image_input(
            local_image=args.local_image,
            image_url=args.image_url,
            feishu_text=args.feishu_text,
            local_image_mode=args.local_image_mode,
            r2_endpoint=args.r2_endpoint,
            r2_access_key=args.r2_access_key,
            r2_secret_key=args.r2_secret_key,
            r2_bucket=args.r2_bucket,
            public_url_base=args.public_url_base,
            r2_user_id=args.r2_user_id,
            r2_object_prefix=args.r2_object_prefix,
        )

        submitted = submit_task(
            image_url=image_ref,
            ak=ak,
            sk=sk,
            guidance=args.guidance,
            lora_name=args.lora_name,
            strength_model=args.strength_model,
        )
        task_uuid = submitted.get("generateUuid")
        print(f"task_uuid={task_uuid}", file=sys.stderr)

        if args.no_poll or not task_uuid:
            print(json.dumps(submitted, ensure_ascii=False, indent=2))
            return

        final = poll_result(task_uuid, ak, sk, interval=args.interval, timeout=args.timeout)
        status = final.get("generateStatus", 0)
        print(json.dumps(final, ensure_ascii=False, indent=2), file=sys.stderr)

        if status == 6:
            print("Task failed (generateStatus=6).", file=sys.stderr)
            sys.exit(1)

        if status != 5:
            print(f"Unexpected status={status}, expected 5 (success).", file=sys.stderr)
            sys.exit(1)

        # Always prefer returning a public URL for chat channels.
        urls = extract_image_urls(final)
        if not urls:
            print("No images in result; nothing to download.", file=sys.stderr)
            return

        first_url = urls[0]

        # For Feishu/OpenClaw channel, MEDIA:https://... 会直接显示图片。
        if args.print_media:
            print(f"MEDIA:{first_url}", flush=True)
        else:
            print(first_url, flush=True)

        # Optional: still download to local workspace for调试/归档.
        if not args.no_download:
            out_base = Path(args.output_dir).expanduser() if args.output_dir else default_output_dir()
            saved_paths = download_result_images(urls, out_base, args.basename)
            for p in saved_paths:
                print(f"saved_path={p}", file=sys.stderr)
        return

    if args.command == "status":
        result = query_status(args.uuid, ak, sk)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
