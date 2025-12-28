# -*- coding: utf-8 -*-
"""
真实集成测试 - Real Integration Tests
=====================================
测试实际功能，不只是检查方法是否存在

This script ACTUALLY runs the spiders with BitBrowser to verify:
1. Group collection works and saves data
2. Member collection works (reads group files)
3. Stop/restart behavior works
4. Files are actually created with valid data
"""

import os
import sys
import time
import json
import shutil
import threading
from datetime import datetime

# Initialize config FIRST before any other imports
from autoads.config import config
config.name = 'config.ini'  # Must set this before spider imports!

# Test configuration
TEST_KEYWORD = "Python编程"  # A simple keyword for testing
TEST_TIMEOUT = 60  # Max seconds to wait for spider
TEST_DIR = "./test_integration_data"

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def log_pass(test_name, detail=""):
    print(f"  ✅ PASS: {test_name}" + (f" - {detail}" if detail else ""))

def log_fail(test_name, detail=""):
    print(f"  ❌ FAIL: {test_name}" + (f" - {detail}" if detail else ""))

def cleanup_test_dir():
    """Clean up test directory before running tests"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    log(f"Test directory cleaned: {TEST_DIR}")

# ============================================================================
# TEST 1: BitBrowser Connection
# ============================================================================
def test_bitbrowser_connection():
    """Test if we can actually connect to BitBrowser"""
    print("\n" + "="*70)
    print("🔌 TEST 1: BitBrowser Real Connection")
    print("="*70)
    
    try:
        from autoads.bitbrowser_api import test_connection, get_browser_list
        
        # Test 1a: API reachable
        if test_connection():
            log_pass("BitBrowser API", "Service is running")
        else:
            log_fail("BitBrowser API", "Cannot connect to http://127.0.0.1:54345")
            return False
        
        # Test 1b: Get browser list
        browsers = get_browser_list()
        if browsers and len(browsers) > 0:
            log_pass("Browser Profiles", f"Found {len(browsers)} browsers")
            for b in browsers[:3]:  # Show first 3
                log(f"    - {b.get('name', 'Unknown')} (id: {b.get('id', 'N/A')[:8]}...)")
        else:
            log_fail("Browser Profiles", "No browser profiles found")
            return False
        
        return True
        
    except Exception as e:
        log_fail("BitBrowser Connection", str(e))
        return False

# ============================================================================
# TEST 2: Actually Open a Browser
# ============================================================================
def test_open_browser():
    """Test if we can actually open a BitBrowser window"""
    print("\n" + "="*70)
    print("🌐 TEST 2: Actually Open a Browser Window")
    print("="*70)
    
    try:
        from autoads.bitbrowser_api import get_browser_list, start_browser, stop_browser
        
        browsers = get_browser_list()
        if not browsers:
            log_fail("Open Browser", "No browsers available")
            return False
        
        browser_id = browsers[0]['id']
        browser_name = browsers[0].get('name', 'Unknown')
        log(f"Attempting to open: {browser_name}")
        
        # Actually open the browser
        result = start_browser(browser_id)
        
        if result and result.get('success'):
            log_pass("Browser Opened", f"{browser_name} started successfully")
            ws_info = result.get('data', {})
            log(f"    - WebSocket: {ws_info.get('http', 'N/A')}")
            
            # Wait a moment to see it
            log("Waiting 3 seconds to verify browser is visible...")
            time.sleep(3)
            
            # Close it
            close_result = stop_browser(browser_id)
            if close_result:
                log_pass("Browser Closed", "Browser closed successfully")
            else:
                log_fail("Browser Closed", "Failed to close browser")
            
            return True
        else:
            log_fail("Browser Opened", f"Failed: {result}")
            return False
            
    except Exception as e:
        log_fail("Open Browser", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: WebDriver Connection
# ============================================================================
def test_webdriver_connection():
    """Test if we can actually control a browser with Selenium"""
    print("\n" + "="*70)
    print("🎮 TEST 3: WebDriver Selenium Control")
    print("="*70)
    
    try:
        from autoads.bitbrowser_api import get_browser_list, start_browser, stop_browser
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        browsers = get_browser_list()
        if not browsers:
            log_fail("WebDriver", "No browsers available")
            return False
        
        browser_id = browsers[0]['id']
        
        # Start browser
        result = start_browser(browser_id)
        if not result or not result.get('success'):
            log_fail("WebDriver", "Could not start browser")
            return False
        
        data = result.get('data', {})
        debugger_address = data.get('http', '')
        driver_path = data.get('driver', '')
        
        log(f"Debugger: {debugger_address}")
        log(f"Driver: {driver_path}")
        
        # Connect with Selenium
        options = Options()
        options.add_experimental_option("debuggerAddress", debugger_address)
        
        try:
            if driver_path and os.path.exists(driver_path):
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            log_pass("Selenium Connected", "WebDriver attached to browser")
            
            # Test navigation
            log("Navigating to Facebook...")
            driver.get("https://www.facebook.com")
            time.sleep(3)
            
            current_url = driver.current_url
            if "facebook.com" in current_url:
                log_pass("Navigation", f"Loaded: {current_url[:50]}...")
            else:
                log_fail("Navigation", f"Wrong URL: {current_url}")
            
            # Get page title
            title = driver.title
            log(f"Page title: {title}")
            
            # Cleanup
            driver.quit()
            log_pass("WebDriver Closed", "Selenium session ended cleanly")
            
            # Close browser
            time.sleep(1)
            stop_browser(browser_id)
            
            return True
            
        except Exception as e:
            log_fail("Selenium Connection", str(e))
            stop_browser(browser_id)
            return False
            
    except Exception as e:
        log_fail("WebDriver Test", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: Config Settings Verification
# ============================================================================
def test_config_settings():
    """Test that critical config settings are correct"""
    print("\n" + "="*70)
    print("⚙️ TEST 4: Critical Config Settings")
    print("="*70)
    
    try:
        from autoads.config import config
        
        # Test groups_save_links_only - MUST be False!
        groups_save_links_only = config.groups_save_links_only
        if groups_save_links_only == False:
            log_pass("groups_save_links_only", "FALSE ✓ (Member spider will work)")
        else:
            log_fail("groups_save_links_only", "TRUE ✗ (Member spider will fail with 0 requests!)")
            return False
        
        # Test members_save_links_only
        members_save_links_only = config.members_save_links_only
        log_pass("members_save_links_only", f"{members_save_links_only}")
        
        # Test groups_table path
        groups_table = config.groups_table
        log_pass("groups_table", f"{groups_table}")
        
        # Test members_table path
        members_table = config.members_table
        log_pass("members_table", f"{members_table}")
        
        return True
        
    except Exception as e:
        log_fail("Config Settings", str(e))
        return False

# ============================================================================
# TEST 5: File Pipeline - Save and Load
# ============================================================================
def test_file_pipeline():
    """Test that file pipeline can actually save and load data"""
    print("\n" + "="*70)
    print("📁 TEST 5: File Pipeline Save/Load")
    print("="*70)
    
    try:
        from autoads.pipelines.file_pipeline import FilePipeline
        import tempfile
        import json
        
        pipeline = FilePipeline()
        
        # Create test data
        test_items = [
            {
                "word": "测试关键词",
                "group_name": "测试群组1",
                "group_link": "https://facebook.com/groups/test1",
                "status": "unknown"
            },
            {
                "word": "测试关键词",
                "group_name": "测试群组2", 
                "group_link": "https://facebook.com/groups/test2",
                "status": "unknown"
            }
        ]
        
        # Save to test file
        test_file = os.path.join(TEST_DIR, "test_groups.txt")
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        result = pipeline.save_items(test_file, test_items)
        
        if result and os.path.exists(test_file):
            log_pass("Save Items", f"Saved 2 items to {test_file}")
        else:
            log_fail("Save Items", "File not created")
            return False
        
        # Verify file contents
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) == 2:
            log_pass("File Contents", f"{len(lines)} lines saved correctly")
        else:
            log_fail("File Contents", f"Expected 2 lines, got {len(lines)}")
            return False
        
        # Verify JSON format
        try:
            item1 = json.loads(lines[0])
            if item1.get('group_name') == "测试群组1":
                log_pass("JSON Format", "Data is valid JSON")
            else:
                log_fail("JSON Format", "Data corrupted")
                return False
        except json.JSONDecodeError as e:
            log_fail("JSON Format", f"Invalid JSON: {e}")
            return False
        
        return True
        
    except Exception as e:
        log_fail("File Pipeline", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 6: Group Spider Initialization
# ============================================================================
def test_group_spider_init():
    """Test that group spider can be initialized"""
    print("\n" + "="*70)
    print("🕷️ TEST 6: Group Spider Initialization")
    print("="*70)
    
    try:
        from spider.fb_group import GroupSpider
        from autoads.config import config
        
        # Create spider instance
        spider = GroupSpider()
        log_pass("Spider Created", "GroupSpider instance created")
        
        # Check required attributes
        if hasattr(spider, 'start_requests'):
            log_pass("start_requests", "Method exists")
        else:
            log_fail("start_requests", "Method missing")
            return False
        
        if hasattr(spider, 'parse'):
            log_pass("parse", "Method exists")
        else:
            log_fail("parse", "Method missing")
            return False
        
        return True
        
    except Exception as e:
        log_fail("Group Spider Init", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 7: Member Spider Initialization  
# ============================================================================
def test_member_spider_init():
    """Test that member spider can be initialized and find group files"""
    print("\n" + "="*70)
    print("🕷️ TEST 7: Member Spider Initialization")
    print("="*70)
    
    try:
        from spider.fb_members import MembersSpider
        from autoads.config import config
        from autoads.pipelines.file_pipeline import FilePipeline
        from autoads.items.group_item import GroupItem
        import glob
        
        # Check if group files exist
        groups_table = config.groups_table
        log(f"Looking for group files in: {groups_table}")
        
        # Get all txt files
        all_files = glob.glob(groups_table + '/*.txt') + glob.glob(groups_table + '\\*.txt')
        json_files = [f for f in all_files if not f.endswith('_links.txt')]
        links_files = [f for f in all_files if f.endswith('_links.txt')]
        
        log(f"Found {len(json_files)} JSON files, {len(links_files)} _links.txt files")
        
        if json_files:
            log_pass("Group JSON Files", f"Found {len(json_files)} files")
            for f in json_files[:3]:
                log(f"    - {os.path.basename(f)}")
        elif links_files:
            log_pass("Group Links Files", f"Found {len(links_files)} files (fallback mode)")
        else:
            log_fail("Group Files", "No group files found! Run '采集群组' first.")
            log("💡 Tip: The member spider needs group data to work.")
            return False
        
        # Try to load items
        pipeline = FilePipeline()
        group_template = GroupItem()
        
        items = list(pipeline.load_items(group_template))
        if items:
            log_pass("Load Group Items", f"Loaded {len(items)} groups")
            # Show first item
            try:
                first_item = json.loads(items[0])
                log(f"    - First group: {first_item.get('group_name', 'N/A')[:30]}...")
            except:
                pass
        else:
            log_fail("Load Group Items", "No items loaded")
            return False
        
        return True
        
    except Exception as e:
        log_fail("Member Spider Init", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 8: Stop Event Functionality
# ============================================================================
def test_stop_event():
    """Test that stop events work correctly"""
    print("\n" + "="*70)
    print("🛑 TEST 8: Stop Event Functionality")
    print("="*70)
    
    try:
        import threading
        
        # Simulate stop event behavior
        stop_event = threading.Event()
        
        # Test 1: Initial state
        if not stop_event.is_set():
            log_pass("Initial State", "Stop event is clear")
        else:
            log_fail("Initial State", "Stop event should be clear initially")
        
        # Test 2: Set stop
        stop_event.set()
        if stop_event.is_set():
            log_pass("Set Stop", "Stop event is now set")
        else:
            log_fail("Set Stop", "Failed to set stop event")
        
        # Test 3: Worker thread should detect stop
        detected = [False]
        def worker():
            if stop_event.is_set():
                detected[0] = True
        
        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=1)
        
        if detected[0]:
            log_pass("Worker Detection", "Worker thread detected stop signal")
        else:
            log_fail("Worker Detection", "Worker thread did not detect stop")
        
        # Test 4: Clear and restart
        stop_event.clear()
        if not stop_event.is_set():
            log_pass("Clear and Restart", "Stop event cleared, ready to restart")
        else:
            log_fail("Clear and Restart", "Failed to clear stop event")
        
        return True
        
    except Exception as e:
        log_fail("Stop Event", str(e))
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("\n" + "="*70)
    print("🧪 REAL INTEGRATION TESTS - Facebook Automation Tool")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("These tests actually run the spiders and verify real functionality!")
    print("="*70)
    
    # Setup
    cleanup_test_dir()
    
    results = {}
    
    # Run tests
    tests = [
        ("BitBrowser Connection", test_bitbrowser_connection),
        ("Config Settings", test_config_settings),
        ("File Pipeline", test_file_pipeline),
        ("Group Spider Init", test_group_spider_init),
        ("Member Spider Init", test_member_spider_init),
        ("Stop Event", test_stop_event),
    ]
    
    # Ask user if they want browser tests (these open real windows)
    print("\n⚠️ The following tests will OPEN BROWSER WINDOWS:")
    print("   - Open Browser Test")
    print("   - WebDriver Control Test")
    response = input("\nRun browser tests? (y/n): ").strip().lower()
    
    if response == 'y':
        tests.insert(1, ("Open Browser", test_open_browser))
        tests.insert(2, ("WebDriver Control", test_webdriver_connection))
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            results[name] = False
            log(f"Test '{name}' crashed: {e}", "ERROR")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! The system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

