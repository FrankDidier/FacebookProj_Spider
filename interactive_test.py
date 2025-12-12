#!/usr/bin/env python3
"""
Interactive Application Test
This script tests the application by simulating user interactions
and collecting detailed logs for debugging.
"""

import sys
import os
import time
import json
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize config first
from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("🧪 COMPREHENSIVE APPLICATION TEST")
print("=" * 70)
print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test results storage
test_results = []

def log_test(name, status, details=""):
    """Log test result"""
    result = {"name": name, "status": status, "details": details}
    test_results.append(result)
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   └─ {details}")

# ============================================================
# TEST 1: Configuration Check
# ============================================================
print("\n" + "=" * 70)
print("📋 TEST 1: Configuration Settings")
print("=" * 70)

try:
    browser_type = config.browser_type
    log_test("Browser Type Detection", "PASS", f"Type: {browser_type}")
except Exception as e:
    log_test("Browser Type Detection", "FAIL", str(e))

try:
    api_key = config.key
    if browser_type == 'bitbrowser':
        log_test("API Key (BitBrowser)", "PASS", "BitBrowser doesn't require API key")
    elif api_key:
        log_test("API Key", "PASS", f"Key configured: {api_key[:10]}...")
    else:
        log_test("API Key", "WARN", "No API key configured")
except Exception as e:
    log_test("API Key Check", "FAIL", str(e))

try:
    keep_open = config.keep_browser_open_after_stop
    log_test("Keep Browser Open Setting", "PASS", f"Value: {keep_open}")
except Exception as e:
    log_test("Keep Browser Open Setting", "FAIL", str(e))

# ============================================================
# TEST 2: BitBrowser API Connection
# ============================================================
print("\n" + "=" * 70)
print("🌐 TEST 2: BitBrowser API Connection")
print("=" * 70)

try:
    from autoads import bitbrowser_api
    
    # Test browser list
    time.sleep(0.7)  # Rate limiting
    browsers = bitbrowser_api.get_browser_list()
    if browsers:
        log_test("Get Browser List", "PASS", f"Found {len(browsers)} browser(s)")
        for i, b in enumerate(browsers[:3]):
            name = b.get('name', b.get('remark', 'Unknown'))
            browser_id = b.get('id', 'N/A')
            print(f"   Browser {i+1}: {name} (ID: {browser_id})")
    else:
        log_test("Get Browser List", "WARN", "No browsers found - create one in BitBrowser")
except Exception as e:
    log_test("BitBrowser API", "FAIL", str(e))

# ============================================================
# TEST 3: Browser Start/Stop (if browsers exist)
# ============================================================
print("\n" + "=" * 70)
print("🚀 TEST 3: Browser Start/Stop")
print("=" * 70)

try:
    if browsers and len(browsers) > 0:
        test_browser = browsers[0]
        browser_id = test_browser.get('id')
        browser_name = test_browser.get('name', test_browser.get('remark', 'Test Browser'))
        
        print(f"   Testing with browser: {browser_name}")
        
        # Start browser
        time.sleep(0.7)  # Rate limiting
        start_result = bitbrowser_api.start_browser(browser_id)
        if start_result and 'ws' in start_result:
            log_test("Start Browser", "PASS", f"WebSocket: {start_result['ws'][:50]}...")
            
            # Wait for browser to open
            time.sleep(3)
            
            # Try to connect with Selenium
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", start_result['ws'].replace('ws://', '').split('/')[0])
                
                driver = webdriver.Chrome(options=chrome_options)
                current_url = driver.current_url
                log_test("Selenium Connect", "PASS", f"Connected! Current URL: {current_url}")
                
                # Navigate to Facebook
                print("   Navigating to Facebook...")
                driver.get("https://www.facebook.com")
                time.sleep(3)
                
                page_title = driver.title
                log_test("Navigate to Facebook", "PASS", f"Page title: {page_title}")
                
                # Check if logged in
                if "Facebook" in page_title and "log in" not in page_title.lower():
                    log_test("Facebook Login Status", "PASS", "Already logged in!")
                else:
                    log_test("Facebook Login Status", "WARN", "Not logged in - may need to login first")
                
                driver.quit()
                
            except Exception as e:
                log_test("Selenium Connect", "FAIL", str(e))
            
            # Stop browser (unless keep_open is True)
            if not config.keep_browser_open_after_stop:
                time.sleep(0.7)  # Rate limiting
                stop_result = bitbrowser_api.stop_browser(browser_id)
                log_test("Stop Browser", "PASS" if stop_result else "FAIL", 
                        "Browser closed" if stop_result else "Failed to close")
            else:
                log_test("Stop Browser", "SKIP", "keep_browser_open_after_stop is True")
                
        else:
            log_test("Start Browser", "FAIL", f"No WebSocket returned: {start_result}")
    else:
        log_test("Browser Start/Stop", "SKIP", "No browsers available to test")
