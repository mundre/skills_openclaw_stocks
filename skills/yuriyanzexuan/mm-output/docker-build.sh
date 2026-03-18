#!/bin/bash
# Build and manage PosterGen Docker image

set -e

IMAGE_NAME="postergen-parser"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_help() {
    cat << EOF
PosterGen Docker Build Script

Usage: $0 [command]

Commands:
    build       Build the Docker image
    build-nc    Build without cache
    run         Run interactive shell
    parse       Parse a PDF file (usage: $0 parse /path/to/file.pdf)
    convert     Convert HTML to multi-modal (usage: $0 convert /path/to/file.html)
    push        Push to registry (set REGISTRY env var)
    save        Save image to tar file
    load        Load image from tar file
    clean       Remove image and containers
    help        Show this help

Environment Variables:
    REGISTRY    Docker registry URL (e.g., registry.example.com)
    IMAGE_NAME  Image name (default: postergen-parser)
    IMAGE_TAG   Image tag (default: latest)

Examples:
    # Build image
    $0 build

    # Parse a PDF
    $0 parse ./input/my_paper.pdf

    # Convert HTML to PDF/PNG/DOCX
    $0 convert ./output/poster.html --format all

    # Save for offline transfer
    $0 save
    # Then on target machine:
    $0 load postergen-parser-latest.tar.gz
EOF
}

build_image() {
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build \
        --target final \
        -t ${IMAGE_NAME}:${IMAGE_TAG} \
        -t ${IMAGE_NAME}:latest \
        "$@" \
        .
    echo -e "${GREEN}Build complete!${NC}"
    docker images ${IMAGE_NAME}:${IMAGE_TAG}
}

run_interactive() {
    echo -e "${GREEN}Starting interactive container...${NC}"
    docker run -it --rm \
        -v "$(pwd)/input:/app/input:ro" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/outputs:/app/outputs" \
        -v "$(pwd)/.env:/app/.env:ro" \
        -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
        ${IMAGE_NAME}:${IMAGE_TAG} \
        /bin/bash
}

parse_pdf() {
    local pdf_path="$1"
    shift
    
    if [ -z "$pdf_path" ]; then
        echo -e "${RED}Error: PDF path required${NC}"
        echo "Usage: $0 parse /path/to/file.pdf"
        exit 1
    fi
    
    if [ ! -f "$pdf_path" ]; then
        echo -e "${RED}Error: File not found: $pdf_path${NC}"
        exit 1
    fi
    
    # Get absolute path
    pdf_path=$(realpath "$pdf_path")
    pdf_dir=$(dirname "$pdf_path")
    pdf_name=$(basename "$pdf_path")
    
    echo -e "${GREEN}Parsing PDF: $pdf_name${NC}"
    
    docker run --rm \
        -v "$pdf_dir:/app/input:ro" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/outputs:/app/outputs" \
        -v "$(pwd)/.env:/app/.env:ro" \
        -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
        ${IMAGE_NAME}:${IMAGE_TAG} \
        python run.py \
        --pdf_path "/app/input/$pdf_name" \
        --output_dir /app/output \
        "$@"
}

convert_html() {
    local html_path="$1"
    shift
    
    if [ -z "$html_path" ]; then
        echo -e "${RED}Error: HTML path required${NC}"
        echo "Usage: $0 convert /path/to/file.html [options]"
        exit 1
    fi
    
    if [ ! -f "$html_path" ]; then
        echo -e "${RED}Error: File not found: $html_path${NC}"
        exit 1
    fi
    
    html_path=$(realpath "$html_path")
    html_dir=$(dirname "$html_path")
    html_name=$(basename "$html_path")
    
    echo -e "${GREEN}Converting HTML: $html_name${NC}"
    
    docker run --rm \
        -v "$html_dir:/app/input:ro" \
        -v "$(pwd)/mm_outputs:/app/mm_outputs" \
        -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
        ${IMAGE_NAME}:${IMAGE_TAG} \
        python -m mm_output.cli \
        "/app/input/$html_name" \
        --format all \
        --output-dir /app/mm_outputs \
        "$@"
}

push_image() {
    if [ -z "$REGISTRY" ]; then
        echo -e "${RED}Error: REGISTRY environment variable not set${NC}"
        echo "Example: REGISTRY=registry.example.com $0 push"
        exit 1
    fi
    
    echo -e "${GREEN}Pushing to registry: $REGISTRY${NC}"
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    echo -e "${GREEN}Push complete!${NC}"
}

save_image() {
    local filename="${IMAGE_NAME}-${IMAGE_TAG}.tar.gz"
    echo -e "${GREEN}Saving image to $filename...${NC}"
    docker save ${IMAGE_NAME}:${IMAGE_TAG} | gzip > "$filename"
    echo -e "${GREEN}Saved! Size: $(du -h "$filename" | cut -f1)${NC}"
}

load_image() {
    local filename="$1"
    if [ -z "$filename" ]; then
        filename="${IMAGE_NAME}-${IMAGE_TAG}.tar.gz"
    fi
    
    if [ ! -f "$filename" ]; then
        echo -e "${RED}Error: File not found: $filename${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Loading image from $filename...${NC}"
    gunzip -c "$filename" | docker load
    echo -e "${GREEN}Load complete!${NC}"
}

clean_up() {
    echo -e "${YELLOW}Removing containers and images...${NC}"
    docker rm -f $(docker ps -aq -f "ancestor=${IMAGE_NAME}:${IMAGE_TAG}") 2>/dev/null || true
    docker rmi ${IMAGE_NAME}:${IMAGE_TAG} 2>/dev/null || true
    docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Main
case "${1:-help}" in
    build)
        shift
        build_image "$@"
        ;;
    build-nc)
        build_image --no-cache
        ;;
    run)
        run_interactive
        ;;
    parse)
        shift
        parse_pdf "$@"
        ;;
    convert)
        shift
        convert_html "$@"
        ;;
    push)
        push_image
        ;;
    save)
        save_image
        ;;
    load)
        shift
        load_image "$@"
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_help
        exit 1
        ;;
esac
