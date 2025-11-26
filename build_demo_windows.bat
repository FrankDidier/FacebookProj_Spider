@echo off
REM Build script for creating demo version executable (Windows)
REM Run this script on a Windows machine

echo ==========================================
echo Building Facebook Marketing Tool Demo (Windows)
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "facebook.py" (
    echo Error: facebook.py not found. Please run this script from the project root.
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: venv not found. Using system Python.
)

REM Check if PyInstaller is installed
echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds (but keep build_demo_windows.spec)
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo.

REM Build the executable
echo Building executable (this may take a few minutes)...
echo.

REM Use the spec file
pyinstaller build_demo_windows.spec

REM Check if build was successful
if exist "dist\FacebookMarketingTool.exe" (
    echo.
    echo ==========================================
    echo Build Successful!
    echo ==========================================
    echo.
    echo Executable location:
    echo   dist\FacebookMarketingTool.exe
    echo.
    echo To test the app:
    echo   dist\FacebookMarketingTool.exe
    echo.
    echo To create a distributable package:
    echo   cd dist
    echo   powershell Compress-Archive -Path FacebookMarketingTool.exe -DestinationPath FacebookMarketingTool_Demo.zip
    echo.
    echo Note: The executable includes all dependencies.
    echo You can distribute this to your client without source code.
    echo.
) else (
    echo.
    echo Build failed. Check the output above for errors.
    exit /b 1
)

pause

