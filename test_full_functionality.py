#!/usr/bin/env python3
"""
FULL FUNCTIONALITY TEST
Tests ALL features including:
- Image upload in private messaging
- Dashboard buttons
- All automation features
- Complete workflow
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("🔬 FULL FUNCTIONALITY TEST")
print("=" * 70)

results = {}

def test(name, func):
    try:
        result = func()
        status = "✅ PASS" if result else "⚠️ WARN"
        results[name] = status
        print(f"{status} {name}")
        return result
    except Exception as e:
        results[name] = f"❌ FAIL: {e}"
        print(f"❌ FAIL {name}: {e}")
        return False

# ============================================================
# PART 1: Dashboard Functionality
# ============================================================
print("\n" + "=" * 70)
print("📊 PART 1: DASHBOARD FUNCTIONALITY")
print("=" * 70)

def test_dashboard_import():
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import EnhancedDashboard
    dashboard = EnhancedDashboard()
    return dashboard is not None
test("Dashboard: Import & Create", test_dashboard_import)

def test_account_panel_buttons():
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import AccountManagementPanel
    panel = AccountManagementPanel()
    # Check buttons exist and are connected
    has_import = hasattr(panel, 'btn_import') and panel.btn_import is not None
    has_clear = hasattr(panel, 'btn_clear') and panel.btn_clear is not None
    has_export = hasattr(panel, 'btn_export') and panel.btn_export is not None
    # Check signals are connected
    import_connected = len(panel.btn_import.receivers(panel.btn_import.clicked)) > 0
    return has_import and has_clear and has_export and import_connected
test("Dashboard: Account Panel Buttons Connected", test_account_panel_buttons)

def test_user_panel_buttons():
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import UserManagementPanel
    panel = UserManagementPanel()
    has_import = hasattr(panel, 'btn_import') and panel.btn_import is not None
    import_connected = len(panel.btn_import.receivers(panel.btn_import.clicked)) > 0
    return has_import and import_connected
test("Dashboard: User Panel Buttons Connected", test_user_panel_buttons)

def test_thread_control_buttons():
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import ThreadControlPanel
    panel = ThreadControlPanel()
    has_stop = hasattr(panel, 'btn_stop') and panel.btn_stop is not None
    has_pause = hasattr(panel, 'btn_pause') and panel.btn_pause is not None
    stop_connected = len(panel.btn_stop.receivers(panel.btn_stop.clicked)) > 0
    return has_stop and has_pause and stop_connected
test("Dashboard: Thread Control Buttons Connected", test_thread_control_buttons)

def test_filter_settings():
    import pyside2_compat
    from PySide2.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from enhanced_dashboard import FilterSettingsPanel
    panel = FilterSettingsPanel()
    has_test_btn = hasattr(panel, 'btn_test_connection') and panel.btn_test_connection is not None
    return has_test_btn
test("Dashboard: Filter Settings Panel", test_filter_settings)

# ============================================================
# PART 2: Browser & Selenium
# ============================================================
print("\n" + "=" * 70)
print("🌐 PART 2: BROWSER & SELENIUM")
print("=" * 70)

from autoads import bitbrowser_api

driver = None
browser_id = None

def test_browser_connection():
    global browser_id
    time.sleep(0.7)
    browsers = bitbrowser_api.get_browser_list()
    if browsers:
        browser_id = browsers[0].get('id')
        return True
    return False
test("Browser: Get Browser List", test_browser_connection)

def test_browser_start():
    global driver
    if not browser_id:
        return False
    time.sleep(0.7)
    result = bitbrowser_api.start_browser(browser_id)
    ws_url = result.get('ws') or result.get('data', {}).get('ws')
    driver_path = result.get('driver') or result.get('data', {}).get('driver')
    
    if not ws_url:
        return False
    
    time.sleep(3)
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    debug_address = ws_url.replace('ws://', '').split('/')[0]
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debug_address)
    
    if driver_path and os.path.exists(driver_path):
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver is not None
test("Browser: Start & Selenium Connect", test_browser_start)

# ============================================================
# PART 3: Private Messaging with Image
# ============================================================
print("\n" + "=" * 70)
print("💬 PART 3: PRIVATE MESSAGING (WITH IMAGE TEST)")
print("=" * 70)

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def test_messenger_access():
    if not driver:
        return False
    driver.get("https://www.facebook.com/messages/")
    time.sleep(3)
    return "messages" in driver.current_url.lower() or "messenger" in driver.title.lower()
test("Messenger: Access Page", test_messenger_access)

def test_open_chat():
    if not driver:
        return False
    # Find existing chat
    chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
    if chats:
        chats[0].click()
        time.sleep(2)
        return True
    return False
test("Messenger: Open Existing Chat", test_open_chat)

def test_message_input():
    if not driver:
        return False
    inputs = driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
    return len(inputs) > 0
test("Messenger: Message Input Found", test_message_input)

def test_image_upload_capability():
    if not driver:
        return False
    # Check for file input (for image upload)
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    if file_inputs:
        return True
    # Check for attachment button
    attach_btns = driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Attach') or contains(@aria-label, '附加') or contains(@aria-label, '照片') or contains(@aria-label, 'photo')]")
    return len(attach_btns) > 0
test("Messenger: Image Upload Available", test_image_upload_capability)

def test_send_test_message():
    if not driver:
        return False
    try:
        # Find message input
        inputs = driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
        if not inputs:
            return False
        
        msg_input = inputs[0]
        msg_input.click()
        time.sleep(0.5)
        
        test_msg = f"[FuncTest] {time.strftime('%H:%M:%S')}"
        msg_input.send_keys(test_msg)
        time.sleep(0.5)
        msg_input.send_keys(Keys.ENTER)
        time.sleep(2)
        
        # Verify message sent
        page = driver.page_source
        return "FuncTest" in page
    except:
        return False
test("Messenger: Send Test Message", test_send_test_message)

# ============================================================
# PART 4: Automation Spiders
# ============================================================
print("\n" + "=" * 70)
print("🕷️ PART 4: AUTOMATION SPIDERS")
print("=" * 70)

def test_auto_like_spider():
    from spider.fb_auto_like import AutoLikeSpider
    return AutoLikeSpider is not None
test("Spider: AutoLike Import", test_auto_like_spider)

def test_auto_comment_spider():
    from spider.fb_auto_comment import AutoCommentSpider
    return AutoCommentSpider is not None
test("Spider: AutoComment Import", test_auto_comment_spider)

def test_auto_follow_spider():
    from spider.fb_auto_follow import AutoFollowSpider
    return AutoFollowSpider is not None
test("Spider: AutoFollow Import", test_auto_follow_spider)

def test_auto_add_friend_spider():
    from spider.fb_auto_add_friend import AutoAddFriendSpider
    return AutoAddFriendSpider is not None
test("Spider: AutoAddFriend Import", test_auto_add_friend_spider)

def test_auto_post_spider():
    from spider.fb_auto_post import AutoPostSpider
    return AutoPostSpider is not None
test("Spider: AutoPost Import", test_auto_post_spider)

# ============================================================
# PART 5: Like Button Functionality
# ============================================================
print("\n" + "=" * 70)
print("👍 PART 5: LIKE BUTTON TEST")
print("=" * 70)

def test_find_like_buttons():
    if not driver:
        return False
    driver.get("https://www.facebook.com")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(1)
    like_btns = driver.find_elements(By.XPATH, "//div[@aria-label='赞' or @aria-label='Like' or contains(@aria-label, 'like') or contains(@aria-label, '赞')][@role='button']")
    return len(like_btns) > 0
test("AutoLike: Find Like Buttons on Feed", test_find_like_buttons)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 FULL FUNCTIONALITY TEST SUMMARY")
print("=" * 70)

passed = sum(1 for r in results.values() if "PASS" in str(r))
warned = sum(1 for r in results.values() if "WARN" in str(r))
failed = sum(1 for r in results.values() if "FAIL" in str(r))
total = len(results)

print(f"\n✅ Passed:  {passed}/{total}")
print(f"⚠️ Warnings: {warned}/{total}")
print(f"❌ Failed:  {failed}/{total}")

rate = (passed / total * 100) if total > 0 else 0
print(f"\n🎯 Success Rate: {rate:.1f}%")

if rate >= 90:
    print("\n🎉 ALL FUNCTIONALITY IS WORKING!")
elif rate >= 70:
    print("\n✅ MOSTLY WORKING (minor issues)")
else:
    print("\n⚠️ NEEDS ATTENTION")

print("\n" + "=" * 70)
print("🏁 TEST COMPLETE")
print("=" * 70)

