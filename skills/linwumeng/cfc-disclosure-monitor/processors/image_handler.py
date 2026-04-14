"""
图片公告处理器（扫描件 / 头条文章图片）
匹配 .png/.jpg/.jpeg/.gif 结尾的图片URL
下载图片，用 OCR/图像识别 提取文字
"""
import asyncio
from pathlib import Path
from processors import register_handler, ContentHandler, ContentResult


@register_handler
class ImageHandler(ContentHandler):
    name = "image"
    priority = 5  # 高优先级（URL后缀匹配）

    def match_url(self, url: str) -> bool:
        from urllib.parse import urlparse
        ext = urlparse(url).path.lower().split('.')[-1].split('?')[0]
        return ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp")

    async def fetch(self, announcement: dict, out_dir: Path, page=None) -> ContentResult:
        import urllib.request, urllib.error

        url = announcement.get("url", "")
        title = announcement.get("title", "")
        attachments_dir = out_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        from urllib.parse import urlparse
        filename = Path(urlparse(url).path).name or f"{make_id(title, announcement.get('date',''))}.png"
        filepath = attachments_dir / filename

        text = ""
        error = ""

        try:
            # 下载图片
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    return ContentResult(False, "image", error=f"HTTP {resp.status}")
                data = resp.read()

            filepath.write_bytes(data)
            file_size = len(data)

            # 尝试 OCR（如果有 pytesseract）
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(filepath)
                text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            except ImportError:
                # 没有 OCR，直接保存图片，返回文件路径提示
                text = f"[图片文件已保存，大小: {file_size} bytes，请手动查看]"
                error = "pytesseract not installed"
            except Exception as e:
                error = str(e)[:100]

        except urllib.error.HTTPError as e:
            error = f"HTTP {e.code}"
        except Exception as e:
            error = str(e)[:200]

        attachments = [{
            "filename": filename,
            "path": str(filepath.relative_to(out_dir.parent)) if filepath.exists() else "",
            "size": filepath.stat().st_size if filepath.exists() else 0,
        }] if filepath.exists() else []

        return ContentResult(
            success=bool(text) and filepath.exists(),
            content_type="image_article",
            text=text.strip()[:8000],
            attachments=attachments,
            error=error,
        )


def make_id(title: str, date: str) -> str:
    import hashlib
    key = f"{title[:40]}|{date}"
    return hashlib.md5(key.encode()).hexdigest()[:8]
