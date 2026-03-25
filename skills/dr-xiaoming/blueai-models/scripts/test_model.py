#!/usr/bin/env python3
"""
验证 BlueAI 模型连通性
用法: python3 test_model.py <model-id> [--api-key <key>] [--base-url <url>]
"""

import json, sys, urllib.request, os, argparse

def test_model(model_id, api_key, base_url="https://bmc-llm-relay.bluemediagroup.cn/v1"):
    """Test a model with a simple request"""
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "回复OK"}],
        "max_tokens": 10
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        model_used = data.get("model", model_id)
        usage = data.get("usage", {})
        print(f"✅ {model_id}")
        print(f"   Response: {content[:50]}")
        print(f"   Model: {model_used}")
        if usage:
            print(f"   Tokens: {usage.get('prompt_tokens',0)} in / {usage.get('completion_tokens',0)} out")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"❌ {model_id} — HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"❌ {model_id} — {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test BlueAI model connectivity")
    parser.add_argument("model_id", nargs="?", help="Model ID to test")
    parser.add_argument("--api-key", default=None, help="API key")
    parser.add_argument("--base-url", default="https://bmc-llm-relay.bluemediagroup.cn/v1")
    parser.add_argument("--all-configured", action="store_true", help="Test all models in openclaw.json")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("BLUEAI_API_KEY")
    if not api_key:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            for pname, pconf in config.get("models", {}).get("providers", {}).items():
                if pconf.get("apiKey"):
                    api_key = pconf["apiKey"]
                    break
            if not api_key:
                api_key = config.get("agents",{}).get("defaults",{}).get("memorySearch",{}).get("remote",{}).get("apiKey","")

    if not api_key:
        print("❌ No API key found. Use --api-key or set BLUEAI_API_KEY")
        return

    if args.all_configured:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path) as f:
            config = json.load(f)
        ok = 0
        fail = 0
        for pname, pconf in config.get("models", {}).get("providers", {}).items():
            for m in pconf.get("models", []):
                if m.get("api") == "anthropic-messages":
                    continue  # Skip anthropic (different endpoint)
                if test_model(m["id"], api_key, args.base_url):
                    ok += 1
                else:
                    fail += 1
        print(f"\nResults: {ok} ok, {fail} failed")
    elif args.model_id:
        test_model(args.model_id, api_key, args.base_url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
