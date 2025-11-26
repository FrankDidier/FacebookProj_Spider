# 📦 Packaging Guide - Creating Demo Version

This guide explains how to create a standalone executable (demo version) of the Facebook Marketing Tool that can be distributed to clients **without providing source code**.

## 🎯 What You'll Get

After packaging, you'll have:
- A standalone executable file (`.app` on macOS, `.exe` on Windows)
- All dependencies bundled
- No source code visible to the client
- Ready to distribute

## 📋 Prerequisites

1. **Python 3.9+** installed
2. **Virtual environment** set up (already done)
3. **All dependencies** installed (already done)

## 🚀 Quick Start

### Option 1: Automated Build (Recommended)

```bash
# Make the script executable
chmod +x build_demo.sh

# Run the build script
./build_demo.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Install PyInstaller if needed
- ✅ Clean previous builds
- ✅ Build the executable
- ✅ Show you where the result is

### Option 2: Manual Build

```bash
# Activate virtual environment
source venv/bin/activate

# Install PyInstaller
pip install pyinstaller

# Build using the spec file
pyinstaller build_demo.spec
```

## 📁 Output Location

After building, you'll find:
- **macOS**: `dist/FacebookMarketingTool.app`
- **Windows**: `dist/FacebookMarketingTool.exe`
- **Linux**: `dist/FacebookMarketingTool`

## 🧪 Testing the Executable

### macOS
```bash
# Test the app
open dist/FacebookMarketingTool.app

# Or from command line
./dist/FacebookMarketingTool.app/Contents/MacOS/FacebookMarketingTool
```

### Windows
```bash
# Double-click or run from command line
dist\FacebookMarketingTool.exe
```

## 📦 Creating Distribution Package

### macOS
```bash
cd dist
zip -r FacebookMarketingTool_Demo.zip FacebookMarketingTool.app
```

### Windows
```bash
cd dist
# Use 7-Zip or WinRAR to create a zip file
# Or use PowerShell:
Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Demo.zip
```

## 📤 Distributing to Client

1. **Create the zip file** (see above)
2. **Send the zip file** to your client
3. **Client extracts** and runs the executable
4. **No source code** is included!

## ⚙️ Customization

### Adding an Icon

1. Create or obtain an `.icns` file (macOS) or `.ico` file (Windows)
2. Update `build_demo.spec`:
   ```python
   icon='path/to/your/icon.icns',  # macOS
   # or
   icon='path/to/your/icon.ico',   # Windows
   ```
3. Rebuild

### Changing App Name

Edit `build_demo.spec`:
```python
name='YourCustomName',
```

### Including Additional Files

Edit `build_demo.spec`:
```python
datas = [
    ('config.ini', '.'),
    ('fb_main.ui', '.'),
    ('additional_file.txt', '.'),  # Add more files here
],
```

## 🔍 Troubleshooting

### "Module not found" errors

If the executable can't find a module:
1. Add it to `hiddenimports` in `build_demo.spec`
2. Rebuild

### Large file size

The executable includes Python and all dependencies, so it will be large (100-300MB). This is normal.

### App won't start

1. Check console output (if console=True in spec file)
2. Verify all data files are included in `datas`
3. Check file permissions

### macOS: "App is damaged" warning

This is a macOS security feature. To fix:
```bash
# Remove quarantine attribute
xattr -cr dist/FacebookMarketingTool.app
```

Or have the client right-click → Open (first time only).

## 📝 Notes

- **First run** may be slower (extracting bundled files)
- **File size** will be large (includes Python runtime)
- **Config file** is bundled - client can modify `config.ini` if needed
- **Data directories** will be created in the same folder as the executable

## ✅ Verification Checklist

Before distributing:
- [ ] Executable runs without errors
- [ ] All features accessible
- [ ] UI displays correctly
- [ ] Config file is included
- [ ] No source code visible
- [ ] Tested on clean system (if possible)

## 🎉 You're Done!

Your demo version is ready to distribute. The client can run it without:
- Installing Python
- Installing dependencies
- Seeing source code
- Any technical setup

Just extract and run!