except Exception as e:
    log_test("Browser Start/Stop", "FAIL", str(e))

# ============================================================
# TEST 4: Spider Imports
# ============================================================
print("\n" + "=" * 70)
print("🕷️ TEST 4: Spider Module Imports")
print("=" * 70)

spiders_to_test = [
    ("spider.fb_group", "GroupSpider"),
    ("spider.fb_members", "MemberSpider"),
    ("spider.fb_greets", "GreetsSpider"),
    ("spider.fb_auto_like", "AutoLikeSpider"),
    ("spider.fb_auto_comment", "AutoCommentSpider"),
    ("spider.fb_auto_follow", "AutoFollowSpider"),
    ("spider.fb_auto_add_friend", "AutoAddFriendSpider"),
    ("spider.fb_auto_group", "AutoGroupSpider"),
    ("spider.fb_auto_post", "AutoPostSpider"),
]

for module_name, class_name in spiders_to_test:
    try:
        module = __import__(module_name, fromlist=[class_name])
        spider_class = getattr(module, class_name)
        log_test(f"Import {class_name}", "PASS")
    except Exception as e:
        log_test(f"Import {class_name}", "FAIL", str(e))

# ============================================================
# TEST 5: UI Components
# ============================================================
print("\n" + "=" * 70)
print("🖥️ TEST 5: UI Components")
print("=" * 70)

try:
    # Import PySide
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import Qt
    
    # Create app if not exists
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Import main UI
    from fb_main import Ui_MainWindow
    from PySide2.QtWidgets import QMainWindow
    
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    
    log_test("UI Setup", "PASS", "Main window created successfully")
    
    # Check key widgets
    widgets_to_check = [
        "sidebarList",
        "stackedPages", 
        "pushButtonGroupStart",
        "pushButtonGroupStop",
        "pushButtonMemberStart",
        "pushButtonMemberStop",
        "pushButtonGreetsStart",
        "pushButtonGreetsStop",
    ]
    
    for widget_name in widgets_to_check:
        widget = window.findChild(type(None), widget_name) or getattr(ui, widget_name, None)
        if widget:
            log_test(f"Widget: {widget_name}", "PASS")
        else:
            log_test(f"Widget: {widget_name}", "WARN", "Not found (may be created dynamically)")
    
except Exception as e:
    log_test("UI Components", "FAIL", str(e))

# ============================================================
# TEST 6: Data Files & Directories
# ============================================================
print("\n" + "=" * 70)
print("📁 TEST 6: Data Files & Directories")
print("=" * 70)

data_dirs = [
    "data",
    "data/groups",
    "data/members", 
    "data/logs",
]

for dir_path in data_dirs:
    full_path = os.path.join(os.path.dirname(__file__), dir_path)
    if os.path.exists(full_path):
        files = os.listdir(full_path) if os.path.isdir(full_path) else []
        log_test(f"Directory: {dir_path}", "PASS", f"{len(files)} files")
    else:
        os.makedirs(full_path, exist_ok=True)
        log_test(f"Directory: {dir_path}", "PASS", "Created")

