#!/usr/bin/env bash
# Build and Install Script for B2B Content Agent System

set -e  # Exit on error

echo "🚀 Building B2B Content Agent System..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Verify Python 3.9+
PYTHON_MAJOR=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1)
PYTHON_MINOR=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Error: Python 3.9+ required (you have $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python version compatible"
echo ""

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "✓ Virtual environment created and activated"
else
    echo "✓ Using existing virtual environment: $VIRTUAL_ENV"
fi

echo ""
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Configure your .env file with API keys"
echo "      GOOGLE_API_KEY (Gemini) or GROQ_API_KEY or OPENAI_API_KEY"
echo "   2. Run the system:"
echo "      ./run.sh"
echo ""
echo "🧪 To run tests:"
echo "   pytest tests/ -v"
echo ""
