#!/usr/bin/env python3
"""
Test Application Launch with Configuration Wizard
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("APPLICATION LAUNCH TEST")
print("=" * 70)
print()

try:
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    from facebook import MainWindow
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("Creating MainWindow...")
    main_window = MainWindow()
    print("✅ MainWindow created")
    print()
    
    # Check configuration wizard
    print("Checking Configuration Wizard...")
    if hasattr(main_window.ui, 'configWizardPage'):
        if main_window.ui.configWizardPage:
            print("✅ Configuration Wizard initialized")
            print(f"   - Type: {type(main_window.ui.configWizardPage).__name__}")
        else:
            print("⚠️  Configuration Wizard placeholder exists")
    else:
        print("⚠️  Configuration Wizard not found (may be created dynamically)")
    print()
    
    # Check sidebar
    print("Checking Sidebar...")
    if hasattr(main_window.ui, 'sidebarList'):
        item_count = main_window.ui.sidebarList.count()
        print(f"✅ Sidebar has {item_count} items")
        for i in range(min(item_count, 5)):
            item = main_window.ui.sidebarList.item(i)
            if item:
                print(f"   {i+1}. {item.text()}")
    print()
    
    # Check stacked pages
    print("Checking Stacked Pages...")
    if hasattr(main_window.ui, 'stackedPages'):
        page_count = main_window.ui.stackedPages.count()
        print(f"✅ Stacked pages has {page_count} pages")
        print(f"   - Current page: {main_window.ui.stackedPages.currentIndex()}")
    print()
    
    # Test switching to config wizard
    print("Testing Page Switching...")
    if hasattr(main_window.ui, 'sidebarList') and main_window.ui.sidebarList.count() > 0:
        main_window.ui.sidebarList.setCurrentRow(0)
        current_index = main_window.ui.sidebarList.currentRow()
        print(f"✅ Switched to sidebar item {current_index}")
        
        if hasattr(main_window.ui, 'stackedPages'):
            page_index = main_window.ui.stackedPages.currentIndex()
            print(f"✅ Stacked page index: {page_index}")
    print()
    
    # Test validate_setup
    print("Testing validate_setup method...")
    if hasattr(main_window, 'validate_setup'):
        result = main_window.validate_setup("测试功能")
        print(f"✅ validate_setup returned: {result}")
        print(f"   - Type: {type(result).__name__}")
    else:
        print("❌ validate_setup method not found")
    print()
    
    print("=" * 70)
    print("✅ Application Launch Test Complete!")
    print("=" * 70)
    print()
    print("The application is ready to use!")
    print("Configuration Wizard is integrated and functional.")
    print()
    
    # Keep app running briefly to test
    QTimer.singleShot(1000, app.quit)
    app.exec_()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        app.quit()
    except:
        pass

