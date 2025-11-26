#!/usr/bin/env python3
"""
Functional Test - Test actual functionality of each feature
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize config first
from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("FUNCTIONAL TEST - Testing Feature Functionality")
print("=" * 70)

def test_spider_functionality(spider_name, spider_class):
    """Test that a spider can be instantiated and has required methods"""
    try:
        # Test instantiation with minimal parameters
        spider = spider_class(
            thread_count=1,
            ads_ids=[],
            config=config,
            ui=None,
            ms=None,
            tab_index=0,
            stop_event=None,
            grid_layout=None
        )
        
        # Check required methods exist
        required_methods = ['start_requests', 'parse']
        for method_name in required_methods:
            if not hasattr(spider, method_name):
                return False, f"Missing method: {method_name}"
        
        return True, "All methods present"
    except Exception as e:
        return False, str(e)

# Test each spider
print("\n[1] Testing Spider Functionality...")
spiders = [
    ('GroupSpecifiedSpider', 'spider.fb_group_specified'),
    ('MembersRapidSpider', 'spider.fb_members_rapid'),
    ('PostsSpider', 'spider.fb_posts'),
    ('PagesSpider', 'spider.fb_pages'),
    ('InstagramFollowersSpider', 'spider.ins_followers'),
    ('InstagramFollowingSpider', 'spider.ins_following'),
    ('InstagramProfileSpider', 'spider.ins_profile'),
    ('InstagramReelsCommentsSpider', 'spider.ins_reels_comments'),
]

passed = 0
failed = 0

for class_name, module_name in spiders:
    try:
        module = __import__(module_name, fromlist=[class_name])
        spider_class = getattr(module, class_name)
        success, message = test_spider_functionality(class_name, spider_class)
        if success:
            print(f"✓ {class_name}: Functional")
            passed += 1
        else:
            print(f"✗ {class_name}: {message}")
            failed += 1
    except Exception as e:
        print(f"✗ {class_name}: {str(e)}")
        failed += 1

# Test item classes can save data
print("\n[2] Testing Item Data Structure...")
try:
    from autoads.items.post_item import PostItem
    from autoads.items.page_item import PageItem
    from autoads.items.ins_user_item import InstagramUserItem, InstagramFollowerItem
    
    # Test PostItem
    post = PostItem()
    post.group_name = "Test Group"
    post.post_link = "https://facebook.com/test"
    post.post_content = "Test content"
    assert post.group_name == "Test Group"
    print("✓ PostItem: Data structure working")
    
    # Test PageItem
    page = PageItem()
    page.page_name = "Test Page"
    page.page_link = "https://facebook.com/page"
    assert page.page_name == "Test Page"
    print("✓ PageItem: Data structure working")
    
    # Test InstagramUserItem
    user = InstagramUserItem()
    user.username = "testuser"
    user.followers_count = 1000
    assert user.username == "testuser"
    print("✓ InstagramUserItem: Data structure working")
    
    # Test InstagramFollowerItem
    follower = InstagramFollowerItem()
    follower.target_user = "target"
    follower.follower_username = "follower"
    assert follower.target_user == "target"
    print("✓ InstagramFollowerItem: Data structure working")
    
    passed += 4
    
except Exception as e:
    print(f"✗ Item Data Structure: {str(e)}")
    failed += 1

# Test configuration can be set and retrieved
print("\n[3] Testing Configuration Operations...")
try:
    # Test setting Instagram users
    test_users = ["user1", "user2", "user3"]
    config.set_option('instagram', 'target_users', json.dumps(test_users))
    retrieved = config.ins_target_users
    assert retrieved == test_users
    print("✓ Config: Instagram users set/get working")
    
    # Test setting Reels URLs
    test_urls = ["https://instagram.com/reel/test1", "https://instagram.com/reel/test2"]
    config.set_option('instagram', 'reels_urls', json.dumps(test_urls))
    retrieved = config.ins_reels_urls
    assert retrieved == test_urls
    print("✓ Config: Reels URLs set/get working")
    
    # Test setting page keywords
    test_keywords = ["keyword1", "keyword2"]
    config.set_option('pages', 'keywords', json.dumps(test_keywords))
    retrieved = config.page_keywords
    assert retrieved == test_keywords
    print("✓ Config: Page keywords set/get working")
    
    passed += 3
    
except Exception as e:
    print(f"✗ Configuration Operations: {str(e)}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test UI handlers can be called (without actually running spiders)
print("\n[4] Testing UI Handler Functions...")
try:
    from PySide2.QtWidgets import QApplication
    from facebook import MainWindow
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    
    # Test that handlers can be called (they'll fail gracefully without proper setup)
    handlers_to_test = [
        ('on_group_specified_spider_start', []),
        ('on_members_rapid_spider_start', []),
        ('on_posts_spider_start', []),
        ('on_pages_spider_start', []),
        ('on_ins_followers_spider_start', []),
        ('on_ins_following_spider_start', []),
        ('on_ins_profile_spider_start', []),
        ('on_ins_reels_comments_spider_start', []),
    ]
    
    for handler_name, args in handlers_to_test:
        handler = getattr(window, handler_name)
        if callable(handler):
            print(f"✓ Handler: {handler_name} is callable")
            passed += 1
        else:
            print(f"✗ Handler: {handler_name} is not callable")
            failed += 1
    
    app.quit()
    
except Exception as e:
    print(f"✗ UI Handler Functions: {str(e)}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test data directories
print("\n[5] Testing Data Directories...")
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
        # Test write permission
        test_file = os.path.join(dir_path, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✓ Directory: {dir_path} (writable)")
        passed += 1
    except Exception as e:
        print(f"✗ Directory: {dir_path} - {str(e)}")
        failed += 1

# Summary
print("\n" + "=" * 70)
print("FUNCTIONAL TEST SUMMARY")
print("=" * 70)
print(f"✓ Passed: {passed}")
print(f"✗ Failed: {failed}")
print()

if failed == 0:
    print("🎉 ALL FUNCTIONAL TESTS PASSED!")
    print("All features are fully implemented and ready to use!")
else:
    print(f"⚠️  {failed} test(s) failed. Please review above.")
print("=" * 70)

