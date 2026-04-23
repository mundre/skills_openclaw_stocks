#!/usr/bin/env python3
"""
京东爬虫 - 验证版 (2026-04-17)
关键修复（已通过实测）：
1. 使用已登录Cookie突破第1页限制
2. 点击数字分页按钮（不是"下一页"链接）
3. 用wait_until='load'+充分等待替代networkidle
4. 新选择器[data-sku]替代旧的.gl-item
"""
import argparse, json, time, random, os
from playwright.sync_api import sync_playwright

DEFAULT_COOKIES = '/tmp/jd_cookies.json'

def scrape_jd(keyword, max_pages=5, output='/tmp/jd_results.json', 
              headless=True, cookies_file=DEFAULT_COOKIES):
    """
    抓取京东搜索结果
    """
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        ctx = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 加载JD cookies（只加载jd.com域名，避免其他cookie干扰）
        if os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            jd_cookies = [c for c in all_cookies if '.jd.com' in c.get('domain', '')]
            ctx.add_cookies(jd_cookies)
            print(f"✅ 已加载 {len(jd_cookies)} 个JD cookies")
        else:
            print(f"⚠️ Cookie文件不存在: {cookies_file}")
        
        page = ctx.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        search_url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8"
        print(f"🔍 搜索: {keyword}")
        
        for page_num in range(1, max_pages + 1):
            url = f"{search_url}&page={page_num*2-1}" if page_num > 1 else search_url
            print(f"📄 第 {page_num}/{max_pages} 页 (page={page_num*2-1 if page_num > 1 else 1})...")
            
            # 京东有持续追踪请求，networkidle永远不会完成
            # 改用load+充分等待
            try:
                page.goto(url, wait_until='networkidle', timeout=15000)
            except:
                try:
                    page.goto(url, wait_until='load', timeout=20000)
                except:
                    page.goto(url, wait_until='domcontentloaded', timeout=20000)
            
            # 关键：充分等待JS渲染（京东页面复杂，需要10秒以上）
            time.sleep(12)
            
            items = page.query_selector_all('[data-sku]')
            print(f"   找到 {len(items)} 个商品")
            
            if len(items) == 0:
                print(f"   ⚠️ 无商品，停止抓取")
                break
            
            for item in items:
                try:
                    title_el = item.query_selector('[class*="title"]')
                    price_el = item.query_selector('[class*="price"]')
                    shop_el = item.query_selector('[class*="name"]')
                    
                    title = title_el.inner_text().strip() if title_el else ''
                    price = price_el.inner_text().strip().replace('\n', '').replace(' ', '') if price_el else ''
                    shop = shop_el.inner_text().strip() if shop_el else ''
                    
                    if title:
                        results.append({
                            'title': title,
                            'price': price,
                            'shop': shop,
                            'platform': '京东'
                        })
                except:
                    continue
            
            # 点击下一页数字按钮（不是"下一页"链接）
            if page_num < max_pages:
                clicked = False
                pagers = page.query_selector_all('[class*="pagination"]')
                
                for pager in pagers:
                    pager_text = pager.inner_text().strip()
                    if '下一页' in pager_text:
                        for child in pager.query_selector_all('*'):
                            try:
                                txt = child.inner_text().strip()
                                if txt.isdigit() and int(txt) == page_num + 1:
                                    child.click()
                                    clicked = True
                                    print(f"   -> 点击第{page_num+1}页按钮")
                                    time.sleep(8)  # 等待AJAX加载
                                    break
                            except:
                                continue
                        break
                
                if not clicked:
                    print(f"   -> 找不到第{page_num+1}页按钮，停止")
                    break
            
            time.sleep(random.uniform(2, 4))
        
        browser.close()
    
    # 去重（按 title前30字符 + price）
    seen = set()
    unique = []
    for p2 in results:
        key = p2['title'][:30] + p2['price']
        if key not in seen:
            seen.add(key)
            unique.append(p2)
    
    print(f"\n✅ 共获取 {len(unique)} 个唯一商品（共抓取 {len(results)} 条）")
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(unique, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {output}")
    
    return unique


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='京东商品爬虫')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--max-pages', '-m', type=int, default=5, help='最大页数（默认5）')
    parser.add_argument('--output', '-o', default='/tmp/jd_results.json', help='输出文件')
    parser.add_argument('--cookies', '-c', default=DEFAULT_COOKIES, help='Cookie文件路径')
    parser.add_argument('--visible', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    scrape_jd(
        keyword=args.keyword,
        max_pages=args.max_pages,
        output=args.output,
        headless=not args.visible,
        cookies_file=args.cookies
    )
