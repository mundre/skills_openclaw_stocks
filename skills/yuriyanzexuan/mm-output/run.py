
import argparse
from parser_unit import PosterGenParserUnit
from renderer_unit import PosterGenRendererUnit
import os
from dotenv import load_dotenv
from typing import List, Optional

try:
    from image_unit import AutoImageUnit  # type: ignore
except Exception:
    AutoImageUnit = None  # pragma: no cover

try:
    from mm_output.integrate import add_mm_output_args, generate_mm_outputs
except Exception:
    add_mm_output_args = None
    generate_mm_outputs = None

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a PDF or Markdown to extract text/assets, then render a preview.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf_path", type=str, help="Path to the PDF file.")
    group.add_argument("--md_path", type=str, help="Path to the Markdown (.md) file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the output.")
    parser.add_argument("--render_mode", type=str, default="llm", choices=["llm", "simple"], help="Render mode: 'llm' (default) or 'simple'.")
    parser.add_argument("--text_model", type=str, default=None, help="Text model name, e.g. gpt-4.1-2025-04-14. If unset, will use env TEXT_MODEL or default.")
    parser.add_argument("--temperature", type=float, default=None, help="LLM temperature (default 0.7).")
    parser.add_argument("--max_tokens", type=int, default=16384, help="Max tokens for LLM output (default 8192).")
    parser.add_argument("--max_attempts", type=int, default=None, help="Max retry attempts for LLM generation (default 3).")
    # New: auto image enhancement options
    parser.add_argument("--auto_images", action="store_true", help="Extract keywords from Markdown, search and download related images for rendering.")
    parser.add_argument("--max_keywords", type=int, default=5, help="Maximum number of keywords to extract (default 5).")
    parser.add_argument("--images_per_keyword", type=int, default=2, help="Maximum number of images to download per keyword (default 2).")
    parser.add_argument("--template", type=str, default=None, help="Specific template path or name to use. Overrides POSTER_TEMPLATE env var.")
    if add_mm_output_args:
        add_mm_output_args(parser)
    args = parser.parse_args()

    # Input file existence check
    if args.pdf_path and not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        exit(1)
    if args.md_path and not os.path.exists(args.md_path):
        print(f"Error: Markdown file not found at {args.md_path}")
        exit(1)

    # Step 1: Parse the input (PDF or Markdown)
    parser_unit = PosterGenParserUnit()
    if args.pdf_path:
        parser_results = parser_unit.parse(args.pdf_path, args.output_dir)
    else:
        parser_results = parser_unit.parse_markdown(args.md_path, args.output_dir)
    
    print("\nParsing complete.")
    print(f"Results saved in {os.path.abspath(args.output_dir)}")
    print(f"  - Markdown text: {parser_results['raw_text_path']}")
    print(f"  - Figures JSON: {parser_results['figures_path']} ({parser_results['figure_count']} figures)")
    print(f"  - Tables JSON: {parser_results['tables_path']} ({parser_results['table_count']} tables)")

    # Step 1.5: Optional - Auto image enhancement: keyword extraction + search & download + optional VLM filtering
    if args.auto_images:
        if AutoImageUnit is None:
            print("Warning: auto_images enabled but image_unit module not available. Skipping auto images.")
        else:
            print("\n[AutoImages] Starting keyword extraction and image search...")
            image_unit = AutoImageUnit()
            # Prepare keywords (default: extract via LLM, fallback to heuristic on failure)
            try:
                keywords = image_unit.extract_keywords_via_llm(parser_results["raw_text_path"], max_keywords=args.max_keywords)
                if not keywords:
                    raise RuntimeError("empty keywords from llm")
            except Exception as _:
                keywords = image_unit.extract_keywords_from_md(parser_results["raw_text_path"], max_keywords=args.max_keywords)
            print(f"[AutoImages] Keywords: {', '.join(keywords) if keywords else '(none)'}")
            # Search and download
            web_images_info = image_unit.search_and_download_images(
                keywords=keywords,
                output_dir=args.output_dir,
                max_per_keyword=max(1, args.images_per_keyword),
            )
            # Automatically try VLM selection (fallback to heuristic if env not configured or on failure)
            try:
                selected = image_unit.select_images_via_vlm(
                    md_path=parser_results["raw_text_path"],
                    images_info=web_images_info,
                    output_dir=args.output_dir,
                )
                if selected:
                    web_images_info = selected
                    print(f"[AutoImages] VLM selected {len(web_images_info)} images.")
            except Exception as e:
                print(f"[AutoImages] VLM selection not applied, fallback to heuristic. Info: {e}")
            # Write metadata for renderer to load
            auto_json = image_unit.write_web_images_meta(web_images_info, args.output_dir)
            # Clean up unreferenced/invalid leftover files
            try:
                removed = image_unit.cleanup_auto_images(args.output_dir, [w.filepath for w in web_images_info])
                if removed:
                    print(f"[AutoImages] Cleanup removed {removed} stale files.")
            except Exception as _:
                pass
            parser_results["web_images_path"] = auto_json
            parser_results["web_image_count"] = len(web_images_info)
            print(f"[AutoImages] Completed. Images saved and metadata at: {auto_json}")

    # Step 2: Render the parsed content to HTML
    renderer_unit = PosterGenRendererUnit()
    
    # Determine template to use (argument takes precedence, then env var)
    selected_template = args.template or os.getenv("POSTER_TEMPLATE")
    if selected_template:
        print(f"Template selection: '{selected_template}'")
    else:
        print("Template selection: None (will render all available templates)")

    html_path = renderer_unit.render(
        parser_results,
        args.output_dir,
        mode=args.render_mode,
        model_id=args.text_model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_attempts=args.max_attempts,
        template_name=selected_template
    )

    if html_path:
        print("\nRendering complete.")
        if isinstance(html_path, list):
            for p in html_path:
                print(f"  - HTML Output: {p}")
        else:
            print(f"  - HTML Output: {html_path}")

        # Step 3: Multi-modal output (PDF/PNG/DOCX)
        if generate_mm_outputs:
            html_paths = html_path if isinstance(html_path, list) else [html_path]
            for hp in html_paths:
                generate_mm_outputs(hp, args.output_dir, args)
