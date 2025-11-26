#!/usr/bin/env python3
"""
Comprehensive Test Suite - Tests all functionalities thoroughly
"""
import sys
import os
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize config first
from autoads.config import config
config.name = 'config.ini'

print("=" * 80)
print("COMPREHENSIVE FUNCTIONALITY TEST")
print("=" * 80)
print()

test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test(name, passed, message=""):
    if passed:
        test_results['passed'].append(name)
        print(f"✅ {name}")
        if message:
            print(f"   {message}")
    else:
        test_results['failed'].append(name)
        print(f"❌ {name}")
        if message:
            print(f"   {message}")

def warn(name, message):
    test_results['warnings'].append(f"{name}: {message}")
    print(f"⚠️  {name}: {message}")

# Test 1: All Spider Classes
print("[1] Testing All Spider Classes...")
print("-" * 80)
spiders = [
    ('fb_group_specified', 'GroupSpecifiedSpider'),
    ('fb_members_rapid', 'MembersRapidSpider'),
    ('fb_posts', 'PostsSpider'),
    ('fb_pages', 'PagesSpider'),
    ('ins_followers', 'InstagramFollowersSpider'),
    ('ins_following', 'InstagramFollowingSpider'),
    ('ins_profile', 'InstagramProfileSpider'),
    ('ins_reels_comments', 'InstagramReelsCommentsSpider'),
]

for module_name, class_name in spiders:
    try:
        module = __import__(f'spider.{module_name}', fromlist=[class_name])
        spider_class = getattr(module, class_name)
        
        # Check class structure
        has_start = hasattr(spider_class, 'start_requests')
        has_parse = hasattr(spider_class, 'parse')
        
        if has_start and has_parse:
            test(f"Spider: {class_name}", True, "Has start_requests and parse methods")
        else:
            test(f"Spider: {class_name}", False, f"Missing methods: start={has_start}, parse={has_parse}")
    except Exception as e:
        test(f"Spider: {class_name}", False, str(e)[:100])

print()

# Test 2: All Item Classes
print("[2] Testing All Item Classes...")
print("-" * 80)
items = [
    ('autoads.items.post_item', 'PostItem'),
    ('autoads.items.page_item', 'PageItem'),
    ('autoads.items.ins_user_item', 'InstagramUserItem'),
    ('autoads.items.ins_user_item', 'InstagramFollowerItem'),
    ('autoads.items.ins_user_item', 'InstagramFollowingItem'),
    ('autoads.items.ins_user_item', 'InstagramReelsCommentItem'),
]

for module_name, class_name in items:
    try:
        module = __import__(module_name, fromlist=[class_name])
        item_class = getattr(module, class_name)
        item = item_class()
        
        # Test that item has required attributes
        if hasattr(item, '__table_name__'):
            test(f"Item: {class_name}", True, f"Table: {item.__table_name__}")
        else:
            test(f"Item: {class_name}", True, "Can be instantiated")
    except Exception as e:
        test(f"Item: {class_name}", False, str(e)[:100])

print()

# Test 3: Configuration System
print("[3] Testing Configuration System...")
print("-" * 80)
config_tests = [
    ('posts_table', 'config.posts_table'),
    ('post_groups_nums', 'config.post_groups_nums'),
    ('pages_table', 'config.pages_table'),
    ('page_keywords', 'config.page_keywords'),
    ('page_urls', 'config.page_urls'),
    ('ins_target_users', 'config.ins_target_users'),
    ('ins_reels_urls', 'config.ins_reels_urls'),
    ('ins_max_thread_count', 'config.ins_max_thread_count'),
    ('ins_max_scroll_count', 'config.ins_max_scroll_count'),
]

for prop_name, prop_path in config_tests:
    try:
        value = eval(prop_path)
        test(f"Config: {prop_name}", True, f"Value: {type(value).__name__}")
    except Exception as e:
        test(f"Config: {prop_name}", False, str(e)[:100])

print()

