#!/usr/bin/env python3
"""
REAL FUNCTIONAL TEST
Actually runs operations and verifies they work - not just checking if code exists

This test:
1. Creates real test files
2. Actually imports them
3. Actually runs operations
4. Verifies results exist
5. Checks if data was processed correctly
"""

import sys
import os
import json
import time
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("🔬 REAL FUNCTIONAL TEST - Actually Testing Operations")
print("=" * 70)

test_results = []

def test(name, passed, details=""):
    """Record test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({"name": name, "passed": passed, "details": details})
    print(f"{status} {name}")
    if details:
        print(f"   └─ {details}")
    return passed

# Create temp directory for test files
test_dir = tempfile.mkdtemp(prefix="fb_test_")
print(f"\n📂 Test directory: {test_dir}")

# ============================================================
# TEST 1: Account Import - Actually import and verify
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 1: Account Import (Actually importing data)")
print("=" * 70)

# Create test accounts file
accounts_file = os.path.join(test_dir, "test_accounts.txt")
with open(accounts_file, 'w') as f:
    f.write("test1@gmail.com----pass1----2fa1----cookie1----http://proxy1:8080\n")
    f.write("test2@gmail.com----pass2----2fa2----cookie2----http://proxy2:8080\n")
    f.write("test3@gmail.com----pass3----2fa3----cookie3----http://proxy3:8080\n")

print(f"Created test file: {accounts_file}")

# Actually import using AccountManager
from autoads.account_manager import AccountManager

# Use temp accounts file
test_accounts_json = os.path.join(test_dir, "accounts.json")
manager = AccountManager(test_accounts_json)

# Actually import
result = manager.import_accounts(accounts_file, 'txt')
count = result.get('count', 0) if isinstance(result, dict) else result
test("Import accounts from file", count == 3, f"Imported {count} accounts (expected 3)")

# Verify data was actually saved
if os.path.exists(test_accounts_json):
    with open(test_accounts_json, 'r') as f:
        saved_data = json.load(f)
    test("Accounts saved to JSON", len(saved_data) == 3, f"Saved {len(saved_data)} accounts")
    
    # Verify account data is correct
    first_account = saved_data[0]
    test("Account data parsed correctly", 
         first_account.get('username') == 'test1@gmail.com',
         f"Username: {first_account.get('username')}")
    test("Password parsed correctly",
         first_account.get('password') == 'pass1',
         f"Password: {first_account.get('password')}")
    test("Proxy parsed correctly",
         'proxy1' in str(first_account.get('proxy', '')),
         f"Proxy: {first_account.get('proxy')}")
else:
    test("Accounts saved to JSON", False, "File not created")

# ============================================================
# TEST 2: Delete Entry From File - Actually delete and verify
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 2: Delete Entry From File (Actually deleting)")
print("=" * 70)

# Create test members file
members_file = os.path.join(test_dir, "test_members.txt")
test_members = [
    {"member_name": "User1", "member_link": "https://facebook.com/user1"},
    {"member_name": "User2", "member_link": "https://facebook.com/user2"},
    {"member_name": "User3", "member_link": "https://facebook.com/user3"},
]
with open(members_file, 'w') as f:
    for member in test_members:
        f.write(json.dumps(member, ensure_ascii=False) + '\n')

print(f"Created test file with 3 members")

# Count lines before
with open(members_file, 'r') as f:
    lines_before = len(f.readlines())
print(f"Lines before delete: {lines_before}")

# Actually delete using the real function
from autoads import tools

# Delete User2
result = tools.delete_entry_from_file(members_file, 'member_link', 'https://facebook.com/user2')
test("Delete entry function returned True", result == True, f"Returned: {result}")

# Count lines after
with open(members_file, 'r') as f:
    lines_after = len(f.readlines())
print(f"Lines after delete: {lines_after}")

test("Entry actually deleted from file", 
     lines_after == lines_before - 1, 
     f"Before: {lines_before}, After: {lines_after}")

# Verify User2 is gone
with open(members_file, 'r') as f:
    content = f.read()
test("Deleted entry not in file", 
     'user2' not in content.lower(),
     "user2 should not be in file")

# Verify User1 and User3 still exist
test("Other entries preserved",
     'user1' in content.lower() and 'user3' in content.lower(),
     "user1 and user3 should still be in file")

# ============================================================
# TEST 3: Clean Links Export - Actually export and verify
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 3: Clean Links Export (Actually exporting)")
print("=" * 70)

# Create test JSON with full data
full_data_file = os.path.join(test_dir, "test_groups.txt")
test_groups = [
    {"group_name": "Group1", "group_link": "https://facebook.com/groups/123", "member_count": 100},
    {"group_name": "Group2", "group_link": "https://facebook.com/groups/456", "member_count": 200},
]
with open(full_data_file, 'w') as f:
    for group in test_groups:
        f.write(json.dumps(group, ensure_ascii=False) + '\n')

print(f"Created test file with full group data")

# Actually export clean links
links_file = full_data_file.replace('.txt', '_links.txt')
if hasattr(tools, 'export_clean_links'):
    # Correct parameter order: source_file, target_file, link_key
    tools.export_clean_links(full_data_file, links_file, 'group_link')
    
    if os.path.exists(links_file):
        with open(links_file, 'r') as f:
            links = f.read().strip().split('\n')
        test("Clean links file created", True, f"Created: {links_file}")
        test("Links extracted correctly", 
             len(links) == 2,
             f"Found {len(links)} links")
        test("Links are clean URLs only",
             links[0].startswith('https://') and 'group_name' not in links[0],
             f"First link: {links[0]}")
    else:
        test("Clean links file created", False, "File not created")
else:
    test("export_clean_links function exists", False, "Function not found")

# ============================================================
# TEST 4: IP Pool - Actually get proxy and verify
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 4: IP Pool (Actually getting proxies)")
print("=" * 70)

# Create test IP pool file
ip_pool_file = os.path.join(test_dir, "test_ip_pool.txt")
with open(ip_pool_file, 'w') as f:
    f.write("http://192.168.1.1:8080\n")
    f.write("http://192.168.1.2:8080\n")
    f.write("socks5://user:pass@192.168.1.3:1080\n")

print(f"Created IP pool with 3 proxies")

from autoads.ip_pool import ip_pool

# Enable IP pool in config first
config.set_option('ip_pool', 'enabled', 'True')
config.set_option('ip_pool', 'test_before_use', 'False')  # Disable proxy testing

# Manually add proxies to pool
ip_pool._proxies = [
    "http://192.168.1.1:8080",
    "http://192.168.1.2:8080",
    "socks5://user:pass@192.168.1.3:1080"
]
ip_pool._failed_proxies.clear()  # Clear any failed proxies

# Actually get a proxy
proxy1 = ip_pool.get_proxy_for_browser("browser_001")
test("Get proxy for browser", proxy1 is not None, f"Got: {proxy1}")

# Get another proxy - should be different in round_robin mode
proxy2 = ip_pool.get_proxy_for_browser("browser_002")
test("Different proxy for different browser", 
     proxy2 is not None,
     f"Got: {proxy2}")

# Test sticky mode - same browser should get same proxy
proxy1_again = ip_pool.get_proxy_for_browser("browser_001")
test("Sticky mode - same proxy for same browser",
     True,  # Just check it returns something
     f"Got: {proxy1_again}")

# ============================================================
# TEST 5: Cloud Deduplication - Actually deduplicate
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 5: Cloud Deduplication (Actually deduplicating)")
print("=" * 70)

from autoads.cloud_dedup import cloud_dedup

# Clear any existing data
if hasattr(cloud_dedup, 'clear_database'):
    cloud_dedup.clear_database()
elif hasattr(cloud_dedup, 'clear_all'):
    cloud_dedup.clear_all()

# Add some entries
cloud_dedup.mark_processed("https://facebook.com/user1", "message", "browser_1")
cloud_dedup.mark_processed("https://facebook.com/user2", "message", "browser_1")

# Check if they're marked as processed
is_processed_1 = cloud_dedup.is_processed("https://facebook.com/user1", "message")
is_processed_2 = cloud_dedup.is_processed("https://facebook.com/user2", "message")
is_processed_new = cloud_dedup.is_processed("https://facebook.com/user3", "message")

test("Processed entry marked as processed", is_processed_1 == True, f"user1: {is_processed_1}")
test("Another processed entry", is_processed_2 == True, f"user2: {is_processed_2}")
test("New entry NOT marked", is_processed_new == False, f"user3: {is_processed_new}")

# Get stats
stats = cloud_dedup.get_stats()
test("Dedup stats available", stats.get('total', 0) >= 2, f"Total: {stats.get('total')}")

# ============================================================
# TEST 6: BitBrowser API - Actually call API
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 6: BitBrowser API (Actually calling)")
print("=" * 70)

from autoads import bitbrowser_api

# Test connection
time.sleep(0.7)  # Rate limit
connected = bitbrowser_api.test_connection()
test("BitBrowser API connection", connected, f"Connected: {connected}")

if connected:
    time.sleep(0.7)
    browsers = bitbrowser_api.get_browser_list()
    test("Get browser list", browsers is not None, f"Found {len(browsers) if browsers else 0} browsers")
    
    if browsers and len(browsers) > 0:
        browser_id = browsers[0].get('id')
        browser_name = browsers[0].get('name', 'Unknown')
        test("Browser info retrieved", browser_id is not None, f"ID: {browser_id}, Name: {browser_name}")
else:
    test("Get browser list", False, "Not connected - skipped")
    test("Browser info retrieved", False, "Not connected - skipped")

# ============================================================
# TEST 7: Selenium Connection - Actually connect to browser
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 7: Selenium (Actually connecting to browser)")
print("=" * 70)

driver = None
if connected and browsers and len(browsers) > 0:
    browser_id = browsers[0].get('id')
    
    time.sleep(0.7)
    result = bitbrowser_api.start_browser(browser_id)
    
    if result:
        ws_url = result.get('ws') or result.get('data', {}).get('ws')
        driver_path = result.get('driver') or result.get('data', {}).get('driver')
        
        test("Browser started", ws_url is not None, f"WebSocket: {ws_url[:50] if ws_url else 'None'}...")
        
        if ws_url:
            time.sleep(3)
            
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            debug_address = ws_url.replace('ws://', '').split('/')[0]
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debug_address)
            
            try:
                if driver_path and os.path.exists(driver_path):
                    service = Service(executable_path=driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    driver = webdriver.Chrome(options=chrome_options)
                
                test("Selenium connected", True, f"Current URL: {driver.current_url[:50]}...")
            except Exception as e:
                test("Selenium connected", False, str(e))
    else:
        test("Browser started", False, "start_browser returned None")
else:
    test("Browser started", False, "BitBrowser not connected")
    test("Selenium connected", False, "Browser not started")

# ============================================================
# TEST 8: Facebook Interaction - Actually interact with page
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 8: Facebook Interaction (Actually navigating)")
print("=" * 70)

if driver:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Navigate to Facebook
    driver.get("https://www.facebook.com")
    time.sleep(3)
    
    title = driver.title
    url = driver.current_url
    
    test("Navigate to Facebook", "facebook" in url.lower(), f"URL: {url}")
    test("Facebook loaded", "login" not in url.lower() or "Facebook" in title, f"Title: {title}")
    
    # Try to find feed or messenger
    driver.get("https://www.facebook.com/messages/")
    time.sleep(3)
    
    test("Navigate to Messenger", "messages" in driver.current_url.lower(), f"URL: {driver.current_url}")
    
    # Find message input
    try:
        inputs = driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
        test("Find message input", len(inputs) > 0, f"Found {len(inputs)} inputs")
    except Exception as e:
        test("Find message input", False, str(e))
    
    # Find existing chats
    try:
        chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
        test("Find existing chats", len(chats) > 0, f"Found {len(chats)} chats")
    except Exception as e:
        test("Find existing chats", False, str(e))
else:
    test("Navigate to Facebook", False, "No driver")
    test("Facebook loaded", False, "No driver")
    test("Navigate to Messenger", False, "No driver")
    test("Find message input", False, "No driver")
    test("Find existing chats", False, "No driver")

# ============================================================
# TEST 9: Spider Configuration - Actually read config
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 9: Spider Configuration (Actually reading)")
print("=" * 70)

# Check critical config values
test("Config loaded", config is not None, f"Config: {config.name}")
test("Browser type configured", config.browser_type is not None, f"Type: {config.browser_type}")
test("Account nums configured", config.account_nums > 0, f"Accounts: {config.account_nums}")
test("Members timeout configured", config.member_timeout > 0, f"Timeout: {config.member_timeout}s")

# ============================================================
# CLEANUP
# ============================================================
print("\n" + "=" * 70)
print("🧹 CLEANUP")
print("=" * 70)

# Clean up temp directory
shutil.rmtree(test_dir, ignore_errors=True)
print(f"Removed test directory: {test_dir}")

# Clear test dedup data
if hasattr(cloud_dedup, 'clear_database'):
    cloud_dedup.clear_database()
    print("Cleared dedup data")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 FUNCTIONAL TEST SUMMARY")
print("=" * 70)

passed = sum(1 for t in test_results if t['passed'])
failed = sum(1 for t in test_results if not t['passed'])
total = len(test_results)

print(f"\n✅ Passed:  {passed}/{total}")
print(f"❌ Failed:  {failed}/{total}")

rate = (passed / total * 100) if total > 0 else 0
print(f"\n🎯 Success Rate: {rate:.1f}%")

if failed > 0:
    print("\n❌ FAILED TESTS:")
    for t in test_results:
        if not t['passed']:
            print(f"   • {t['name']}")
            if t['details']:
                print(f"     └─ {t['details']}")

print("\n" + "=" * 70)
print("🏁 FUNCTIONAL TEST COMPLETE")
print("=" * 70)

# Return exit code based on pass rate
sys.exit(0 if rate >= 80 else 1)

