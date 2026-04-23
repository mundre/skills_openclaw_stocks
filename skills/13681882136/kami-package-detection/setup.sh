#!/bin/bash
set -e

SKILL_DIR="$(dirname "$(realpath "$0")")"
VENV_DIR="$SKILL_DIR/.venv"

# Step 1: Check python3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install python3 and python3-venv first:"
    echo "  sudo apt install -y python3 python3-venv"
    exit 1
fi

echo "Using Python: $(command -v python3) (version: $(python3 --version))"

# Step 2: Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "ERROR: venv module not available. Please install python3-venv first:"
        echo "  sudo apt install -y python3-venv"
        exit 1
    fi
fi

# Step 3: Install dependencies
"$VENV_DIR/bin/pip" install -q -r "$SKILL_DIR/requirements.txt"

echo "Setup complete."
