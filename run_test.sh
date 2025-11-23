#!/bin/bash
# Test mode execution script for blockchain daily automation

echo "🚀 Starting blockchain daily automation (TEST MODE)"
echo "=================================================="
echo ""
echo "Configuration:"
echo "- News limit: 10 items"
echo "- Article length: ~1000 words"
echo "- Max images: 2"
echo "- PDF + Email enabled"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: venv not found. Please run 'python3 -m venv venv' first"
    exit 1
fi

# Install dependencies if needed
echo "✓ Checking dependencies..."
pip install -q -r requirements.txt

# Run the main script
echo "✓ Running main.py..."
echo ""
python main.py

# Deactivate venv
deactivate

echo ""
echo "=================================================="
echo "✅ Test run completed!"
