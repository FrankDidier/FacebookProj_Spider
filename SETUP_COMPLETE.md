# Setup Complete! 🎉

Your Facebook Marketing Tool project is now set up and ready to run.

## Quick Start

### Option 1: Using the run script (Easiest)
```bash
./run.sh
```

### Option 2: Manual run
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 facebook.py
```

## What Was Fixed

1. ✅ **PySide2 Compatibility**: Created a compatibility layer (`pyside2_compat.py`) to use PySide6 instead of PySide2 (which isn't available for macOS arm64)

2. ✅ **WMI Compatibility**: Made the Windows-only `wmi` library optional for macOS compatibility

3. ✅ **Path Fixes**: Fixed Windows-style path separators in `config.py` to work on macOS

4. ✅ **Dependencies**: Installed all required packages:
   - PySide6 (GUI framework)
   - Selenium (web automation)
   - Requests (HTTP library)
   - pyDes (encryption)
   - loguru (logging)
   - better-exceptions (exception formatting)
   - All sub-dependencies

## Important Notes

⚠️ **Before Running**:
- You need **AdsPower Global Browser** installed
- You need an **AdsPower Global API key**
- You need an **activation code** (license) to use the application
- The application requires internet connection for activation

⚠️ **macOS Specific**:
- The `wmi` library is Windows-only and will be skipped (this is normal)
- Some Windows-specific features may not work on macOS
- The application uses PySide6 instead of PySide2 (compatibility layer handles this)

## Configuration

The application will prompt you for:
1. **AdsPower Global Browser Key**: Your API key
2. **AdsPower Global Browser Path**: Path to the executable (e.g., `/Applications/AdsPower Global.app/Contents/MacOS/AdsPower Global`)
3. **Activation Code**: Your license code

You can also edit `config.ini` directly if needed.

## Troubleshooting

If you encounter issues:

1. **Import Errors**: Make sure virtual environment is activated
   ```bash
   source venv/bin/activate
   ```

2. **GUI Not Showing**: 
   - Verify PySide6 is installed: `pip list | grep PySide6`
   - On macOS, you may need to allow the app in System Preferences > Security & Privacy

3. **AdsPower Issues**:
   - Make sure AdsPower Global is installed and running
   - Check that the API key is correct
   - Verify the executable path is correct

4. **Activation Issues**:
   - Check your internet connection
   - Verify the activation server is accessible
   - Ensure your activation code is valid

## Project Structure

```
src-facebook/
├── venv/              # Virtual environment (don't edit)
├── autoads/           # Core modules
├── spider/            # Facebook spiders
├── config.ini         # Configuration file
├── facebook.py        # Main application
├── fb_main.py         # UI definitions
├── pyside2_compat.py  # PySide6 compatibility layer
├── run.sh             # Run script
└── requirements.txt   # Dependencies
```

## Next Steps

1. Install AdsPower Global Browser if you haven't already
2. Get your AdsPower Global API key
3. Get your activation code
4. Run the application: `./run.sh`
5. Configure the application through the GUI

Enjoy using the Facebook Marketing Tool! 🚀

