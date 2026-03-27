"""MoltAssist localhost dashboard server -- port 7430, stdlib only."""

import json
import logging
import os
import subprocess
import threading
import time
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from moltassist.config import load_config, save_config, validate_config
from moltassist.log import _get_log_path, _read_log
from moltassist.onboard import (
    detect_installed_skills,
    generate_suggestions,
    generate_suggestions_with_context,
    generate_follow_up_questions,
    generate_config_from_onboarding,
    _get_profile,
    SKILL_MAP,
    CATEGORY_DISPLAY,
    ALL_CATEGORIES,
)

log = logging.getLogger("moltassist.server")


DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"
ONBOARD_HTML = Path(__file__).parent / "onboard.html"

# In-memory onboarding session state (one at a time -- localhost only)
_onboard_session: dict = {}

# Categories that require specific skills to be installed
CATEGORY_SKILL_MAP = {
    "email": "gog",
    "calendar": "gog",
    "health": "healthcheck",
    "weather": "weather",
    "dev": "github",
    "finance": None,      # built-in
    "compliance": None,    # built-in
    "travel": None,        # future
    "staff": None,         # built-in
    "social": None,        # built-in
    "system": None,        # built-in
    "custom": None,        # built-in
}


def set_onboard_session(
    role_text: str, detected_role: str, suggestions: list[dict],
) -> None:
    """Set the active onboarding session data for the /onboard page."""
    global _onboard_session
    profile = _get_profile(detected_role)
    _onboard_session = {
        "role_text": role_text,
        "detected_role": detected_role,
        "role_label": profile.get("label", detected_role),
        "suggestions": suggestions,
        "profile": profile,
        "created": time.time(),
    }


