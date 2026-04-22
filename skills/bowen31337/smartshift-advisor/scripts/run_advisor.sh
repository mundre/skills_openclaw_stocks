#!/bin/bash
set -e

cd "$(dirname "$0")"

# Set environment variables
export AMBER_API_KEY="${AMBER_API_KEY:-}"  # Set your Amber API key here or via env var
export AMBER_SITE_ID="${AMBER_SITE_ID:-}"  # Set your Amber site ID here

# Run scripts
python3 amber_prices.py
python3 inverter_state.py
python3 solar_forecast.py

echo "=== All scripts completed ==="