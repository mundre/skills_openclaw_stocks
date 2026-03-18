#!/usr/bin/env python3
"""
Command-line interface for MMOutput multi-modal output generation.

Usage:
    # Convert HTML to PDF
    python -m mm_output.cli input.html --format pdf --output output.pdf
    
    # Convert HTML to PNG (full page screenshot)
    python -m mm_output.cli input.html --format png --output output.png
    
    # Convert HTML to DOCX
    python -m mm_output.cli input.html --format docx --output output.docx
    
    # Convert to all formats
    python -m mm_output.cli input.html --format all --output-dir ./outputs/
    
    # Multiple HTML files
    python -m mm_output.cli file1.html file2.html --format all --output-dir ./outputs/
"""

import argparse
import sys
from pathlib import Path

from .converter import MMOutputGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML to PDF, PNG, or DOCX formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.html --format pdf --output poster.pdf
  %(prog)s input.html --format png --output poster.png --full-page
  %(prog)s input.html --format docx --output poster.docx
  %(prog)s input.html --format all --output-dir ./outputs/
        """
    )
    
    parser.add_argument(
        "input",
        nargs="+",
        help="Input HTML file(s)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["pdf", "png", "docx", "all"],
        default="all",
        help="Output format (default: all)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (for single input, single format)"
    )
    
    parser.add_argument(
        "--output-dir", "-d",
        default="./mm_outputs",
        help="Output directory for batch conversion (default: ./mm_outputs)"
    )
    
    # PDF options
    parser.add_argument(
        "--page-size",
        default="A4",
        choices=["A4", "Letter", "Legal", "A3", "A5"],
        help="PDF page size (default: A4)"
    )
    
    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Use landscape orientation for PDF"
    )
    
    parser.add_argument(
        "--margin",
        type=str,
        default="1cm",
        help="Page margins for PDF (default: 1cm)"
    )
    
    # PNG options
    parser.add_argument(
        "--full-page",
        action="store_true",
        default=True,
        help="Capture full page for PNG (default: True)"
    )
    
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=1200,
        help="Viewport width for PNG capture (default: 1200)"
    )
    
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=1600,
        help="Viewport height for PNG capture (default: 1600)"
    )
    
    # DOCX options
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Exclude images from DOCX output"
    )
    
    # Chrome path
    parser.add_argument(
        "--chrome-path",
        help="Path to Chrome/Chromium executable"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    input_files = [Path(f) for f in args.input]
    for f in input_files:
        if not f.exists():
            print(f"Error: Input file not found: {f}", file=sys.stderr)
            sys.exit(1)
        if f.suffix.lower() != ".html":
            print(f"Warning: Input file may not be HTML: {f}", file=sys.stderr)
    
    # Determine formats to generate
    if args.format == "all":
        formats = ["pdf", "png", "docx"]
    else:
        formats = [args.format]
    
    # Setup output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = MMOutputGenerator(chrome_path=args.chrome_path)
    
    # Process each input file
    results = []
    
    for html_path in input_files:
        print(f"\nProcessing: {html_path}")
        
        # Determine output paths
        if len(input_files) == 1 and args.output and args.format != "all":
            # Single file, single format, explicit output path
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == "pdf":
                margin_dict = {
                    "top": args.margin,
                    "right": args.margin,
                    "bottom": args.margin,
                    "left": args.margin
                }
                result = generator.html_to_pdf(
                    html_path,
                    output_path,
                    page_size=args.page_size,
                    margin=margin_dict,
                    landscape=args.landscape
                )
                results.append((args.format, result))
                
            elif args.format == "png":
                result = generator.html_to_png(
                    html_path,
                    output_path,
                    full_page=args.full_page,
                    viewport_size=(args.viewport_width, args.viewport_height)
                )
                results.append((args.format, result))
                
            elif args.format == "docx":
                result = generator.html_to_docx(
                    html_path,
                    output_path,
                    include_images=not args.no_images
                )
                results.append((args.format, result))
        else:
            # Batch mode or all formats
            result = generator.convert_all(
                html_path,
                output_dir,
                formats=formats
            )
            results.append((html_path.name, result))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    
    if len(input_files) == 1 and args.output and args.format != "all":
        for fmt, path in results:
            print(f"  {fmt.upper()}: {path}")
    else:
        for name, result_dict in results:
            print(f"\n{name}:")
            for fmt, path in result_dict.items():
                print(f"  {fmt.upper()}: {path}")
    
    print("\nDone!")
    
    # Cleanup
    generator._close_browser()


if __name__ == "__main__":
    main()
