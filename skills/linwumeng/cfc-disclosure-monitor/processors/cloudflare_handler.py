"""
Cloudflare绕过处理器
cloudscraper自动处理Challenge页面，返回干净HTML
适用于被Cloudflare WAF拦截的站点（如 boccfc.cn、sykcfc.cn）
"""
import re
import cloudscraper
from pathlib import Path
from urllib.parse import urlparse, urljoin
from processors import register_handler, ContentHandler, ContentResult


@register_handler
class CloudflareHandler(ContentHandler):
    """Cloudflare WAF 绕过处理器（cloudscraper）"""
    name = "cloudflare"
    priority = 8  # 高优先级（优先于 HTMLHandler）

    # Cloudflare 阻断关键词
    CF_PATTERNS = (
        'cf-error-details',
        'RayID',
        '__cf_chl_rt',
        'cdn-cgi/trace',
        'Cloudflare',
        'attention-required',
        'check-your-browser',
    )

    def match_url(self, url: str) -> bool:
        # 明确知道被 Cloudflare 保护的站点
        blocked = ('boccfc.cn', 'sykcfc.cn', 'hncy58.com')
        return any(d in url for d in blocked)

    def match_content_type(self, content_type_hint: str) -> bool:
        return False

    async def fetch(self, announcement: dict, out_dir: Path, page=None) -> ContentResult:
        import concurrent.futures
        url = announcement.get("url", "")

        html_file = out_dir / "content.html"

        def _sync_fetch():
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
            # Cloudflare JS challenge 有时卡住，最多等15秒
            return scraper.get(url, timeout=15)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_sync_fetch)
                resp = future.result(timeout=20)
        except Exception as e:
            return ContentResult(False, "cloudflare", error=str(e)[:200])
            status = resp.status_code

            if status == 200:
                html_content = resp.text
                html_file.write_text(html_content, encoding="utf-8")

                # 清理 HTML 提取纯文本
                text = self._extract_text(html_content)

                # 找附件
                attachments = []
                for match in re.finditer(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html_content, re.I):
                    href = match.group(1)
                    if not href.startswith("http"):
                        href = urljoin(url, href)
                    fname = Path(urlparse(href).path).name or "attachment.pdf"
                    attachments.append({"filename": fname, "path": href, "type": "pdf_link"})

                return ContentResult(
                    success=bool(text),
                    content_type="html_cf",
                    text=text[:5000],
                    attachments=attachments,
                )
            elif status in (403, 412, 429):
                return ContentResult(False, "cloudflare", error=f"HTTP {status} (Cloudflare blocked)")
            else:
                return ContentResult(False, "cloudflare", error=f"HTTP {status}")

        except cloudscraper.exceptions.CloudflareChallengeError:
            return ContentResult(False, "cloudflare", error="Cloudflare challenge failed")
        except Exception as e:
            return ContentResult(False, "cloudflare", error=str(e)[:200])

    def _extract_text(self, html: str) -> str:
        """从 HTML 提取干净文本"""
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<noscript[^>]*>.*?</noscript>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'&nbsp;', ' ', clean)
        clean = re.sub(r'&amp;', '&', clean)
        clean = re.sub(r'&#\d+;', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean


from urllib.parse import urlparse, urljoin
