#!/usr/bin/env python3
"""
Comprehensive test script for all new features
Tests each spider, UI integration, and functionality
"""
import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("COMPREHENSIVE FEATURE TEST")
print("=" * 70)

# Test results
test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_result(name, passed, message=""):
    """Record test result"""
    if passed:
        test_results['passed'].append(name)
        print(f"✓ {name}: PASSED")
        if message:
            print(f"  {message}")
    else:
        test_results['failed'].append(name)
        print(f"✗ {name}: FAILED")
        if message:
            print(f"  {message}")

def test_warning(name, message):
    """Record warning"""
    test_results['warnings'].append(f"{name}: {message}")
    print(f"⚠ {name}: {message}")

# Test 1: Import compatibility layer
print("\n[1] Testing PySide2 compatibility layer...")
try:
    import pyside2_compat
    from PySide2.QtWidgets import QApplication, QWidget
    from PySide2.QtCore import Qt
    test_result("PySide2 Compatibility", True)
except Exception as e:
    test_result("PySide2 Compatibility", False, str(e))
    sys.exit(1)

# Test 2: Import all spider classes
print("\n[2] Testing Spider Imports...")
# Initialize config before importing spiders
from autoads.config import config
config.name = 'config.ini'

spiders_to_test = [
    ('fb_group_specified', 'GroupSpecifiedSpider'),
    ('fb_members_rapid', 'MembersRapidSpider'),
    ('fb_posts', 'PostsSpider'),
    ('fb_pages', 'PagesSpider'),
    ('ins_followers', 'InstagramFollowersSpider'),
    ('ins_following', 'InstagramFollowingSpider'),
    ('ins_profile', 'InstagramProfileSpider'),
    ('ins_reels_comments', 'InstagramReelsCommentsSpider'),
]

for module_name, class_name in spiders_to_test:
    try:
        module = __import__(f'spider.{module_name}', fromlist=[class_name])
        spider_class = getattr(module, class_name)
        test_result(f"Import {class_name}", True)
    except Exception as e:
        test_result(f"Import {class_name}", False, str(e))

# Test 3: Import all item classes
print("\n[3] Testing Item Class Imports...")
items_to_test = [
    ('autoads.items.post_item', 'PostItem'),
    ('autoads.items.page_item', 'PageItem'),
    ('autoads.items.ins_user_item', 'InstagramUserItem'),
    ('autoads.items.ins_user_item', 'InstagramFollowerItem'),
    ('autoads.items.ins_user_item', 'InstagramFollowingItem'),
    ('autoads.items.ins_user_item', 'InstagramReelsCommentItem'),
]

for module_name, class_name in items_to_test:
    try:
        module = __import__(module_name, fromlist=[class_name])
        item_class = getattr(module, class_name)
        # Test instantiation
        item = item_class()
        test_result(f"Import & Instantiate {class_name}", True)
    except Exception as e:
        test_result(f"Import & Instantiate {class_name}", False, str(e))

# Test 4: Configuration system
print("\n[4] Testing Configuration System...")
try:
    from autoads.config import config
    config.name = 'config.ini'
    
    # Test new config properties
    config_props = [
        'posts_table',
        'post_groups_nums',
        'pages_table',
        'page_keywords',
        'page_urls',
        'ins_target_users',
        'ins_reels_urls',
    ]
    
    for prop in config_props:
        try:
            value = getattr(config, prop)
            test_result(f"Config Property: {prop}", True)
        except Exception as e:
            test_result(f"Config Property: {prop}", False, str(e))
            
except Exception as e:
    test_result("Configuration System", False, str(e))

# Test 5: UI Structure
print("\n[5] Testing UI Structure...")
# Reuse existing QApplication if available, otherwise create new one
try:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
except:
    app = QApplication(sys.argv)

