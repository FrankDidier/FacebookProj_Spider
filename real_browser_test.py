#!/usr/bin/env python3
"""
Real Browser Test - Actually opens BitBrowser and tests Facebook interaction
Uses BitBrowser's built-in ChromeDriver for compatibility
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("🌐 REAL BROWSER TEST - BitBrowser + Facebook")
print("=" * 70)

# Step 1: Get browser list
print("\n📋 Step 1: Getting browser list...")
from autoads import bitbrowser_api

time.sleep(0.7)  # Rate limiting
browsers = bitbrowser_api.get_browser_list()

if not browsers:
    print("❌ No browsers found in BitBrowser!")
    print("   Please create a browser profile in BitBrowser first.")
    sys.exit(1)

print(f"✅ Found {len(browsers)} browser(s):")
for i, b in enumerate(browsers):
    name = b.get('name', b.get('remark', 'Unknown'))
    browser_id = b.get('id', 'N/A')
    print(f"   {i+1}. {name} (ID: {browser_id[:16]}...)")

# Step 2: Start browser
test_browser = browsers[0]
browser_id = test_browser.get('id')
browser_name = test_browser.get('name', test_browser.get('remark', 'Test'))

print(f"\n🚀 Step 2: Starting browser '{browser_name}'...")
time.sleep(0.7)  # Rate limiting
start_result = bitbrowser_api.start_browser(browser_id)

if not start_result:
    print("❌ Failed to start browser!")
    sys.exit(1)

# Check for WebSocket and driver path in the result
ws_url = None
driver_path = None
if isinstance(start_result, dict):
    if 'ws' in start_result:
        ws_url = start_result['ws']
        driver_path = start_result.get('driver')
    elif 'data' in start_result and isinstance(start_result['data'], dict):
        ws_url = start_result['data'].get('ws')
        driver_path = start_result['data'].get('driver')

if not ws_url:
    print(f"❌ No WebSocket URL in response: {start_result}")
    sys.exit(1)

print(f"✅ Browser started!")
print(f"   WebSocket: {ws_url}")
print(f"   Driver: {driver_path}")

# Step 3: Connect with Selenium using BitBrowser's ChromeDriver
print("\n🔗 Step 3: Connecting with Selenium...")
time.sleep(3)  # Wait for browser to fully open

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Extract debug address from WebSocket URL
    debug_address = ws_url.replace('ws://', '').split('/')[0]
    print(f"   Debug address: {debug_address}")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debug_address)
    
    # Use BitBrowser's ChromeDriver if available
    if driver_path and os.path.exists(driver_path):
        print(f"   Using BitBrowser's ChromeDriver: {driver_path}")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Try default ChromeDriver
        print("   Using system ChromeDriver")
        driver = webdriver.Chrome(options=chrome_options)
    
    print(f"✅ Selenium connected!")
    print(f"   Current URL: {driver.current_url}")
    print(f"   Title: {driver.title}")
    
except Exception as e:
    print(f"❌ Selenium connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Navigate to Facebook
print("\n📱 Step 4: Navigating to Facebook...")
try:
    driver.get("https://www.facebook.com")
    time.sleep(3)
    
    print(f"✅ Navigated to Facebook!")
    print(f"   URL: {driver.current_url}")
    print(f"   Title: {driver.title}")
    
    # Check if logged in
    if "log in" in driver.title.lower() or "login" in driver.current_url.lower():
        print("\n⚠️ Not logged in - need to login first")
        print("   Please login in the browser window, then this test can continue")
    else:
        print("\n✅ Already logged in to Facebook!")
        
except Exception as e:
    print(f"❌ Navigation failed: {e}")

# Step 5: Test Facebook Groups page
print("\n👥 Step 5: Testing Groups page...")
try:
    driver.get("https://www.facebook.com/groups/")
    time.sleep(3)
    
    print(f"✅ Navigated to Groups!")
    print(f"   URL: {driver.current_url}")
    
    # Try to find group elements
    groups = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
    print(f"   Found {len(groups)} group links on page")
    
except Exception as e:
    print(f"❌ Groups page test failed: {e}")

# Step 6: Test sending a message (dry run - just find elements)
print("\n💬 Step 6: Testing Messenger accessibility...")
try:
    driver.get("https://www.facebook.com/messages/")
    time.sleep(3)
    
    print(f"✅ Navigated to Messenger!")
    print(f"   URL: {driver.current_url}")
    
except Exception as e:
    print(f"❌ Messenger test failed: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 BROWSER TEST SUMMARY")
print("=" * 70)
print(f"""
✅ BitBrowser API: Working
✅ Browser Profiles: {len(browsers)} found
✅ Browser Start: Success
✅ Selenium Connect: Success
✅ Facebook Access: {'Logged In' if 'log in' not in driver.title.lower() else 'Need Login'}

🔍 Current Browser State:
   - URL: {driver.current_url}
   - Title: {driver.title}
""")

# Keep browser open for user inspection
print("\n⏸️ Browser will stay open for 10 seconds for inspection...")
time.sleep(10)

# Check if we should close the browser
try:
    keep_open = config.get_option('ads', 'keep_browser_open_after_stop')
    if keep_open and keep_open.lower() == 'true':
        print("\n✅ Keeping browser open as configured")
    else:
        print("\n🛑 Closing browser...")
        driver.quit()
        time.sleep(0.7)
        bitbrowser_api.stop_browser(browser_id)
        print("✅ Browser closed")
except:
    print("\n✅ Keeping browser open (default behavior)")

print("\n" + "=" * 70)
print("🏁 BROWSER TEST COMPLETE")
print("=" * 70)
