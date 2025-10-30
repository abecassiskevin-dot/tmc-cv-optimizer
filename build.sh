#!/bin/bash

# Install system dependencies
echo "📦 Installing system packages..."
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-fra poppler-utils

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Build complete!"