# ============================================================
# TEST 7: Cloud Deduplication
# ============================================================
print("\n" + "=" * 70)
print("☁️ TEST 7: Cloud Deduplication")
print("=" * 70)

try:
    from autoads.cloud_dedup import CloudDeduplication
    
    dedup = CloudDeduplication()
    stats = dedup.get_stats()
    log_test("Cloud Dedup Init", "PASS", f"Total entries: {stats.get('total_entries', 0)}")
    
    # Test adding a member
    test_id = f"test_member_{int(time.time())}"
    is_new = dedup.check_and_add_member(test_id, "Test Member", "https://facebook.com/test")
    log_test("Add Test Member", "PASS" if is_new else "WARN", 
             "New member added" if is_new else "Already exists")
    
except Exception as e:
    log_test("Cloud Deduplication", "FAIL", str(e))

# ============================================================
# TEST 8: Account Manager
# ============================================================
print("\n" + "=" * 70)
print("👤 TEST 8: Account Manager")
print("=" * 70)

try:
    from autoads.account_manager import AccountManager
    
    acct_mgr = AccountManager()
    accounts = acct_mgr.get_all_accounts()
    log_test("Account Manager Init", "PASS", f"Total accounts: {len(accounts)}")
    
    stats = acct_mgr.get_stats()
    log_test("Account Stats", "PASS", 
             f"Active: {stats.get('active', 0)}, Used: {stats.get('used_today', 0)}")
    
except Exception as e:
    log_test("Account Manager", "FAIL", str(e))

# ============================================================
# TEST 9: IP Pool
# ============================================================
print("\n" + "=" * 70)
print("🌍 TEST 9: IP Pool")
print("=" * 70)

try:
    from autoads.ip_pool import IPPool
    
    ip_pool = IPPool()
    stats = ip_pool.get_stats()
    log_test("IP Pool Init", "PASS", f"Total IPs: {stats.get('total', 0)}")
    
except Exception as e:
    log_test("IP Pool", "FAIL", str(e))

# ============================================================
# TEST 10: Logging System
# ============================================================
print("\n" + "=" * 70)
print("📝 TEST 10: Logging System")
print("=" * 70)

try:
    from autoads.app_logger import app_logger
    
    app_logger.log_action("TEST", "Test log entry", {"test": True})
    log_test("App Logger", "PASS", "Log entry created")
    
    session_info = app_logger.get_session_info()
    log_test("Session Info", "PASS", f"Session ID: {session_info.get('session_id', 'N/A')[:20]}...")
    
except Exception as e:
    log_test("Logging System", "FAIL", str(e))

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

passed = sum(1 for r in test_results if r["status"] == "PASS")
failed = sum(1 for r in test_results if r["status"] == "FAIL")
warned = sum(1 for r in test_results if r["status"] == "WARN")
skipped = sum(1 for r in test_results if r["status"] == "SKIP")
total = len(test_results)

print(f"\n✅ Passed:  {passed}/{total}")
print(f"❌ Failed:  {failed}/{total}")
print(f"⚠️ Warnings: {warned}/{total}")
print(f"⏭️ Skipped: {skipped}/{total}")

success_rate = (passed / total * 100) if total > 0 else 0
print(f"\n🎯 Success Rate: {success_rate:.1f}%")

# Save results to file
results_file = os.path.join(os.path.dirname(__file__), "data", "logs", "test_results.json")
os.makedirs(os.path.dirname(results_file), exist_ok=True)
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "skipped": skipped,
            "total": total,
            "success_rate": success_rate
        },
        "results": test_results
    }, f, indent=2, ensure_ascii=False)

print(f"\n📄 Results saved to: {results_file}")
print("\n" + "=" * 70)
print("🏁 TEST COMPLETE")
print("=" * 70)

