#!/usr/bin/env python3
"""
Example: Using MMOutput with PosterGen

This example shows how to integrate multi-modal output generation
into your PosterGen workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mm_output import MMOutputGenerator


def example_standalone():
    """Example: Standalone usage after HTML generation"""
    
    # Assuming you have generated HTML files
    html_files = [
        "output/poster_llm.html",
        "output/poster_preview.html"
    ]
    
    output_dir = "output/mm_outputs"
    
    with MMOutputGenerator() as gen:
        for html_path in html_files:
            if Path(html_path).exists():
                print(f"\nProcessing: {html_path}")
                
                # Convert to all formats
                results = gen.convert_all(
                    html_path,
                    output_dir,
                    base_name=Path(html_path).stem
                )
                
                print("Generated:")
                for fmt, path in results.items():
                    print(f"  - {fmt}: {path}")


def example_specific_format():
    """Example: Generate only specific formats"""
    
    html_path = "output/poster_llm.html"
    output_dir = "output/mm_outputs"
    
    with MMOutputGenerator() as gen:
        # Only PDF and PNG
        results = gen.convert_all(
            html_path,
            output_dir,
            formats=["pdf", "png"]
        )
        print(f"Generated: {results}")


def example_custom_options():
    """Example: Custom options for each format"""
    
    html_path = "output/poster_llm.html"
    output_dir = "output/mm_outputs"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with MMOutputGenerator() as gen:
        # PDF with landscape orientation
        gen.html_to_pdf(
            html_path,
            f"{output_dir}/poster_landscape.pdf",
            page_size="A4",
            landscape=True
        )
        
        # PNG with custom viewport
        gen.html_to_png(
            html_path,
            f"{output_dir}/poster_screenshot.png",
            viewport_size=(1920, 1080),
            full_page=False
        )
        
        # DOCX without images
        gen.html_to_docx(
            html_path,
            f"{output_dir}/poster_text_only.docx",
            include_images=False
        )
        
        print(f"Custom outputs saved to: {output_dir}")


def example_command_line():
    """Example: Using command line interface"""
    import subprocess
    
    html_path = "output/poster_llm.html"
    
    # Convert to PDF
    subprocess.run([
        "python", "-m", "mm_output.cli",
        html_path,
        "--format", "pdf",
        "--output", "output/poster.pdf"
    ])
    
    # Convert to all formats
    subprocess.run([
        "python", "-m", "mm_output.cli",
        html_path,
        "--format", "all",
        "--output-dir", "output/mm_outputs/"
    ])


if __name__ == "__main__":
    print("MMOutput Examples")
    print("=================\n")
    
    print("Available examples:")
    print("1. example_standalone() - Process existing HTML files")
    print("2. example_specific_format() - Generate only specific formats")
    print("3. example_custom_options() - Use custom options for each format")
    print("4. example_command_line() - Use command line interface")
    
    print("\nTo run an example, modify the script to call the function:")
    print("  example_standalone()")
    
    # Uncomment to run:
    # example_standalone()
