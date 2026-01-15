#!/bin/bash
# Simple runner for Content Agent System
# Usage: ./run.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   QuickNote AI - B2B Content Agent System${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: ./install.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✓${NC} Activating virtual environment..."
source .venv/bin/activate

# Check if input file exists
if [ ! -f "input.txt" ]; then
    echo -e "${YELLOW}⚠️  No input.txt file found!${NC}"
    echo ""
    echo "Creating a sample input.txt file for you..."
    cat > input.txt << 'EOF'
Product: QuickNote AI

QuickNote AI is a lightweight note-taking app with AI-powered organization. Perfect for students and professionals who need to capture ideas quickly.

Key Features:
- Voice-to-text notes
- AI categorization
- Cross-device sync
- Smart search

Pricing: $5/month or $50/year
Target: Students, professionals, content creators
EOF
    echo -e "${GREEN}✓${NC} Created input.txt with sample data"
    echo ""
    echo -e "${BLUE}💡 Edit input.txt to customize your product information${NC}"
    echo ""
fi

echo -e "${GREEN}✓${NC} Input file: input.txt"
echo ""

# Check for old output files
old_outputs_exist=false
if ls output/*.md output/*/*.md 2>/dev/null | grep -q .; then
    old_outputs_exist=true
    echo -e "${YELLOW}⚠️  Found existing output files from previous runs:${NC}"
    echo ""
    ls -lh output/*.md output/*/*.md 2>/dev/null | tail -5
    echo ""
    echo -e "${RED}WARNING: These files may be from different products/sessions!${NC}"
    echo -e "${YELLOW}Using old outputs can mix data from different test runs.${NC}"
    echo ""
    echo "Options:"
    echo "  [1] Clean ALL outputs and start fresh (recommended)"
    echo "  [2] Keep existing outputs (only if testing same product)"
    echo ""
    read -p "Your choice (1 or 2): " clean_choice
    echo ""
    
    if [ "$clean_choice" = "1" ]; then
        echo -e "${GREEN}✓${NC} Cleaning old outputs..."
        mkdir -p output/archive/$(date +%Y%m%d_%H%M%S)
        mv output/*.md output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        mv output/case_studies output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        mv output/white_papers output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        mv output/pitch_decks output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        mv output/social_media output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        mv output/reviews output/archive/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Old outputs archived to output/archive/"
        echo ""
    else
        echo -e "${BLUE}ℹ️  Keeping existing outputs - they will be reused if compatible${NC}"
        echo ""
    fi
fi

# Ask if user wants to use previous session
if ls output/hitl/hitl_session_*.json 1> /dev/null 2>&1; then
    latest_session=$(ls -t output/hitl/hitl_session_*.json | head -1)
    session_id=$(basename "$latest_session" | sed 's/hitl_session_//' | sed 's/.json//')
    
    echo -e "${YELLOW}⚠️  Found previous session: $session_id${NC}"
    echo ""
    echo -e "${RED}WARNING: If your previous session had errors, it may have corrupted data.${NC}"
    echo -e "${YELLOW}It's recommended to start fresh to ensure clean data.${NC}"
    echo ""
    echo "Options:"
    echo "  [1] Start FRESH session (recommended)"
    echo "  [2] Resume session $session_id (only if it was working)"
    echo ""
    read -p "Your choice (1 or 2): " choice
    echo ""
    
    if [ "$choice" = "2" ]; then
        echo -e "${BLUE}🔄 Resuming session $session_id...${NC}"
        echo ""
        python run_hitl.py --input-sources input.txt --resume "$session_id" --max-api-calls 200
    else
        echo -e "${GREEN}✓${NC} Starting fresh session with clean data..."
        echo ""
        # Archive old session to prevent confusion
        if [ ! -d "output/hitl/archive" ]; then
            mkdir -p output/hitl/archive
        fi
        mv output/hitl/hitl_session_*.json output/hitl/archive/ 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Old sessions archived to output/hitl/archive/"
        echo ""
        python run_hitl.py --input-sources input.txt --max-api-calls 200
    fi
else
    echo -e "${BLUE}🚀 Starting fresh session...${NC}"
    echo ""
    python run_hitl.py --input-sources input.txt --max-api-calls 200
fi
