#!/bin/bash
# Activation script for LexiGlow backend virtual environment

echo "Activating LexiGlow backend virtual environment..."
source .venv/bin/activate

echo "Virtual environment activated!"
echo "Python path: $(which python)"
echo "Virtual env: $VIRTUAL_ENV"
echo ""
echo "Available commands:"
echo "  python debug.py          - Run debug script"
echo "  python wsgi.py           - Run the Flask app"
echo "  pip list                 - Show installed packages"
echo "  deactivate               - Exit virtual environment"
echo ""
