#!/bin/bash
# Convenience script to run PLM scraper

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$BACKEND_DIR")"

cd "$PROJECT_ROOT"

echo "🚀 PLM Medication Scraper"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv backend/venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies if needed
if ! python -c "import httpx, bs4, pydantic" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install httpx beautifulsoup4 lxml pydantic
    echo "✅ Dependencies installed"
fi

echo ""
echo "🔍 Starting scraper..."
echo ""

# Run the scraper
python backend/scripts/plm_scraper.py "$@"

echo ""
echo "✅ Scraping complete!"
echo ""
echo "📄 Check results at: backend/data/plm_medications.json"
