# Facebook Marketing Tool

A Python-based GUI application for Facebook group scraping, member collection, and automated messaging using Selenium and PySide2.

## Prerequisites

### System Requirements
- **Python 3.7 or higher** (Python 3.8+ recommended)
- **macOS, Windows, or Linux** (Note: Some features may be Windows-specific)
- **AdsPower Global Browser** (External application required)

### External Dependencies
1. **AdsPower Global Browser**: This application requires AdsPower Global browser to be installed
   - Download from: https://www.adspower.com/
   - The application path will need to be configured in the GUI

## Installation

### Step 1: Check Python Version

First, verify you have Python 3.7 or higher installed:

```bash
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Create a Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other projects:

```bash
# Navigate to the project directory
cd /Users/vv/Desktop/src-facebook

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note for macOS/Linux users**: The `wmi` package is Windows-only and will be skipped on non-Windows systems. This is expected and won't cause issues unless you're running Windows-specific features.

### Step 4: Verify Installation

Check that all packages are installed correctly:

```bash
pip list
```

You should see packages like:
- PySide2
- selenium
- requests
- pyDes
- loguru
- better-exceptions

## Configuration

### Step 1: Configure the Application

Before running, you'll need to configure the application:

1. **AdsPower Global Browser Key**: You'll need an API key from AdsPower Global
2. **AdsPower Global Browser Path**: Path to the AdsPower Global executable
3. **Activation Code**: The application requires an activation code (license)

These can be configured through the GUI when you first run the application.

### Step 2: Check config.ini

The `config.ini` file contains default settings. You can edit it directly or configure through the GUI:

- `activator_service`: The activation server URL
- `ads_key`: Your AdsPower Global API key
- `service_app_path`: Path to AdsPower Global executable

## Running the Application

### Method 1: Run the Main Application

```bash
# Make sure you're in the project directory and virtual environment is activated
python3 facebook.py
```

### Method 2: Run with Python Module

```bash
python3 -m facebook
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Verify you're using the correct Python version: `python3 --version`

2. **GUI Not Showing**
   - Ensure PySide2 is installed: `pip install PySide2`
   - On Linux, you may need: `sudo apt-get install python3-pyside2` (Ubuntu/Debian)

3. **Selenium/WebDriver Issues**
   - Make sure Chrome/Chromium is installed
   - Selenium will use the browser from AdsPower Global

4. **AdsPower Global Connection Issues**
   - Verify AdsPower Global is installed and running
   - Check that the API key is correct
   - Ensure the executable path in config.ini is correct

5. **Activation Code Issues**
   - Verify your internet connection
   - Check that the activation server is accessible
   - Ensure the activation code is valid

6. **macOS Specific Issues**
   - The `wmi` package is Windows-only and will be skipped (this is normal)
   - Some Windows-specific features may not work on macOS

### Getting Help

If you encounter issues:
1. Check the log files in the `log/` directory
2. Verify all dependencies are installed
3. Ensure Python version is 3.7 or higher
4. Check that AdsPower Global is properly configured

## Project Structure

```
src-facebook/
├── autoads/          # Core automation and scraping modules
├── spider/           # Facebook-specific spider implementations
├── config.ini        # Configuration file
├── facebook.py       # Main application entry point
├── fb_main.py        # UI definitions (auto-generated)
├── fb_main.ui        # UI design file
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Features

- **Group Scraping**: Automatically scrape Facebook groups based on keywords
- **Member Collection**: Collect member information from groups
- **Automated Messaging**: Send automated messages to group members
- **Multi-threaded**: Supports concurrent operations
- **GUI Interface**: User-friendly graphical interface

## Important Notes

⚠️ **Legal and Ethical Considerations**:
- This tool is for educational purposes
- Ensure compliance with Facebook's Terms of Service
- Respect privacy and data protection regulations
- Use responsibly and ethically

⚠️ **System Compatibility**:
- Some features may be Windows-specific (WMI usage)
- AdsPower Global browser is required
- Internet connection required for activation

## License

Please check with the original author for licensing information.

