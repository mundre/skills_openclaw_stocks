#!/usr/bin/env python3
"""
深知可信搜索 - 公文素材召回脚本

用于公文写作场景中的政策法规素材检索。
基于深知可信搜索 API，返回可溯源的权威素材。
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# ========== 搜索限制配置 ==========

MAX_QUERY_LENGTH = 500
MIN_QUERY_LENGTH = 2

QUERY_TOO_LONG_ERROR = f"错误：查询关键词过长，超过限制（最大 {MAX_QUERY_LENGTH} 字符）"
QUERY_TOO_SHORT_ERROR = f"错误：查询关键词过短，最少需要 {MIN_QUERY_LENGTH} 个字符"


# ========== 环境变量加载 ==========

def _load_env_config():
    """从进程环境变量读取配置（OpenClaw 会自动注入 skill 级 env）。"""


def _get_env(name):
    """获取环境变量（OpenClaw 已注入 skill 级 env 到进程）。"""
    return os.environ.get(name)


def _load_search_config():
    """加载搜索 API 配置。

    Returns:
        (api_key, api_url) 元组
    """
    api_key = _get_env("DKNOWC_SEARCH_API_KEY")
    api_url = _get_env("DKNOWC_SEARCH_ENDPOINT")

    if not api_key:
        print("错误：搜索 API Key 未配置。", file=sys.stderr)
        print("请在对话中告诉 AI 你的深知 API Key 和搜索地址，AI 会自动完成配置。", file=sys.stderr)
        print("获取方式：访问 https://platform.dknowc.cn 注册并实名认证（送100元）后创建搜索应用。", file=sys.stderr)
        sys.exit(1)

    return api_key, api_url


# ========== 数据清洗 ==========

def clean_response(api_response: dict) -> dict:
    """清洗搜索结果：去 HTML 转义、网页干扰词，分配唯一段落 ID。"""

    try:
        inner_content = api_response.get("content", {})

        if "data" in inner_content:
            real_data = inner_content.get("data", {})
        else:
            real_data = inner_content

        articles = real_data.get("检索文章", [])
        knowledge_base_url = inner_content.get("knowledgeBase", "")

        if not articles:
            return {
                "cleaned": True,
                "articles": [],
                "message": "未检索到相关参考文章",
                "knowledgeBase": knowledge_base_url
            }

        cleaned_articles = []
        global_id_counter = 1

        for art in articles:
            cleaned_art = {
                "文章标题": art.get("文章标题", "无标题"),
                "发布日期": art.get("发布日期", ""),
                "数据源": art.get("数据源", "未知来源"),
                "段落": []
            }

            for p in art.get("段落", []):
                p_title = p.get("标题", "").strip()
                p_content = p.get("内容", "").strip()
                full_text = f"{p_title}\n{p_content}" if p_title else p_content

                # 清洗
                content = html.unescape(full_text)
                content = re.sub(r'首页\s*>\s*.*?\s*打印\s*\]', '', content, flags=re.DOTALL)
                content = re.sub(r'点击\s*\d+.*?次', '', content)
                content = re.sub(r'分享\s*到.*?$', '', content, flags=re.MULTILINE)
                content = content.replace('\r', '\n')
                content = re.sub(r'\n+', '\n', content)
                content = re.sub(r'[ \t]+', ' ', content)
                content = content.strip()

                if content:
                    cleaned_art["段落"].append({
                        "id": global_id_counter,
                        "内容": content
                    })
                    global_id_counter += 1

            if cleaned_art["段落"]:
                cleaned_articles.append(cleaned_art)

        if not cleaned_articles:
            return {
                "cleaned": True,
                "articles": [],
                "message": "素材内容经过清洗后为空"
            }

        policy_files = real_data.get("policyFiles", [])

        return {
            "cleaned": True,
            "articles": cleaned_articles,
            "total_articles": len(cleaned_articles),
            "total_paragraphs": global_id_counter - 1,
            "knowledgeBase": knowledge_base_url,
            "policyFiles": policy_files
        }

    except Exception as e:
        return {
            "cleaned": False,
            "error": True,
            "message": f"数据清洗报错: {type(e).__name__} - {str(e)}"
        }


# ========== 搜索接口 ==========

def dkag_search(
    query: str,
    area: Optional[str] = None,
    api_key: Optional[str] = None,
    clean: bool = False,
    policy: bool = False
) -> dict:
    """调用深知可信搜索接口召回素材。

    Args:
        query: 搜索关键词（必填）
        area: 地域（可选，默认"中国"）
        api_key: API 密钥（可选，默认从配置读取）
        clean: 是否清洗结果（默认 False）
        policy: 是否返回规范性文件清单（默认 False）

    Returns:
        搜索结果字典
    """
    if len(query) > MAX_QUERY_LENGTH:
        return {"error": True, "message": QUERY_TOO_LONG_ERROR}
    if len(query) < MIN_QUERY_LENGTH:
        return {"error": True, "message": QUERY_TOO_SHORT_ERROR}

    _api_key, api_url = _load_search_config()
    if not api_key:
        api_key = _api_key

    payload = {
        "query": query,
        "eff_time": [""],
        "service_area": [area] if area else [""],
        "knowBase": True,
        "policy": policy
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("api-key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # 兼容处理：统一包装格式
        if "content" in result and "检索文章" in result.get("content", {}):
            result = {"content": {"data": result["content"]}}

        if clean:
            return clean_response(result)
        return result

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return {
            "error": True,
            "message": f"HTTP {e.code} - {e.reason}",
            "status_code": e.code,
            "response_body": body[:500]
        }
    except urllib.error.URLError as e:
        return {
            "error": True,
            "message": f"网络请求失败: {e.reason}"
        }


def main():
    parser = argparse.ArgumentParser(description="深知可信搜索 - 公文素材召回")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--area", help="地域（默认: 中国）")
    parser.add_argument("--api-key", help="API 密钥（可选，默认从配置读取）")
    parser.add_argument("--clean", action="store_true", help="清洗结果（去HTML转义、干扰词）")
    parser.add_argument("--policy", action="store_true", help="返回规范性文件清单")

    args = parser.parse_args()

    result = dkag_search(
        query=args.query,
        area=args.area,
        api_key=args.api_key,
        clean=args.clean,
        policy=args.policy
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
