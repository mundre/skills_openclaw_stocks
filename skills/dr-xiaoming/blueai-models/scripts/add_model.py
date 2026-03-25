#!/usr/bin/env python3
"""
BlueAI 模型快速添加脚本
用法: python3 add_model.py <model-id> [--provider <name>] [--primary]

示例:
  python3 add_model.py gemini-2.5-flash
  python3 add_model.py claude-sonnet-4-6 --provider anthropic
  python3 add_model.py gpt-4.1-mini --primary
"""

import json, sys, os, argparse

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")

# 预定义模型库（从BlueAI文档）
MODEL_DB = {
    # Claude (anthropic-messages)
    "claude-opus-4-6-v1": {"name": "Claude Opus 4.6", "api": "anthropic-messages", "reasoning": True, "input": ["text","image"], "cost": {"input":0.015,"output":0.075,"cacheRead":0.00187,"cacheWrite":0.01875}, "contextWindow": 200000, "maxTokens": 128000, "provider_type": "anthropic"},
    "claude-opus-4-5-20251101": {"name": "Claude Opus 4.5", "api": "anthropic-messages", "reasoning": True, "input": ["text","image"], "cost": {"input":0.015,"output":0.075,"cacheRead":0.00187,"cacheWrite":0.01875}, "contextWindow": 200000, "maxTokens": 32000, "provider_type": "anthropic"},
    "claude-sonnet-4-6": {"name": "Claude Sonnet 4.6", "api": "anthropic-messages", "reasoning": True, "input": ["text","image"], "cost": {"input":0.003,"output":0.015,"cacheRead":0.0003,"cacheWrite":0.00375}, "contextWindow": 200000, "maxTokens": 64000, "provider_type": "anthropic"},
    "claude-sonnet-4-5-20250929": {"name": "Claude Sonnet 4.5", "api": "anthropic-messages", "reasoning": True, "input": ["text","image"], "cost": {"input":0.003,"output":0.015,"cacheRead":0.0003,"cacheWrite":0.00375}, "contextWindow": 200000, "maxTokens": 64000, "provider_type": "anthropic"},
    "claude-haiku-4-5-20251001": {"name": "Claude Haiku 4.5", "api": "anthropic-messages", "reasoning": False, "input": ["text","image"], "cost": {"input":0.001,"output":0.005,"cacheRead":0.0001,"cacheWrite":0.00125}, "contextWindow": 200000, "maxTokens": 64000, "provider_type": "anthropic"},
    # GPT (openai-completions)
    "gpt-4.1": {"name": "GPT-4.1", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.002,"output":0.008}, "contextWindow": 128000, "maxTokens": 32768, "provider_type": "openai"},
    "gpt-4.1-mini": {"name": "GPT-4.1 Mini", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.0004,"output":0.0016}, "contextWindow": 128000, "maxTokens": 32768, "provider_type": "openai"},
    "gpt-4.1-nano": {"name": "GPT-4.1 Nano", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.0001,"output":0.0004}, "contextWindow": 128000, "maxTokens": 32768, "provider_type": "openai"},
    "gpt-4o": {"name": "GPT-4o", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.0025,"output":0.01}, "contextWindow": 128000, "maxTokens": 16384, "provider_type": "openai"},
    "gpt-4o-mini": {"name": "GPT-4o Mini", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.00015,"output":0.0006}, "contextWindow": 128000, "maxTokens": 16384, "provider_type": "openai"},
    "o4-mini": {"name": "o4-mini", "api": "openai-completions", "reasoning": True, "input": ["text","image"], "cost": {"input":0.0011,"output":0.0044}, "contextWindow": 200000, "maxTokens": 100000, "provider_type": "openai"},
    # Gemini (openai-completions)
    "gemini-2.5-flash": {"name": "Gemini 2.5 Flash", "api": "openai-completions", "reasoning": True, "input": ["text","image"], "cost": {"input":0.00015,"output":0.0035}, "contextWindow": 1048576, "maxTokens": 65535, "provider_type": "openai"},
    "gemini-2.5-pro": {"name": "Gemini 2.5 Pro", "api": "openai-completions", "reasoning": True, "input": ["text","image"], "cost": {"input":0.00125,"output":0.01}, "contextWindow": 1048576, "maxTokens": 65535, "provider_type": "openai"},
    "gemini-3.1-pro-preview": {"name": "Gemini 3.1 Pro", "api": "openai-completions", "reasoning": True, "input": ["text","image"], "cost": {"input":0.00125,"output":0.01}, "contextWindow": 1048576, "maxTokens": 65536, "provider_type": "openai"},
    "gemini-3-flash-preview": {"name": "Gemini 3 Flash", "api": "openai-completions", "reasoning": True, "input": ["text","image"], "cost": {"input":0.00015,"output":0.0035}, "contextWindow": 1048576, "maxTokens": 65536, "provider_type": "openai"},
    # DeepSeek (openai-completions, text only)
    "DeepSeek-R1": {"name": "DeepSeek R1", "api": "openai-completions", "reasoning": True, "input": ["text"], "cost": {"input":0.00055,"output":0.0022}, "contextWindow": 128000, "maxTokens": 32000, "provider_type": "openai"},
    "DeepSeek-V3.2": {"name": "DeepSeek V3.2", "api": "openai-completions", "reasoning": False, "input": ["text"], "cost": {"input":0.00027,"output":0.0011}, "contextWindow": 128000, "maxTokens": 32000, "provider_type": "openai"},
    # Qwen
    "qwen3-235b-a22b": {"name": "Qwen3 235B", "api": "openai-completions", "reasoning": True, "input": ["text"], "cost": {"input":0.0008,"output":0.002}, "contextWindow": 131072, "maxTokens": 16384, "provider_type": "openai"},
    "qwen-vl-max-latest": {"name": "Qwen VL Max", "api": "openai-completions", "reasoning": False, "input": ["text","image"], "cost": {"input":0.003,"output":0.009}, "contextWindow": 131072, "maxTokens": 8192, "provider_type": "openai"},
}

