#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite - Test all features and UI integration
"""
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test results tracking
test_results = []
errors = []
warnings = []

def test(name, condition, message=""):
    """Record test result"""
    if condition:
        test_results.append(("✅", name, message))
        print(f"✅ {name}" + (f": {message}" if message else ""))
    else:
        test_results.append(("❌", name, message))
        errors.append(f"❌ {name}: {message}")
        print(f"❌ {name}" + (f": {message}" if message else ""))

def test_warning(name, message):
    """Record warning"""
    warnings.append(f"⚠️  {name}: {message}")
    print(f"⚠️  {name}: {message}")

print("=" * 80)
print("COMPREHENSIVE FEATURE TEST SUITE")
print("=" * 80)
print()

# ============================================================================
# 1. Test Imports
# ============================================================================
print("1. Testing Imports...")
print("-" * 80)

try:
    import pyside2_compat
    test("Import: pyside2_compat", True)
except Exception as e:
    test("Import: pyside2_compat", False, str(e))

try:
    from autoads.config import config
    config.name = 'config.ini'
    config.init_config()
    test("Import: autoads.config", True)
except Exception as e:
    test("Import: autoads.config", False, str(e))

try:
    from autoads.automation_actions import AutomationActions
    test("Import: AutomationActions", True)
except Exception as e:
    test("Import: AutomationActions", False, str(e))

# Test all automation spiders
automation_spiders = [
    ('fb_auto_like', 'AutoLikeSpider'),
    ('fb_auto_comment', 'AutoCommentSpider'),
    ('fb_auto_follow', 'AutoFollowSpider'),
    ('fb_auto_add_friend', 'AutoAddFriendSpider'),
    ('fb_auto_group', 'AutoGroupSpider'),
    ('fb_auto_post', 'AutoPostSpider'),
    ('fb_advanced_messaging', 'AdvancedMessagingSpider'),
    ('fb_auto_register', 'AutoRegisterSpider'),
    ('fb_contact_list', 'ContactListSpider'),
]

for module_name, class_name in automation_spiders:
    try:
        module = __import__(f'spider.{module_name}', fromlist=[class_name])
        spider_class = getattr(module, class_name)
        test(f"Import: {class_name}", spider_class is not None)
    except Exception as e:
        test(f"Import: {class_name}", False, str(e))

print()

# ============================================================================
# 2. Test Configuration
# ============================================================================
print("2. Testing Configuration...")
print("-" * 80)

config_properties = [
    'like_mode', 'like_keywords', 'like_count', 'like_interval',
    'comment_mode', 'comment_keywords', 'comment_content', 'comment_count',
    'follow_mode', 'follow_keywords', 'follow_count',
    'add_friend_mode', 'add_friend_count', 'add_friend_interval',
    'group_action', 'group_keywords', 'group_join_count',
    'main_post_content', 'main_post_count', 'main_post_interval',
    'message_mode', 'advanced_message_content', 'advanced_message_count',
    'register_count', 'register_name_lang', 'register_country_code',
    'contact_action', 'contact_count', 'contact_region',
]

for prop in config_properties:
    try:
        value = getattr(config, prop, None)
        test(f"Config: {prop}", value is not None or hasattr(config, prop))
    except Exception as e:
        test(f"Config: {prop}", False, str(e))

print()

# ============================================================================
# 3. Test UI Creation
# ============================================================================
print("3. Testing UI Creation...")
print("-" * 80)

try:
    from PySide2.QtWidgets import QApplication
    from fb_main import Ui_MainWindow
    from PySide2.QtWidgets import QMainWindow
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    
    test("UI: MainWindow creation", True)
    
    # Test sidebar
    test("UI: Sidebar exists", hasattr(ui, 'sidebarList'))
    if hasattr(ui, 'sidebarList'):
        sidebar_count = ui.sidebarList.count()
        test("UI: Sidebar items", sidebar_count >= 20, f"{sidebar_count} items")
        
        # Check for automation items
        automation_items = []
        for i in range(sidebar_count):
            item = ui.sidebarList.item(i)
            if item:
                text = item.text()
                if any(x in text for x in ['自动', '🤍', '💬', '👥', '➕', '📝', '💌', '📋']):
                    automation_items.append(text)
        
        test("UI: Automation sidebar items", len(automation_items) >= 9, 
             f"Found {len(automation_items)} automation items")
    
    # Test stacked pages
    test("UI: StackedPages exists", hasattr(ui, 'stackedPages'))
    if hasattr(ui, 'stackedPages'):
        pages_count = ui.stackedPages.count()
        test("UI: StackedPages count", pages_count >= 20, f"{pages_count} pages")
    
    # Test automation tabs
    automation_tabs = [
        'tabAutoLike', 'tabAutoComment', 'tabAutoFollow', 'tabAutoAddFriend',
        'tabAutoGroup', 'tabAutoPost', 'tabAdvancedMessaging', 
        'tabAutoRegister', 'tabContactList'
    ]
    
    for tab_name in automation_tabs:
        test(f"UI: {tab_name}", hasattr(ui, tab_name))
    
    # Test automation buttons
    automation_buttons = [
        'pushButtonAutoLikeStart', 'pushButtonAutoLikeStop',
        'pushButtonAutoCommentStart', 'pushButtonAutoCommentStop',
        'pushButtonAutoFollowStart', 'pushButtonAutoFollowStop',
        'pushButtonAutoAddFriendStart', 'pushButtonAutoAddFriendStop',
        'pushButtonAutoGroupStart', 'pushButtonAutoGroupStop',
        'pushButtonAutoPostStart', 'pushButtonAutoPostStop',
        'pushButtonAdvancedMessagingStart', 'pushButtonAdvancedMessagingStop',
        'pushButtonAutoRegisterStart', 'pushButtonAutoRegisterStop',
        'pushButtonContactListStart', 'pushButtonContactListStop',
    ]
    
    for btn_name in automation_buttons:
        test(f"UI: {btn_name}", hasattr(ui, btn_name))
    
    app.quit()
    
except Exception as e:
    test("UI: Creation", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# 4. Test Handlers
# ============================================================================
print("4. Testing Handlers...")
print("-" * 80)

try:
    from facebook import MainWindow
    from PySide2.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    
    # Test automation handlers
    automation_handlers = [
        'on_auto_like_spider_start', 'on_auto_like_spider_stop',
        'on_auto_comment_spider_start', 'on_auto_comment_spider_stop',
        'on_auto_follow_spider_start', 'on_auto_follow_spider_stop',
        'on_auto_add_friend_spider_start', 'on_auto_add_friend_spider_stop',
        'on_auto_group_spider_start', 'on_auto_group_spider_stop',
        'on_auto_post_spider_start', 'on_auto_post_spider_stop',
        'on_advanced_messaging_spider_start', 'on_advanced_messaging_spider_stop',
        'on_auto_register_spider_start', 'on_auto_register_spider_stop',
        'on_contact_list_spider_start', 'on_contact_list_spider_stop',
    ]
    
    for handler_name in automation_handlers:
        test(f"Handler: {handler_name}", hasattr(window, handler_name))
        if hasattr(window, handler_name):
            handler = getattr(window, handler_name)
            test(f"Handler callable: {handler_name}", callable(handler))
    
    app.quit()
    
except Exception as e:
    test("Handlers: Test", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# 5. Test Automation Actions
# ============================================================================
print("5. Testing Automation Actions...")
print("-" * 80)

try:
    from autoads.automation_actions import AutomationActions
    
    # Test static methods exist
    action_methods = [
        'like_post',
        'comment_on_post',
        'follow_user',
        'add_friend',
        'join_group',
        'post_to_group',
    ]
    
    for method_name in action_methods:
        test(f"Action: {method_name}", hasattr(AutomationActions, method_name))
        if hasattr(AutomationActions, method_name):
            method = getattr(AutomationActions, method_name)
            test(f"Action callable: {method_name}", callable(method))
    
except Exception as e:
    test("Automation Actions: Test", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# 6. Test Spider Manager
# ============================================================================
print("6. Testing Spider Manager...")
print("-" * 80)

try:
    from spider_manager import SpiderManager
    
    # Test automation spiders in manager
    automation_spider_names = [
        'auto_like', 'auto_comment', 'auto_follow', 'auto_add_friend',
        'auto_group', 'auto_post', 'advanced_messaging', 
        'auto_register', 'contact_list'
    ]
    
    for spider_name in automation_spider_names:
        spider_class = SpiderManager.get_spider_class(spider_name)
        test(f"SpiderManager: {spider_name}", spider_class is not None)
    
except Exception as e:
    test("Spider Manager: Test", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# 7. Test Contact List Generator
# ============================================================================
print("7. Testing Contact List Generator...")
print("-" * 80)

try:
    from spider.fb_contact_list import ContactListGenerator
    
    # Test methods exist
    generator_methods = [
        'generate_english_names',
        'generate_phone_numbers',
        'generate_contacts',
        'save_contacts',
        'import_from_file',
    ]
    
    for method_name in generator_methods:
        test(f"ContactList: {method_name}", hasattr(ContactListGenerator, method_name))
    
    # Test generation
    try:
        contacts = ContactListGenerator.generate_contacts(5, 'US', 'en', '+1')
        test("ContactList: Generate contacts", len(contacts) == 5)
        if contacts:
            test("ContactList: Contact structure", 'name' in contacts[0] and 'phone' in contacts[0])
    except Exception as e:
        test("ContactList: Generate contacts", False, str(e))
    
except Exception as e:
    test("Contact List: Test", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# 8. Test Button Connections
# ============================================================================
print("8. Testing Button Connections...")
print("-" * 80)

try:
    from facebook import MainWindow
    from PySide2.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    
    # Check if buttons are connected
    button_connections = {
        'pushButtonAutoLikeStart': 'on_auto_like_spider_start',
        'pushButtonAutoLikeStop': 'on_auto_like_spider_stop',
        'pushButtonAutoCommentStart': 'on_auto_comment_spider_start',
        'pushButtonAutoCommentStop': 'on_auto_comment_spider_stop',
        'pushButtonAutoFollowStart': 'on_auto_follow_spider_start',
        'pushButtonAutoFollowStop': 'on_auto_follow_spider_stop',
    }
    
    for btn_name, handler_name in button_connections.items():
        if hasattr(window.ui, btn_name):
            btn = getattr(window.ui, btn_name)
            # Check if button has connections
            receivers = btn.receivers(btn.clicked)
            test(f"Button connection: {btn_name}", receivers > 0, 
                 f"{receivers} receiver(s)" if receivers > 0 else "No connections")
        else:
            test(f"Button exists: {btn_name}", False)
    
    app.quit()
    
except Exception as e:
    test("Button Connections: Test", False, str(e))
    traceback.print_exc()

print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = len(test_results)
passed_tests = len([r for r in test_results if r[0] == "✅"])
failed_tests = len([r for r in test_results if r[0] == "❌"])

print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"⚠️  Warnings: {len(warnings)}")

if failed_tests > 0:
    print("\n❌ FAILED TESTS:")
    for error in errors:
        print(f"  {error}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for warning in warnings:
        print(f"  {warning}")

print("\n" + "=" * 80)
if failed_tests == 0:
    print("✅ ALL TESTS PASSED!")
else:
    print(f"❌ {failed_tests} TEST(S) FAILED")
print("=" * 80)

sys.exit(0 if failed_tests == 0 else 1)

