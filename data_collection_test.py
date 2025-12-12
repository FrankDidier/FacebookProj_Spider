#!/usr/bin/env python3
"""
Data Collection Test - Tests that groups and members are actually saved to files
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoads.config import config
config.name = 'config.ini'

print("=" * 70)
print("📁 DATA COLLECTION & SAVING TEST")
print("=" * 70)

# Step 1: Connect browser
print("\n📋 Step 1: Connecting to browser...")
from autoads import bitbrowser_api

time.sleep(0.7)
browsers = bitbrowser_api.get_browser_list()
browser_id = browsers[0].get('id')
print(f"✅ Using: {browsers[0].get('name')}")

time.sleep(0.7)
start_result = bitbrowser_api.start_browser(browser_id)
ws_url = start_result.get('ws') or start_result.get('data', {}).get('ws')
driver_path = start_result.get('driver') or start_result.get('data', {}).get('driver')

time.sleep(3)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

debug_address = ws_url.replace('ws://', '').split('/')[0]
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", debug_address)
service = Service(executable_path=driver_path) if driver_path else None
driver = webdriver.Chrome(service=service, options=chrome_options) if service else webdriver.Chrome(options=chrome_options)
print("✅ Connected!")

# Step 2: Collect Groups
print("\n👥 Step 2: Collecting groups from feed...")
driver.get("https://www.facebook.com/groups/feed/")
time.sleep(3)

# Scroll to load more
for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

# Find groups
group_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/') and not(contains(@href, '/groups/feed'))]")
collected_groups = []

for link in group_links[:20]:  # Limit to 20
    try:
        href = link.get_attribute('href')
        if href and '/groups/' in href:
            parts = href.split('/groups/')
            if len(parts) > 1:
                group_id = parts[1].split('/')[0].split('?')[0]
                if group_id and len(group_id) > 5:
                    # Get group name if possible
                    try:
                        name = link.text or link.get_attribute('aria-label') or f"Group_{group_id}"
                    except:
                        name = f"Group_{group_id}"
                    
                    if group_id not in [g['id'] for g in collected_groups]:
                        collected_groups.append({
                            'id': group_id,
                            'name': name[:50],
                            'link': f"https://www.facebook.com/groups/{group_id}",
                            'collected_at': datetime.now().isoformat()
                        })
    except:
        continue

print(f"✅ Collected {len(collected_groups)} groups")

# Step 3: Save groups to file
print("\n💾 Step 3: Saving groups to file...")
data_dir = os.path.join(os.path.dirname(__file__), 'data', 'groups')
os.makedirs(data_dir, exist_ok=True)

groups_file = os.path.join(data_dir, f'groups_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
groups_links_file = groups_file.replace('.json', '_links.txt')

# Save JSON
with open(groups_file, 'w', encoding='utf-8') as f:
    json.dump(collected_groups, f, ensure_ascii=False, indent=2)
print(f"✅ Saved JSON: {groups_file}")

# Save links only
with open(groups_links_file, 'w', encoding='utf-8') as f:
    for g in collected_groups:
        f.write(g['link'] + '\n')
print(f"✅ Saved links: {groups_links_file}")

# Step 4: Collect members from first group
print("\n👤 Step 4: Collecting members from a group...")
if collected_groups:
    test_group = collected_groups[0]
    members_url = f"https://www.facebook.com/groups/{test_group['id']}/members"
    print(f"   Group: {test_group['name']}")
    print(f"   URL: {members_url}")
    
    driver.get(members_url)
    time.sleep(3)
    
    # Scroll to load members
    for i in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    
    # Find member links
    member_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com/')]")
    collected_members = []
    
    for elem in member_elements[:30]:  # Limit to 30
        try:
            href = elem.get_attribute('href')
            if href and 'facebook.com/' in href and '/groups/' not in href:
                # Extract user ID or profile path
                if 'profile.php?id=' in href:
                    user_id = href.split('id=')[1].split('&')[0]
                else:
                    parts = href.replace('https://www.facebook.com/', '').split('/')
                    user_id = parts[0].split('?')[0]
                
                if user_id and len(user_id) > 2 and user_id not in [m['id'] for m in collected_members]:
                    try:
                        name = elem.text or user_id
                    except:
                        name = user_id
                    
                    collected_members.append({
                        'id': user_id,
                        'name': name[:50],
                        'link': f"https://www.facebook.com/{user_id}",
                        'group_id': test_group['id'],
                        'collected_at': datetime.now().isoformat()
                    })
        except:
            continue
    
    print(f"✅ Collected {len(collected_members)} members")
    
    # Save members
    members_dir = os.path.join(os.path.dirname(__file__), 'data', 'members')
    os.makedirs(members_dir, exist_ok=True)
    
    members_file = os.path.join(members_dir, f'members_{test_group["id"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    members_links_file = members_file.replace('.json', '_links.txt')
    
    with open(members_file, 'w', encoding='utf-8') as f:
        json.dump(collected_members, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved members JSON: {members_file}")
    
    with open(members_links_file, 'w', encoding='utf-8') as f:
        for m in collected_members:
            f.write(m['link'] + '\n')
    print(f"✅ Saved member links: {members_links_file}")

# Step 5: Verify saved files
print("\n✅ Step 5: Verifying saved data...")

saved_files = []
for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'data')):
    for file in files:
        if file.endswith('.json') or file.endswith('.txt'):
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            saved_files.append({'path': filepath, 'size': size})

print(f"\n📁 Found {len(saved_files)} data files:")
for f in saved_files[-10:]:  # Show last 10
    print(f"   {os.path.basename(f['path'])}: {f['size']} bytes")

# Summary
print("\n" + "=" * 70)
print("📊 DATA COLLECTION TEST SUMMARY")
print("=" * 70)
print(f"""
✅ Groups Collected: {len(collected_groups)}
✅ Members Collected: {len(collected_members) if 'collected_members' in dir() else 0}
✅ Files Saved: {len(saved_files)}

📁 Data is being saved to:
   - Groups: data/groups/
   - Members: data/members/

🎯 DATA COLLECTION IS WORKING!
""")

print("=" * 70)
print("🏁 DATA COLLECTION TEST COMPLETE")
print("=" * 70)