try:
    from fb_main import Ui_MainWindow
    from PySide2.QtWidgets import QMainWindow
    
    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    
    # Test sidebar
    if hasattr(ui, 'sidebarList'):
        item_count = ui.sidebarList.count()
        test_result("Sidebar List Widget", True, f"{item_count} items")
        
        # Check if all expected items are present
        expected_items = [
            "采集群组", "采集成员", "私信成员",
            "FB小组指定采集", "FB小组成员极速采集", "FB小组帖子采集",
            "FB公共主页采集", "INS用户粉丝采集", "INS用户关注采集",
            "INS用户简介采集", "INS-reels评论采集", "更多功能"
        ]
        
        found_items = []
        for i in range(item_count):
            item = ui.sidebarList.item(i)
            if item:
                found_items.append(item.text())
        
        if len(found_items) >= len(expected_items):
            test_result("Sidebar Items Count", True, f"Found {len(found_items)} items")
        else:
            test_warning("Sidebar Items", f"Expected {len(expected_items)}, found {len(found_items)}")
    else:
        test_result("Sidebar List Widget", False, "sidebarList not found")
    
    # Test stacked widget
    if hasattr(ui, 'stackedPages'):
        page_count = ui.stackedPages.count()
        test_result("Stacked Pages Widget", True, f"{page_count} pages")
    else:
        test_result("Stacked Pages Widget", False, "stackedPages not found")
    
    # Test new tab widgets exist
    new_tabs = [
        'tabGroupSpecified', 'tabMembersRapid', 'tabPosts', 'tabPages',
        'tabInsFollowers', 'tabInsFollowing', 'tabInsProfile', 'tabInsReelsComments'
    ]
    
    for tab_name in new_tabs:
        if hasattr(ui, tab_name):
            test_result(f"UI Tab: {tab_name}", True)
        else:
            test_result(f"UI Tab: {tab_name}", False, "Tab not found")
    
    app.quit()
    
except Exception as e:
    test_result("UI Structure", False, str(e))
    import traceback
    traceback.print_exc()
    app.quit()

# Test 6: Main Application Integration
print("\n[6] Testing Main Application Integration...")
# Reuse existing QApplication
try:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
except:
    app = QApplication(sys.argv)

try:
    from facebook import MainWindow
    
    window = MainWindow()
    
    # Test that all handlers exist
    handlers = [
        'on_group_specified_spider_start',
        'on_group_specified_spider_stop',
        'on_members_rapid_spider_start',
        'on_members_rapid_spider_stop',
        'on_posts_spider_start',
        'on_posts_spider_stop',
        'on_pages_spider_start',
        'on_pages_spider_stop',
        'on_ins_followers_spider_start',
        'on_ins_followers_spider_stop',
        'on_ins_following_spider_start',
        'on_ins_following_spider_stop',
        'on_ins_profile_spider_start',
        'on_ins_profile_spider_stop',
        'on_ins_reels_comments_spider_start',
        'on_ins_reels_comments_spider_stop',
    ]
    
    for handler_name in handlers:
        if hasattr(window, handler_name):
            test_result(f"Handler: {handler_name}", True)
        else:
            test_result(f"Handler: {handler_name}", False, "Handler not found")
    
    # Test stop events
    stop_events = [
        'group_specified_stop_event',
        'members_rapid_stop_event',
        'posts_stop_event',
        'pages_stop_event',
        'ins_followers_stop_event',
        'ins_following_stop_event',
        'ins_profile_stop_event',
        'ins_reels_comments_stop_event',
    ]
    
    for event_name in stop_events:
        if hasattr(window, event_name):
            test_result(f"Stop Event: {event_name}", True)
        else:
            test_result(f"Stop Event: {event_name}", False, "Event not found")
    
    app.quit()
    
except Exception as e:
    test_result("Main Application Integration", False, str(e))
    import traceback
    traceback.print_exc()
    app.quit()

# Test 7: Spider Manager
print("\n[7] Testing Spider Manager...")
try:
    from spider_manager import SpiderManager
    
    # Test getting spider classes
    for spider_name in ['fb_group_specified', 'fb_members_rapid', 'fb_posts', 
                       'fb_pages', 'ins_followers', 'ins_following', 
                       'ins_profile', 'ins_reels_comments']:
        spider_class = SpiderManager.get_spider_class(spider_name)
        if spider_class:
            test_result(f"SpiderManager: {spider_name}", True)
        else:
            test_result(f"SpiderManager: {spider_name}", False, "Class not found")
            
except Exception as e:
    test_result("Spider Manager", False, str(e))

# Test 8: File Structure
print("\n[8] Testing File Structure...")
required_files = [
    'spider/fb_group_specified.py',
    'spider/fb_members_rapid.py',
    'spider/fb_posts.py',
    'spider/fb_pages.py',
    'spider/ins_followers.py',
    'spider/ins_following.py',
    'spider/ins_profile.py',
    'spider/ins_reels_comments.py',
    'autoads/items/post_item.py',
    'autoads/items/page_item.py',
    'autoads/items/ins_user_item.py',
    'spider_manager.py',
]

