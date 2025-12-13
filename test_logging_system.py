#!/usr/bin/env python3
"""
COMPREHENSIVE LOGGING TEST
Verifies that ALL actions are being logged properly
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("📝 COMPREHENSIVE LOGGING SYSTEM TEST")
print("=" * 70)

# Import app_logger
from autoads.app_logger import app_logger

print(f"\n📂 Log Directory: {os.path.abspath(app_logger.default_log_dir)}")
print(f"📄 Current Log File: {app_logger.log_file}")
print(f"📄 JSON Log File: {app_logger.json_log_file}")
print(f"🆔 Session ID: {app_logger.session_id}")

# ============================================================
# TEST 1: Verify log_action works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 1: Logging Actions")
print("=" * 70)

# Log various types of actions
app_logger.log_action("TEST_START", "Starting logging test")
app_logger.log_action("BUTTON_CLICK", "Test button clicked", {"button": "test_btn"})
app_logger.log_action("SPIDER_START", "Test spider started", {"spider": "TestSpider"})
app_logger.log_action("DATA_COLLECTED", "Test data collected", {"count": 10})
app_logger.log_action("TEST_END", "Logging test completed")

print(f"✅ Logged {len(app_logger.actions)} actions")
for action in app_logger.actions[-5:]:
    print(f"   └─ [{action.get('event')}] {action.get('message')}")

# ============================================================
# TEST 2: Verify log_button_click works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 2: Button Click Logging")
print("=" * 70)

app_logger.log_button_click("采集群组-启动", "GroupSpider页面")
app_logger.log_button_click("采集成员-停止", "MemberSpider页面")
app_logger.log_button_click("私信发送", "GreetsSpider页面")

button_clicks = [a for a in app_logger.actions if a.get('event') == 'BUTTON_CLICK']
print(f"✅ Logged {len(button_clicks)} button clicks")

# ============================================================
# TEST 3: Verify spider logging works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 3: Spider Action Logging")
print("=" * 70)

app_logger.log_spider_start("GroupSpider", thread_count=2, ads_count=1)
app_logger.log_spider_progress("GroupSpider", current=5, total=10, message="采集中")
app_logger.log_spider_stop("GroupSpider", reason="完成")
app_logger.log_data_collection("groups", count=5, source="facebook.com")
app_logger.log_message_send("TestUser", "https://facebook.com/test", success=True)

spider_actions = [a for a in app_logger.actions if 'SPIDER' in a.get('event', '')]
print(f"✅ Logged {len(spider_actions)} spider actions")

# ============================================================
# TEST 4: Verify log_error works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 4: Error Logging")
print("=" * 70)

try:
    raise ValueError("Test error for logging")
except Exception as e:
    app_logger.log_error("TEST_ERROR", str(e), {"context": "test"})

app_logger.log_error("NETWORK_ERROR", "Connection timeout", {"url": "https://test.com"})

print(f"✅ Logged {len(app_logger.errors)} errors")

# ============================================================
# TEST 5: Verify log_config_change works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 5: Config Change Logging")
print("=" * 70)

app_logger.log_config_change("main", "account_nums", "2", "5")
app_logger.log_config_change("ads", "browser_type", "adspower", "bitbrowser")

config_changes = [a for a in app_logger.actions if a.get('event') == 'CONFIG_CHANGE']
print(f"✅ Logged {len(config_changes)} config changes")

# ============================================================
# TEST 6: Verify log_browser_action works
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 6: Browser Action Logging")
print("=" * 70)

app_logger.log_browser_action("browser_123", "START", url=None, success=True)
app_logger.log_browser_action("browser_123", "NAVIGATE", url="https://facebook.com", success=True)
app_logger.log_browser_action("browser_123", "STOP", url=None, success=True)
app_logger.log_selenium_action("click", element="like_button", value=None, success=True)
app_logger.log_network_request("https://facebook.com/api", "GET", status_code=200)

browser_actions = [a for a in app_logger.actions if 'BROWSER' in a.get('event', '') or 'SELENIUM' in a.get('event', '')]
print(f"✅ Logged {len(browser_actions)} browser/selenium actions")

# ============================================================
# TEST 7: Get session summary
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 7: Session Summary")
print("=" * 70)

summary = app_logger.get_session_summary()
print(f"📊 Session Summary:")
print(f"   Session ID: {summary['session_id']}")
print(f"   Duration: {summary['duration_formatted']}")
print(f"   Total Actions: {summary['total_actions']}")
print(f"   Total Errors: {summary['total_errors']}")
print(f"   Event Counts: {summary['event_counts']}")

# ============================================================
# TEST 8: Save logs and verify files
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 8: Save Logs")
print("=" * 70)

log_file, json_file = app_logger.save_logs()
print(f"📄 Log file saved: {log_file}")
print(f"📄 JSON file saved: {json_file}")

# Verify files exist and have content
if os.path.exists(log_file):
    size = os.path.getsize(log_file)
    print(f"✅ Log file exists: {size} bytes")
else:
    print(f"❌ Log file not found!")

if os.path.exists(json_file):
    size = os.path.getsize(json_file)
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ JSON file exists: {size} bytes")
    print(f"   └─ Contains {len(data.get('actions', []))} actions")
    print(f"   └─ Contains {len(data.get('errors', []))} errors")
else:
    print(f"❌ JSON file not found!")

# ============================================================
# TEST 9: Verify log file content
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 9: Verify Log Content")
print("=" * 70)

with open(log_file, 'r', encoding='utf-8') as f:
    log_content = f.read()

# Check if our test actions are in the log
test_actions = [
    "TEST_START",
    "BUTTON_CLICK",
    "SPIDER_START",
    "CONFIG_CHANGE",
    "BROWSER_START"
]

found_in_log = []
missing_in_log = []

for action in test_actions:
    if action in log_content:
        found_in_log.append(action)
    else:
        missing_in_log.append(action)

print(f"✅ Found in log: {found_in_log}")
if missing_in_log:
    print(f"⚠️ Missing in log: {missing_in_log}")
else:
    print(f"✅ All test actions found in log file!")

# ============================================================
# TEST 10: List all log files
# ============================================================
print("\n" + "=" * 70)
print("🔬 TEST 10: All Log Files")
print("=" * 70)

log_dir = app_logger.default_log_dir
if os.path.exists(log_dir):
    files = sorted(os.listdir(log_dir), reverse=True)
    print(f"📂 Log directory: {os.path.abspath(log_dir)}")
    print(f"   Total files: {len(files)}")
    for f in files[:10]:  # Show latest 10
        filepath = os.path.join(log_dir, f)
        size = os.path.getsize(filepath)
        print(f"   └─ {f} ({size} bytes)")
else:
    print(f"❌ Log directory not found: {log_dir}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 LOGGING TEST SUMMARY")
print("=" * 70)

print(f"""
Log Files Location: {os.path.abspath(app_logger.default_log_dir)}

Current Session:
  📄 Text Log: {app_logger.log_file}
  📄 JSON Log: {app_logger.json_log_file}

Statistics:
  📝 Total Actions Logged: {len(app_logger.actions)}
  ❌ Total Errors Logged: {len(app_logger.errors)}
  📺 Terminal Output Captured: {len(app_logger.terminal_output)}

Log Content:
  ✅ Actions in Log File: {len(found_in_log)}/{len(test_actions)}
  
When App Closes:
  📢 User gets notification with log location
  📂 Logs auto-saved to ./logs/ directory
  🔗 User can click "Open Log Folder" button
""")

if len(found_in_log) == len(test_actions) and os.path.exists(log_file) and os.path.exists(json_file):
    print("🎉 LOGGING SYSTEM IS WORKING CORRECTLY!")
else:
    print("⚠️ SOME LOGGING FEATURES NEED ATTENTION")

print("\n" + "=" * 70)
print("🏁 LOGGING TEST COMPLETE")
print("=" * 70)

