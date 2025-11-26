# 🌍 Cross-Platform Build Guide

## Platform Support

This application can be built for:
- ✅ **macOS** (Apple Silicon & Intel)
- ✅ **Windows** (10/11)
- ✅ **Linux** (Ubuntu, Debian, etc.)

## Current Build Status

### macOS Build ✅
- **Location**: `dist/FacebookMarketingTool.app`
- **Status**: Built and ready
- **Size**: ~41MB

### Windows Build 📋
- **Status**: Configuration ready, needs Windows machine to build
- **Spec File**: `build_demo_windows.spec`
- **Build Script**: `build_demo_windows.bat`

### Linux Build 📋
- **Status**: Can use macOS spec file
- **Build Script**: `build_demo_universal.sh`

## 🪟 Building for Windows

### Option 1: Build on Windows Machine (Recommended)

1. **Transfer the project** to a Windows PC
2. **Set up Python environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. **Run the Windows build script**:
   ```cmd
   build_demo_windows.bat
   ```
4. **Result**: `dist\FacebookMarketingTool.exe`

### Option 2: Use Windows Subsystem for Linux (WSL)

If you have WSL installed:
```bash
# In WSL
cd /mnt/c/path/to/project
./build_demo_universal.sh
```

### Option 3: Cross-Compilation (Advanced)

Cross-compilation from macOS to Windows is complex and not recommended. It's better to build on the target platform.

## 🍎 Building for macOS

Already done! Use:
```bash
./build_demo.sh
```

Or use the universal script:
```bash
./build_demo_universal.sh
```

## 🐧 Building for Linux

```bash
# On a Linux machine
./build_demo_universal.sh
```

Or manually:
```bash
pyinstaller build_demo.spec
```

## 📦 Distribution Packages

### macOS
```bash
cd dist
zip -r FacebookMarketingTool_macOS.zip FacebookMarketingTool.app
```

### Windows
```cmd
cd dist
powershell Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Windows.zip
```

### Linux
```bash
cd dist
zip -r FacebookMarketingTool_Linux.zip FacebookMarketingTool
```

## 🔄 Building All Platforms

To build for all platforms, you'll need:

1. **macOS build**: Run on macOS
   ```bash
   ./build_demo.sh
   ```

2. **Windows build**: Run on Windows
   ```cmd
   build_demo_windows.bat
   ```

3. **Linux build**: Run on Linux
   ```bash
   ./build_demo_universal.sh
   ```

## 📋 Platform-Specific Notes

### Windows
- Uses `build_demo_windows.spec`
- Includes `wmi` library (Windows-specific)
- Creates `.exe` file
- May need Visual C++ Redistributable on client machine

### macOS
- Uses `build_demo.spec`
- Creates `.app` bundle
- May need to remove quarantine: `xattr -cr dist/FacebookMarketingTool.app`

### Linux
- Uses `build_demo.spec`
- Creates standalone executable
- May need to set execute permissions: `chmod +x dist/FacebookMarketingTool`

## 🧪 Testing Each Platform

### macOS
```bash
open dist/FacebookMarketingTool.app
```

### Windows
```cmd
dist\FacebookMarketingTool.exe
```

### Linux
```bash
./dist/FacebookMarketingTool
```

## 📤 Client Distribution

### For macOS Clients
- Send: `FacebookMarketingTool_macOS.zip`
- Instructions: Extract and double-click `.app` file

### For Windows Clients
- Send: `FacebookMarketingTool_Windows.zip`
- Instructions: Extract and double-click `.exe` file
- Note: May need to allow through Windows Defender

### For Linux Clients
- Send: `FacebookMarketingTool_Linux.zip`
- Instructions: Extract, `chmod +x FacebookMarketingTool`, then run

## ⚠️ Important Notes

1. **Platform-Specific Builds**: Each platform needs its own build
2. **No Cross-Compilation**: Build on the target platform for best results
3. **File Sizes**: Each build will be ~40-50MB
4. **Dependencies**: All bundled, no external requirements
5. **Source Code**: Never included, always compiled

## 🎯 Quick Reference

| Platform | Spec File | Build Script | Output |
|----------|-----------|--------------|--------|
| macOS | `build_demo.spec` | `build_demo.sh` | `.app` |
| Windows | `build_demo_windows.spec` | `build_demo_windows.bat` | `.exe` |
| Linux | `build_demo.spec` | `build_demo_universal.sh` | executable |

## ✅ Checklist for Multi-Platform Distribution

- [ ] macOS build completed
- [ ] Windows build completed (on Windows machine)
- [ ] Linux build completed (if needed)
- [ ] All builds tested
- [ ] Distribution packages created
- [ ] Client instructions prepared