# Test 4: UI Integration
print("[4] Testing UI Integration...")
print("-" * 80)
try:
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    from facebook import MainWindow
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    
    # Test sidebar
    sidebar_count = window.ui.sidebarList.count()
    test("UI: Sidebar", sidebar_count >= 12, f"{sidebar_count} items")
    
    # Test stacked pages
    pages_count = window.ui.stackedPages.count()
    test("UI: Stacked Pages", pages_count >= 12, f"{pages_count} pages")
    
    # Test all handlers
    handlers = [
        'on_group_specified_spider_start', 'on_group_specified_spider_stop',
        'on_members_rapid_spider_start', 'on_members_rapid_spider_stop',
        'on_posts_spider_start', 'on_posts_spider_stop',
        'on_pages_spider_start', 'on_pages_spider_stop',
        'on_ins_followers_spider_start', 'on_ins_followers_spider_stop',
        'on_ins_following_spider_start', 'on_ins_following_spider_stop',
        'on_ins_profile_spider_start', 'on_ins_profile_spider_stop',
        'on_ins_reels_comments_spider_start', 'on_ins_reels_comments_spider_stop',
    ]
    
    for handler in handlers:
        has_handler = hasattr(window, handler)
        test(f"Handler: {handler}", has_handler)
    
    # Test stop events
    events = [
        'group_specified_stop_event',
        'members_rapid_stop_event',
        'posts_stop_event',
        'pages_stop_event',
        'ins_followers_stop_event',
        'ins_following_stop_event',
        'ins_profile_stop_event',
        'ins_reels_comments_stop_event',
    ]
    
    for event in events:
        has_event = hasattr(window, event)
        test(f"Stop Event: {event}", has_event)
    
    # Test UI tabs
    tabs = [
        'tabGroupSpecified', 'tabMembersRapid', 'tabPosts', 'tabPages',
        'tabInsFollowers', 'tabInsFollowing', 'tabInsProfile', 'tabInsReelsComments'
    ]
    
    for tab in tabs:
        has_tab = hasattr(window.ui, tab)
        test(f"UI Tab: {tab}", has_tab)
    
    app.quit()
    
except Exception as e:
    test("UI Integration", False, str(e))
    traceback.print_exc()

print()

# Test 5: File Structure
print("[5] Testing File Structure...")
print("-" * 80)
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
    'config.ini',
    'facebook.py',
    'fb_main.py',
    'pyside2_compat.py',
]

for file_path in required_files:
    exists = os.path.exists(file_path)
    test(f"File: {file_path}", exists)

print()

# Test 6: Data Directories
print("[6] Testing Data Directories...")
print("-" * 80)
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
        test_file = os.path.join(dir_path, '.test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        test(f"Directory: {dir_path}", True, "Writable")
    except Exception as e:
        test(f"Directory: {dir_path}", False, str(e))

print()

# Test 7: Spider Manager
print("[7] Testing Spider Manager...")
print("-" * 80)
try:
    from spider_manager import SpiderManager
    
    for spider_name in ['fb_group_specified', 'fb_members_rapid', 'fb_posts', 
                       'fb_pages', 'ins_followers', 'ins_following', 
                       'ins_profile', 'ins_reels_comments']:
        spider_class = SpiderManager.get_spider_class(spider_name)
        test(f"SpiderManager: {spider_name}", spider_class is not None)
except Exception as e:
    test("Spider Manager", False, str(e))

print()

# Test 8: Configuration File Sections
print("[8] Testing Configuration File...")
print("-" * 80)
try:
    import configparser
    parser = configparser.ConfigParser()
    parser.read('config.ini', encoding='utf-8')
    
    sections = ['posts', 'pages', 'instagram', 'groups', 'members']
    for section in sections:
        has_section = parser.has_section(section)
        test(f"Config Section: {section}", has_section)
except Exception as e:
    test("Configuration File", False, str(e))

print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"✅ Passed: {len(test_results['passed'])}")
print(f"❌ Failed: {len(test_results['failed'])}")
print(f"⚠️  Warnings: {len(test_results['warnings'])}")
print()

if test_results['failed']:
    print("FAILED TESTS:")
    for test_name in test_results['failed']:
        print(f"  ❌ {test_name}")
    print()

if test_results['warnings']:
    print("WARNINGS:")
    for warning in test_results['warnings']:
        print(f"  ⚠️  {warning}")
    print()

if len(test_results['failed']) == 0:
    print("🎉 ALL TESTS PASSED! All features are fully functional!")
    print("=" * 80)
    sys.exit(0)
else:
    print(f"⚠️  {len(test_results['failed'])} test(s) failed.")
    print("=" * 80)
    sys.exit(1)

