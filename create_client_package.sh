#!/bin/bash
# Create client distribution package - NO SOURCE CODE

set -e

PACKAGE_NAME="FacebookMarketingTool_Demo"
VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FINAL_PACKAGE="${PACKAGE_NAME}_v${VERSION}_${TIMESTAMP}.zip"

echo "=========================================="
echo "Creating Client Distribution Package"
echo "=========================================="
echo ""
echo "Package will include:"
echo "  ✅ Built executable (NO source code)"
echo "  ✅ Configuration file"
echo "  ✅ Client instructions"
echo "  ❌ NO .py source files"
echo "  ❌ NO build artifacts"
echo "  ❌ NO development files"
echo ""

# Create temporary package directory
PACKAGE_DIR="client_package_${TIMESTAMP}"
rm -rf "$PACKAGE_DIR" 2>/dev/null || true
mkdir -p "$PACKAGE_DIR"

echo "Step 1: Copying built executable..."
if [ -d "dist/FacebookMarketingTool.app" ]; then
    cp -R "dist/FacebookMarketingTool.app" "$PACKAGE_DIR/"
    echo "  ✅ macOS App Bundle included"
elif [ -f "dist/FacebookMarketingTool" ]; then
    cp "dist/FacebookMarketingTool" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/FacebookMarketingTool"
    echo "  ✅ Executable included"
else
    echo "  ❌ Error: No built executable found!"
    echo "  Please run ./build_demo.sh first"
    exit 1
fi

echo ""
echo "Step 2: Copying configuration file..."
if [ -f "config.ini" ]; then
    cp "config.ini" "$PACKAGE_DIR/"
    echo "  ✅ config.ini included"
else
    echo "  ⚠️  Warning: config.ini not found"
fi

echo ""
echo "Step 3: Creating client instructions..."
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         Facebook Marketing Tool - Client Instructions         ║
╚════════════════════════════════════════════════════════════════╝

QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

macOS Users:
  1. Double-click "FacebookMarketingTool.app"
  2. If macOS warns about security:
     - Right-click the app → "Open" (first time only)
     - Or run: xattr -cr FacebookMarketingTool.app
  3. The application will start automatically

Windows Users:
  1. Double-click "FacebookMarketingTool.exe"
  2. If Windows warns about security:
     - Click "More info" → "Run anyway" (first time only)
  3. The application will start automatically

Linux Users:
  1. Open terminal in this folder
  2. Run: chmod +x FacebookMarketingTool
  3. Run: ./FacebookMarketingTool

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEATURES INCLUDED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Facebook Features:
  • FB Group Specified Collection
  • FB Group Member Rapid Collection
  • FB Group Post Collection
  • FB Public Page Collection
  • Plus all original features

Instagram Features:
  • Instagram Follower Collection
  • Instagram Following Collection
  • Instagram Profile Collection
  • Instagram Reels Comment Collection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONFIGURATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can modify "config.ini" to customize settings:
  • Account numbers
  • Thread counts
  • Target users/keywords
  • Data storage paths

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

macOS: "App is damaged"
  → Run: xattr -cr FacebookMarketingTool.app

Windows: "Windows protected your PC"
  → Right-click → Properties → Unblock
  → Or: Right-click → Run as administrator

App won't start:
  → Make sure you have extracted all files
  → Check that config.ini is in the same folder
  → Try running from terminal/command prompt for error messages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUPPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For support or questions, please contact your provider.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: 1.0.0
Build Date: $(date +"%Y-%m-%d")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
echo "  ✅ README.txt created"

echo ""
echo "Step 4: Creating package..."
cd "$PACKAGE_DIR"
zip -r "../${FINAL_PACKAGE}" . -q
cd ..

echo ""
echo "Step 5: Verifying package contents..."
unzip -l "$FINAL_PACKAGE" | head -20
echo ""

echo "Step 6: Cleaning up..."
rm -rf "$PACKAGE_DIR"

echo ""
echo "=========================================="
echo "✅ Package Created Successfully!"
echo "=========================================="
echo ""
echo "Package: ${FINAL_PACKAGE}"
echo "Size: $(ls -lh "${FINAL_PACKAGE}" | awk '{print $5}')"
echo ""
echo "Package Contents:"
echo "  ✅ Executable (NO source code)"
echo "  ✅ Configuration file"
echo "  ✅ Client instructions"
echo "  ❌ NO .py files"
echo "  ❌ NO source code"
echo "  ❌ NO development files"
echo ""
echo "Ready to send to client!"
echo ""
echo "To verify contents:"
echo "  unzip -l ${FINAL_PACKAGE}"
echo ""

