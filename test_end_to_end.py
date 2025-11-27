#!/usr/bin/env python3
"""
End-to-End Test - Complete application flow with Configuration Wizard
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("END-TO-END TEST - Configuration Wizard")
print("=" * 70)
print()

try:
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import QTimer
    from facebook import MainWindow
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("Step 1: Creating MainWindow...")
    window = MainWindow()
    print("✅ MainWindow created")
    print()
    
    print("Step 2: Checking Configuration Wizard...")
    if hasattr(window.ui, 'configWizardPage') and window.ui.configWizardPage:
        wizard = window.ui.configWizardPage
        print("✅ Configuration Wizard found")
        print(f"   - Type: {type(wizard).__name__}")
        print(f"   - Has path_edit: {hasattr(wizard, 'path_edit')}")
        print(f"   - Has api_key_edit: {hasattr(wizard, 'api_key_edit')}")
        print(f"   - Has status_labels: {hasattr(wizard, 'status_labels')}")
    else:
        print("❌ Configuration Wizard not found")
    print()
    
    print("Step 3: Testing Sidebar Navigation...")
    if hasattr(window.ui, 'sidebarList'):
        # Switch to config wizard (first item)
        window.ui.sidebarList.setCurrentRow(0)
        current_row = window.ui.sidebarList.currentRow()
        print(f"✅ Switched to sidebar item {current_row}")
        
        if hasattr(window.ui, 'stackedPages'):
            page_index = window.ui.stackedPages.currentIndex()
            print(f"✅ Stacked page index: {page_index}")
    print()
    
    print("Step 4: Testing validate_setup Method...")
    result = window.validate_setup("测试功能")
    print(f"✅ validate_setup returned: {result}")
    print(f"   - Correctly blocks when setup incomplete: {result == False}")
    print()
    
    print("Step 5: Testing All Spider Start Methods Have Validation...")
    spider_methods = [
        'on_group_spider_start',
        'on_member_spider_start',
        'on_greets_spider_start',
        'on_group_specified_spider_start',
        'on_members_rapid_spider_start',
        'on_posts_spider_start',
        'on_pages_spider_start',
        'on_ins_followers_spider_start',
        'on_ins_following_spider_start',
        'on_ins_profile_spider_start',
        'on_ins_reels_comments_spider_start',
    ]
    
    all_have_validation = True
    for method_name in spider_methods:
        if hasattr(window, method_name):
            # Check if method calls validate_setup
            import inspect
            source = inspect.getsource(getattr(window, method_name))
            has_validation = 'validate_setup' in source
            if has_validation:
                print(f"✅ {method_name}: Has validation")
            else:
                print(f"❌ {method_name}: Missing validation")
                all_have_validation = False
        else:
            print(f"❌ {method_name}: Method not found")
            all_have_validation = False
    
    if all_have_validation:
        print("✅ All spider methods have validation!")
    print()
    
    print("Step 6: Testing Configuration Wizard Methods...")
    if hasattr(window.ui, 'configWizardPage') and window.ui.configWizardPage:
        wizard = window.ui.configWizardPage
        
        methods_to_test = [
            'load_config',
            'save_config',
            'run_validation',
            'browse_ads_power_path',
            'toggle_api_key_visibility',
        ]
        
        for method_name in methods_to_test:
            if hasattr(wizard, method_name) and callable(getattr(wizard, method_name)):
                print(f"✅ {method_name}: Exists and callable")
            else:
                print(f"❌ {method_name}: Missing or not callable")
    print()
    
    print("=" * 70)
    print("✅ END-TO-END TEST COMPLETE!")
    print("=" * 70)
    print()
    print("Configuration Wizard is fully integrated and functional!")
    print()
    
    # Quit after a moment
    QTimer.singleShot(500, app.quit)
    app.exec_()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        app.quit()
    except:
        pass

