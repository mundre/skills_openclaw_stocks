"""
OpenAPI 凭证前置检查与自动初始化流程。
"""

import base64
from datetime import datetime
import importlib.util
import os
import subprocess
import sys
import tempfile
import uuid

import requests
from cryptography.hazmat.primitives import serialization


def _resolve_workspace_root():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."
        )
    )


def _resolve_sdk_setup_dir():
    candidates = [
        os.path.join(WORKSPACE_ROOT, "fw-tradings", "fosun-sdk-setup"),
        os.path.join(WORKSPACE_ROOT, "skills", "fw-tradings", "fosun-sdk-setup"),
        os.path.normpath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "fosun-sdk-setup",
            )
        ),
    ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return candidates[0]


WORKSPACE_ROOT = _resolve_workspace_root()
ENV_PATH = os.path.join(WORKSPACE_ROOT, "fosun.env")
SDK_SETUP_DIR = _resolve_sdk_setup_dir()
GENKEY_SCRIPT = os.path.join(SDK_SETUP_DIR, "genkey.sh")
DEFAULT_BASE_URL = "https://openapi.fosunxcz.com"
API_KEY_STATUS_KEY = "FSOPENAPI_API_KEY_STATUS"
API_KEY_VERIFIED_AT_KEY = "FSOPENAPI_API_KEY_VERIFIED_AT"
TICKET_KEY = "FSOPENAPI_TICKET"
TICKET_STATUS_KEY = "FSOPENAPI_TICKET_STATUS"
TICKET_EXPIRE_TIME_KEY = "FSOPENAPI_TICKET_EXPIRE_TIME"
OPEN_URL_KEY = "FSOPENAPI_OPEN_URL"
MAC_ID_KEY = "FSOPENAPI_MAC_ID"
API_KEY_KEY = "FSOPENAPI_API_KEY"
BASE_URL_KEY = "FSOPENAPI_BASE_URL"
PRIVATE_KEY_KEY = "FSOPENAPI_CLIENT_PRIVATE_KEY"
SERVER_PUBLIC_KEY_KEY = "FSOPENAPI_SERVER_PUBLIC_KEY"

_PEM_WRAPPERS = {
    PRIVATE_KEY_KEY: ("-----BEGIN PRIVATE KEY-----", "-----END PRIVATE KEY-----"),
    SERVER_PUBLIC_KEY_KEY: ("-----BEGIN PUBLIC KEY-----", "-----END PUBLIC KEY-----"),
}


def _parse_env_file(text):
    result = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        key, sep, val = line.partition("=")
        if not sep:
            i += 1
            continue
        key, val = key.strip(), val.strip()
        if val.startswith("-----BEGIN "):
            pem_lines = [val]
            i += 1
            while i < len(lines):
                pem_line = lines[i].rstrip()
                pem_lines.append(pem_line)
                if pem_line.strip().startswith("-----END "):
                    i += 1
                    break
                i += 1
            val = "\n".join(pem_lines)
        else:
            i += 1
        if key:
            result[key] = val
    return result


def _ensure_pem(key_name, value):
    value = str(value or "").strip()
    if not value or value.startswith("-----BEGIN "):
        return value
    wrapper = _PEM_WRAPPERS.get(key_name)
    if not wrapper:
        return value
    try:
        decoded = base64.b64decode(value).decode("utf-8")
        if decoded.strip().startswith("-----BEGIN "):
            return decoded.strip()
    except Exception:
        pass
    begin, end = wrapper
    raw = value.replace("\n", "").replace("\r", "").replace(" ", "")
    lines = [raw[i : i + 64] for i in range(0, len(raw), 64)]
    return begin + "\n" + "\n".join(lines) + "\n" + end


def _encode_env_value(key, value):
    if value is None:
        return ""
    value = str(value).strip()
    if key in _PEM_WRAPPERS and value.startswith("-----BEGIN "):
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")
    return value


def load_env_entries():
    if not os.path.isfile(ENV_PATH):
        return {}
    with open(ENV_PATH, encoding="utf-8") as f:
        return _parse_env_file(f.read())


def save_env_entries(entries):
    serialized = {}
    for key, value in entries.items():
        if value is None:
            continue
        serialized[key] = _encode_env_value(key, value)
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for key in sorted(serialized.keys()):
            f.write(f"{key}={serialized[key]}\n")


def load_credentials_into_env():
    entries = load_env_entries()
    for key, value in entries.items():
        if not os.environ.get(key):
            os.environ[key] = _ensure_pem(key, value)
    return entries


