# -*- coding: utf-8 -*-
"""
学术创新网（xueshuchuangxin.com）理论详情文章爬虫
用法：
  python crawl_theory.py --start 318 --end 2000 --output "C:\AIDOW\lunwen\pdf01" --delay 2
  python crawl_theory.py --start 1 --end 500 --output "D:\output" --delay 3 --no-images

功能：
  - 按guid范围批量采集理论详情页，保存为Markdown
  - 断点续爬：自动跳过已存在文件
  - 浏览器自动重连：检测断连后自动重建
  - 保存后校验：写入后验证文件是否存在
"""

import os
import sys
import time
import re
import argparse
from DrissionPage import ChromiumPage, ChromiumOptions

BASE_URL = "https://www.xueshuchuangxin.com/theory/theoryDetail?guid="

# 页面标题中的站点后缀，需剥离
TITLE_SUFFIXES = ["-青泥学术", "-研究理论", "-青泥学术-研究理论"]

# 内容选择器优先级
CONTENT_SELECTORS = [
    "css:.theory-content",
    "css:.detail-content",
    "css:.article-content",
    "css:.main-content",
    "css:.content",
]

# 最短有效内容长度
MIN_CONTENT_LENGTH = 50
# 最短有效段落长度（备用提取策略）
MIN_PARAGRAPH_LENGTH = 20


def sanitize_filename(title):
    """清理文件名，移除非法字符"""
    illegal_chars = r'[<>:"/\\|?*]'
    title = re.sub(illegal_chars, "_", title)
    title = title.strip(". ")
    if len(title) > 150:
        title = title[:150]
    return title if title else "untitled"


def create_browser(no_images=False):
    """创建无头浏览器实例"""
    try:
        co = ChromiumOptions()
        co.headless()
        if no_images:
            co.no_imgs()
        page = ChromiumPage(co)
        return page
    except Exception as e:
        print(f"[ERROR] Browser create failed: {e}")
        return None


def extract_content(page, guid):
    """
    提取指定guid页面的标题和正文。
    返回 (title, content, error) 三元组：
      - 成功: (title_str, content_str, None)
      - 失败: (None_or_title, None, error_str)
    """
    url = f"{BASE_URL}{guid}"

    try:
        page.get(url)
        time.sleep(2)

        # --- 提取标题 ---
        page_title = page.title
        if not page_title or page_title == "青泥学术":
            return None, None, "Empty title"

        title = page_title
        for suffix in TITLE_SUFFIXES:
            title = title.replace(suffix, "")
        title = title.strip()

        if not title or title == "undefined":
            return None, None, "Invalid title"

        # --- 提取正文（选择器策略）---
        content_text = None
        for selector in CONTENT_SELECTORS:
            try:
                elem = page.ele(selector, timeout=2)
                if elem:
                    text = elem.text.strip()
                    if text and len(text) > 100:
                        content_text = text
                        break
            except Exception:
                continue

        # --- 备用：段落拼接策略 ---
        if not content_text or len(content_text) < MIN_CONTENT_LENGTH:
            try:
                paragraphs = page.eles("tag:p")
                texts = []
                for p in paragraphs:
                    text = p.text.strip()
                    if text and len(text) > MIN_PARAGRAPH_LENGTH:
                        texts.append(text)
                if texts:
                    content_text = "\n\n".join(texts)
            except Exception:
                pass

        if not content_text or len(content_text) < MIN_CONTENT_LENGTH:
            return title, None, "Content too short"

        return title, content_text, None

    except Exception as e:
        error_msg = str(e)
        if "断开" in error_msg or "disconnect" in error_msg.lower():
            return None, None, "BROWSER_DISCONNECTED"
        return None, None, error_msg[:80]


def validate_output_dir(output_dir):
    """验证输出目录是否可写"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        test_file = os.path.join(output_dir, ".write_test_tmp")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_file)
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="学术创新网理论详情文章爬虫")
    parser.add_argument("--start", type=int, required=True, help="起始guid")
    parser.add_argument("--end", type=int, required=True, help="结束guid")
    parser.add_argument("--output", type=str, required=True, help="输出目录路径")
    parser.add_argument("--delay", type=float, default=2.0, help="请求间隔秒数（默认2）")
    parser.add_argument("--no-images", action="store_true", help="不加载图片（加速）")
    parser.add_argument("--max-reconnect", type=int, default=5, help="最大重连次数（默认5）")
    args = parser.parse_args()

    print("=" * 60)
    print("学术创新网 理论详情文章爬虫")
    print(f"范围: guid {args.start} - {args.end} ({args.end - args.start + 1} 篇)")
    print(f"输出: {args.output}")
    print(f"格式: guid_title.md")
    print(f"延时: {args.delay}s")
    print("=" * 60)

    # 验证输出目录
    ok, err = validate_output_dir(args.output)
    if not ok:
        print(f"[FAIL] 输出目录不可写: {err}")
        sys.exit(1)
    print("[OK] 输出目录就绪")

    success = 0
    fail = 0
    skip = 0
    page = None
    reconnect_count = 0

    print("\n[启动浏览器...]")

    try:
        for guid in range(args.start, args.end + 1):
            # --- 浏览器状态检查 ---
            if page is None:
                print(f"\n[重新连接浏览器...]")
                page = create_browser(no_images=args.no_images)
                if page is None:
                    print("[WARN] 浏览器创建失败，10秒后重试...")
                    time.sleep(10)
                    continue
                reconnect_count = 0

            # --- 断点续爬 ---
            try:
                existing = [f for f in os.listdir(args.output) if f.startswith(f"{guid}_")]
                if existing:
                    print(f"[{guid}/{args.end}] Skip: 已存在")
                    skip += 1
                    time.sleep(0.5)
                    continue
            except Exception:
                pass

            print(f"[{guid}/{args.end}] ", end="", flush=True)

            title, content, error = extract_content(page, guid)

            # --- 断连处理 ---
            if error == "BROWSER_DISCONNECTED":
                print("浏览器断开，正在重连...")
                try:
                    page.quit()
                except Exception:
                    pass
                page = None
                reconnect_count += 1
                if reconnect_count >= args.max_reconnect:
                    print(f"[WARN] 重连次数过多（{reconnect_count}），等待5分钟...")
                    time.sleep(300)
                    reconnect_count = 0
                guid -= 1  # 重试当前guid
                continue

            # --- 失败处理 ---
            if error:
                print(f"Fail: {error[:40]}")
                fail += 1
                time.sleep(args.delay)
                continue

            if not title or not content:
                print("Fail: 内容为空")
                fail += 1
                time.sleep(args.delay)
                continue

            # --- 保存文件 ---
            safe_title = sanitize_filename(title)
            filename = f"{guid}_{safe_title}.md"
            filepath = os.path.join(args.output, filename)

            md_content = (
                f"# {title}\n\n"
                f"{content}\n\n"
                f"---\n"
                f"*GUID: {guid}*\n"
                f"*Crawled: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"
            )

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(md_content)
                # 保存后校验
                if os.path.exists(filepath):
                    print(f"OK: {title}")
                    success += 1
                else:
                    print(f"Verify fail: {title}")
                    fail += 1
            except Exception as e:
                print(f"Save fail: {e}")
                fail += 1

            time.sleep(args.delay)

        print("\n" + "=" * 60)
        print(f"完成! 成功:{success} 失败:{fail} 跳过:{skip}")
        print(f"输出: {args.output}")
        print("=" * 60)

    except KeyboardInterrupt:
        print(f"\n\n中断! 成功:{success} 失败:{fail} 跳过:{skip}")
    finally:
        if page:
            try:
                page.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()
