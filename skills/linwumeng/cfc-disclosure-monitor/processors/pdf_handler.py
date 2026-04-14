"""
PDF 附件处理器
匹配 .pdf 结尾的 URL，下载并用 pdfplumber 提取文本
"""
import asyncio
import shutil
from pathlib import Path
from processors import register_handler, ContentHandler, ContentResult, make_id
from urllib.parse import urlparse


@register_handler
class PDFHandler(ContentHandler):
    name = "pdf"
    priority = 10  # 高优先级（URL后缀匹配）

    def match_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.path.lower().endswith(".pdf")

    async def fetch(self, announcement: dict, out_dir: Path, page=None) -> ContentResult:
        url = announcement.get("url", "")
        title = announcement.get("title", "")

        attachments_dir = out_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        # 从 URL 提取文件名
        parsed = urlparse(url)
        filename = Path(parsed.path).name or f"{make_id(title, announcement.get('date',''))}.pdf"
        filepath = attachments_dir / filename

        # 下载 PDF（直接 aiohttp，不依赖 playwright tab 行为）
        text = ""
        error = ""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        return ContentResult(False, "pdf", error=f"HTTP {resp.status}")
                    data = await resp.read()

            filepath.write_bytes(data)

            # 提取文本
            try:
                import pdfplumber
                with pdfplumber.open(filepath) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text() or ""
                        text += t + "\n"
            except ImportError:
                error = "pdfplumber not installed (binary saved only)"

        except asyncio.TimeoutError:
            error = "timeout"
        except Exception as e:
            error = str(e)[:200]

        attachments = [{
            "filename": filename,
            "path": str(filepath.relative_to(out_dir.parent)) if filepath.exists() else "",
            "size": filepath.stat().st_size if filepath.exists() else 0,
        }] if filepath.exists() else []

        return ContentResult(
            success=bool(text or filepath.exists()),
            content_type="pdf",
            text=text.strip()[:10000],  # 最多1万字符
            attachments=attachments,
            error=error,
        )
