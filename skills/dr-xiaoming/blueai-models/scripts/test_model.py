#!/usr/bin/env python3
"""
验证 BlueAI 模型连通性
用法:
  python3 test_model.py <model-id>                   # 文本测试
  python3 test_model.py <model-id> --image-gen        # 图像生成测试
  python3 test_model.py --all-configured              # 测试所有已配置模型
"""

import json, sys, urllib.request, os, argparse, re, base64

IMAGE_MODELS = {
    "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview",
    "gemini-2.5-flash-image", "gpt-image-1", "gpt-image-1.5"
}

def get_api_key():
    """从 openclaw.json 中提取 API key"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        for pconf in config.get("models", {}).get("providers", {}).values():
            if pconf.get("apiKey"):
                return pconf["apiKey"]
    return None

def test_text(model_id, api_key, base_url):
    """Test a model with a simple text request"""
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "回复OK"}],
        "max_tokens": 10
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        print(f"✅ {model_id}")
        print(f"   Response: {content[:50]}")
        print(f"   Model: {data.get('model', model_id)}")
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

def test_image_gen(model_id, api_key, base_url, save_path=None):
    """Test a Gemini image generation model via chat completions"""
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Generate a simple test image: a red circle on white background. Return the image."}],
        "max_tokens": 4096
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})

        # Check for base64 image in response
        match = re.search(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)', content)
        if match:
            fmt = match.group(1)
            img_bytes = base64.b64decode(match.group(2))
            print(f"✅ {model_id} — image generated ({len(img_bytes)} bytes, {fmt})")
            if save_path:
                out = f"{save_path}.{fmt}"
                with open(out, "wb") as f:
                    f.write(img_bytes)
                print(f"   Saved: {out}")
        else:
            # Maybe text-only response
            print(f"⚠️  {model_id} — response received but no image found")
            print(f"   Content preview: {content[:150]}")

        if usage:
            print(f"   Tokens: {usage.get('prompt_tokens',0)} in / {usage.get('completion_tokens',0)} out")
        return bool(match)
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
    parser.add_argument("--image-gen", action="store_true", help="Test as image generation model")
    parser.add_argument("--save", default=None, help="Save generated image to path (without extension)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("BLUEAI_API_KEY") or get_api_key()
    if not api_key:
        print("❌ No API key found. Use --api-key or set BLUEAI_API_KEY")
        return

    if args.all_configured:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path) as f:
            config = json.load(f)
        ok = fail = 0
        for pconf in config.get("models", {}).get("providers", {}).values():
            for m in pconf.get("models", []):
                if m.get("api") == "anthropic-messages":
                    continue
                mid = m["id"]
                if mid in IMAGE_MODELS:
                    result = test_image_gen(mid, api_key, args.base_url)
                else:
                    result = test_text(mid, api_key, args.base_url)
                if result:
                    ok += 1
                else:
                    fail += 1
        print(f"\nResults: {ok} ok, {fail} failed")
    elif args.model_id:
        is_image = args.image_gen or args.model_id in IMAGE_MODELS
        if is_image:
            test_image_gen(args.model_id, api_key, args.base_url, args.save)
        else:
            test_text(args.model_id, api_key, args.base_url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
