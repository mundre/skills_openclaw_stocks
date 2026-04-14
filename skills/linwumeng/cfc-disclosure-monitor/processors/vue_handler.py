"""
Vue / SPA 页面处理器
针对苏银凯基、建信等使用 Vue Router 的页面
等待 JS 执行后再提取内容
"""
import asyncio
from pathlib import Path
from processors import register_handler, ContentHandler, ContentResult


@register_handler
class VueHandler(ContentHandler):
    name = "vue"
    priority = 20

    def match_url(self, url: str) -> bool:
        return "#" in url and ("layout" in url or "News" in url or "information" in url)

    async def fetch(self, announcement: dict, out_dir: Path, page=None) -> ContentResult:
        url = announcement.get("url", "")
        if not page:
            return ContentResult(False, "vue_page", error="no browser page")

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(4)  # 等待 Vue 渲染完成

            # 滚动触发懒加载
            for _ in range(5):
                await page.evaluate("window.scrollBy(0, 600)")
                await asyncio.sleep(0.5)

            text = await page.evaluate("""
                () => {
                    const clone = document.body.cloneNode(true);
                    clone.querySelectorAll('script,style').forEach(e => e.remove());
                    return clone.innerText.replace(/\\s+/g, ' ').trim();
                }
            """)

            html_content = await page.content()
            (out_dir / "content.html").write_text(html_content, encoding="utf-8")

            return ContentResult(success=bool(text), content_type="vue_page", text=text[:5000])

        except Exception as e:
            return ContentResult(False, "vue_page", error=str(e)[:200])
