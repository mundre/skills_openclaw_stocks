PDF_PATH="pth/pdf_file.pdf"
OUTPUT_DIR="pth/output"
MD_PATH="pth/markdown_file.md"
POSTER_TEMPLATE="templates/report_web_reduced.txt"
python run.py\
  --pdf_path "$PDF_PATH"\
  --output_dir "$OUTPUT_DIR"

python run.py\
  --md_path "$MD_PATH"\
  --output_dir "$OUTPUT_DIR"\
  --template "$POSTER_TEMPLATE"
# Package output folder to current path with auto-incrementing numeric suffix: <output_dir_name>_001.tar.gz, _002.tar.gz, ...
prefix="$(basename "$OUTPUT_DIR")"
n=1
while [ -e "${prefix}_$(printf '%03d' "$n").tar.gz" ]; do
  n=$((n+1))
done
outfile="${prefix}_$(printf '%03d' "$n").tar.gz"
tar -czf "$outfile" -C "$(dirname "$OUTPUT_DIR")" "$prefix"
echo "Packaging complete: $outfile"