def _import_device_id_helper():
    module_path = os.path.join(SDK_SETUP_DIR, "device_id.py")
    spec = importlib.util.spec_from_file_location("fosun_device_id", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 device_id.py: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_or_create_device_id


def _ensure_device_id(entries):
    get_or_create_device_id = _import_device_id_helper()
    device_id = get_or_create_device_id(ENV_PATH)
    entries[MAC_ID_KEY] = device_id
    return device_id


def _generate_client_key_pair():
    with tempfile.TemporaryDirectory(prefix="fosun-key-") as tmp_dir:
        private_path = os.path.join(tmp_dir, "private.pem")
        public_path = os.path.join(tmp_dir, "public.pem")
        subprocess.run(
            ["bash", GENKEY_SCRIPT, private_path, public_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        with open(private_path, encoding="utf-8") as f:
            private_pem = f.read().strip()
        with open(public_path, encoding="utf-8") as f:
            public_pem = f.read().strip()
    return private_pem, public_pem


def _derive_public_key(private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None,
    )
    public_key = private_key.public_key()
    return (
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
        .strip()
    )


def _ensure_client_key_pair(entries):
    private_key = _ensure_pem(PRIVATE_KEY_KEY, entries.get(PRIVATE_KEY_KEY))
    if private_key:
        entries[PRIVATE_KEY_KEY] = private_key
        return False, private_key

    private_key, _ = _generate_client_key_pair()
    entries[PRIVATE_KEY_KEY] = private_key
    entries[API_KEY_STATUS_KEY] = "unknown"
    return True, private_key


def _now_ts():
    return int(datetime.now().timestamp())


def _format_expire_time(expire_time):
    try:
        ts = int(expire_time)
    except (TypeError, ValueError):
        return "未知"
    if ts <= 0:
        return "未知"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _ticket_headers():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Request-Id": str(uuid.uuid4()),
    }


def _extract_response_data(body):
    if not isinstance(body, dict):
        raise RuntimeError(f"认证接口返回格式不正确: {body!r}")
    code = body.get("code")
    if code not in (None, 0):
        message = body.get("message") or "认证接口调用失败"
        raise RuntimeError(f"{message} (code={code})")
    content = body.get("content")
    if isinstance(content, dict):
        data = content.get("data")
        if isinstance(data, dict):
            return data
        return content
    data = body.get("data")
    if isinstance(data, dict):
        return data
    return body


def _post_auth_json(base_url, path, payload):
    url = f"{base_url.rstrip('/')}{path}"
    response = requests.post(
        url,
        json=payload,
        headers=_ticket_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return _extract_response_data(response.json())


def _validate_api_key(base_url, api_key, entries):
    try:
        data = _post_auth_json(
            base_url,
            "/api/v1/auth/APIKeyCheck",
            {"apiKey": api_key},
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"API Key 校验失败，认证服务不可达: {exc}") from exc

    status = int(str(data.get("status", 0) or 0))

    if status == 1:
        return True

    return False


def _refresh_ticket_state(entries, base_url):
    ticket = str(entries.get(TICKET_KEY, "")).strip()
    if not ticket:
        entries[TICKET_STATUS_KEY] = "unknown"
        return False

    expire_time = int(str(entries.get(TICKET_EXPIRE_TIME_KEY, "0") or "0"))
    if expire_time and expire_time <= _now_ts():
        entries[TICKET_STATUS_KEY] = "expired"
        entries[TICKET_EXPIRE_TIME_KEY] = "0"
        return False

    try:
        data = _post_auth_json(base_url, "/api/v1/auth/TicketQuery", {"ticket": ticket})
    except requests.RequestException as exc:
        raise RuntimeError(f"Ticket 状态查询失败: {exc}") from exc

    is_active = bool(data.get("isActive"))
    latest_expire = int(str(data.get("expireTime", 0) or 0))
    entries[TICKET_EXPIRE_TIME_KEY] = str(latest_expire)
    entries[TICKET_STATUS_KEY] = "active" if is_active else "expired"
    return is_active


def _build_pending_message(entries, created):
    action = "已创建新的开通票据" if created else "当前开通票据仍有效"
    url = entries.get(OPEN_URL_KEY, "").strip()
    expire_time = _format_expire_time(entries.get(TICKET_EXPIRE_TIME_KEY))
    lines = [
        f"OpenAPI API Key 尚未生效，{action}。",
        f"开通 URL: {url or '未返回'}",
        f"Ticket 过期时间: {expire_time}",
        "请先完成开通流程后再重试当前命令。",
    ]
    raise SystemExit("\n".join(lines))


def _create_ticket(entries, base_url, private_key_pem):
    client_public_key = _derive_public_key(private_key_pem)
    payload = {
        "macId": str(entries.get(MAC_ID_KEY, "")).strip(),
        "clientPubKey": client_public_key,
    }
    try:
        data = _post_auth_json(base_url, "/api/v1/auth/TicketCreate", payload)
    except requests.RequestException as exc:
        raise RuntimeError(f"Ticket 创建失败: {exc}") from exc

    api_key = str(data.get("apiKey", "")).strip()
    server_public_key = str(data.get("serverPubKey", "")).strip()
    ticket = str(data.get("ticket", "")).strip()
    open_url = str(data.get("url", "")).strip()
    expire_time = str(data.get("expireTime", "0") or "0")

    if not all([api_key, server_public_key, ticket, open_url]):
        raise RuntimeError("TicketCreate 返回缺少必要字段，无法写入本地凭证。")

    entries[API_KEY_KEY] = api_key
    entries[SERVER_PUBLIC_KEY_KEY] = server_public_key
    entries[TICKET_KEY] = ticket
    entries[TICKET_STATUS_KEY] = "active"
    entries[TICKET_EXPIRE_TIME_KEY] = expire_time
    entries[OPEN_URL_KEY] = open_url
    entries[API_KEY_STATUS_KEY] = "pending"
    entries[API_KEY_VERIFIED_AT_KEY] = ""
    save_env_entries(entries)
    _build_pending_message(entries, created=True)


def _ensure_ticket_ready(entries, base_url, private_key_pem, allow_existing_ticket):
    if allow_existing_ticket and _refresh_ticket_state(entries, base_url):
        entries[API_KEY_STATUS_KEY] = "pending"
        save_env_entries(entries)
        _build_pending_message(entries, created=False)
    _create_ticket(entries, base_url, private_key_pem)


def prepare_client_runtime(api_key=None, base_url=None, sdk_type=None):
    entries = load_env_entries()
    _ensure_device_id(entries)

    key_created, private_key_pem = _ensure_client_key_pair(entries)
    if not entries.get(BASE_URL_KEY):
        entries[BASE_URL_KEY] = DEFAULT_BASE_URL
    if base_url:
        entries[BASE_URL_KEY] = str(base_url).strip().rstrip("/")
    resolved_base_url = entries.get(BASE_URL_KEY) or DEFAULT_BASE_URL
    entries[BASE_URL_KEY] = resolved_base_url
    save_env_entries(entries)

    if sdk_type:
        normalized = str(sdk_type).strip().lower()
        if normalized in {"default", "api", "normal"}:
            os.environ.pop("SDK_TYPE", None)
        else:
            os.environ["SDK_TYPE"] = normalized

    if api_key:
        entries[API_KEY_KEY] = api_key
        save_env_entries(entries)
        load_credentials_into_env()
        os.environ[API_KEY_KEY] = api_key
        os.environ[BASE_URL_KEY] = resolved_base_url
        return {"base_url": resolved_base_url, "api_key": api_key}

    api_key_value = str(entries.get(API_KEY_KEY, "")).strip()
    api_key_status = (
        str(entries.get(API_KEY_STATUS_KEY, "unknown") or "unknown").strip().lower()
    )
    has_complete_key_material = bool(
        _ensure_pem(PRIVATE_KEY_KEY, entries.get(PRIVATE_KEY_KEY))
        and _ensure_pem(SERVER_PUBLIC_KEY_KEY, entries.get(SERVER_PUBLIC_KEY_KEY))
    )

    if key_created or not has_complete_key_material:
        _ensure_ticket_ready(
            entries,
            resolved_base_url,
            private_key_pem,
            allow_existing_ticket=False,
        )

    if api_key_value and api_key_status == "valid":
        load_credentials_into_env()
        os.environ[BASE_URL_KEY] = resolved_base_url
        return {"base_url": resolved_base_url, "api_key": api_key_value}

    if api_key_value:
        is_valid = _validate_api_key(resolved_base_url, api_key_value, entries)
        if is_valid:
            entries[API_KEY_STATUS_KEY] = "valid"
            entries[API_KEY_VERIFIED_AT_KEY] = str(_now_ts())
            save_env_entries(entries)
            load_credentials_into_env()
            os.environ[BASE_URL_KEY] = resolved_base_url
            return {"base_url": resolved_base_url, "api_key": api_key_value}

        entries[API_KEY_STATUS_KEY] = "invalid"
        save_env_entries(entries)
        _ensure_ticket_ready(
            entries,
            resolved_base_url,
            private_key_pem,
            allow_existing_ticket=True,
        )

    _ensure_ticket_ready(
        entries,
        resolved_base_url,
        private_key_pem,
        allow_existing_ticket=True,
    )
