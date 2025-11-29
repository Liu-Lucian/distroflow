#!/bin/bash
# DistroFlow CLI Wrapper
# This script ensures the CLI runs with the correct virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   ./venv/bin/pip install -e ."
    exit 1
fi

# Run CLI with venv python
exec "$VENV_PYTHON" -m distroflow.cli "$@"
