#!/usr/bin/env bash
# Build and Install Script for B2B Content Agent System

set -e  # Exit on error

echo "🚀 Building B2B Content Agent System..."
echo ""

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   It's recommended to use a virtual environment"
    echo ""
    read -p "   Create .venv and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m venv .venv
        source .venv/bin/activate
        echo "✓ Virtual environment created and activated"
    fi
else
    echo "✓ Virtual environment: $VIRTUAL_ENV"
fi

echo ""
echo "📦 Installing package in editable mode..."
pip install -e . --quiet

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Available commands:"
echo "   hitl-run          - Run HITL content generation pipeline"
echo "   content-agent     - Main CLI entry point"
echo ""
echo "📖 Next steps:"
echo "   1. Configure your .env file with GOOGLE_API_KEY"
echo "   2. Read HITL_GUIDE.md for usage instructions"
echo "   3. Run: hitl-run --help"
echo ""
echo "🧪 To run tests:"
echo "   pytest tests/ -v"
echo ""