def _detect_skills() -> list[dict]:
    """Detect installed OpenClaw skills via clawhub CLI or direct directory scan."""
    skills: list[dict] = []

    # Method 1: Try clawhub list (may not be installed)
    try:
        result = subprocess.run(
            ["clawhub", "list"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                name = line.strip().split()[0] if line.strip() else ""
                if name:
                    skills.append({"name": name, "installed": True})
            return skills
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    # Method 2: Scan skill directories directly
    skill_dirs = [
        Path.home() / ".openclaw" / "workspace" / "skills",
        Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "skills",
    ]
    seen: set[str] = set()
    for skill_dir in skill_dirs:
        if skill_dir.exists():
            for d in skill_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists() and d.name not in seen:
                    skills.append({"name": d.name, "installed": True})
                    seen.add(d.name)
    return skills


class DashboardHandler(BaseHTTPRequestHandler):
    """Request handler for the MoltAssist dashboard."""

    def __init__(self, *args, workspace: Path, idle_timer: dict, **kwargs):
        self.workspace = workspace
        self.idle_timer = idle_timer
        super().__init__(*args, **kwargs)

    def _touch_idle(self):
        self.idle_timer["last_request"] = time.monotonic()

    def _config_path(self) -> Path:
        return self.workspace / "moltassist" / "config.json"

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def log_message(self, format, *args):
        pass  # Suppress default stderr logging

    def do_OPTIONS(self):
        self._touch_idle()
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self._touch_idle()
        path = urlparse(self.path).path

        if path == "/" or path == "":
            if ONBOARD_HTML.exists():
                self._send_html(ONBOARD_HTML.read_text(encoding="utf-8"))
            else:
                self._send_json({"error": "onboard.html not found"}, 404)

        elif path == "/dashboard":
            if DASHBOARD_HTML.exists():
                self._send_html(DASHBOARD_HTML.read_text(encoding="utf-8"))
            else:
                self._send_json({"error": "dashboard.html not found"}, 404)

        elif path == "/api/config":
            config = load_config(self._config_path())
            self._send_json(config)

        elif path == "/api/log":
            log_path = _get_log_path()
            entries = _read_log(log_path)
            # Return last 50 entries, newest first
            self._send_json(entries[-50:][::-1])

        elif path == "/api/skills":
            # Use detect_installed_skills which scans all dirs, not just clawhub lockfile
            skill_names = detect_installed_skills()
            self._send_json([{"name": n, "installed": True} for n in skill_names])

        elif path == "/api/onboard/suggestions":
            # Return the current onboarding session's suggestions
            if not _onboard_session or not _onboard_session.get("suggestions"):
                # No pre-seeded session -- return empty so the HTML shows the role input
                self._send_json({"needs_role": True})
                return
            installed_skills = detect_installed_skills()
            self._send_json({
                "suggestions": _onboard_session["suggestions"],
                "installed_skills": installed_skills,
                "role_label": _onboard_session.get("role_label", "General"),
                "role_text": _onboard_session.get("role_text", ""),
                "detected_role": _onboard_session.get("detected_role", "fallback"),
            })

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        self._touch_idle()
        path = urlparse(self.path).path

        if path == "/api/config":
            try:
                body = self._read_body()
                new_config = json.loads(body)
                validate_config(new_config)
                save_config(new_config, self._config_path())
                self._send_json({"ok": True})
            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"ok": False, "error": str(e)}, 400)

        elif path == "/api/test":
            try:
                from moltassist.core import notify
                import time as _time
                result = notify(
                    message=f"👋 Test notification from MoltAssist — if you're seeing this, delivery is working. ({int(_time.time())})",
                    urgency="critical",  # always bypasses threshold check
                    category="system",
                    source="dashboard_test",
                    event_id=f"dashboard_test_{int(_time.time())}",  # unique each time, bypasses dedup
                    dry_run=False,
                )
                sent = result.get("sent", False) if isinstance(result, dict) else False
                channel = result.get("channel", "unknown") if isinstance(result, dict) else "unknown"
                err = result.get("error") if isinstance(result, dict) else None
                if sent:
                    self._send_json({"ok": True, "result": f"Sent via {channel}"})
                else:
                    self._send_json({"ok": False, "error": err or "Delivery failed — check your channel config"})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)})

        elif path == "/api/onboard/role":
            # POST /api/onboard/role -- submit role text, detect role, return follow-up questions
            try:
                body = self._read_body()
                data = json.loads(body)
                role_text = data.get("role_text", "").strip()
                if not role_text:
                    self._send_json({"error": "role_text is required"}, 400)
                    return
                from moltassist.onboard import detect_role
                detected_role = detect_role(role_text)
                profile = _get_profile(detected_role)
                follow_up_questions = generate_follow_up_questions(role_text, detected_role)

                # Store partial session for later
                _onboard_session.clear()
                _onboard_session["role_text"] = role_text
                _onboard_session["detected_role"] = detected_role
                _onboard_session["role_label"] = profile.get("label", detected_role)
                _onboard_session["profile"] = profile
                _onboard_session["created"] = time.time()

                self._send_json({
                    "detected_role": detected_role,
                    "role_label": profile.get("label", detected_role),
                    "follow_up_questions": follow_up_questions,
                })
            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"error": str(e)}, 400)

        elif path == "/api/onboard/answers":
            # POST /api/onboard/answers -- submit follow-up answers, get suggestions
            try:
                body = self._read_body()
                data = json.loads(body)
                role_text = data.get("role_text", "").strip()
                answers = data.get("answers", {})

                if not role_text and _onboard_session.get("role_text"):
                    role_text = _onboard_session["role_text"]

                detected_role = _onboard_session.get("detected_role", "fallback")
                profile = _onboard_session.get("profile") or _get_profile(detected_role)

                if answers:
                    suggestions = generate_suggestions_with_context(
                        role_text, detected_role, answers
                    )
                else:
                    suggestions = generate_suggestions(
                        role_text, detected_role, profile
                    )

                set_onboard_session(role_text, detected_role, suggestions)
                # Store answers in session for config persistence at confirm time
                if answers:
                    _onboard_session["answers"] = answers
                installed_skills = detect_installed_skills()

                self._send_json({
                    "suggestions": suggestions,
                    "installed_skills": installed_skills,
                    "role_label": profile.get("label", detected_role),
                    "role_text": role_text,
                    "detected_role": detected_role,
                })
            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"error": str(e)}, 400)

        elif path == "/onboard/confirm":
            try:
                body = self._read_body()
                data = json.loads(body)
                selected = data.get("selected", [])

                if not _onboard_session:
                    self._send_json(
                        {"ok": False, "error": "No active onboarding session."},
                        400,
                    )
                    return

                # Build config from selected suggestions
                detected_role = _onboard_session.get("detected_role", "fallback")
                profile = _onboard_session.get("profile", {})

                # Determine which categories are needed from selections
                selected_categories = list({
                    s.get("category", "custom") for s in selected
                })

                state = {
                    "role_id": detected_role,
                    "channel": "telegram",  # default, user can change in dashboard
                    "visible_categories": selected_categories,
                    "selected_categories": selected_categories,
                    "role_text": _onboard_session.get("role_text", ""),
                }

                config = generate_config_from_onboarding(state)

                # Persist full onboarding selections including required_skill for dashboard
                config["onboarding_selections"] = [
                    {
                        "title": s.get("title"),
                        "description": s.get("description"),
                        "category": s.get("category"),
                        "priority": s.get("priority"),
                        "required_skill": s.get("required_skill"),
                        "build_needed": s.get("build_needed", False),
                    }
                    for s in selected
                ]

                # Persist onboarding answers for dashboard personalisation
                if _onboard_session.get("answers"):
                    config["onboarding_answers"] = _onboard_session["answers"]

                # Persist role text for dashboard personalisation
                config["role_text"] = _onboard_session.get("role_text", "")

                # Apply quiet hours from the browser form
                quiet_hours = data.get("quiet_hours")
                if quiet_hours and isinstance(quiet_hours, dict):
                    config.setdefault("quiet_hours", {})
                    config["quiet_hours"]["enabled"] = quiet_hours.get("enabled", True)
                    config["quiet_hours"]["start"] = quiet_hours.get("start", "23:00")
                    config["quiet_hours"]["end"] = quiet_hours.get("end", "08:00")

                # Save config
                config_path = self._config_path()
                save_config(config, config_path)

                # Clear onboarding session
                _onboard_session.clear()

                self._send_json({
                    "ok": True,
                    "message": f"Config saved with {len(selected)} notifications.",
                    "config_path": str(config_path),
                })

            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"ok": False, "error": str(e)}, 400)

        elif path == "/onboard/session":
            # POST /onboard/session -- create a new onboarding session
            try:
                from moltassist.onboard import start_onboarding
                step_data = start_onboarding()
                session_id = str(int(time.time() * 1000))
                _onboard_session["session_id"] = session_id
                _onboard_session["step"] = step_data.get("step", 1)
                _onboard_session["state"] = {}
                self._send_json({
                    "step": step_data.get("step"),
                    "message": step_data.get("message"),
                    "buttons": step_data.get("buttons"),
                    "session_id": session_id,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/onboard/respond":
            # POST /onboard/respond -- process onboarding response
            try:
                body = self._read_body()
                data = json.loads(body)
                session_id = data.get("session_id", "")
                response = data.get("response", "")

                if not _onboard_session or _onboard_session.get("session_id") != session_id:
                    self._send_json({"error": "Invalid or expired session"}, 400)
                    return

                from moltassist.onboard import process_onboarding_response
                step = _onboard_session.get("step", 1)
                state = _onboard_session.get("state", {})
                result = process_onboarding_response(step, response, state)

                _onboard_session["step"] = result.get("step", step)
                _onboard_session["state"] = result.get("state", state)

                self._send_json({
                    "step": result.get("step"),
                    "message": result.get("message"),
                    "buttons": result.get("buttons"),
                    "done": result.get("done", False),
                    "session_id": session_id,
                })
            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"error": str(e)}, 400)

        elif path == "/onboard/save":
            # POST /onboard/save -- save final selections
            try:
                body = self._read_body()
                data = json.loads(body)

                if not _onboard_session:
                    self._send_json({"error": "No active onboarding session"}, 400)
                    return

                state = _onboard_session.get("state", {})
                state.update(data)

                config = generate_config_from_onboarding(state)
                config_path = self._config_path()
                save_config(config, config_path)

                # Count enabled categories
                watching = sum(
                    1 for c in config.get("categories", {}).values()
                    if c.get("enabled")
                )

                _onboard_session.clear()

                self._send_json({"saved": True, "watching": watching})
            except (json.JSONDecodeError, ValueError) as e:
                self._send_json({"error": str(e)}, 400)

        else:
            self._send_json({"error": "not found"}, 404)


def start_server(workspace: Path | None = None, port: int = 7430, idle_timeout: int = 1800):
    """Start the dashboard server. Shuts down after idle_timeout seconds of no requests."""
    import os
    if workspace is None:
        ws = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
        workspace = Path(ws)

    idle_timer = {"last_request": time.monotonic()}

    handler = partial(DashboardHandler, workspace=workspace, idle_timer=idle_timer)
    server = HTTPServer(("127.0.0.1", port), handler)
    server.timeout = 1  # Check idle every second

    def idle_watchdog():
        while True:
            time.sleep(5)
            elapsed = time.monotonic() - idle_timer["last_request"]
            if elapsed > idle_timeout:
                server.shutdown()
                return

    watchdog = threading.Thread(target=idle_watchdog, daemon=True)
    watchdog.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()
