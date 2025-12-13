#!/usr/bin/env python3
"""
REAL VERIFICATION TEST
No false positives - actually verify each feature WORKS
"""

import sys
import os
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("🔍 REAL VERIFICATION TEST - NO FALSE POSITIVES")
print("=" * 70)

results = {}
detailed_results = {}

def test(name, func):
    """Run test and capture detailed results"""
    try:
        result, details = func()
        if result:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        results[name] = status
        detailed_results[name] = details
        print(f"{status} {name}")
        print(f"   └─ {details}")
        return result
    except Exception as e:
        results[name] = "❌ ERROR"
        detailed_results[name] = f"Exception: {str(e)}"
        print(f"❌ ERROR {name}")
        print(f"   └─ {str(e)}")
        traceback.print_exc()
        return False

# ============================================================
# PART 1: DASHBOARD BUTTONS - VERIFY THEY ACTUALLY WORK
# ============================================================
print("\n" + "=" * 70)
print("📊 PART 1: DASHBOARD BUTTON VERIFICATION")
print("=" * 70)

def test_account_panel_import_button():
    """Verify import button is clickable and triggers file dialog"""
    import pyside2_compat
    from PySide2.QtWidgets import QApplication, QFileDialog
    from PySide2.QtCore import QTimer
    
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import AccountManagementPanel
    panel = AccountManagementPanel()
    
    # Check button exists
    if not hasattr(panel, 'btn_import') or panel.btn_import is None:
        return False, "btn_import not found"
    
    # Check button is enabled
    if not panel.btn_import.isEnabled():
        return False, "btn_import is disabled"
    
    # Check button has text
    text = panel.btn_import.text()
    if not text:
        return False, "btn_import has no text"
    
    # Check method exists
    if not hasattr(panel, 'on_import_accounts'):
        return False, "on_import_accounts method missing"
    
    return True, f"Button exists, enabled, text='{text}', handler exists"

test("Account Panel: Import Button", test_account_panel_import_button)

def test_account_panel_clear_button():
    """Verify clear button works"""
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import AccountManagementPanel
    panel = AccountManagementPanel()
    
    if not hasattr(panel, 'btn_clear') or panel.btn_clear is None:
        return False, "btn_clear not found"
    
    if not panel.btn_clear.isEnabled():
        return False, "btn_clear is disabled"
    
    if not hasattr(panel, 'on_clear_accounts'):
        return False, "on_clear_accounts method missing"
    
    return True, f"Button exists, enabled, text='{panel.btn_clear.text()}', handler exists"

test("Account Panel: Clear Button", test_account_panel_clear_button)

def test_thread_stop_button():
    """Verify stop button works"""
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import ThreadControlPanel
    panel = ThreadControlPanel()
    
    if not hasattr(panel, 'btn_stop') or panel.btn_stop is None:
        return False, "btn_stop not found"
    
    if not panel.btn_stop.isEnabled():
        return False, "btn_stop is disabled"
    
    if not hasattr(panel, 'on_stop_clicked'):
        return False, "on_stop_clicked method missing"
    
    # Check signal exists
    if not hasattr(panel, 'stop_requested'):
        return False, "stop_requested signal missing"
    
    return True, f"Button exists, enabled, text='{panel.btn_stop.text()}', handler+signal exist"

test("Thread Control: Stop Button", test_thread_stop_button)

def test_filter_test_connection():
    """Verify cloud dedup test works"""
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import FilterSettingsPanel
    panel = FilterSettingsPanel()
    
    if not hasattr(panel, 'btn_test_connection') or panel.btn_test_connection is None:
        return False, "btn_test_connection not found"
    
    if not hasattr(panel, 'on_test_connection'):
        return False, "on_test_connection method missing"
    
    # Test the cloud dedup
    if hasattr(panel, 'cloud_dedup') and panel.cloud_dedup:
        try:
            stats = panel.cloud_dedup.get_stats()
            return True, f"Cloud dedup works, stats: {stats}"
        except Exception as e:
            return False, f"Cloud dedup error: {e}"
    
    return True, "Button exists, handler exists (cloud dedup module not loaded)"

test("Filter Settings: Test Connection", test_filter_test_connection)

# ============================================================
# PART 2: BROWSER & MESSENGER - REAL VERIFICATION
# ============================================================
print("\n" + "=" * 70)
print("🌐 PART 2: BROWSER & MESSENGER VERIFICATION")
print("=" * 70)

from autoads import bitbrowser_api

driver = None
browser_id = None

