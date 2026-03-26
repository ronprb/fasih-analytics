#!/bin/bash

cd "$(dirname "$0")"

source "$(dirname "$0")/venv/bin/activate"

echo ""
echo "========================================"
echo "   FASIH Scraping - Survey Monitoring"
echo "========================================"
echo ""

# Ask if user wants to relogin
read -p "Force fresh login? (y/N): " relogin
echo ""

if [[ "$relogin" =~ ^[Yy]$ ]]; then
    python main.py --relogin
else
    python main.py
fi

echo ""
echo "========================================"
echo "   Done. Press any key to close."
echo "========================================"
read -n 1
