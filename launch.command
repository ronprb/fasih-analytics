#!/bin/bash

cd "$(dirname "$0")"

PYTHON_BIN="$(pwd)/venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Could not find the project Python at:"
    echo "$PYTHON_BIN"
    echo ""
    echo "Create the virtual environment and install dependencies first:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    echo ""
    read -n 1 -s -r -p "Press any key to close."
    exit 1
fi

source "$(pwd)/venv/bin/activate"

echo ""
echo "========================================"
echo "   fasih-analytics"
echo "========================================"
echo ""

# Ask if user wants to relogin
read -p "Force fresh login? (y/N): " relogin
echo ""

if [[ "$relogin" =~ ^[Yy]$ ]]; then
    "$PYTHON_BIN" main.py --relogin
else
    "$PYTHON_BIN" main.py
fi

echo ""
echo "========================================"
echo "   Done. Press any key to close."
echo "========================================"
read -n 1
