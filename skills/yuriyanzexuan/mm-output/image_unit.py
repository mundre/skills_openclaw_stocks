import base64
import io
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from PIL import Image

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None


_EN_STOPWORDS = {
    "the","is","are","a","an","and","or","to","of","in","on","for","with","as","at","by","from","that","this",
    "be","been","was","were","it","its","we","you","they","he","she","his","her","our","their","not","no","yes",
    "can","could","may","might","will","would","shall","should","than","then","there","here","how","what","when",
    "which","who","whom","why","into","over","under","about","between","across","within","without","via"
}
_CN_STOPWORDS = {
    "的","了","在","是","我","有","和","就","不","人","都","一","一个","上","也","很","到","说","要","去","你","会","着","没有",
    "看","好","自己","这","那","对","与","及","并","及其","通过","进行","同时","以及","其中","基于","有关","相关"
}


@dataclass
class WebImage:
    keyword: str
    title: str
    filepath: str
    rel_path: str
    source: Optional[str] = None
    domain: Optional[str] = None
    link: Optional[str] = None
    image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    score: Optional[float] = None  # relevance score (heuristic or VLM)


class AutoImageUnit:
    def __init__(self) -> None:
        self.name = "AutoImageUnit"
        self.api_key_env = os.getenv("SERPER_API_KEY_ENV") or "X_API_KEY"
        self.serper_api_key = os.getenv(self.api_key_env)  # Compatible with GoogleSearchService.py X_API_KEY
        self.serper_endpoint = os.getenv("SERPER_ENDPOINT") or "https://google.serper.dev/images"
        # Relative storage path under output directory
        self.subdir = "assets/auto_images"

    # ---------- Keyword Extraction ----------
    def extract_keywords_via_llm(self, md_path: str, max_keywords: int = 5) -> List[str]:
        """
        Extract keywords from Markdown using HTTP Chat Completions (same style as renderer_unit.py).
        Required environment variables:
          - OPENAI_API_KEY or RUNWAY_API_KEY
          - OPENAI_BASE_URL or RUNWAY_API_BASE (optional)
          - RUNWAY_API_VERSION (optional, default 2024-12-01-preview)
          - TEXT_MODEL (optional, default gpt-4.1-2025-04-14)
        """
        text = Path(md_path).read_text(encoding="utf-8")[:8000]
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("RUNWAY_API_BASE") or "https://runway.devops.xiaohongshu.com/openai"
        api_version = os.getenv("RUNWAY_API_VERSION") or "2024-12-01-preview"
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise RuntimeError("HTTP client not configured (missing api key) for keyword extraction")
        model = os.getenv("TEXT_MODEL") or "gpt-4.1-2025-04-14"
        system_prompt = (
            "You are a professional information extraction assistant. Extract the most critical thematic keywords from the user-provided Markdown text. "
            "Return strictly a JSON array (array only), with array elements as keyword strings. Do not include any explanation. "
            f"Limit to at most {max_keywords} keywords, preferring short words or proper nouns."
        )
        user_payload = {"md_text": text, "max_keywords": max_keywords}
        endpoint = f"{base_url.rstrip('/')}/chat/completions?api-version={api_version}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        body = {
            "model": model,
            "temperature": 0.0,
            "max_tokens": 8192, # Pass the (potentially larger) token limit
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
        }
        r = requests.post(endpoint, headers=headers, json=body, timeout=60)
        if r.status_code < 200 or r.status_code >= 300:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
        data = r.json()
        choices = data.get("choices") or []
        content = (choices[0].get("message", {}).get("content") if choices else "") or ""
        content = self._strip_code_fences(content)
        arr = json.loads(content)
        if not isinstance(arr, list):
            raise RuntimeError("LLM keyword parse failed: not list")
        kws: List[str] = []
        for x in arr:
            if isinstance(x, str):
                t = x.strip()
                if t and not self._is_noise_token(t.lower()):
                    kws.append(t)
            if len(kws) >= max_keywords:
                break
        return kws[:max_keywords]

    def extract_keywords_from_md(self, md_path: str, max_keywords: int = 5) -> List[str]:
        text = Path(md_path).read_text(encoding="utf-8")
        # 1) Boost weight for headings/bold text
        weighted_tokens: Dict[str, int] = {}
        lines = text.splitlines()
        for raw in lines:
            line = raw.strip()
            weight = 1
            if line.startswith("#"):
                weight = 4
            bolds = re.findall(r"\*\*(.+?)\*\*", line)
            if bolds:
                for b in bolds:
                    for t in self._tokenize(b):
                        if not self._is_noise_token(t):
                            weighted_tokens[t] = weighted_tokens.get(t, 0) + 3
            # Normal tokenization
            for t in self._tokenize(line):
                if not self._is_noise_token(t):
                    weighted_tokens[t] = weighted_tokens.get(t, 0) + weight
        # Sort and trim
        ranked = sorted(weighted_tokens.items(), key=lambda kv: kv[1], reverse=True)
        return [w for w, _ in ranked[:max(1, max_keywords)]]

    def _tokenize(self, text: str) -> List[str]:
        # Mixed Chinese-English tokenization (simplified)
        tokens: List[str] = []
        # English words
        for w in re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}", text):
            tokens.append(w.lower())
        # Chinese (contiguous CJK character segments)
        for seg in re.findall(r"[\u4e00-\u9fff]{2,}", text):
            # Rough split into 2-3 char windows for better recall
            for i in range(0, len(seg) - 1, 2):
                tokens.append(seg[i:i+2])
        return tokens

    def _is_noise_token(self, t: str) -> bool:
        if len(t) <= 1:
            return True
        if t in _EN_STOPWORDS or t in _CN_STOPWORDS:
            return True
        if re.fullmatch(r"\d+(\.\d+)?", t):
            return True
        return False

    # ---------- Image Search & Download ----------
    def search_and_download_images(self, keywords: List[str], output_dir: str, max_per_keyword: int = 2) -> List[WebImage]:
        out_dir = Path(output_dir)
        save_dir = out_dir / self.subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        results: List[WebImage] = []

        for kw in keywords:
            items = self._search_images_serper(kw) if self.serper_api_key else []
            count = 0
            for item in items:
                if count >= max_per_keyword:
                    break
                image_url = item.get("imageUrl")
                if not image_url:
                    continue
                try:
                    local_path = self._download_image(image_url, save_dir)
                    if not local_path:
                        continue
                    pil = Image.open(local_path)
                    rel = str(Path(self.subdir) / Path(local_path).name)
                    wi = WebImage(
                        keyword=kw,
                        title=item.get("title") or kw,
                        filepath=str(local_path),
                        rel_path=rel,
                        source=item.get("source"),
                        domain=item.get("domain"),
                        link=item.get("link"),
                        image_url=image_url,
                        width=getattr(pil, "width", None),
                        height=getattr(pil, "height", None),
                    )
                    results.append(wi)
                    count += 1
                except Exception:
                    continue

        # Simple heuristic scoring: overlap between title and keywords
        for img in results:
            img.score = self._heuristic_score(img.title or "", keywords)
        # Sort
        results.sort(key=lambda x: (x.score or 0), reverse=True)
        return results

    def _search_images_serper(self, query: str) -> List[Dict[str, Any]]:
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {"q": query}
        r = requests.post(self.serper_endpoint, headers=headers, json=payload, timeout=30)
        if r.status_code < 200 or r.status_code >= 300:
            return []
        data = r.json()
        return data.get("images") or []

    def _download_image(self, url: str, save_dir: Path) -> Optional[Path]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            }
            r = requests.get(url, timeout=30, stream=True, headers=headers)
            if r.status_code != 200:
                return None
            # Accept raster image types only, exclude svg
            ctype = (r.headers.get("Content-Type") or "").lower()
            if not ctype.startswith("image/") or "svg" in ctype:
                return None
            # Extension detection
            ext = ".jpg"
            if "png" in ctype:
                ext = ".png"
            elif "webp" in ctype:
                ext = ".webp"
            elif "gif" in ctype:
                ext = ".gif"
            filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", Path(url).name)[:80] or "img"
            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                filename += ext
            path = save_dir / filename
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            # File validation: try to open and verify
            try:
                with Image.open(path) as im:
                    im.verify()
                # Re-open to get dimensions (must reopen after verify)
                with Image.open(path) as _:
                    pass
            except Exception:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                return None
            return path
        except Exception:
            return None

    def _heuristic_score(self, title: str, keywords: List[str]) -> float:
        t = title.lower()
        score = 0.0
        for kw in keywords:
            if kw.lower() in t:
                score += 1.0
        return score

    # ---------- Optional VLM selection ----------
    def select_images_via_vlm(self, md_path: str, images_info: List[WebImage], output_dir: str, top_k: int = 6) -> List[WebImage]:
        """
        Use a multimodal model to score image relevance and return TopK.
        API call style matches renderer_unit.py HTTP path:
         - Based on OPENAI_BASE_URL or RUNWAY base URL, call /chat/completions?api-version=...
         - Header uses api-key
         - Body is {model, temperature, max_tokens, messages}
        Raises exception if env not configured or call fails; caller falls back to heuristic.
        """
        # Read HTTP direct config (consistent with renderer_unit.py)
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("RUNWAY_API_BASE") or "https://runway.devops.xiaohongshu.com/openai"
        api_version = os.getenv("RUNWAY_API_VERSION") or "2024-12-01-preview"
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise RuntimeError("VLM HTTP client not configured (missing api key)")
        model = os.getenv("VISION_MODEL") or os.getenv("TEXT_MODEL") or "gpt-4.1"

        md_text = Path(md_path).read_text(encoding="utf-8")
        md_text = md_text[:4000]

        # Build multimodal message content (content blocks supported by HTTP chat.completions)
        contents: List[Dict[str, Any]] = [{"type": "text", "text": self._vlm_instruction(md_text)}]
        used_images: List[WebImage] = []
        for img in images_info:
            try:
                b64 = self._encode_image_small(img.filepath, max_w=512)
                if not b64:
                    continue
                contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}"
                    }
                })
                used_images.append(img)
            except Exception:
                continue

        if not used_images:
            raise RuntimeError("No images available for VLM scoring")

        endpoint = f"{base_url.rstrip('/')}/chat/completions?api-version={api_version}"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }
        body = {
            "model": model,
            "temperature": 0.0,
            "max_tokens": 8192, # Pass the (potentially larger) token limit
            "messages": [
                {"role": "user", "content": contents}
            ],
        }
        r = requests.post(endpoint, headers=headers, json=body, timeout=60)
        if r.status_code < 200 or r.status_code >= 300:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
        data = r.json()
        choices = data.get("choices") or []
        content = (choices[0].get("message", {}).get("content") if choices else "") or ""
        scores: List[float] = self._parse_scores(content, expected=len(used_images))
        for i, img in enumerate(used_images):
            img.score = float(scores[i]) if i < len(scores) else (img.score or 0.0)
        used_images.sort(key=lambda x: (x.score or 0.0), reverse=True)
        return used_images[:max(1, top_k)]

    def _vlm_instruction(self, md_text: str) -> str:
        return (
            "You will see text from a paper/poster and multiple images. Based on the text semantics, evaluate relevance for each image. "
            "Output only a JSON array where each element is a float between 0 and 1 representing the relevance score for the corresponding image. "
            "Score order must match image order. Do not output any explanatory text.\n\nText:\n" + md_text
        )

    def _encode_image_small(self, path: str, max_w: int = 512) -> Optional[str]:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        if w > max_w:
            ratio = max_w / float(w)
            img = img.resize((max_w, int(h * ratio)))
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b = buf.getvalue()
        return base64.b64encode(b).decode("utf-8")

    def _parse_scores(self, text: str, expected: int) -> List[float]:
        try:
            arr = json.loads(text.strip())
            if isinstance(arr, list) and all(isinstance(x, (int, float)) for x in arr):
                # Normalize and trim count
                vals = [max(0.0, min(1.0, float(x))) for x in arr][:expected]
                if len(vals) < expected:
                    vals += [0.0] * (expected - len(vals))
                return vals
        except Exception:
            pass
        # Parse failed, fallback to all zeros
        return [0.0] * expected

    # ---------- Persist Metadata ----------
    def write_web_images_meta(self, images: List[WebImage], output_dir: str) -> str:
        assets_dir = Path(output_dir) / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        meta_path = assets_dir / "web_images.json"
        payload = []
        for img in images:
            payload.append({
                "keyword": img.keyword,
                "title": img.title,
                "rel_path": img.rel_path,
                "filepath": img.filepath,
                "source": img.source,
                "domain": img.domain,
                "link": img.link,
                "image_url": img.image_url,
                "width": img.width,
                "height": img.height,
                "score": img.score,
            })
        meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(meta_path)

    def cleanup_auto_images(self, output_dir: str, keep_filepaths: List[str]) -> int:
        """
        Remove leftover files under auto_images directory that are not referenced by metadata. Returns count of removed files.
        """
        base = Path(output_dir) / self.subdir
        if not base.exists():
            return 0
        keep_set = {str(Path(p)) for p in keep_filepaths}
        removed = 0
        for p in base.glob("*"):
            try:
                if str(p) not in keep_set:
                    p.unlink()
                    removed += 1
            except Exception:
                continue
        return removed

    # ---------- Helpers ----------
    def _strip_code_fences(self, text: str) -> str:
        if not text:
            return text
        t = text.strip()
        t = re.sub(r"^\s*```[a-zA-Z0-9_-]*\s*\n", "", t)
        t = re.sub(r"\n?\s*```\s*$", "", t)
        return t.strip()


