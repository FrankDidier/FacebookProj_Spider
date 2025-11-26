# 🪟 Windows Build Instructions

## Quick Answer

**Current macOS build**: ❌ **Cannot run on Windows** - it's macOS-specific (arm64)

**Windows version**: ✅ **Configuration ready** - needs to be built on a Windows machine

## 🚀 Building Windows Version

### Step 1: Transfer Project to Windows PC

Copy the entire project folder to a Windows machine.

### Step 2: Set Up Python Environment

On Windows, open Command Prompt or PowerShell:

```cmd
# Navigate to project folder
cd C:\path\to\src-facebook

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Step 3: Build Windows Executable

```cmd
# Run the Windows build script
build_demo_windows.bat
```

Or manually:
```cmd
pyinstaller build_demo_windows.spec
```

### Step 4: Find Your Executable

After building, you'll find:
```
dist\FacebookMarketingTool.exe
```

### Step 5: Create Distribution Package

```cmd
cd dist
powershell Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Windows.zip
```

## 📋 What's Different for Windows?

### Windows-Specific Features:
- ✅ Includes `wmi` library (Windows system info)
- ✅ Creates `.exe` file (not `.app`)
- ✅ Uses Windows paths (`\` instead of `/`)
- ✅ May need Visual C++ Redistributable

### Windows Build Configuration:
- **Spec File**: `build_demo_windows.spec`
- **Build Script**: `build_demo_windows.bat`
- **Output**: `FacebookMarketingTool.exe`

## 🧪 Testing Windows Build

```cmd
# Run the executable
dist\FacebookMarketingTool.exe
```

The app should launch with the GUI.

## ⚠️ Common Windows Issues

### Issue 1: "Windows protected your PC"
**Solution**: 
- Right-click the `.exe`
- Select "Properties"
- Check "Unblock" if available
- Or: Right-click → "Run as administrator" (first time)

### Issue 2: Missing DLL errors
**Solution**: Install Visual C++ Redistributable:
- Download from Microsoft
- Install both x64 and x86 versions

### Issue 3: Antivirus blocks it
**Solution**: 
- Add exception in Windows Defender
- Or temporarily disable during first run

## 📤 Distributing Windows Version

### Create Zip File:
```cmd
cd dist
powershell Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Windows.zip
```

### Client Instructions:
```
1. Extract FacebookMarketingTool_Windows.zip
2. Double-click FacebookMarketingTool.exe
3. If Windows warns about security:
   - Click "More info"
   - Click "Run anyway"
4. The app will start automatically
```

## 🔄 Alternative: Build on macOS for Windows

**Note**: Cross-compilation from macOS to Windows is **not recommended** and very complex. It's better to:

1. Use a Windows machine (physical or VM)
2. Or use cloud build services
3. Or ask a colleague with Windows to build it

## ✅ Windows Build Checklist

- [ ] Project copied to Windows machine
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] PyInstaller installed
- [ ] Build script executed
- [ ] Executable created
- [ ] Executable tested
- [ ] Distribution package created

## 🎯 Quick Commands Summary

```cmd
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

# Build
build_demo_windows.bat

# Test
dist\FacebookMarketingTool.exe

# Package
cd dist
powershell Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Windows.zip
```

## 📞 Need Help?

If you encounter issues:
1. Check that all dependencies are installed
2. Verify Python version (3.9+)
3. Make sure PyInstaller is latest version
4. Check build output for errors
5. Test on clean Windows machine if possible

---

**Remember**: The Windows build must be done **on a Windows machine**. The macOS build cannot run on Windows.

