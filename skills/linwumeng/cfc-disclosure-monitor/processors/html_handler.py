"""
HTML 静态页面处理器
匹配普通公告详情页，抓取完整 HTML → 提取正文文本
"""
import asyncio
import re
from pathlib import Path
from processors import register_handler, ContentHandler, ContentResult


@register_handler
class HTMLHandler(ContentHandler):
    """通用 HTML 页面处理器"""
    name = "html"
    priority = 50

    def match_url(self, url: str) -> bool:
        # 排除已知 PDF 和特殊页面
        if url.lower().endswith(".pdf"):
            return False
        if "#" in url and "layout" in url:
            return False  # Vue SPA 由 VueHandler 处理
        return True

    async def fetch(self, announcement: dict, out_dir: Path, page=None) -> ContentResult:
        url = announcement.get("url", "")
        content_type = announcement.get("category", "")

        if not page:
            return ContentResult(False, "html", error="no browser page provided")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            # 提取纯文本
            text = await page.evaluate("""
                () => {
                    // 移除 script/style/nav/footer
                    const clone = document.body.cloneNode(true);
                    clone.querySelectorAll('script,style,nav,footer,header,[role="navigation"]').forEach(e => e.remove());
                    return clone.innerText.replace(/\s+/g, ' ').trim();
                }
            """)

            # 保存 HTML 原文
            html_content = await page.content()
            html_file = out_dir / "content.html"
            html_file.write_text(html_content, encoding="utf-8")

            # 检查是否有附件（PDF链接等）
            attachments = []
            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href") or ""
                if href.lower().endswith(".pdf"):
                    # 转为绝对路径
                    if not href.startswith("http"):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    fname = Path(urlparse(href).path).name or "attachment.pdf"
                    attachments.append({"filename": fname, "path": href, "type": "pdf_link"})

            return ContentResult(
                success=bool(text),
                content_type="html",
                text=text[:5000],  # 截取前5000字符
                attachments=attachments,
            )

        except Exception as e:
            return ContentResult(False, "html", error=str(e)[:200])

from urllib.parse import urlparse, urljoin
