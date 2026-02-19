#!/bin/bash
# TruthGPT Universal Installer - Enterprise Edition
# Works on macOS/Linux. Supports arguments for automation.

set -e

# --- Configuration ---
PYTHON_CMD="python3"
CUDA_VERSION="11.8" # Default
SKIP_VENV=false
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# --- Colors ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper Functions ---
log_step() { echo -e "\n${CYAN}➤ $1${NC}"; }
log_success() { echo -e "\n${GREEN}✅ $1${NC}"; }
log_error() { echo -e "\n${RED}❌ ERROR: $1${NC}"; }
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --python <path>    Specify python executable (default: python3)"
    echo "  --cuda <ver>       CUDA version: 11.8 (default), 12.1, or cpu"
    echo "  --skip-venv        Do not create a virtual environment"
    echo "  --help             Show this help"
    exit 1
}

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --python)
        PYTHON_CMD="$2"
        shift; shift
        ;;
        --cuda)
        CUDA_VERSION="$2"
        shift; shift
        ;;
        --skip-venv)
        SKIP_VENV=true
        shift
        ;;
        --help)
        usage
        ;;
        *)
        echo "Unknown option: $1"
        usage
        ;;
    esac
done

echo -e "${CYAN}============================================================"
echo -e "   TRUTHGPT - OPTIMIZATION CORE"
echo -e "   Enterprise Installer v2.0"
echo -e "============================================================${NC}"

# 1. Python Check
log_step "Detecting Python Runtime..."
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    log_error "$PYTHON_CMD not found. Please install Python 3.10+."
    exit 1
fi
PY_VER=$($PYTHON_CMD --version 2>&1)
echo "   Found: $PY_VER"

# 2. Virtual Environment
TARGET_PYTHON="$PYTHON_CMD"
TARGET_PIP="pip"

if [ "$SKIP_VENV" = false ]; then
    log_step "Configuring Virtual Environment..."
    VENV_PATH="$SCRIPT_DIR/.venv"
    
    if [ ! -d "$VENV_PATH" ]; then
        echo "   Creating .venv at $VENV_PATH..."
        $PYTHON_CMD -m venv "$VENV_PATH"
    else
        echo "   Using existing .venv."
    fi

    TARGET_PYTHON="$VENV_PATH/bin/python"
    TARGET_PIP="$VENV_PATH/bin/pip"
else
    log_step "Skipping Venv creation. Using system python (Be careful!)"
fi

# 3. Upgrade Core Tools
log_step "Upgrading Pip & Build Tools..."
$TARGET_PIP install --upgrade pip setuptools wheel build --quiet

# 4. PyTorch Installation
log_step "Installing Neural Engine (PyTorch)..."

OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "   Detected macOS. Installing MPS-enabled build..."
    $TARGET_PIP install torch torchvision torchaudio --quiet
else
    # Linux Logic
    if [ "$CUDA_VERSION" == "cpu" ]; then
        echo "   Targeting CPU only..."
        $TARGET_PIP install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
    elif [ "$CUDA_VERSION" == "12.1" ]; then
        echo "   Targeting CUDA 12.1..."
        $TARGET_PIP install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
    else
        echo "   Targeting CUDA 11.8 (Default)..."
        $TARGET_PIP install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet
    fi
fi

# 5. Core Installation
log_step "Installing TruthGPT Optimization Core..."
CORE_PATH="$SCRIPT_DIR/optimization_core"

if [ ! -d "$CORE_PATH" ]; then
    log_error "Directory 'optimization_core' not found."
    exit 1
fi

# Install requirements
if [ -f "$CORE_PATH/requirements_advanced.txt" ]; then
    echo "   Installing dependencies..."
    $TARGET_PIP install -r "$CORE_PATH/requirements_advanced.txt" --quiet
fi

# Install editable
echo "   Installing package in editable mode..."
$TARGET_PIP install -e "$CORE_PATH" --quiet

# 6. Success
log_success "Installation Complete."
if [ "$SKIP_VENV" = false ]; then
    echo -e "${CYAN}============================================================"
    echo -e "   NEXT STEPS:"
    echo -e "   1. Activate: source .venv/bin/activate"
    echo -e "   2. Run:      python optimization_core/train_llm.py --help"
    echo -e "============================================================${NC}"
fi
