#!/bin/bash
# Council of LLMs — Multi-model deliberation script
# Version: 1.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/../prompts"
CONFIG_FILE="${HOME}/.openclaw/council-config.json"
DEFAULT_TIMEOUT=120
MAX_TIMEOUT=300
COST_WARNING=25000

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage
usage() {
    cat << EOF
Council of LLMs — Multi-model deliberation for high-stakes decisions

Usage:
    council [OPTIONS] "QUESTION"

Options:
    --select-models         Interactive model selection
    --models "m1,m2,m3"     Explicit comma-separated model list
    --list-models          Show available models
    --preset NAME          Use predefined council (security, architecture)
    --sequential          Run models sequentially (slower, less hardware)
    --timeout SECONDS     Per-model timeout (default: ${DEFAULT_TIMEOUT}, max: ${MAX_TIMEOUT})
    --output FILE         Save report to file
    --review FILE         Review file content (for code/docs)
    --help               Show this help

Examples:
    council "Should we use JWT or session cookies?"
    council --select-models "Architecture decision"
    council --models "ollama/kimi-k2.5,openai/gpt-4o" --timeout 180
    council --review ./auth.py --preset security

Pre-requisites:
    - OpenClaw with 2+ LLM providers configured
    - Recommended: Ollama Cloud for parallel execution
EOF
    exit 0
}

# Check if openclaw is available
check_openclaw() {
    if ! command -v openclaw &> /dev/null; then
        echo -e "${RED}Error: OpenClaw not found${NC}"
        echo "Install: https://openclaw.ai/docs/install"
        exit 1
    fi
}

# Check pre-requisites
check_prerequisites() {
    check_openclaw
    
    # Check for multiple models
    local model_count
    model_count=$(openclaw models list 2>/dev/null | wc -l || echo "0")
    
    if [ "$model_count" -lt 2 ]; then
        echo -e "${RED}Error: Council requires 2+ LLM providers configured${NC}"
        echo "Current models: $model_count"
        echo ""
        echo "To configure:"
        echo "  1. Add providers: openclaw config add provider ollama ..."
        echo "  2. Or set env: OPENCLAW_MODELS='ollama/kimi-k2.5,openai/gpt-4o'"
        echo ""
        echo -e "${YELLOW}Recommended: Ollama Cloud for parallel multi-model access${NC}"
        echo "  Sign up: https://ollama.com/cloud"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Found $model_count configured models${NC}"
}

# List available models
list_models() {
    echo "Available models:"
    openclaw models list 2>/dev/null || echo "  (Could not retrieve model list)"
    echo ""
    echo -e "${YELLOW}Recommended configuration:${NC}"
    echo "  ollama/kimi-k2.5     — Reasoning and analysis"
    echo "  openai/gpt-4o        — Security and code review"
    echo "  anthropic/claude-3-opus — Architecture and design"
}

# Get models (from config, selection, or default)
get_models() {
    local models=""
    
    # Check if user specified models
    if [ -n "$USER_MODELS" ]; then
        models="$USER_MODELS"
    # Check preset
    elif [ -n "$PRESET" ]; then
        models=$(get_preset_models "$PRESET")
    # Check config file
    elif [ -f "$CONFIG_FILE" ]; then
        models=$(jq -r '.default_models | join(",")' "$CONFIG_FILE" 2>/dev/null || echo "")
    fi
    
    # Fallback to default
    if [ -z "$models" ]; then
        models="ollama/kimi-k2.5,openai/gpt-4o,anthropic/claude-3-opus"
    fi
    
    echo "$models"
}

# Get models for a preset
get_preset_models() {
    local preset="$1"
    if [ -f "$CONFIG_FILE" ]; then
        jq -r ".presets.${preset}.models | join(\",\")" "$CONFIG_FILE" 2>/dev/null || echo ""
    fi
}

# Interactive model selection
select_models_interactive() {
    echo "Select models for this council session:"
    echo ""
    
    local available
    available=$(openclaw models list 2>/dev/null || echo "")
    
    if [ -z "$available" ]; then
        echo "Could not retrieve model list. Using defaults."
        echo "ollama/kimi-k2.5,openai/gpt-4o"
        return
    fi
    
    echo "$available" | nl
    echo ""
    echo "Enter model numbers (comma-separated, e.g., 1,3,4):"
    read -r selections
    
    # Convert numbers to model names
    local result=""
    for num in $(echo "$selections" | tr ',' ' '); do
        local model
        model=$(echo "$available" | sed -n "${num}p" 2>/dev/null || echo "")
        if [ -n "$model" ]; then
            result="${result}${model},"
        fi
    done
    
    # Remove trailing comma
    result="${result%,}"
    echo "$result"
}

# Run council debate
run_council() {
    local question="$1"
    local models="$2"
    local timeout="$3"
    local sequential="$4"
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  COUNCIL OF LLMs v1.0.0${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Question: $question"
    echo "Models: $models"
    echo "Timeout: ${timeout}s per model"
    echo "Mode: $([ "$sequential" = "true" ] && echo "Sequential" || echo "Parallel")"
    echo ""
    echo -e "${YELLOW}Running deliberation...${NC}"
    echo ""
    
    # TODO: Implement actual council logic with sessions_spawn
    # For MVP, this is a placeholder showing the structure
    
    echo "Council deliberation complete!"
    echo ""
    echo -e "${GREEN}Note: This is a framework skill.${NC}"
    echo "Full implementation requires OpenClaw sessions_spawn capability."
    echo "See SKILL.md for integration instructions."
}

# Main
main() {
    local question=""
    local timeout=$DEFAULT_TIMEOUT
    local sequential="false"
    local select_models="false"
    local output_file=""
    local review_file=""
    
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                usage
                ;;
            --list-models)
                check_openclaw
                list_models
                exit 0
                ;;
            --select-models)
                select_models="true"
                shift
                ;;
            --models)
                USER_MODELS="$2"
                shift 2
                ;;
            --preset)
                PRESET="$2"
                shift 2
                ;;
            --sequential)
                sequential="true"
                shift
                ;;
            --timeout)
                timeout="$2"
                if [ "$timeout" -gt "$MAX_TIMEOUT" ]; then
                    timeout=$MAX_TIMEOUT
                    echo -e "${YELLOW}Warning: Timeout capped at ${MAX_TIMEOUT}s${NC}"
                fi
                shift 2
                ;;
            --output)
                output_file="$2"
                shift 2
                ;;
            --review)
                review_file="$2"
                shift 2
                ;;
            -*)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                ;;
            *)
                if [ -z "$question" ]; then
                    question="$1"
                else
                    question="$question $1"
                fi
                shift
                ;;
        esac
    done
    
    # Check pre-requisites
    check_prerequisites
    
    # Get models
    local models
    if [ "$select_models" = "true" ]; then
        models=$(select_models_interactive)
    else
        models=$(get_models)
    fi
    
    # Validate question
    if [ -z "$question" ] && [ -z "$review_file" ]; then
        echo -e "${YELLOW}No question provided. Running demo...${NC}"
        question="Should we use JWT or session cookies for authentication?"
    fi
    
    # Load review file if specified
    if [ -n "$review_file" ]; then
        if [ -f "$review_file" ]; then
n            question="Review this file: $(cat "$review_file")"
        else
            echo -e "${RED}Error: File not found: $review_file${NC}"
            exit 1
        fi
    fi
    
    # Run council
    run_council "$question" "$models" "$timeout" "$sequential"
}

main "$@"
