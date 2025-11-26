#!/bin/bash
# Universal build script - detects platform and builds accordingly

set -e

echo "=========================================="
echo "Building Facebook Marketing Tool Demo"
echo "Platform Detection and Build"
echo "=========================================="
echo ""

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "Detected OS: $OS"
echo "Detected Architecture: $ARCH"
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

# Clean previous builds (but keep spec files)
echo ""
echo "Cleaning previous builds..."
rm -rf build/ dist/ 2>/dev/null || true
echo ""

# Determine which spec file to use
if [[ "$OS" == "Darwin" ]]; then
    SPEC_FILE="build_demo.spec"
    echo "Building for macOS..."
elif [[ "$OS" == "Linux" ]]; then
    SPEC_FILE="build_demo.spec"  # Linux can use same as macOS
    echo "Building for Linux..."
else
    echo "Error: Unsupported platform: $OS"
    echo "For Windows, please use: build_demo_windows.bat"
    exit 1
fi

# Build the executable
echo ""
echo "Building executable (this may take a few minutes)..."
echo "Using spec file: $SPEC_FILE"
echo ""

pyinstaller "$SPEC_FILE"

# Check if build was successful
if [ -f "dist/FacebookMarketingTool" ] || [ -d "dist/FacebookMarketingTool.app" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Build Successful!"
    echo "=========================================="
    echo ""
    echo "Executable location:"
    if [ -d "dist/FacebookMarketingTool.app" ]; then
        echo "  📦 dist/FacebookMarketingTool.app (macOS App Bundle)"
        echo ""
        echo "To test the app:"
        echo "  open dist/FacebookMarketingTool.app"
        echo ""
        echo "To create a distributable package:"
        echo "  cd dist"
        echo "  zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool.app"
    elif [ -f "dist/FacebookMarketingTool" ]; then
        echo "  📦 dist/FacebookMarketingTool (Linux executable)"
        echo ""
        echo "To test the app:"
        echo "  ./dist/FacebookMarketingTool"
        echo ""
        echo "To create a distributable package:"
        echo "  cd dist"
        echo "  zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool"
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

