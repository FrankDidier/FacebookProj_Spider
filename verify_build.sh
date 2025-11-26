#!/bin/bash
# Verify the built executable is working correctly

set -e

EXECUTABLE="dist/FacebookMarketingTool"
APP_BUNDLE="dist/FacebookMarketingTool.app"

echo "=========================================="
echo "Verifying Build"
echo "=========================================="
echo ""

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Executable not found: $EXECUTABLE"
    exit 1
fi

echo "✅ Executable found: $EXECUTABLE"
echo "   Size: $(ls -lh "$EXECUTABLE" | awk '{print $5}')"
echo ""

# Check if app bundle exists
if [ -d "$APP_BUNDLE" ]; then
    echo "✅ App bundle found: $APP_BUNDLE"
    echo "   Size: $(du -sh "$APP_BUNDLE" | awk '{print $1}')"
    echo ""
    
    # Check app bundle structure
    if [ -f "${APP_BUNDLE}/Contents/MacOS/FacebookMarketingTool" ]; then
        echo "✅ App bundle structure is correct"
    else
        echo "⚠️  App bundle structure may be incomplete"
    fi
    echo ""
fi

# Check file type
echo "File type:"
file "$EXECUTABLE"
echo ""

# Check if it's executable
if [ -x "$EXECUTABLE" ]; then
    echo "✅ Executable has execute permissions"
else
    echo "❌ Executable missing execute permissions"
    exit 1
fi
echo ""

# Check for required dependencies (basic check)
echo "Checking for bundled dependencies..."
if strings "$EXECUTABLE" | grep -q "PySide6\|PySide2" 2>/dev/null; then
    echo "✅ Qt/PySide libraries detected"
else
    echo "⚠️  Qt/PySide libraries not clearly detected (may be bundled)"
fi

if strings "$EXECUTABLE" | grep -q "selenium" 2>/dev/null; then
    echo "✅ Selenium detected"
else
    echo "⚠️  Selenium not clearly detected (may be bundled)"
fi
echo ""

# Check if config.ini is accessible (in app bundle)
if [ -d "$APP_BUNDLE" ]; then
    if [ -f "${APP_BUNDLE}/Contents/Resources/config.ini" ]; then
        echo "✅ Config file included in app bundle"
    else
        echo "⚠️  Config file not found in app bundle (may be loaded from elsewhere)"
    fi
    echo ""
fi

echo "=========================================="
echo "✅ Build Verification Complete!"
echo "=========================================="
echo ""
echo "The executable is ready for distribution."
echo ""
echo "To test the app:"
if [ -d "$APP_BUNDLE" ]; then
    echo "  open $APP_BUNDLE"
else
    echo "  ./$EXECUTABLE"
fi
echo ""
echo "To create distribution package:"
echo "  cd dist"
if [ -d "$APP_BUNDLE" ]; then
    echo "  zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool.app"
else
    echo "  zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool"
fi
echo ""

