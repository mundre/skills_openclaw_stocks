#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Web Search V2 - 极简网络搜索增强版
支持：通用搜索 + 社交媒体搜索（小红书/知乎/微博）
"""

import sys
import json
import subprocess
import urllib.parse
import re
from html import unescape
from typing import Dict, Any, List
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

EXA_SEARCH_SCRIPT = "/home/lin/.openclaw/scripts/exa-search.sh"


# ============== 通用搜索引擎 ==============

def search_exa(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Exa AI 搜索 (OpenCode 同款) - 优先使用"""
    results = []
    
    try:
        cmd = [EXA_SEARCH_SCRIPT, query, str(num_results)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8')
        
        if proc.returncode == 0 and proc.stdout:
            lines = proc.stdout.strip().split('\n')
            current = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current.get('title') and current.get('href'):
                        results.append(current)
                        current = {}
                    continue
                
                if line.startswith('📄'):
                    if current.get('title') and current.get('href'):
                        results.append(current)
                    current = {'title': line[2:].strip(), 'href': '', 'body': ''}
                elif line.startswith('🔗'):
                    current['href'] = line[2:].strip()
            
            if current.get('title') and current.get('href'):
                results.append(current)
                
    except Exception as e:
        pass
    
    return results[:num_results]


def search_baidu(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """百度搜索"""
    results = []
    
    if not HAS_REQUESTS:
        return results
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.baidu.com/s?wd={encoded_query}&rn={num_results * 2}"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            patterns = [
                r'<h3[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\s*</h3>',
                r'class="t"[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for href, title in matches:
                    if len(results) >= num_results:
                        break
                    
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    title = unescape(title)
                    
                    if not title or len(title) < 4:
                        continue
                    if not href.startswith('http'):
                        continue
                    if any(x in href for x in ['baidu.com/home', 'passport.baidu.com']):
                        continue
                    
                    results.append({'title': title, 'href': href, 'body': ''})
                    
    except Exception:
        pass
    
    return results


def search_bing(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """必应搜索"""
    results = []
    
    if not HAS_REQUESTS:
        return results
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://cn.bing.com/search?q={encoded_query}&count=20"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            pattern = r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)'
            matches = re.findall(pattern, html, re.IGNORECASE)
            
            for href, title in matches:
                if len(results) >= num_results:
                    break
                
                title = re.sub(r'<[^>]+>', '', title).strip()
                title = unescape(title)
                
                if not title or len(title) < 4:
                    continue
                if not is_valid_link(href):
                    continue
                
                results.append({'title': title, 'href': href, 'body': ''})
                    
    except Exception:
        pass
    
    return results


def is_valid_link(href: str) -> bool:
    """检查链接是否有效"""
    if not href.startswith(('http://', 'https://')):
        return False
    
    blocked = [
        'bing.com/search', 'bing.com/images', 'bing.com/videos',
        'bing.com/maps', 'javascript:', 'passport.bing.com', 'login.live.com',
    ]
    
    if any(b in href for b in blocked):
        return False
    
    if re.match(r'^https?://\d+\.\d+\.\d+\.\d+', href):
        return False
    
    return True


# ============== 社交媒体搜索 ==============

def search_xiaohongshu(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    小红书搜索 - 通过 web_fetch 抓取搜索结果页
    注意：小红书有反爬，可能需要动态网页抓取
    """
    results = []
    
    try:
        # 使用动态 webfetch 抓取小红书搜索结果
        from scripts.fetch_page import fetch_page
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_query}&source=web_search_result_notes"
        
        result = fetch_page(url, format="text", wait_seconds=5, timeout=20000)
        
        if result.get('success') and result.get('content'):
            content = result['content']
            
            # 提取笔记标题和链接（简化版）
            lines = content.split('\n')
            for line in lines:
                if len(results) >= num_results:
                    break
                
                # 匹配笔记标题（通常包含 emoji 和关键词）
                if query in line and len(line) > 10 and len(line) < 100:
                    results.append({
                        'title': f"[小红书] {line.strip()}",
                        'href': f"https://www.xiaohongshu.com/search_result?keyword={encoded_query}",
                        'body': '小红书笔记',
                        'source': 'xiaohongshu'
                    })
    except Exception:
        pass
    
    # 如果动态抓取失败，返回搜索指引
    if not results:
        results.append({
            'title': f"[小红书] 搜索 \"{query}\"",
            'href': f"https://www.xiaohongshu.com/search_result?keyword={urllib.parse.quote(query)}",
            'body': '点击链接查看小红书搜索结果',
            'source': 'xiaohongshu'
        })
    
    return results[:num_results]


def search_zhihu(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    知乎搜索 - 通过 web_fetch 抓取搜索结果页
    """
    results = []
    
    try:
        from scripts.fetch_page import fetch_page
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.zhihu.com/search?q={encoded_query}&type=content"
        
        result = fetch_page(url, format="text", wait_seconds=5, timeout=20000)
        
        if result.get('success') and result.get('content'):
            content = result['content']
            
            # 提取问题和回答
            lines = content.split('\n')
            for line in lines:
                if len(results) >= num_results:
                    break
                
                if query in line and len(line) > 10 and len(line) < 150:
                    results.append({
                        'title': f"[知乎] {line.strip()}",
                        'href': f"https://www.zhihu.com/search?q={encoded_query}&type=content",
                        'body': '知乎问答',
                        'source': 'zhihu'
                    })
    except Exception:
        pass
    
    if not results:
        results.append({
            'title': f"[知乎] 搜索 \"{query}\"",
            'href': f"https://www.zhihu.com/search?q={urllib.parse.quote(query)}",
            'body': '点击链接查看知乎搜索结果',
            'source': 'zhihu'
        })
    
    return results[:num_results]


def search_weibo(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    微博搜索 - 通过 web_fetch 抓取热搜或搜索结果
    """
    results = []
    
    try:
        from scripts.fetch_page import fetch_page
        
        # 先尝试搜索
        encoded_query = urllib.parse.quote(query)
        url = f"https://s.weibo.com/weibo?q={encoded_query}"
        
        result = fetch_page(url, format="text", wait_seconds=3, timeout=15000)
        
        if result.get('success') and result.get('content'):
            content = result['content']
            
            lines = content.split('\n')
            for line in lines:
                if len(results) >= num_results:
                    break
                
                if query in line and len(line) > 10 and len(line) < 140:
                    results.append({
                        'title': f"[微博] {line.strip()}",
                        'href': f"https://s.weibo.com/weibo?q={encoded_query}",
                        'body': '微博动态',
                        'source': 'weibo'
                    })
    except Exception:
        pass
    
    if not results:
        results.append({
            'title': f"[微博] 搜索 \"{query}\"",
            'href': f"https://s.weibo.com/weibo?q={urllib.parse.quote(query)}",
            'body': '点击链接查看微博搜索结果',
            'source': 'weibo'
        })
    
    return results[:num_results]


def search_social_media(query: str, platform: str = None, num_results: int = 5) -> Dict[str, Any]:
    """
    社交媒体搜索入口
    
    Args:
        query: 搜索关键词
        platform: 指定平台 (xiaohongshu/zhihu/weibo/all)
        num_results: 结果数量
    """
    all_results = []
    platforms_used = []
    
    platforms = {
        'xiaohongshu': ('小红书', search_xiaohongshu),
        'zhihu': ('知乎', search_zhihu),
        'weibo': ('微博', search_weibo),
    }
    
    if platform and platform != 'all':
        if platform in platforms:
            platforms = {platform: platforms[platform]}
    
    for plat_id, (plat_name, search_func) in platforms.items():
        results = search_func(query, num_results)
        if results:
            all_results.extend(results)
            platforms_used.append(plat_id)
    
    return {
        'success': len(all_results) > 0,
        'query': query,
        'type': 'social_media',
        'platforms': platforms_used,
        'num_results': len(all_results),
        'results': all_results,
        'message': f'搜索完成 (平台：{", ".join(platforms_used)})'
    }


# ============== 主搜索入口 ==============

def web_search(query: str, num_results: int = 5, search_type: str = 'general') -> Dict[str, Any]:
    """
    执行搜索
    
    Args:
        query: 搜索关键词
        num_results: 结果数量
        search_type: 搜索类型 (general/social_media)
    """
    if not query or not isinstance(query, str):
        return {'success': False, 'message': '搜索关键词不能为空'}
    
    query = query.strip()
    num_results = max(1, min(int(num_results), 20))
    
    if search_type == 'social_media':
        return search_social_media(query, num_results=num_results)
    
    # 通用搜索
    all_results = []
    engines_used = []
    
    # 1. Exa AI 优先
    exa_results = search_exa(query, num_results)
    if exa_results:
        all_results.extend(exa_results)
        engines_used.append('exa')
    
    # 2. 必应补充
    if len(all_results) < num_results and HAS_REQUESTS:
        bing_results = search_bing(query, num_results)
        if bing_results:
            existing_hrefs = {r['href'] for r in all_results}
            for r in bing_results:
                if r['href'] not in existing_hrefs:
                    all_results.append(r)
                    existing_hrefs.add(r['href'])
            engines_used.append('bing')
    
    # 3. 百度补充
    if len(all_results) < num_results and HAS_REQUESTS:
        baidu_results = search_baidu(query, num_results)
        if baidu_results:
            existing_hrefs = {r['href'] for r in all_results}
            for r in baidu_results:
                if r['href'] not in existing_hrefs:
                    all_results.append(r)
                    existing_hrefs.add(r['href'])
            engines_used.append('baidu')
    
    results = all_results[:num_results]
    
    return {
        'success': len(results) > 0,
        'query': query,
        'type': 'general',
        'engine': '+'.join(engines_used) if engines_used else 'none',
        'num_results': len(results),
        'results': results,
        'message': '搜索完成',
        'timestamp': datetime.now().isoformat()
    }


def main(input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """入口函数"""
    if input_data is None:
        input_data = {}
    
    action = input_data.get('action', 'search')
    query = input_data.get('query', '')
    num_results = input_data.get('num_results', 5)
    search_type = input_data.get('type', 'general')
    platform = input_data.get('platform', None)
    
    if action == 'search':
        if search_type == 'social_media':
            return search_social_media(query, platform=platform, num_results=num_results)
        else:
            return web_search(query, num_results=num_results, search_type='general')
    
    elif action == 'test':
        # 测试各搜索引擎可用性
        test_results = {
            'exa': bool(search_exa('test', 1)),
            'bing': bool(search_bing('test', 1)),
            'baidu': bool(search_baidu('test', 1)),
        }
        return {
            'success': True,
            'message': '搜索引擎测试结果',
            'results': test_results
        }
    
    return {'success': False, 'message': f'不支持的操作：{action}'}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        search_type = sys.argv[3] if len(sys.argv) > 3 else 'general'
    else:
        query = "黄金价格"
        num = 5
        search_type = 'general'
    
    result = main({'action': 'search', 'query': query, 'num_results': num, 'type': search_type})
    print(json.dumps(result, ensure_ascii=False, indent=2))