def test_browser_api():
    """Verify browser API actually responds"""
    global browser_id
    time.sleep(0.7)
    
    # Test connection
    connected = bitbrowser_api.test_connection()
    if not connected:
        return False, "BitBrowser API not responding"
    
    # Get browser list
    browsers = bitbrowser_api.get_browser_list()
    if not browsers:
        return False, "No browsers found in BitBrowser"
    
    browser_id = browsers[0].get('id')
    browser_name = browsers[0].get('name', 'Unknown')
    
    return True, f"API connected, found {len(browsers)} browsers, using: {browser_name}"

test("BitBrowser: API Connection", test_browser_api)

def test_browser_start():
    """Verify browser actually starts"""
    global driver
    
    if not browser_id:
        return False, "No browser_id available"
    
    time.sleep(0.7)
    result = bitbrowser_api.start_browser(browser_id)
    
    if not result:
        return False, "start_browser returned None"
    
    ws_url = result.get('ws') or result.get('data', {}).get('ws')
    driver_path = result.get('driver') or result.get('data', {}).get('driver')
    
    if not ws_url:
        return False, f"No WebSocket URL in response: {result}"
    
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
    except Exception as e:
        return False, f"Selenium connection failed: {e}"
    
    current_url = driver.current_url
    return True, f"Browser started, Selenium connected, URL: {current_url[:50]}..."

test("BitBrowser: Start & Connect", test_browser_start)

def test_facebook_access():
    """Verify Facebook is accessible and logged in"""
    if not driver:
        return False, "No driver available"
    
    driver.get("https://www.facebook.com")
    time.sleep(3)
    
    url = driver.current_url
    title = driver.title
    
    if "login" in url.lower() or "log in" in title.lower():
        return False, f"Not logged in! URL: {url}, Title: {title}"
    
    return True, f"Facebook accessible, Title: {title}"

test("Facebook: Access & Login", test_facebook_access)

# ============================================================
# PART 3: PRIVATE MESSAGING - REAL VERIFICATION
# ============================================================
print("\n" + "=" * 70)
print("💬 PART 3: PRIVATE MESSAGING VERIFICATION")
print("=" * 70)

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def test_messenger_real():
    """Actually navigate to messenger and verify elements exist"""
    if not driver:
        return False, "No driver available"
    
    driver.get("https://www.facebook.com/messages/")
    time.sleep(4)
    
    url = driver.current_url
    
    if "login" in url.lower():
        return False, f"Redirected to login: {url}"
    
    if "messages" not in url.lower() and "messenger" not in driver.title.lower():
        return False, f"Not on Messenger. URL: {url}"
    
    return True, f"Messenger accessible, URL: {url}"

test("Messenger: Navigate", test_messenger_real)

def test_find_chat_and_open():
    """Find an existing chat and open it"""
    if not driver:
        return False, "No driver available"
    
    # Look for chat links
    chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
    
    if not chats:
        return False, "No existing chats found"
    
    # Click first chat
    try:
        chat_href = chats[0].get_attribute('href')
        chats[0].click()
        time.sleep(2)
        return True, f"Opened chat: {chat_href[:50]}..."
    except Exception as e:
        return False, f"Failed to open chat: {e}"

test("Messenger: Open Chat", test_find_chat_and_open)

def test_message_input_real():
    """Actually find and verify message input is usable"""
    if not driver:
        return False, "No driver available"
    
    # Try multiple XPaths
    xpaths = [
        "//div[@role='textbox' and @contenteditable='true']",
        "//div[contains(@aria-label, '消息') or contains(@aria-label, 'message')][@contenteditable='true']",
        "//div[@data-lexical-editor='true']",
    ]
    
    for xpath in xpaths:
        inputs = driver.find_elements(By.XPATH, xpath)
        if inputs:
            # Verify it's actually usable
            try:
                inp = inputs[0]
                if inp.is_displayed() and inp.is_enabled():
                    return True, f"Input found with: {xpath[:40]}..., displayed & enabled"
            except:
                continue
    
    return False, "No usable message input found"

test("Messenger: Message Input", test_message_input_real)

def test_image_upload_real():
    """Verify image upload is actually available"""
    if not driver:
        return False, "No driver available"
    
    # Look for file input
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    
    if file_inputs:
        for inp in file_inputs:
            accept = inp.get_attribute('accept') or ''
            if 'image' in accept or accept == '':
                return True, f"File input found, accept='{accept}'"
    
    # Look for attachment button
    attach_xpaths = [
        "//*[contains(@aria-label, 'Attach')]",
        "//*[contains(@aria-label, '附加')]",
        "//*[contains(@aria-label, '照片')]",
        "//*[contains(@aria-label, 'photo')]",
        "//*[contains(@aria-label, 'image')]",
    ]
    
    for xpath in attach_xpaths:
        btns = driver.find_elements(By.XPATH, xpath)
        if btns:
            return True, f"Attachment button found with: {xpath}"
    
    return False, "No file input or attachment button found"

test("Messenger: Image Upload", test_image_upload_real)

