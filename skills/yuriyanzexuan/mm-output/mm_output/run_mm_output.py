#!/usr/bin/env python3
"""
Run PosterGen with Multi-modal Output Support

This is an enhanced version of run.py that includes MMOutput integration.
It provides all the functionality of the original run.py plus multi-modal output generation.

Usage:
    # Basic usage (same as run.py)
    python run_mm_output.py --pdf_path input.pdf --output_dir ./output
    
    # With multi-modal outputs
    python run_mm_output.py --pdf_path input.pdf --output_dir ./output --output-all
    
    # Specific formats only
    python run_mm_output.py --pdf_path input.pdf --output_dir ./output --output-pdf --output-png
    
    # With custom options
    python run_mm_output.py --pdf_path input.pdf --output_dir ./output --output-all \
        --pdf-page-size A3 --pdf-landscape --png-viewport-width 1920
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from parser_unit import PosterGenParserUnit
    from renderer_unit import PosterGenRendererUnit
except ImportError as e:
    print(f"Error: Cannot import PosterGen modules: {e}")
    print("Make sure you are running this script from the mm_output directory or have the parent directory in PYTHONPATH")
    sys.exit(1)

from integrate import add_mm_output_args, generate_mm_outputs

import os
from dotenv import load_dotenv
from typing import List, Optional

try:
    from image_unit import AutoImageUnit
except Exception:
    AutoImageUnit = None

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Parse a PDF or Markdown to extract text/assets, render a preview, and generate multi-modal outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (same as original run.py)
  %(prog)s --pdf_path input.pdf --output_dir ./output
  
  # Generate all multi-modal outputs
  %(prog)s --pdf_path input.pdf --output_dir ./output --output-all
  
  # Generate specific formats
  %(prog)s --pdf_path input.pdf --output_dir ./output --output-pdf --output-png
  
  # Custom PDF options
  %(prog)s --pdf_path input.pdf --output_dir ./output --output-pdf --pdf-page-size A3 --pdf-landscape
        """
    )
    
    # Original arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf_path", type=str, help="Path to the PDF file.")
    group.add_argument("--md_path", type=str, help="Path to the Markdown (.md) file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the output.")
    parser.add_argument("--render_mode", type=str, default="llm", choices=["llm", "simple"], help="Render mode: 'llm' (default) or 'simple'.")
    parser.add_argument("--text_model", type=str, default=None, help="Text model name, e.g. gpt-4.1-2025-04-14.")
    parser.add_argument("--temperature", type=float, default=None, help="LLM temperature (default 0.7).")
    parser.add_argument("--max_tokens", type=int, default=16384, help="Max tokens for LLM output.")
    parser.add_argument("--max_attempts", type=int, default=None, help="Max retry attempts for LLM generation.")
    parser.add_argument("--auto_images", action="store_true", help="Extract keywords, search and download related images.")
    parser.add_argument("--max_keywords", type=int, default=5, help="Max number of keywords to extract (default 5).")
    parser.add_argument("--images_per_keyword", type=int, default=2, help="Max images per keyword (default 2).")
    parser.add_argument("--template", type=str, default=None, help="Template path or name. Overrides POSTER_TEMPLATE env var.")
    
    # Add multi-modal output arguments
    add_mm_output_args(parser)
    
    args = parser.parse_args()
    
    # Validate input files
    if args.pdf_path and not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        sys.exit(1)
    if args.md_path and not os.path.exists(args.md_path):
        print(f"Error: Markdown file not found at {args.md_path}")
        sys.exit(1)
    
    # Step 1: Parse the input
    print("=" * 60)
    print("Step 1: Parsing Input")
    print("=" * 60)
    
    parser_unit = PosterGenParserUnit()
    if args.pdf_path:
        parser_results = parser_unit.parse(args.pdf_path, args.output_dir)
    else:
        parser_results = parser_unit.parse_markdown(args.md_path, args.output_dir)
    
    print(f"\nParsing complete.")
    print(f"Results saved in {os.path.abspath(args.output_dir)}")
    print(f"  - Markdown text: {parser_results['raw_text_path']}")
    print(f"  - Figures JSON: {parser_results['figures_path']} ({parser_results['figure_count']} figures)")
    print(f"  - Tables JSON: {parser_results['tables_path']} ({parser_results['table_count']} tables)")
    
    # Step 1.5: Optional auto image enhancement
    if args.auto_images:
        if AutoImageUnit is None:
            print("Warning: auto_images enabled but image_unit module not available.")
        else:
            print("\n[AutoImages] Starting keyword extraction and image search...")
            image_unit = AutoImageUnit()
            try:
                keywords = image_unit.extract_keywords_via_llm(parser_results["raw_text_path"], max_keywords=args.max_keywords)
                if not keywords:
                    raise RuntimeError("empty keywords from llm")
            except Exception:
                keywords = image_unit.extract_keywords_from_md(parser_results["raw_text_path"], max_keywords=args.max_keywords)
            print(f"[AutoImages] Keywords: {', '.join(keywords) if keywords else '(none)'}")
            
            web_images_info = image_unit.search_and_download_images(
                keywords=keywords,
                output_dir=args.output_dir,
                max_per_keyword=max(1, args.images_per_keyword),
            )
            
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
                print(f"[AutoImages] VLM selection not applied: {e}")
                
            auto_json = image_unit.write_web_images_meta(web_images_info, args.output_dir)
            try:
                removed = image_unit.cleanup_auto_images(args.output_dir, [w.filepath for w in web_images_info])
                if removed:
                    print(f"[AutoImages] Cleanup removed {removed} stale files.")
            except Exception:
                pass
            parser_results["web_images_path"] = auto_json
            parser_results["web_image_count"] = len(web_images_info)
            print(f"[AutoImages] Completed. Images saved at: {auto_json}")
    
    # Step 2: Render to HTML
    print("\n" + "=" * 60)
    print("Step 2: Rendering HTML")
    print("=" * 60)
    
    renderer_unit = PosterGenRendererUnit()
    
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
    else:
        print("Warning: HTML rendering returned None")
        return
    
    # Step 3: Generate multi-modal outputs
    print("\n" + "=" * 60)
    print("Step 3: Multi-modal Output Generation")
    print("=" * 60)
    
    results = generate_mm_outputs(html_path, args.output_dir, args)
    
    if results:
        print("\n" + "=" * 60)
        print("All Done!")
        print("=" * 60)
        print(f"\nOutput files:")
        print(f"  - HTML: {html_path}")
        if isinstance(results, dict):
            for fmt, path in results.items():
                print(f"  - {fmt.upper()}: {path}")
    else:
        print("\nNo multi-modal outputs requested.")
        print("Use --output-all or specific flags (--output-pdf, --output-png, --output-docx) to generate.")


if __name__ == "__main__":
    main()
