#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Page - 动态网页抓取辅助模块
使用 Playwright 抓取动态网页内容
"""

import subprocess
import json
from typing import Dict, Any

DYNAMIC_WEBFETCH_SCRIPT = "/home/lin/.openclaw/workspace/skills/dynamic-webfetch/scripts/fetch.py"


def fetch_page(url: str, format: str = "text", wait_seconds: int = 3, 
               wait_selector: str = None, timeout: int = 30000) -> Dict[str, Any]:
    """
    使用 dynamic-webfetch 抓取网页
    
    Args:
        url: 目标 URL
        format: 输出格式 (text/markdown/html)
        wait_seconds: 等待时间（秒）
        wait_selector: CSS 选择器
        timeout: 超时时间（毫秒）
    
    Returns:
        dict: 抓取结果
    """
    try:
        input_data = {
            "url": url,
            "format": format,
            "wait_seconds": wait_seconds,
            "timeout": timeout
        }
        
        if wait_selector:
            input_data["wait_selector"] = wait_selector
        
        proc = subprocess.run(
            ["python3", DYNAMIC_WEBFETCH_SCRIPT],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        if proc.returncode == 0 and proc.stdout:
            return json.loads(proc.stdout)
        else:
            return {
                "success": False,
                "error": proc.stderr or "抓取失败"
            }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "抓取超时"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # 测试
    test_url = "https://m.cngold.org/quote/gjs/jjs_hj9999.html"
    result = fetch_page(test_url, format="text", wait_seconds=3)
    print(json.dumps(result, ensure_ascii=False, indent=2))
