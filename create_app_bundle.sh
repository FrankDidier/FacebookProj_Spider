#!/bin/bash
# Create a proper macOS .app bundle from the executable

set -e

EXECUTABLE="dist/FacebookMarketingTool"
APP_NAME="FacebookMarketingTool"
APP_BUNDLE="dist/${APP_NAME}.app"

if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: $EXECUTABLE not found. Please build first with ./build_demo.sh"
    exit 1
fi

echo "Creating macOS .app bundle..."

# Create app bundle structure
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# Copy executable
cp "$EXECUTABLE" "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

# Make it executable
chmod +x "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

# Create Info.plist
cat > "${APP_BUNDLE}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.facebookmarketingtool.app</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Copy config.ini to Resources if it exists
if [ -f "config.ini" ]; then
    cp config.ini "${APP_BUNDLE}/Contents/Resources/"
fi

echo ""
echo "✅ App bundle created: ${APP_BUNDLE}"
echo ""
echo "To test:"
echo "  open ${APP_BUNDLE}"
echo ""
echo "To create distribution package:"
echo "  cd dist"
echo "  zip -r ${APP_NAME}_Demo.zip ${APP_NAME}.app"

