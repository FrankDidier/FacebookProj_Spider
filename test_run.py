#!/usr/bin/env python3
"""
Quick test script to verify the application can start
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Facebook Marketing Tool - Startup Test")
print("=" * 60)

# Test 1: Import compatibility layer
print("\n[1/5] Testing PySide2 compatibility layer...")
try:
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    print("   ✓ PySide2 compatibility layer working")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Import main modules
print("\n[2/5] Testing core imports...")
try:
    from autoads.config import config
    config.name = 'config.ini'
    print("   ✓ Config module loaded")
except Exception as e:
    print(f"   ✗ Error loading config: {e}")
    sys.exit(1)

# Test 3: Import application
print("\n[3/5] Testing application import...")
try:
    # Import without running
    import facebook
    print("   ✓ Application module imported successfully")
except Exception as e:
    print(f"   ✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check QApplication can be created
print("\n[4/5] Testing GUI framework...")
try:
    app = QApplication(sys.argv)
    print("   ✓ QApplication created successfully")
    app.quit()
except Exception as e:
    print(f"   ✗ Error creating QApplication: {e}")
    sys.exit(1)

# Test 5: Check config file
print("\n[5/5] Testing configuration...")
try:
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    if os.path.exists(config_path):
        print(f"   ✓ Config file found: {config_path}")
    else:
        print(f"   ⚠ Config file not found: {config_path}")
except Exception as e:
    print(f"   ✗ Error checking config: {e}")

print("\n" + "=" * 60)
print("✓ All tests passed! Application is ready to run.")
print("=" * 60)
print("\nTo run the application:")
print("  ./run.sh")
print("  OR")
print("  source venv/bin/activate && python3 facebook.py")
print()