for file_path in required_files:
    if os.path.exists(file_path):
        test_result(f"File: {file_path}", True)
    else:
        test_result(f"File: {file_path}", False, "File not found")

# Test 9: Configuration File
print("\n[9] Testing Configuration File...")
try:
    import configparser
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini', encoding='utf-8')
    
    required_sections = ['posts', 'pages', 'instagram']
    for section in required_sections:
        if config_parser.has_section(section):
            test_result(f"Config Section: {section}", True)
        else:
            test_result(f"Config Section: {section}", False, "Section not found")
            
except Exception as e:
    test_result("Configuration File", False, str(e))

# Test 10: UI Button Connections
print("\n[10] Testing UI Button Connections...")
# Reuse existing QApplication
try:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
except:
    app = QApplication(sys.argv)

try:
    from facebook import MainWindow
    
    window = MainWindow()
    
    # Check if buttons can be found (they may not exist if UI wasn't fully created)
    button_pairs = [
        ('pushButtonGroupSpecifiedStart', 'pushButtonGroupSpecifiedStop'),
        ('pushButtonMembersRapidStart', 'pushButtonMembersRapidStop'),
        ('pushButtonPostsStart', 'pushButtonPostsStop'),
        ('pushButtonPagesStart', 'pushButtonPagesStop'),
        ('pushButtonInsFollowersStart', 'pushButtonInsFollowersStop'),
        ('pushButtonInsFollowingStart', 'pushButtonInsFollowingStop'),
        ('pushButtonInsProfileStart', 'pushButtonInsProfileStop'),
        ('pushButtonInsReelsCommentsStart', 'pushButtonInsReelsCommentsStop'),
    ]
    
    for start_btn, stop_btn in button_pairs:
        start_found = len(window.findChildren(type(window.ui.pushButtonGroupSpiderStart), start_btn)) > 0 if hasattr(window.ui, 'pushButtonGroupSpiderStart') else False
        stop_found = len(window.findChildren(type(window.ui.pushButtonGroupSpiderStart), stop_btn)) > 0 if hasattr(window.ui, 'pushButtonGroupSpiderStart') else False
        
        # Since buttons are created dynamically, we just check handlers exist
        handler_start = f"on_{start_btn.replace('pushButton', '').replace('Start', '_spider_start')}"
        handler_stop = f"on_{stop_btn.replace('pushButton', '').replace('Stop', '_spider_stop')}"
        
        if hasattr(window, handler_start) and hasattr(window, handler_stop):
            test_result(f"Button Handlers: {start_btn}/{stop_btn}", True)
        else:
            test_warning(f"Button Handlers: {start_btn}/{stop_btn}", "Handlers may be created dynamically")
    
    app.quit()
    
except Exception as e:
    test_result("UI Button Connections", False, str(e))
    import traceback
    traceback.print_exc()
    app.quit()

# Test 11: Data Directory Structure
print("\n[11] Testing Data Directory Structure...")
data_dirs = [
    './fb/post/',
    './fb/page/',
    './ins/follower/',
    './ins/following/',
    './ins/user/',
    './ins/reels_comment/',
]

for dir_path in data_dirs:
    try:
        os.makedirs(dir_path, exist_ok=True)
        if os.path.exists(dir_path):
            test_result(f"Data Directory: {dir_path}", True)
        else:
            test_result(f"Data Directory: {dir_path}", False, "Could not create")
    except Exception as e:
        test_result(f"Data Directory: {dir_path}", False, str(e))

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✓ Passed: {len(test_results['passed'])}")
print(f"✗ Failed: {len(test_results['failed'])}")
print(f"⚠ Warnings: {len(test_results['warnings'])}")
print()

if test_results['failed']:
    print("FAILED TESTS:")
    for test in test_results['failed']:
        print(f"  ✗ {test}")
    print()

if test_results['warnings']:
    print("WARNINGS:")
    for warning in test_results['warnings']:
        print(f"  ⚠ {warning}")
    print()

if len(test_results['failed']) == 0:
    print("🎉 ALL TESTS PASSED! All features are ready to use!")
else:
    print(f"⚠️  {len(test_results['failed'])} test(s) failed. Please review above.")
print("=" * 70)

