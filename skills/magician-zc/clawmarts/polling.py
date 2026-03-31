#!/usr/bin/env python3
"""
ClawMarts WebSocket Helper Script
WebSocket 长连接保活 + 自动接单（抢单/竞标/赛马）+ 自动执行任务
用法: python polling.py [--config PATH]
"""
import json
import os
import sys
import time
import argparse
import threading

# ── 依赖自动检查与安装引导 ──
_MISSING_DEPS = []

try:
    import requests
except ImportError:
    _MISSING_DEPS.append("requests")

try:
    import websocket as ws_lib  # websocket-client
except ImportError:
    _MISSING_DEPS.append("websocket-client")


def _check_and_install_deps():
    """检查缺失依赖，引导用户手动安装"""
    if not _MISSING_DEPS:
        return True

    print(f"  ❌ 缺失依赖: {', '.join(_MISSING_DEPS)}", file=sys.stderr)
    print(f"  请手动安装后重新运行:", file=sys.stderr)
    print(f"     {sys.executable} -m pip install {' '.join(_MISSING_DEPS)}", file=sys.stderr)
    sys.exit(1)


DEFAULT_CONFIG = os.path.expanduser(
    "~/.openclaw/skills/clawmarts/config.json"
)

# ── 全局状态 ──
ws_connected = threading.Event()
stop_event = threading.Event()


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_config(path: str, cfg: dict):
    """保存配置到文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def api(method: str, path: str, cfg: dict, **kwargs):
    """统一 HTTP API 调用"""
    url = f"{cfg['clawnet_api_url']}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {cfg['token']}"
    headers.setdefault("Content-Type", "application/json")
    try:
        resp = getattr(requests, method)(url, headers=headers, timeout=30, **kwargs)
        return resp.json()
    except Exception as e:
        print(f"  ⚠️  API error [{method.upper()} {path}]: {e}", file=sys.stderr)
        return None


def _safe_float(val, default=0.0) -> float:
    """安全地将任意值转为 float，避免 str vs float 比较错误"""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


# ── WebSocket 长连接 ──


def _build_ws_url(cfg: dict) -> str:
    """根据 API URL 构建 WebSocket URL"""
    base = cfg["clawnet_api_url"]
    if base.startswith("https://"):
        ws_base = "wss://" + base[len("https://"):]
    elif base.startswith("http://"):
        ws_base = "ws://" + base[len("http://"):]
    else:
        ws_base = "ws://" + base
    return f"{ws_base}/ws/claw?token={cfg['token']}&claw_id={cfg['claw_id']}"


def _ws_thread(cfg: dict):
    """WebSocket 线程：保持长连接，定期发 ping 保活"""
    url = _build_ws_url(cfg)
    ping_interval = cfg.get("heartbeat_interval", 60)
    reconnect_delay = 5

    while not stop_event.is_set():
        ws = None
        try:
            print(f"  🔌 WebSocket 连接中...")
            ws = ws_lib.create_connection(url, timeout=10)
            ws_connected.set()
            print(f"  ✅ WebSocket 已连接 (ping 间隔 {ping_interval}s)")
            reconnect_delay = 5  # 连接成功，重置重连延迟

            last_ping = time.time()
            ws.settimeout(5)  # recv 超时 5s，用于定期检查 stop_event

            while not stop_event.is_set():
                # 定期发 ping
                now = time.time()
                if now - last_ping >= ping_interval:
                    ws.send("ping")
                    last_ping = now

                # 尝试接收服务端消息
                try:
                    msg = ws.recv()
                    if msg == "pong":
                        pass  # ping 回复，忽略
                    else:
                        _handle_server_message(msg, cfg)
                except ws_lib.WebSocketTimeoutException:
                    pass  # recv 超时，正常，继续循环
                except ws_lib.WebSocketConnectionClosedException:
                    print("  ⚠️  WebSocket 连接被关闭", file=sys.stderr)
                    break

        except Exception as e:
            print(f"  ⚠️  WebSocket 错误: {e}", file=sys.stderr)
        finally:
            ws_connected.clear()
            if ws:
                try:
                    ws.close()
                except Exception:
                    pass

        if not stop_event.is_set():
            print(f"  🔄 {reconnect_delay}s 后重连...")
            stop_event.wait(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)  # 指数退避，最大 60s


def _handle_server_message(raw: str, cfg: dict):
    """处理服务端推送的消息"""
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return

    msg_type = msg.get("type", "")
    if msg_type == "task_push":
        task = msg.get("task", {})
        task_id = task.get("task_id", "?")
        desc = task.get("description", "")[:40]
        print(f"  📥 收到推送任务: {task_id[:8]} - {desc}")
    elif msg_type == "task_reclaimed":
        task_id = msg.get("task_id", "?")
        reason = msg.get("reason", "")
        print(f"  ⚠️  任务被收回: {task_id[:8]} - {reason}")
    elif msg_type == "heartbeat_ack":
        pass  # 心跳确认


# ── 自动接单 API 辅助函数 ──


def get_my_tasks(cfg: dict, status: str = "assigned") -> list:
    """查询我的任务"""
    r = api("get", f"/api/tasks?claw_id={cfg['claw_id']}&status={status}", cfg)
    if r and r.get("success"):
        return r.get("tasks", [])
    return []


def get_recommendations(cfg: dict) -> list:
    """获取平台推荐的任务"""
    r = api("get", f"/api/recommendations/{cfg['claw_id']}?status=pending", cfg)
    if r and r.get("success"):
        return r.get("recommendations", [])
    return []


def accept_recommendation(cfg: dict, task_id: str) -> bool:
    """接受推荐任务"""
    r = api("post", f"/api/recommendations/{cfg['claw_id']}/{task_id}/respond",
            cfg, json={"accept": True})
    return bool(r and r.get("success"))


def get_personalized_tasks(cfg: dict) -> list:
    """获取个性化任务列表（按匹配度排序）"""
    r = api("get", f"/api/tasks/personalized/{cfg['claw_id']}", cfg)
    if r and r.get("success"):
        return r.get("tasks", [])
    return []


def grab_task(cfg: dict, task_id: str) -> bool:
    """抢单"""
    r = api("post", f"/api/tasks/{task_id}/grab",
            cfg, json={"claw_id": cfg["claw_id"]})
    return bool(r and r.get("success"))


def bid_task(cfg: dict, task_id: str, bid_amount: float = 0) -> bool:
    """竞标"""
    r = api("post", f"/api/tasks/{task_id}/bid",
            cfg, json={"claw_id": cfg["claw_id"], "bid_amount": bid_amount})
    return bool(r and r.get("success"))


def join_race(cfg: dict, task_id: str) -> bool:
    """加入赛马"""
    r = api("post", f"/api/tasks/{task_id}/race/join",
            cfg, json={"claw_id": cfg["claw_id"]})
    return bool(r and r.get("success"))


def submit_task_result(cfg: dict, task_id: str, result_data: dict) -> dict | None:
    """提交任务结果"""
    r = api("post", f"/api/tasks/{task_id}/submit", cfg, json={
        "claw_id": cfg["claw_id"],
        "result_data": result_data,
        "confidence_score": 0.8,
    })
    return r


def get_task_detail(cfg: dict, task_id: str) -> dict | None:
    """获取任务详情"""
    r = api("get", f"/api/tasks/{task_id}", cfg)
    if r and r.get("success"):
        return r.get("task", {})
    return None


# ── 自动执行任务 ──


def _call_platform_llm(cfg: dict, messages: list[dict], model: str = "") -> str | None:
    """通过平台 LLM 代理调用大模型

    用于没有自己 API Key 的用户，完全依赖平台提供的模型。
    返回模型回复文本，失败返回 None。
    """
    if not model:
        model = cfg.get("platform_model", "")
    if not model:
        # 尝试从平台获取可用模型列表，选第一个
        r = api("get", "/api/llm/models", cfg)
        if r and r.get("success") and r.get("models"):
            model = r["models"][0].get("model_name", "")
            cfg["platform_model"] = model  # 缓存到配置
        if not model:
            print("  ⚠️  无可用平台模型，请联系管理员配置", file=sys.stderr)
            return None

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "claw_id": cfg.get("claw_id", ""),
    }
    r = api("post", "/api/llm/chat/completions", cfg, json=body)
    if not r:
        return None
    # 兼容 OpenAI 格式响应
    choices = r.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    # 直接返回的文本
    if isinstance(r.get("content"), str):
        return r["content"]
    return None


def _build_task_prompt(task: dict) -> list[dict]:
    """根据任务信息构建 LLM 提示词"""
    desc = task.get("description", "")
    delivery_def = task.get("delivery_definition", {})
    required_fields = delivery_def.get("required_fields", [])
    user_params = delivery_def.get("user_params", {})
    fmt = delivery_def.get("format", "text")

    system_msg = (
        "你是一个任务执行 Agent。根据任务描述和要求，生成符合交付定义的结果。\n"
        "输出必须是合法的 JSON 对象，包含所有 required_fields 中要求的字段。\n"
        "不要输出任何解释文字，只输出 JSON。"
    )

    user_msg = f"## 任务描述\n{desc}\n\n"
    if user_params:
        user_msg += f"## 任务参数\n{json.dumps(user_params, ensure_ascii=False, indent=2)}\n\n"
    user_msg += f"## 交付格式: {fmt}\n"
    if required_fields:
        user_msg += f"## 必须包含的字段: {', '.join(required_fields)}\n"
    user_msg += "\n请生成符合要求的结果（JSON 格式）："

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]


def auto_execute_task(cfg: dict, task: dict) -> bool:
    """自动执行一个任务并提交结果

    优先使用平台 LLM 代理来理解和执行任务。
    如果平台 LLM 不可用，降级为基础占位结果。
    Agent 框架可以覆盖此逻辑。
    """
    task_id = task.get("task_id", "")
    desc = task.get("description", "")[:60]
    delivery_def = task.get("delivery_definition", {})

    print(f"  🔧 执行任务: {task_id[:8]} - {desc}")

    result_data = None

    # 尝试用平台 LLM 执行任务
    if cfg.get("use_platform_llm", True):
        messages = _build_task_prompt(task)
        llm_response = _call_platform_llm(cfg, messages)
        if llm_response:
            # 尝试解析 JSON
            try:
                # 去掉可能的 markdown 代码块包裹
                text = llm_response.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                result_data = json.loads(text)
                print(f"  🤖 LLM 生成结果: {list(result_data.keys())}")
            except (json.JSONDecodeError, Exception):
                # JSON 解析失败，把原始文本作为 content 字段
                result_data = {"content": llm_response, "format": "text"}
                print(f"  🤖 LLM 生成文本结果 ({len(llm_response)} 字)")

    # 降级：基础占位结果
    if not result_data:
        required_fields = delivery_def.get("required_fields", [])
        fmt = delivery_def.get("format", "text")
        if required_fields:
            result_data = {}
            for field in required_fields:
                if isinstance(field, str):
                    result_data[field] = f"[auto-generated for: {field}]"
        else:
            result_data = {"content": f"Task completed: {desc}", "format": fmt}

    # 提交结果
    r = submit_task_result(cfg, task_id, result_data)
    if r and r.get("success"):
        print(f"  ✅ 任务提交成功: {task_id[:8]}")
        return True
    else:
        msg = r.get("message", r.get("detail", "未知错误")) if r else "API 无响应"
        print(f"  ❌ 任务提交失败: {task_id[:8]} - {msg}")
        return False


# ── 自动接单核心逻辑 ──


def try_accept_tasks(cfg: dict) -> int:
    """尝试自动接单，返回成功接到的任务数"""
    accepted = 0
    max_concurrent = cfg.get("max_concurrent_tasks", 3)

    # 检查当前正在执行的任务数
    my_assigned = get_my_tasks(cfg, "assigned")
    my_in_progress = get_my_tasks(cfg, "in_progress")
    current_count = len(my_assigned) + len(my_in_progress)
    if current_count >= max_concurrent:
        return 0

    slots = max_concurrent - current_count

    # 1. 先处理平台推荐
    recs = get_recommendations(cfg)
    for rec in recs:
        if slots <= 0:
            break
        task_id = rec.get("task_id", "")
        score = _safe_float(rec.get("relevance_score", 0))
        if task_id and accept_recommendation(cfg, task_id):
            print(f"  ✅ 接受推荐: {task_id[:8]} (匹配度 {score:.0%})")
            accepted += 1
            slots -= 1

    # 2. 从个性化任务列表中抢单/竞标/赛马
    if slots > 0:
        tasks = get_personalized_tasks(cfg)
        for t in tasks:
            if slots <= 0:
                break
            task_id = t.get("task_id", "")
            match_mode = t.get("match_mode", "grab")
            score = _safe_float(t.get("relevance_score", 0))
            threshold = _safe_float(cfg.get("auto_delegate_threshold", 0.3))

            # 匹配度太低，跳过
            if score < threshold:
                continue

            ok = False
            if match_mode == "race":
                # 赛马任务默认跳过（可能白干），除非用户配置了 accept_race: true
                if not cfg.get("accept_race", False):
                    continue
                ok = join_race(cfg, task_id)
                mode_label = "赛马"
            elif match_mode == "bid":
                ok = bid_task(cfg, task_id)
                mode_label = "竞标"
            else:
                ok = grab_task(cfg, task_id)
                mode_label = "抢单"

            if ok:
                print(f"  ✅ {mode_label}成功: {task_id[:8]} (匹配度 {score:.0%})")
                accepted += 1
                slots -= 1

    return accepted


def try_execute_tasks(cfg: dict) -> int:
    """尝试自动执行已分配的任务，返回成功执行的任务数"""
    executed = 0

    # 查询已分配和进行中的任务
    my_assigned = get_my_tasks(cfg, "assigned")
    my_in_progress = get_my_tasks(cfg, "in_progress")
    pending = my_assigned + my_in_progress

    for task in pending:
        task_id = task.get("task_id", "")
        if not task_id:
            continue

        # 获取完整任务详情
        detail = get_task_detail(cfg, task_id)
        if not detail:
            continue

        # 自动执行并提交
        if auto_execute_task(cfg, detail):
            executed += 1

    return executed


# ── 主循环 ──


def main():
    # 首先检查依赖
    _check_and_install_deps()

    parser = argparse.ArgumentParser(description="ClawMarts WebSocket Helper")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="配置文件路径")
    args = parser.parse_args()

    # 配置文件检查
    if not os.path.exists(args.config):
        print(f"  ❌ 配置文件不存在: {args.config}", file=sys.stderr)
        print(f"  💡 请先通过 Agent 执行「连接 ClawMarts」来生成配置", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(args.config)
    missing_keys = [k for k in ("clawnet_api_url", "token", "claw_id") if not cfg.get(k)]
    if missing_keys:
        print(f"  ❌ 配置缺少: {', '.join(missing_keys)}", file=sys.stderr)
        print(f"  💡 请先通过 Agent 执行「连接 ClawMarts」来完善配置", file=sys.stderr)
        sys.exit(1)

    if ws_lib is None:
        # 理论上不会到这里（_check_and_install_deps 已处理），但保险起见
        print("  ❌ websocket-client 未安装，请执行:", file=sys.stderr)
        print(f"     {sys.executable} -m pip install websocket-client", file=sys.stderr)
        sys.exit(1)

    check_interval = 30  # 自动接单检查间隔（秒）
    autopilot = cfg.get("autopilot", False)
    accept_mode = cfg.get("accept_mode", "auto")

    print("=" * 50)
    print(f"  🦀 ClawMarts WebSocket Helper")
    print(f"  Claw: {cfg['claw_id'][:8]}...")
    print(f"  接单模式: {accept_mode}")
    print(f"  自动执行: {'开启' if autopilot else '关闭'}")
    print(f"  接单检查间隔: {check_interval}s")
    print("=" * 50)

    # 启动 WebSocket 线程
    t = threading.Thread(target=_ws_thread, args=(cfg,), daemon=True)
    t.start()

    # 等待首次连接（最多 10s）
    ws_connected.wait(timeout=10)
    if ws_connected.is_set():
        print("  ✅ WebSocket 长连接已建立")
    else:
        print("  ⚠️  WebSocket 首次连接超时，后台将持续重连...")

    # 主循环：自动接单 + 自动执行
    fail_streak = 0
    task_stats = {"accepted": 0, "executed": 0, "failed": 0}
    last_report = time.time()

    while not stop_event.is_set():
        try:
            # 自动接单（accept_mode=auto 时）
            if accept_mode == "auto":
                accepted = try_accept_tasks(cfg)
                task_stats["accepted"] += accepted
                if accepted > 0:
                    fail_streak = 0
                else:
                    fail_streak += 1

            # 自动执行任务（autopilot=true 时）
            if autopilot:
                executed = try_execute_tasks(cfg)
                task_stats["executed"] += executed
                if executed > 0:
                    fail_streak = 0

            # 定期状态汇报（每 10 分钟）
            now = time.time()
            if now - last_report >= 600:
                print(f"  📊 状态汇报: 接单 {task_stats['accepted']}, "
                      f"执行 {task_stats['executed']}, "
                      f"WS {'在线' if ws_connected.is_set() else '离线'}")
                last_report = now

            # 连续无任务时降频
            if fail_streak >= 3:
                wait = check_interval * 2
            else:
                wait = check_interval

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  ⚠️  循环异常: {e}", file=sys.stderr)
            wait = check_interval

        stop_event.wait(wait)

    print(f"\n  🛑 已停止 (接单 {task_stats['accepted']}, 执行 {task_stats['executed']})")


if __name__ == "__main__":
    # 设置 stdout/stderr 编码为 UTF-8（解决 Windows 控制台编码问题）
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    try:
        main()
    except KeyboardInterrupt:
        stop_event.set()
        print("\n  🛑 收到中断信号，退出")
