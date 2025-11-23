#!/bin/bash
# Test PDF and Email functionality (without image generation)

echo "🧪 Testing PDF + Email (Image Generation Disabled)"
echo "=" * 70
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

# Temporarily disable image generation
echo "Temporarily disabling image generation..."
cp .env .env.backup

# Update .env to disable image generation
if grep -q "^ENABLE_IMAGE_GENERATION=" .env; then
    sed -i '' 's/^ENABLE_IMAGE_GENERATION=.*/ENABLE_IMAGE_GENERATION=false/' .env
else
    echo "ENABLE_IMAGE_GENERATION=false" >> .env
fi

echo "✓ Image generation disabled"
echo ""

# Activate venv and run
echo "Running main.py..."
echo ""

source venv/bin/activate && python main.py

echo ""
echo "=" * 70
echo "Test completed!"
echo ""
echo "To restore image generation, run:"
echo "  mv .env.backup .env"
