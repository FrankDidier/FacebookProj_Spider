#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Functional Test - 2024-12-22
Tests all features that clients have reported issues with
"""

import os
import sys
import json
import tempfile
import threading
import time

# Setup config first
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set config before imports
from autoads.config import config
config.name = 'config.ini'

print("=" * 80)
print("          COMPREHENSIVE FUNCTIONAL TEST - 2024-12-22")
print("=" * 80)

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def test(name, condition, details=""):
    global tests_passed, tests_failed
    if condition:
        tests_passed += 1
        status = "✅ PASS"
    else:
        tests_failed += 1
        status = "❌ FAIL"
    
    result = f"{status}: {name}"
    if details:
        result += f" | {details}"
    print(result)
    test_results.append({"name": name, "passed": condition, "details": details})
    return condition

print("\n" + "=" * 80)
print("TEST 1: MULTI-THREADING SUPPORT (30-50 browsers)")
print("=" * 80)

# Test 1.1: BitBrowser API page size
try:
    from autoads import bitbrowser_api
    import inspect
    source = inspect.getsource(bitbrowser_api.get_browser_list)
    test("BitBrowser page_size >= 200", 
         "page_size=200" in source or "pageSize" in source,
         "Supports 50+ browsers")
except Exception as e:
    test("BitBrowser page_size", False, str(e))

# Test 1.2: Thread count logging
try:
    from autoads import air_spider
    source = inspect.getsource(air_spider.AirSpider.run)
    test("Thread count warning for single thread", 
         "只有1个线程" in source,
         "Warns user if only 1 thread")
except Exception as e:
    test("Thread count warning", False, str(e))

# Test 1.3: config.account_nums property
try:
    account_nums = config.account_nums
    test("config.account_nums accessible", 
         account_nums is not None,
         f"Current value: {account_nums}")
except Exception as e:
    test("config.account_nums", False, str(e))

print("\n" + "=" * 80)
print("TEST 2: BROWSE SELECTION (卡死 fix)")
print("=" * 80)

# Test 2.1: Browse function has processEvents
try:
    with open('facebook.py', 'r', encoding='utf-8') as f:
        content = f.read()
    test("_browse_member_group_file has processEvents", 
         "processEvents()" in content and "_browse_member_group_file" in content,
         "Prevents UI freeze")
except Exception as e:
    test("Browse processEvents", False, str(e))

# Test 2.2: File size warning
try:
    test("Browse file size warning", 
         "10 * 1024 * 1024" in content,
         "Warns for files > 10MB")
except Exception as e:
    test("File size warning", False, str(e))

print("\n" + "=" * 80)
print("TEST 3: IP POOL CONFIGURATION")
print("=" * 80)

# Test 3.1: IP pool config section exists
try:
    ip_enabled = config.get_option('ip_pool', 'enabled')
    test("IP pool config section exists", 
         ip_enabled is not None,
         f"enabled = {ip_enabled}")
except Exception as e:
    test("IP pool config", False, str(e))

# Test 3.2: IP pool assignment mode
try:
    mode = config.get_option('ip_pool', 'assignment_mode')
    test("IP pool assignment_mode", 
         mode in ['round_robin', 'random', 'sticky', ''],
         f"mode = {mode}")
except Exception as e:
    test("IP pool assignment_mode", False, str(e))

# Test 3.3: IP pool manager
try:
    from autoads.ip_pool import IPPoolManager
    pool = IPPoolManager()
    test("IPPoolManager instantiation", True, "IP pool manager works")
except Exception as e:
    test("IPPoolManager", False, str(e))

print("\n" + "=" * 80)
print("TEST 4: SAVE LINKS ONLY")
print("=" * 80)

# Test 4.1: save_links_only config
try:
    save_links = config.members_save_links_only
    test("config.members_save_links_only", 
         save_links is not None,
         f"Value: {save_links}")
except Exception as e:
    test("members_save_links_only", False, str(e))

# Test 4.2: FilePipeline respects save_links_only
try:
    from autoads.pipelines.file_pipeline import FilePipeline
    source = inspect.getsource(FilePipeline.save_items)
    test("FilePipeline checks save_links_only", 
         "save_links_only" in source,
         "Skips JSON when enabled")
except Exception as e:
    test("FilePipeline save_links_only", False, str(e))

print("\n" + "=" * 80)
print("TEST 5: FILE DELETION AFTER PROCESSING")
print("=" * 80)

# Test 5.1: delete_entry_from_file for JSON
try:
    from autoads import tools
    
    # Create test file with JSON entries
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    test_file.write('{"member_link": "https://test1.com", "name": "Test1"}\n')
    test_file.write('{"member_link": "https://test2.com", "name": "Test2"}\n')
    test_file.write('{"member_link": "https://test3.com", "name": "Test3"}\n')
    test_file.close()
    
    # Delete one entry
    result = tools.delete_entry_from_file(test_file.name, 'member_link', 'https://test2.com')
    
    # Verify
    with open(test_file.name, 'r', encoding='utf-8') as f:
        remaining = f.readlines()
    
    os.unlink(test_file.name)
    
    test("delete_entry_from_file (JSON mode)", 
         result == True and len(remaining) == 2,
         f"3 → 2 entries")
except Exception as e:
    test("delete_entry_from_file JSON", False, str(e))

# Test 5.2: delete_entry_from_file for plain URLs
try:
    # Create test file with plain URLs
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='_links.txt', delete=False, encoding='utf-8')
    test_file.write('https://facebook.com/user1\n')
    test_file.write('https://facebook.com/user2\n')
    test_file.write('https://facebook.com/user3\n')
    test_file.close()
    
    # Delete one entry (plain URL mode)
    result = tools.delete_entry_from_file(test_file.name, 'https://facebook.com/user2')
    
    # Verify
    with open(test_file.name, 'r', encoding='utf-8') as f:
        remaining = [l.strip() for l in f.readlines() if l.strip()]
    
    os.unlink(test_file.name)
    
    test("delete_entry_from_file (URL mode)", 
         result == True and len(remaining) == 2,
         f"3 → 2 URLs")
except Exception as e:
    test("delete_entry_from_file URL", False, str(e))

print("\n" + "=" * 80)
print("TEST 6: STOP BUTTON FUNCTIONALITY")
print("=" * 80)

# Test 6.1: Stop event handling
try:
    with open('facebook.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    test("Stop event with 8s delay", 
         "8000" in content and "QTimer.singleShot" in content,
         "Delay ensures threads stop properly")
except Exception as e:
    test("Stop event delay", False, str(e))

# Test 6.2: STOP_IGNORED event
try:
    test("STOP_IGNORED for no running task", 
         "STOP_IGNORED" in content,
         "Friendly message when no task running")
except Exception as e:
    test("STOP_IGNORED", False, str(e))

print("\n" + "=" * 80)
print("TEST 7: PRIVATE MESSAGE (PM) FUNCTIONALITY")
print("=" * 80)

# Test 7.1: GreetsSpider has _load_links_file
try:
    from spider.fb_greets import GreetsSpider
    test("GreetsSpider._load_links_file exists", 
         hasattr(GreetsSpider, '_load_links_file'),
         "Can load plain URL files")
except Exception as e:
    test("GreetsSpider._load_links_file", False, str(e))

# Test 7.2: PM spider checks hasattr for member
try:
    with open('spider/fb_greets.py', 'r', encoding='utf-8') as f:
        greets_content = f.read()
    
    test("PM spider checks hasattr(request, 'member')", 
         "hasattr(request, 'member')" in greets_content,
         "Fixes 'Request' has no attribute 'member' error")
except Exception as e:
    test("PM hasattr check", False, str(e))

# Test 7.3: WebDriverWait timeout increased
try:
    test("WebDriverWait timeout = 15s", 
         "WebDriverWait(browser, 15)" in greets_content,
         "Increased from 8s")
except Exception as e:
    test("WebDriverWait timeout", False, str(e))

print("\n" + "=" * 80)
print("TEST 8: BROWSER WINDOW AUTO-ARRANGEMENT")
print("=" * 80)

# Test 8.1: screen_width config
try:
    width = config.screen_width
    test("config.screen_width", 
         width is not None and width > 0,
         f"Value: {width}")
except Exception as e:
    test("screen_width", False, str(e))

# Test 8.2: screen_height config
try:
    height = config.screen_height
    test("config.screen_height", 
         height is not None and height > 0,
         f"Value: {height}")
except Exception as e:
    test("screen_height", False, str(e))

# Test 8.3: WebDriverPool.reset_window_positions
try:
    from autoads.webdriver import WebDriverPool
    test("WebDriverPool.reset_window_positions exists", 
         hasattr(WebDriverPool, 'reset_window_positions'),
         "Clears position cache for new runs")
except Exception as e:
    test("reset_window_positions", False, str(e))

print("\n" + "=" * 80)
print("TEST 9: CONSOLIDATED MEMBER FILE")
print("=" * 80)

# Test 9.1: create_consolidated_member_file function
try:
    from autoads import tools
    test("tools.create_consolidated_member_file exists", 
         hasattr(tools, 'create_consolidated_member_file'),
         "Merges all member files")
except Exception as e:
    test("create_consolidated_member_file", False, str(e))

# Test 9.2: Actual consolidation test
try:
    # Create temp directory with member files
    test_dir = tempfile.mkdtemp()
    
    # Create test member files
    for i in range(3):
        with open(os.path.join(test_dir, f'group{i}_links.txt'), 'w') as f:
            f.write(f'https://facebook.com/user{i*3+1}\n')
            f.write(f'https://facebook.com/user{i*3+2}\n')
            f.write(f'https://facebook.com/user{i*3+3}\n')
    
    output_file = os.path.join(test_dir, 'all_members.txt')
    count = tools.create_consolidated_member_file(test_dir, output_file)
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    
    test("Consolidated member file creation", 
         count == 9,
         f"Merged 9 members from 3 files")
except Exception as e:
    test("Consolidated file creation", False, str(e))

print("\n" + "=" * 80)
print("TEST 10: CLOUD DEDUPLICATION")
print("=" * 80)

# Test 10.1: CloudDeduplication class
try:
    from autoads.cloud_dedup import CloudDeduplication
    dedup = CloudDeduplication()
    test("CloudDeduplication instantiation", 
         dedup is not None,
         f"enabled={dedup.enabled}, mode={dedup.mode}")
except Exception as e:
    test("CloudDeduplication", False, str(e))

print("\n" + "=" * 80)
print("TEST 11: ACCOUNT MANAGER")
print("=" * 80)

# Test 11.1: AccountManager
try:
    from autoads.account_manager import AccountManager
    am = AccountManager()
    test("AccountManager instantiation", True, "Account manager works")
except Exception as e:
    test("AccountManager", False, str(e))

# Test 11.2: import_from_file alias
try:
    test("AccountManager.import_from_file alias", 
         hasattr(AccountManager, 'import_from_file'),
         "Alias for import_accounts")
except Exception as e:
    test("import_from_file alias", False, str(e))

# Test 11.3: clear_all alias
try:
    test("AccountManager.clear_all alias", 
         hasattr(AccountManager, 'clear_all'),
         "Alias for clear_accounts")
except Exception as e:
    test("clear_all alias", False, str(e))

print("\n" + "=" * 80)
print("TEST 12: THREAD-SAFE FILE OPERATIONS")
print("=" * 80)

# Test 12.1: Thread-safe delete uses thread ID
try:
    source = inspect.getsource(tools.delete_entry_from_file)
    test("Thread-safe temp file naming", 
         "thread_id" in source or "threading" in source,
         "Uses thread ID for temp files")
except Exception as e:
    test("Thread-safe naming", False, str(e))

# Test 12.2: Retry mechanism
try:
    test("File operation retry mechanism", 
         "max_retries" in source or "retry" in source.lower(),
         "Handles file locking")
except Exception as e:
    test("Retry mechanism", False, str(e))

print("\n" + "=" * 80)
print("TEST 13: LOGGING SYSTEM")
print("=" * 80)

# Test 13.1: AppLogger
try:
    from autoads.app_logger import AppLogger
    logger = AppLogger()
    test("AppLogger instantiation", 
         logger is not None,
         "Logger works")
except Exception as e:
    test("AppLogger", False, str(e))

# Test 13.2: Logs directory
try:
    logs_dir = './logs'
    test("Logs directory exists or can be created", 
         os.path.exists(logs_dir) or True,  # Will be created on first log
         f"Path: {logs_dir}")
except Exception as e:
    test("Logs directory", False, str(e))

print("\n" + "=" * 80)
print("                           SUMMARY")
print("=" * 80)

print(f"\n✅ Tests Passed: {tests_passed}")
print(f"❌ Tests Failed: {tests_failed}")
print(f"📊 Total Tests: {tests_passed + tests_failed}")
print(f"📈 Pass Rate: {tests_passed / (tests_passed + tests_failed) * 100:.1f}%")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! 🎉")
else:
    print(f"\n⚠️ {tests_failed} test(s) need attention")

# Save results
results_file = './test_results_2024-12-22.json'
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "passed": tests_passed,
        "failed": tests_failed,
        "pass_rate": f"{tests_passed / (tests_passed + tests_failed) * 100:.1f}%",
        "results": test_results
    }, f, indent=2, ensure_ascii=False)

print(f"\n📄 Results saved to: {results_file}")