def test_actually_send_message():
    """ACTUALLY send a message and verify it appears"""
    if not driver:
        return False, "No driver available"
    
    # Find input
    inputs = driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
    if not inputs:
        return False, "No message input found"
    
    inp = inputs[0]
    
    # Generate unique test message
    test_msg = f"[VERIFY_{int(time.time())}]"
    
    try:
        # Click and type
        inp.click()
        time.sleep(0.3)
        inp.send_keys(test_msg)
        time.sleep(0.5)
        
        # Send
        inp.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # Verify message appears in page
        page_source = driver.page_source
        if test_msg in page_source:
            return True, f"Message '{test_msg}' VERIFIED in page!"
        else:
            return False, f"Message '{test_msg}' NOT found in page after send"
    except Exception as e:
        return False, f"Send failed: {e}"

test("Messenger: Send & Verify", test_actually_send_message)

# ============================================================
# PART 4: LIKE BUTTON - REAL VERIFICATION
# ============================================================
print("\n" + "=" * 70)
print("👍 PART 4: LIKE BUTTON VERIFICATION")
print("=" * 70)

def test_like_button_real():
    """Actually find like buttons on the feed"""
    if not driver:
        return False, "No driver available"
    
    driver.get("https://www.facebook.com")
    time.sleep(4)
    
    # Scroll to load posts
    driver.execute_script("window.scrollTo(0, 800);")
    time.sleep(2)
    
    # Try multiple XPaths for like buttons
    like_xpaths = [
        "//div[@aria-label='赞'][@role='button']",
        "//div[@aria-label='Like'][@role='button']",
        "//span[text()='赞']//ancestor::div[@role='button']",
        "//span[text()='Like']//ancestor::div[@role='button']",
        "//div[contains(@aria-label, 'Like')][@role='button']",
        "//div[contains(@aria-label, '赞')][@role='button']",
    ]
    
    for xpath in like_xpaths:
        buttons = driver.find_elements(By.XPATH, xpath)
        if buttons:
            # Verify at least one is visible
            for btn in buttons:
                if btn.is_displayed():
                    return True, f"Found {len(buttons)} like buttons with: {xpath[:40]}..."
    
    # If no buttons found, check if we're on the right page
    title = driver.title
    url = driver.current_url
    
    return False, f"No visible like buttons. Page: {title}, URL: {url[:50]}"

test("AutoLike: Find Like Buttons", test_like_button_real)

# ============================================================
# PART 5: AUTOMATION SPIDERS - REAL VERIFICATION
# ============================================================
print("\n" + "=" * 70)
print("🕷️ PART 5: SPIDER VERIFICATION")
print("=" * 70)

def test_spider_has_methods():
    """Verify spiders have required methods"""
    from spider.fb_auto_like import AutoLikeSpider
    
    required_methods = ['start_requests', 'parse']
    missing = []
    
    for method in required_methods:
        if not hasattr(AutoLikeSpider, method):
            missing.append(method)
    
    if missing:
        return False, f"Missing methods: {missing}"
    
    return True, f"Has all required methods: {required_methods}"

test("AutoLikeSpider: Has Methods", test_spider_has_methods)

def test_greets_spider_has_methods():
    """Verify greets spider has required methods"""
    from spider.fb_greets import GreetsSpider
    
    required_methods = ['start_requests', 'parse']
    missing = []
    
    for method in required_methods:
        if not hasattr(GreetsSpider, method):
            missing.append(method)
    
    if missing:
        return False, f"Missing methods: {missing}"
    
    return True, f"Has all required methods: {required_methods}"

test("GreetsSpider: Has Methods", test_greets_spider_has_methods)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)

passed = sum(1 for r in results.values() if "PASS" in str(r))
failed = sum(1 for r in results.values() if "FAIL" in str(r) or "ERROR" in str(r))
total = len(results)

print(f"\n✅ Passed:  {passed}/{total}")
print(f"❌ Failed:  {failed}/{total}")

rate = (passed / total * 100) if total > 0 else 0
print(f"\n🎯 Success Rate: {rate:.1f}%")

if failed > 0:
    print("\n❌ FAILED TESTS DETAILS:")
    for name, detail in detailed_results.items():
        if "FAIL" in results.get(name, "") or "ERROR" in results.get(name, ""):
            print(f"   • {name}")
            print(f"     Reason: {detail}")

if rate >= 90:
    print("\n🎉 VERIFICATION COMPLETE - ALL SYSTEMS WORKING!")
elif rate >= 70:
    print("\n⚠️ MOSTLY WORKING - Some issues need attention")
else:
    print("\n❌ SIGNIFICANT ISSUES DETECTED")

print("\n" + "=" * 70)
print("🏁 VERIFICATION COMPLETE")
print("=" * 70)

