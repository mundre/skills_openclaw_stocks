
import json
import os
import markdown
from pathlib import Path
from typing import Any, Dict, List
import requests
import re

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # lazy import fallback

class PosterGenRendererUnit:
    def __init__(self):
        self.name = "PosterGenRendererUnit"
        print(f"Initializing {self.name}")

    def render(self, parser_results: dict, output_dir: str, mode: str = "llm", model_id: str = None, temperature: float = None, max_tokens: int = None, max_attempts: int = None, template_name: str = None):
        """
        Renders the parsed content into an HTML file.
        mode: "llm" (default) to render via LLM with doubao template, or "simple" to use basic preview.
        """
        print(f"[{self.name}] Starting rendering process...")
        output_path = Path(output_dir)
        # Ensure output directory exists
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            # Clean up old HTML render results to avoid confusion in the output folder
            # This ensures that only the currently generated HTMLs are present.
            for old_html in output_path.glob("poster_llm*.html"):
                try:
                    old_html.unlink()
                except Exception as e:
                    print(f"[{self.name}] Warning: Failed to delete old file {old_html}: {e}")
            # Also clean up preview if exists
            preview_html = output_path / "poster_preview.html"
            if preview_html.exists():
                 try:
                    preview_html.unlink()
                 except Exception:
                    pass

        # Define paths from parser results
        raw_text_path = Path(parser_results['raw_text_path'])
        figures_path = Path(parser_results.get('figures_path', Path(output_path / 'assets' / 'figures.json')))
        tables_path = Path(parser_results.get('tables_path', Path(output_path / 'assets' / 'tables.json')))
        web_images_path = Path(parser_results.get('web_images_path', Path(output_path / 'assets' / 'web_images.json')))

        if not raw_text_path.exists():
            print(f"[{self.name}] Error: Markdown file not found at {raw_text_path}")
            return None

        # Read content from files
        raw_text = raw_text_path.read_text(encoding='utf-8')
        if figures_path.exists():
            try:
                with open(figures_path, 'r', encoding='utf-8') as f:
                    figures = json.load(f)
            except Exception as e:
                print(f"[{self.name}] Warning: Failed to load figures from {figures_path}: {e}")
                figures = {}
        else:
            figures = {}
        if tables_path.exists():
            try:
                with open(tables_path, 'r', encoding='utf-8') as f:
                    tables = json.load(f)
            except Exception as e:
                print(f"[{self.name}] Warning: Failed to load tables from {tables_path}: {e}")
                tables = {}
        else:
            tables = {}
        # Load auto-downloaded web images
        # If web_images_path is not in parser_results, auto-image feature was not enabled for this run
        # In that case, do not load any possibly stale web_images.json file
        if 'web_images_path' in parser_results and web_images_path.exists():
            try:
                with open(web_images_path, 'r', encoding='utf-8') as f:
                    web_images = json.load(f)
            except Exception:
                web_images = []
        else:
            web_images = []

        mode = (mode or "llm").lower()
        if mode == "llm":
            try:
                # Prefer template_name parameter or POSTER_TEMPLATE env var
                # If either is set, use that specific template for rendering
                target_template = template_name or os.getenv("POSTER_TEMPLATE")
                
                if target_template:
                    # Single-template rendering mode
                    print(f"[{self.name}] Using specified template: {target_template}")
                    html = self._render_via_llm(output_path, raw_text, figures, tables, web_images, model_id=model_id, temperature=temperature, max_tokens=max_tokens, max_attempts=max_attempts, template_name=target_template)
                    
                    # Use template name as part of output filename, or keep default poster_llm.html
                    # To avoid ambiguity: if a specific path is given, extract the stem; for default logic, use poster_llm.html
                    stem = Path(target_template).stem
                    if stem == "doubao": # default behavior compat
                        out_name = "poster_llm.html"
                    else:
                        out_name = f"poster_llm__{stem}.html"
                        
                    html_output_path = output_path / out_name
                    html_output_path.write_text(html, encoding='utf-8')
                    print(f"[{self.name}] Successfully rendered HTML poster via LLM to: {html_output_path}")
                    return str(html_output_path)
                else:
                    # No template specified: scan all .txt templates and render (multi-template mode)
                    template_files = self._list_templates()
                    if not template_files:
                        # Fallback: use default doubao.txt
                        print(f"[{self.name}] No templates found or specified, falling back to default.")
                        template_html = self._load_doubao_template()
                        html = self._render_via_llm_with_template(template_html, output_path, raw_text, figures, tables, web_images, model_id=model_id, temperature=temperature, max_tokens=max_tokens, max_attempts=max_attempts)
                        html_output_path = output_path / "poster_llm.html"
                        html_output_path.write_text(html, encoding='utf-8')
                        print(f"[{self.name}] Successfully rendered HTML poster via LLM to: {html_output_path}")
                        return str(html_output_path)
                    
                    print(f"[{self.name}] No specific template specified, rendering all {len(template_files)} templates found...")
                    rendered_paths = []
                    for path in template_files:
                        template_html = Path(path).read_text(encoding='utf-8')
                        html = self._render_via_llm_with_template(template_html, output_path, raw_text, figures, tables, web_images, model_id=model_id, temperature=temperature, max_tokens=max_tokens, max_attempts=max_attempts)
                        out_name = f"poster_llm__{Path(path).stem}.html"
                        out_path = output_path / out_name
                        out_path.write_text(html, encoding='utf-8')
                        print(f"[{self.name}] Rendered via LLM with template '{Path(path).name}' -> {out_path}")
                        rendered_paths.append(str(out_path))
                    return rendered_paths
            except Exception as e:
                print(f"[{self.name}] LLM rendering failed, falling back to simple preview. Error: {e}")
                import traceback
                traceback.print_exc()
                # fall through to simple mode

        # simple preview rendering
        final_html = self._render_simple(raw_text, figures, tables, web_images)
        html_output_path = output_path / "poster_preview.html"
        html_output_path.write_text(final_html, encoding='utf-8')
        print(f"[{self.name}] Successfully rendered HTML poster to: {html_output_path}")
        return str(html_output_path)

    def _render_simple(self, raw_text: str, figures: Dict[str, Any], tables: Dict[str, Any], web_images: list) -> str:
        """
        Natural single-column layout (not three-column): place one Hero image at top, insert the rest
        below matching sections via simple semantic matching; show native figures/tables as appendix.
        """
        html_template = self._get_html_template()

        # 1) Split sections by headings
        sections = []
        current = {"heading": None, "level": 0, "lines": []}
        for ln in raw_text.splitlines():
            m = re.match(r"^(#{1,6})\s+(.*)$", ln.strip())
            if m:
                if current["heading"] is not None or current["lines"]:
                    sections.append(current)
                current = {"heading": m.group(2).strip(), "level": len(m.group(1)), "lines": []}
            else:
                current["lines"].append(ln)
        if current["heading"] is not None or current["lines"]:
            sections.append(current)
        if not sections:
            sections = [{"heading": None, "level": 0, "lines": raw_text.splitlines()}]

        # 2) Pick Hero + assign the rest
        def area_score(w: dict) -> float:
            return float(w.get("width") or 0) * float(w.get("height") or 0)
        def composite_score(w: dict) -> float:
            return float(w.get("score") or 0.0) * 10.0 + area_score(w)
        valid_web = [w for w in web_images if (w.get("image_url") or w.get("rel_path"))]
        hero_html = ""
        if valid_web:
            valid_web.sort(key=composite_score, reverse=True)
            top = valid_web[0]
            hero_url = top.get("image_url") or top.get("rel_path") or ""
            hero_title = top.get("title") or top.get("keyword") or "Hero"
            hero_html = f"""
            <div class="hero-banner">
                <img src="{hero_url}" alt="{hero_title}">
                <div class="hero-caption">{hero_title}</div>
            </div>
            """
            remaining = valid_web[1:]
        else:
            remaining = []

        # 3) Simple semantic matching: pick best section by token overlap of heading/body with image title/keyword/domain
        def tokenize(s: str) -> set:
            if not s:
                return set()
            toks = set()
            for w in re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}", s.lower()):
                toks.add(w)
            for seg in re.findall(r"[\u4e00-\u9fff]{1,}", s):
                toks |= set(list(seg))
            return toks
        section_tokens = []
        for sec in sections:
            tokens = tokenize((sec["heading"] or "") + " " + "\n".join(sec["lines"]))
            section_tokens.append(tokens)

        assigned = {i: [] for i in range(len(sections))}
        for w in remaining:
            tokens = tokenize((w.get("title") or "") + " " + (w.get("keyword") or "") + " " + (w.get("domain") or ""))
            best_idx, best_overlap = 0, -1
            for idx, tok in enumerate(section_tokens):
                overlap = len(tokens & tok)
                if overlap > best_overlap:
                    best_idx, best_overlap = idx, overlap
            assigned[best_idx].append(w)

        # 4) Generate body + per-section image gallery
        article_parts = []
        for idx, sec in enumerate(sections):
            md_block = ""
            if sec["heading"] is not None:
                md_block += ("#" * max(1, sec["level"])) + " " + sec["heading"] + "\n\n"
            if sec["lines"]:
                md_block += "\n".join(sec["lines"])
            html_block = markdown.markdown(md_block) if md_block.strip() else ""

            imgs_html = ""
            for w in assigned.get(idx, []):
                url = w.get("image_url") or w.get("rel_path") or ""
                title = w.get("title") or w.get("keyword") or ""
                width = w.get("width") or 0
                height = w.get("height") or 0
                ratio_class = "square"
                try:
                    if width and height:
                        aspect = float(width) / float(height)
                        ratio_class = "landscape" if aspect >= 1.3 else ("portrait" if aspect <= 0.77 else "square")
                except Exception:
                    ratio_class = "square"
                imgs_html += f"""
                <div class="gallery-item {ratio_class}">
                    <img src="{url}" alt="{title}">
                    <p class="caption">{title}</p>
                </div>
                """
            if imgs_html:
                imgs_html = f'<div class="gallery-grid">{imgs_html}\n</div>'
            article_parts.append(html_block + imgs_html)

        # 5) Appendix: native figures/tables
        appendix = ""
        if figures:
            fig_html = ""
            for fig_id, fig_data in figures.items():
                img_path = Path(fig_data['path'])
                rel = Path('assets') / img_path.name
                fig_html += f"""
                <div class="gallery-item">
                    <img src="{rel}" alt="{fig_data.get('caption','')}">
                    <p class="caption"><strong>Figure {fig_id}</strong> {fig_data.get('caption','')}</p>
                </div>
                """
            if fig_html:
                appendix += f'<h2>Figures</h2><div class="gallery-grid">{fig_html}</div>'
        if tables:
            tab_html = ""
            for tab_id, tab_data in tables.items():
                img_path = Path(tab_data['path'])
                rel = Path('assets') / img_path.name
                tab_html += f"""
                <div class="gallery-item">
                    <img src="{rel}" alt="{tab_data.get('caption','')}">
                    <p class="caption"><strong>Table {tab_id}</strong> {tab_data.get('caption','')}</p>
                </div>
                """
            if tab_html:
                appendix += f'<h2>Tables</h2><div class="gallery-grid">{tab_html}</div>'

        article_content = "\n".join([p for p in article_parts if p.strip()]) + (("\n" + appendix) if appendix else "")
        return html_template.format(hero_content=hero_html, article_content=article_content)

    def _render_via_llm(self, output_path: Path, raw_text: str, figures: Dict[str, Any], tables: Dict[str, Any], web_images: list, model_id: str = None, temperature: float = None, max_tokens: int = None, max_attempts: int = None, template_name: str = None) -> str:
        template_html = self._load_doubao_template(template_name)
        return self._render_via_llm_with_template(template_html, output_path, raw_text, figures, tables, web_images, model_id=model_id, temperature=temperature, max_tokens=max_tokens, max_attempts=max_attempts)

    def _render_via_llm_with_template(self, template_html: str, output_path: Path, raw_text: str, figures: Dict[str, Any], tables: Dict[str, Any], web_images: list, model_id: str = None, temperature: float = None, max_tokens: int = None, max_attempts: int = None) -> str:
        assets: List[Dict[str, Any]] = []
        for fig_id, fig in figures.items():
            assets.append({
                "type": "figure",
                "id": fig_id,
                "caption": fig.get("caption", ""),
                "rel_path": str(Path('assets') / Path(fig.get('path', '')).name),
                "width": fig.get("width"),
                "height": fig.get("height"),
                "aspect": fig.get("aspect")
            })
        for tab_id, tab in tables.items():
            assets.append({
                "type": "table",
                "id": tab_id,
                "caption": tab.get("caption", ""),
                "rel_path": str(Path('assets') / Path(tab.get('path', '')).name),
                "width": tab.get("width"),
                "height": tab.get("height"),
                "aspect": tab.get("aspect")
            })
        # Add web images as an asset type for LLM layout (allows image_url external links)
        for idx, w in enumerate(web_images):
            rel_path = w.get("rel_path") or ""
            image_url = w.get("image_url") or ""
            assets.append({
                "type": "web_image",
                "id": f"web_{idx+1}",
                "caption": w.get("title") or w.get("keyword") or f"Image {idx+1}",
                "rel_path": rel_path,
                "image_url": image_url,
                "width": w.get("width"),
                "height": w.get("height"),
                "score": w.get("score"),
                "source": w.get("source"),
                "domain": w.get("domain"),
            })

        model = model_id or os.getenv("TEXT_MODEL") or "gpt-4.1-2025-04-14"
        temp = 0.7 if temperature is None else float(temperature)
        tokens = 8192 if max_tokens is None else int(max_tokens)
        attempts = 3 if max_attempts is None else int(max_attempts)

        system_prompt = (
            "You are a professional academic poster frontend design assistant. Given the paper text and asset list, "
            "generate a complete, directly openable HTML page. You must:\n"
            "1) Follow the information architecture and visual style of the given template_html (keep Tailwind/fonts/icons consistent or compatible);\n"
            "2) Insert figures/tables correctly by rel_path;\n"
            "2.1) You will also receive web_image assets (auto-fetched from search engines) with image_url and rel_path. "
            "For web_image, prefer image_url for rendering (use rel_path only when image_url is unavailable). "
            "Select and layout wisely based on score/title/context; avoid stacking too many; pick one or a few to enhance visuals;\n"
            "3) Organize content structure (headings, bullet cards, chart areas, etc.) for readability and aesthetics;\n"
            "4) Output only the HTML source code, no extra explanation."
        )

        user_payload = {
            "template_html": template_html,
            "paper_text": raw_text,
            "assets": assets
        }

        # Check if Qwen model; if so, use QST/MAAS OpenAI-compatible API
        if "qwen" in model.lower():
            print(f"[{self.name}] Detected Qwen model '{model}', using QST/MAAS API.")
            return self._call_qwen(
                model=model,
                system_prompt=system_prompt,
                user_payload=user_payload,
                temperature=temp,
                max_tokens=tokens,
                attempts=attempts
            )

        # Check if Gemini model; if so, use native API call logic
        if "gemini" in model.lower():
            print(f"[{self.name}] Detected Gemini model '{model}', switching to native API.")
            return self._call_gemini_native(
                model=model,
                system_prompt=system_prompt,
                user_payload=user_payload,
                temperature=temp,
                max_tokens=tokens, # Pass the (potentially larger) token limit
                attempts=attempts
            )

        # Primary: HTTP direct connection to compatible Chat Completions API
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("RUNWAY_API_BASE") or "https://runway.devops.xiaohongshu.com/openai"
        api_version = os.getenv("RUNWAY_API_VERSION") or "2024-12-01-preview"
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("RUNWAY_API_KEY")

        http_err: Exception | None = None
        if api_key:
            endpoint = f"{base_url.rstrip('/')}/chat/completions?api-version={api_version}"
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "temperature": temp,
                "max_tokens": tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
            }

            for _ in range(max(1, attempts)):
                try:
                    r = requests.post(endpoint, headers=headers, json=body, timeout=60)
                    if r.status_code < 200 or r.status_code >= 300:
                        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
                    data = r.json()
                    choices = data.get("choices") or []
                    content = (choices[0].get("message", {}).get("content") if choices else "") or ""
                    if not content:
                        raise RuntimeError("empty completion content")
                    content = self._strip_code_fences(content)
                    return content
                except Exception as e:  # pragma: no cover
                    http_err = e

        # Fallback: if OpenAI SDK is configured, try SDK
        client = self._init_llm_client()
        if client is not None:
            last_err: Exception | None = None
            for _ in range(max(1, attempts)):
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        temperature=temp,
                        max_tokens=tokens,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                        ],
                    )
                    content = resp.choices[0].message.content if resp and resp.choices else ""
                    if not content:
                        raise RuntimeError("empty completion content")
                    content = self._strip_code_fences(content)
                    return content
                except Exception as e:  # pragma: no cover
                    last_err = e
            raise RuntimeError(f"LLM generation failed after {attempts} attempts: {last_err}")

        raise RuntimeError(f"HTTP client not configured (missing api key). Last error: {http_err}")

    def _call_gemini_native(self, model: str, system_prompt: str, user_payload: dict, temperature: float, max_tokens: int, attempts: int) -> str:
        """
        Call Gemini native API (https://runway.devops.rednote.life/openai/google/v1:generateContent).
        Logic follows PosterGen2/dev/APIconn_test.py.
        """
        endpoint = "https://runway.devops.rednote.life/openai/google/v1:generateContent"
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("RUNWAY_API_KEY")
        if not api_key:
             raise RuntimeError("missing RUNWAY_API_KEY/OPENAI_API_KEY for Gemini call")

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }
        
        # Gemini native API supports systemInstruction
        # For simplicity we pass system prompt as systemInstruction (per test.sh example)
        
        # Build user content text
        user_text = json.dumps(user_payload, ensure_ascii=False)
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": user_text}]
            }],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 1,
            }
        }

        last_err: Exception | None = None
        for _ in range(max(1, attempts)):
            try:
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
                if resp.status_code < 200 or resp.status_code >= 300:
                     raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:800]}")
                
                res_json = resp.json()
                
                # Error check
                if "error" in res_json:
                     raise RuntimeError(f"API Error: {res_json.get('error')}")

                if "candidates" not in res_json or not res_json["candidates"]:
                     raise RuntimeError(f"No candidates returned. Full response: {res_json}")

                candidate = res_json["candidates"][0]
                finish_reason = candidate.get("finishReason")
                if finish_reason and finish_reason != "STOP":
                     print(f"[{self.name}] Warning: Gemini finishReason is {finish_reason}.")

                parts = candidate.get("content", {}).get("parts", [])
                if not parts:
                     raise RuntimeError(f"No parts in response content. Finish reason: {finish_reason}. Full response: {res_json}")
                     
                answer = parts[0].get("text", "")
                if not answer:
                    raise RuntimeError(f"empty response text from Gemini. Full response: {res_json}")
                
                return self._strip_code_fences(answer)

            except Exception as e:
                last_err = e
        
        raise RuntimeError(f"Gemini native call failed: {last_err}")

    def _call_qwen(self, model: str, system_prompt: str, user_payload: dict, temperature: float, max_tokens: int, attempts: int) -> str:
        """Call Qwen/QST MAAS API via OpenAI SDK."""
        if OpenAI is None:
            raise RuntimeError("openai package not installed, cannot call Qwen API")

        api_key = os.getenv("QST_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("QST_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        if not api_key:
            raise RuntimeError("missing QST_API_KEY or OPENAI_API_KEY for Qwen call")
        if not base_url:
            raise RuntimeError("missing QST_BASE_URL or OPENAI_BASE_URL for Qwen call")

        client = OpenAI(api_key=api_key, base_url=base_url)
        user_text = json.dumps(user_payload, ensure_ascii=False)

        last_err: Exception | None = None
        for _ in range(max(1, attempts)):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    stream=False,
                )
                content = resp.choices[0].message.content if resp and resp.choices else ""
                if not content:
                    raise RuntimeError("empty completion content from Qwen")
                return self._strip_code_fences(content)
            except Exception as e:
                last_err = e
        raise RuntimeError(f"Qwen API call failed after {attempts} attempts: {last_err}")

    def _init_llm_client(self):
        if OpenAI is None:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key:
            return None
        if base_url:
            return OpenAI(api_key=api_key, base_url=base_url)
        return OpenAI(api_key=api_key)

    def _strip_code_fences(self, text: str) -> str:
        """
        Remove outermost code fence wrappers like ```html ... ``` or ``` ... ```.
        Only strips leading/trailing fences; does not alter inner content.
        """
        if not text:
            return text
        t = text.strip()
        # Strip leading fence: ``` or ```lang
        t = re.sub(r"^\s*```[a-zA-Z0-9_-]*\s*\n", "", t)
        # Strip trailing fence: ```
        t = re.sub(r"\n?\s*```\s*$", "", t)
        return t.strip()

    def _load_doubao_template(self, template_name: str = None) -> str:
        templates_dir = Path(__file__).parent / "templates"
        # Allow selecting template file or absolute path via parameter or env var; default doubao.txt
        name = template_name or os.getenv("POSTER_TEMPLATE") or "doubao.txt"
        
        candidate_path = Path(name)
        # If absolute path, use directly
        if candidate_path.is_absolute():
            template_path = candidate_path
        # If no extension specified, append .txt by default
        elif not name.endswith(".txt"):
             template_path = templates_dir / f"{name}.txt"
        else:
            template_path = templates_dir / name
            
        if not template_path.exists():
            # Strict error only when user explicitly specified POSTER_TEMPLATE or template_name
            # If default "doubao.txt" is missing, still raise since it is fallback logic
            raise FileNotFoundError(f"template not found at {template_path}")
            
        return template_path.read_text(encoding='utf-8')

    def _list_templates(self) -> list:
        """Scan templates directory and return full paths of all .txt templates."""
        templates_dir = Path(__file__).parent / "templates"
        if not templates_dir.exists():
            return []
        return [str(p) for p in templates_dir.glob("*.txt")]

    def _get_html_template(self) -> str:
        """Single-column natural layout template (Hero + body + gallery style)."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poster Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #212529;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 24px;
        }
        .header {
            text-align: center;
            margin-bottom: 8px;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
        }
        .caption {
            font-style: italic;
            color: #6c757d;
            margin-top: 8px;
            font-size: 0.9em;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin: 10px 0 24px 0;
        }
        .gallery-item {
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .gallery-item.landscape { grid-column: span 2; }
        .gallery-item.portrait { grid-row: span 2; }
        .hero-banner {
            width: 100%;
            border-radius: 12px;
            overflow: hidden;
            margin: 16px 0 24px 0;
            position: relative;
            border: 1px solid #e9ecef;
        }
        .hero-banner img {
            width: 100%;
            height: auto;
            display: block;
        }
        .hero-caption {
            position: absolute;
            left: 12px;
            bottom: 12px;
            background: rgba(0,0,0,0.55);
            color: #fff;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.95em;
        }
        .article {
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .article h1, .article h2, .article h3 {
            color: #3c4043;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Poster Content Preview</h1>
        </div>
        {hero_content}
        <div class="article">
            {article_content}
        </div>
    </div>
</body>
</html>
"""