def main():
    parser = argparse.ArgumentParser(description="Add BlueAI model to OpenClaw config")
    parser.add_argument("model_id", nargs="?", help="Model ID to add")
    parser.add_argument("--provider", default=None, help="Provider name in config")
    parser.add_argument("--primary", action="store_true", help="Set as primary model")
    parser.add_argument("--alias", default=None, help="Short alias for /model command")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--api-key", default=None, help="API key (if not already configured)")
    args = parser.parse_args()

    if args.list:
        print("Available models in BlueAI:")
        for mid, info in sorted(MODEL_DB.items()):
            pt = info["provider_type"]
            ctx = info["contextWindow"] // 1000
            print(f"  {mid:<35} {info['name']:<25} {pt:<10} {ctx}K ctx")
        return

    if not args.model_id:
        parser.print_help()
        return

    if args.model_id not in MODEL_DB:
        print(f"❌ Unknown model: {args.model_id}")
        print(f"   Use --list to see available models")
        print(f"   Or add manually to openclaw.json")
        return

    model_info = MODEL_DB[args.model_id].copy()
    provider_type = model_info.pop("provider_type")

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    providers = config.setdefault("models", {}).setdefault("providers", {})

    # Determine provider name
    if args.provider:
        pname = args.provider
    elif provider_type == "anthropic":
        pname = "anthropic"
    else:
        pname = "blueai"

    # Create provider if not exists
    if pname not in providers:
        if provider_type == "anthropic":
            providers[pname] = {
                "baseUrl": "https://bmc-llm-relay.bluemediagroup.cn",
                "api": "anthropic-messages",
                "models": []
            }
        else:
            providers[pname] = {
                "baseUrl": "https://bmc-llm-relay.bluemediagroup.cn/v1",
                "api": "openai-completions",
                "models": []
            }
        if args.api_key:
            providers[pname]["apiKey"] = args.api_key
        print(f"✅ Created provider: {pname}")

    # Check if model already exists
    existing_ids = [m["id"] for m in providers[pname].get("models", [])]
    if args.model_id in existing_ids:
        print(f"⚠️  Model {args.model_id} already exists in provider {pname}")
        return

    # Add model
    model_entry = {"id": args.model_id, **model_info}
    providers[pname]["models"].append(model_entry)
    print(f"✅ Added {args.model_id} to provider {pname}")

    # Set as primary if requested
    if args.primary:
        config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["primary"] = f"{pname}/{args.model_id}"
        print(f"✅ Set as primary: {pname}/{args.model_id}")

    # Add alias if provided
    if args.alias:
        config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("models", {})[f"{pname}/{args.model_id}"] = {"alias": args.alias}
        print(f"✅ Alias: {args.alias}")

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n💡 Run 'openclaw gateway restart' to apply changes")

if __name__ == "__main__":
    main()
