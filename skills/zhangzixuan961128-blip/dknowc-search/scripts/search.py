#!/usr/bin/env python3
"""深知可信搜索 - API 调用脚本"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def _load_config():
    """从 OpenClaw 配置文件读取环境变量（兜底机制）。

    优先级：进程环境变量 > skills.entries.env > 顶层 env
    """
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _get_env(name, config=None):
    """获取环境变量，兜底读取 OpenClaw 配置文件。"""
    # 优先读进程环境变量
    val = os.environ.get(name)
    if val:
        return val

    if config is None:
        config = _load_config()

    # 其次读 skills.entries.dknowc-search.env
    try:
        val = config["skills"]["entries"]["dknowc-search"]["env"][name]
        if val:
            return val
    except (KeyError, TypeError):
        pass

    # 最后读顶层 env
    try:
        val = config["env"][name]
        if val:
            return val
    except (KeyError, TypeError):
        pass

    return None


def search(query, area=None, time=None, know_base=True, policy=False, item=False):
    config = _load_config()
    api_key = _get_env("DKNOWC_SEARCH_API_KEY", config)
    endpoint = _get_env("DKNOWC_SEARCH_ENDPOINT", config)

    if not api_key:
        print("错误：未配置 DKNOWC_SEARCH_API_KEY", file=sys.stderr)
        print("请提供深知可信搜索的 API Key，OpenClaw 会自动写入配置。", file=sys.stderr)
        print("获取指南见：https://platform.dknowc.cn", file=sys.stderr)
        sys.exit(1)

    if not endpoint:
        print("错误：未配置 DKNOWC_SEARCH_ENDPOINT", file=sys.stderr)
        print("请提供深知可信搜索的调用地址，格式：", file=sys.stderr)
        print("https://open.dknowc.cn/dependable/search/{你的AppID}", file=sys.stderr)
        sys.exit(1)

    # 构建请求参数
    payload = {"query": query}

    if area:
        payload["service_area"] = [area]
    if time:
        payload["eff_time"] = [time]
    if know_base:
        payload["knowBase"] = True
    if policy:
        payload["policy"] = True
    if item:
        payload["item"] = True

    # 发送请求
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, method="POST")
    req.add_header("api-key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8").replace("\x00", ""))
    except urllib.error.HTTPError as e:
        code = e.code
        if code == 401:
            print("错误：API Key 无效，请检查配置", file=sys.stderr)
        elif code == 403:
            print("错误：权限不足，请检查 API Key 对应的应用权限", file=sys.stderr)
        elif code == 429:
            print("错误：余额不足，请登录 https://platform.dknowc.cn 充值", file=sys.stderr)
        else:
            print(f"错误：HTTP {code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"错误：网络请求失败 - {e.reason}", file=sys.stderr)
        sys.exit(1)

    # 解析结果
    content = body.get("content", {})
    data_section = content.get("data", {})
    articles = data_section.get("检索文章", [])
    policy_files = data_section.get("policyFiles", [])
    recommend_items = data_section.get("recommendationItems", [])
    knowledge_base = content.get("knowledgeBase", "")

    # 输出格式化结果
    print(f"=== 深知可信搜索结果 ===")
    print(f"搜索词：{data_section.get('用户问题', query)}")

    if knowledge_base:
        print(f"知识专库链接：{knowledge_base}")

    print(f"召回文章：{len(articles)} 篇")
    print()

    for i, article in enumerate(articles, 1):
        title = article.get("文章标题", "无标题")
        url = article.get("源网址", "")
        date = article.get("发布日期", "")
        source = article.get("数据源", "")
        paragraphs = article.get("段落", [])

        print(f"--- 文章 {i} ---")
        print(f"标题：{title}")
        print(f"来源：{source}")
        if date:
            print(f"日期：{date}")
        if url:
            print(f"链接：{url}")

        for p in paragraphs[:3]:  # 每篇最多展示3个段落
            p_title = p.get("标题", "")
            p_content = p.get("内容", "")
            if p_title:
                print(f"  【{p_title}】")
            if p_content:
                # 截取前200字
                if len(p_content) > 200:
                    p_content = p_content[:200] + "..."
                print(f"  {p_content}")
        print()

    if policy_files:
        print("=== 规范性文件清单 ===")
        for pf in policy_files:
            pf_name = pf.get("name", pf.get("标题", ""))
            pf_url = pf.get("url", pf.get("源网址", ""))
            print(f"  · {pf_name}")
            if pf_url:
                print(f"    {pf_url}")
        print()

    if recommend_items:
        print("=== 在线办理清单 ===")
        for ri in recommend_items:
            ri_name = ri.get("name", ri.get("标题", ""))
            print(f"  · {ri_name}")
        print()

    # 输出原始 JSON（供程序化使用）
    print("=== RAW_JSON_START ===")
    print(json.dumps(body, ensure_ascii=False, indent=2))
    print("=== RAW_JSON_END ===")

    return body


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="深知可信搜索")
    parser.add_argument("query", help="搜索内容")
    parser.add_argument("--area", help="办理地域，如 北京、广东省")
    parser.add_argument("--time", help="生效日期，如 2025年、2025年08月")
    parser.add_argument("--no-knowbase", action="store_true", help="不返回知识专库链接")
    parser.add_argument("--policy", action="store_true", help="返回规范性文件清单")
    parser.add_argument("--item", action="store_true", help="返回在线办理清单")

    args = parser.parse_args()
    search(
        query=args.query,
        area=args.area,
        time=args.time,
        know_base=not args.no_knowbase,
        policy=args.policy,
        item=args.item,
    )
