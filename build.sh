#!/bin/bash
set -e

echo "🔍 Checking for Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo "⚠️  Dockerfile found but Docker not available on free plan"
    echo "📦 Falling back to native build with apt-packages"
fi

echo "🐍 Installing Python packages..."
pip install -r requirements.txt

echo "🔍 Checking for system packages..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR is available"
    tesseract --version
else
    echo "⚠️  WARNING: Tesseract OCR not found!"
    echo "    The app will fail to process scanned PDFs."
    echo "    Make sure apt-packages file is detected by Render."
fi

echo "✅ Build complete!"
