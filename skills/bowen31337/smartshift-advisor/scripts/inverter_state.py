#!/usr/bin/env python3
"""Read current inverter/battery state for SmartShift advisor."""
import json
import os
import ssl
import urllib.request

INVERTER_URL = os.environ.get("INVERTER_URL", "https://10.0.0.2")
INVERTER_SN = os.environ.get("INVERTER_SN", "OE012K01Z2610013")

def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    result = {}

    # Battery state
    try:
        url = f"{INVERTER_URL}/getdevdata.cgi?device=4&sn={INVERTER_SN}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read())
        result["battery"] = {
            "soc_pct": int(data.get("soc", 0)),
            "soh_pct": int(data.get("soh", 0)),
            "power_w": int(data.get("pb", 0)),
            "voltage_mv": int(data.get("vb", 0)),
            "temp_c": int(data.get("tb", 0)) / 10,
        }
    except Exception as e:
        result["battery"] = {"error": str(e)}

    # Current work mode
    try:
        url = f"{INVERTER_URL}/getdev.cgi?device=4"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read())
        mod_r = int(data.get("mod_r", -1))
        mode_names = {2: "self_consumption", 4: "custom", 5: "tou_discharge"}
        result["mode"] = {
            "mod_r": mod_r,
            "name": mode_names.get(mod_r, f"unknown({mod_r})"),
        }
    except Exception as e:
        result["mode"] = {"error": str(e)}

    # Last smartshift state
    state_file = "~/.openclaw/workspace/ha-smartshift/.current_state.json"
    try:
        with open(state_file) as f:
            last = json.load(f)
        result["last_decision"] = {
            "action": last.get("action"),
            "timestamp": last.get("timestamp"),
            "spot_price": last.get("spot_price_ckwh"),
            "export_earn": last.get("export_earn_ckwh"),
            "soc": last.get("soc_pct"),
        }
    except Exception:
        result["last_decision"] = {"error": "no state file"}

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
