#!/bin/bash
# Build script for creating demo version executable

set -e

echo "=========================================="
echo "Building Facebook Marketing Tool Demo"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "facebook.py" ]; then
    echo "Error: facebook.py not found. Please run this script from the project root."
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: venv not found. Using system Python."
fi

# Check if PyInstaller is installed
echo "Checking PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds (but keep build_demo.spec)
echo ""
echo "Cleaning previous builds..."
rm -rf build/ dist/ 2>/dev/null || true
# Don't delete build_demo.spec - we need it!

# Create build directory
mkdir -p dist_demo

# Build the executable
echo ""
echo "Building executable (this may take a few minutes)..."
echo ""

# Use the spec file
pyinstaller build_demo.spec

# Check if build was successful
if [ -f "dist/FacebookMarketingTool" ] || [ -f "dist/FacebookMarketingTool.app" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Build Successful!"
    echo "=========================================="
    echo ""
    echo "Executable location:"
    if [ -f "dist/FacebookMarketingTool.app" ]; then
        echo "  📦 dist/FacebookMarketingTool.app"
        echo ""
        echo "To test the app:"
        echo "  open dist/FacebookMarketingTool.app"
        echo ""
        echo "To create a distributable package:"
        echo "  cd dist"
        echo "  zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool.app"
    elif [ -f "dist/FacebookMarketingTool" ]; then
        echo "  📦 dist/FacebookMarketingTool"
        echo ""
        echo "To test the app:"
        echo "  ./dist/FacebookMarketingTool"
    fi
    echo ""
    echo "Note: The executable includes all dependencies."
    echo "You can distribute this to your client without source code."
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi

