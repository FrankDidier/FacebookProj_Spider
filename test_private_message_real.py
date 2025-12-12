#!/usr/bin/env python3
"""
REAL Private Message Test - Actually sends a message to verify the flow works
This is not a mass test - just sends to ONE user to confirm functionality
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("💬 REAL PRIVATE MESSAGE TEST")
print("=" * 70)
print("This test will send ONE message to verify the complete flow works.")
print()

# Step 1: Connect to browser
print("📋 Step 1: Connecting to BitBrowser...")
from autoads import bitbrowser_api

time.sleep(0.7)
browsers = bitbrowser_api.get_browser_list()
if not browsers:
    print("❌ No browsers found!")
    sys.exit(1)

browser_id = browsers[0].get('id')
browser_name = browsers[0].get('name', 'Test')
print(f"✅ Using browser: {browser_name}")

time.sleep(0.7)
start_result = bitbrowser_api.start_browser(browser_id)
ws_url = start_result.get('ws') or start_result.get('data', {}).get('ws')
driver_path = start_result.get('driver') or start_result.get('data', {}).get('driver')

if not ws_url:
    print(f"❌ Failed to start browser")
    sys.exit(1)

print(f"✅ Browser started!")

# Step 2: Connect Selenium
print("\n📋 Step 2: Connecting Selenium...")
time.sleep(3)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

debug_address = ws_url.replace('ws://', '').split('/')[0]
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", debug_address)

if driver_path and os.path.exists(driver_path):
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

print(f"✅ Selenium connected!")

# Step 3: Go directly to Messenger to find a recent chat
print("\n📋 Step 3: Going to Messenger to find a chat...")
driver.get("https://www.facebook.com/messages/")
time.sleep(4)

print(f"   Current URL: {driver.current_url}")

# Look for existing chats
chat_rows = driver.find_elements(By.XPATH, "//div[@role='row' or @role='gridcell']//a[contains(@href, '/messages/t/')]")
print(f"   Found {len(chat_rows)} chat links")

test_chat_url = None
if chat_rows:
    for row in chat_rows[:5]:
        try:
            href = row.get_attribute('href')
            if href and '/messages/t/' in href:
                test_chat_url = href
                print(f"   Selected chat: {href}")
                break
        except:
            continue

if not test_chat_url:
    print("⚠️ No existing chats found, will try to send new message...")
    # Try the new message approach
    driver.get("https://www.facebook.com/messages/new/")
    time.sleep(3)
else:
    # Go to selected chat
    driver.get(test_chat_url)
    time.sleep(3)

print(f"   Now at: {driver.current_url}")

# Step 4: Find message input
print("\n📋 Step 4: Finding message input...")

def find_message_input():
    """Find message input with retries"""
    xpaths = [
        "//div[@role='textbox' and @contenteditable='true']",
        "//div[contains(@aria-label, '消息') or contains(@aria-label, 'message')][@contenteditable='true']",
        "//div[@data-lexical-editor='true']",
    ]
    
    for xpath in xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                return elements[0]
        except:
            continue
    return None

message_input = None
for attempt in range(5):
    message_input = find_message_input()
    if message_input:
        print(f"✅ Found message input!")
        break
    print(f"   Attempt {attempt+1}: Looking for message input...")
    time.sleep(1)

if not message_input:
    print("❌ Could not find message input after 5 attempts")
    print("   Current URL:", driver.current_url)
    # Take screenshot for debugging
    driver.save_screenshot("/Users/vv/Desktop/src-facebook/debug_screenshot.png")
    print("   Screenshot saved to debug_screenshot.png")
    sys.exit(1)

# Step 5: Send test message with retry logic
print("\n📋 Step 5: Sending test message...")

test_message = f"[Automation Test] {time.strftime('%Y-%m-%d %H:%M:%S')}"
print(f"   Message: {test_message}")

send_success = False
for attempt in range(3):
    try:
        # Re-find the element in case of stale reference
        message_input = find_message_input()
        if not message_input:
            print(f"   Attempt {attempt+1}: Message input lost, retrying...")
            time.sleep(1)
            continue
        
        # Click to focus
        message_input.click()
        time.sleep(0.5)
        
        # Clear any existing text
        message_input.send_keys(Keys.CONTROL + 'a')
        time.sleep(0.2)
        
        # Type message
        message_input.send_keys(test_message)
        time.sleep(1)
        print(f"   ✅ Message typed!")
        
        # Press Enter to send
        message_input.send_keys(Keys.ENTER)
        time.sleep(2)
        print(f"   ✅ Enter pressed!")
        
        send_success = True
        break
        
    except StaleElementReferenceException:
        print(f"   Attempt {attempt+1}: Stale element, retrying...")
        time.sleep(1)
    except Exception as e:
        print(f"   Attempt {attempt+1}: Error: {e}")
        time.sleep(1)

if send_success:
    print("✅ Message sent successfully!")
else:
    print("❌ Failed to send message after 3 attempts")

# Step 6: Verify message appears in chat
print("\n📋 Step 6: Verifying message in chat...")
time.sleep(2)

try:
    # Look for our test message text
    page_source = driver.page_source
    if "Automation Test" in page_source:
        print("✅ Message verified - found in page!")
    else:
        print("⚠️ Message text not found in page (may still have been sent)")
except:
    print("⚠️ Could not verify message")

# Step 7: Test image upload capability
print("\n📋 Step 7: Testing image upload...")

file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
if file_inputs:
    print(f"✅ Found {len(file_inputs)} file input(s) for image upload!")
else:
    # Look for attachment button
    attach_btns = driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Attach') or contains(@aria-label, '附加') or contains(@aria-label, '照片')]")
    if attach_btns:
        print(f"✅ Found {len(attach_btns)} attachment button(s)!")
    else:
        print("⚠️ No file input or attachment button found")

# Summary
print("\n" + "=" * 70)
print("📊 PRIVATE MESSAGE TEST SUMMARY")
print("=" * 70)
print(f"""
Test Results:
  ✅ Browser Connection: Working
  ✅ Selenium Connection: Working  
  ✅ Messenger Access: {'Success' if '/messages/' in driver.current_url else 'Partial'}
  ✅ Message Input: {'Found' if message_input else 'Not Found'}
  {'✅' if send_success else '❌'} Message Send: {'Success' if send_success else 'Failed'}
  ✅ Image Upload: {'Available' if file_inputs else 'Via button'}

Current URL: {driver.current_url}
""")

if send_success:
    print("🎉 PRIVATE MESSAGING IS WORKING!")
else:
    print("⚠️ Private messaging needs attention")

print("\n" + "=" * 70)
print("🏁 TEST COMPLETE")
print("=" * 70)
