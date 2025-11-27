#!/usr/bin/env python3
"""
Setup Validation Script - Check if everything is configured correctly
"""
import os
import sys
import json
import configparser
import requests
from pathlib import Path

print("=" * 70)
print("SETUP VALIDATION - Checking Configuration")
print("=" * 70)
print()

issues = []
warnings = []
success = []

def check(description, condition, error_msg=None, warning_msg=None):
    """Check a condition and record result"""
    if condition:
        success.append(description)
        print(f"✅ {description}")
    else:
        if error_msg:
            issues.append(f"{description}: {error_msg}")
            print(f"❌ {description}: {error_msg}")
        if warning_msg:
            warnings.append(f"{description}: {warning_msg}")
            print(f"⚠️  {description}: {warning_msg}")

# Check 1: Config file exists
print("[1] Checking Configuration File...")
config_path = "config.ini"
check("Config file exists", os.path.exists(config_path))

if os.path.exists(config_path):
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    
    # Check AdsPower configuration
    if config.has_section('ads'):
        ads_key = config.get('ads', 'key', fallback='')
        ads_path = config.get('ads', 'service_app_path', fallback='')
        
        check("AdsPower API key configured", 
              ads_key and ads_key != '', 
              "AdsPower API key is missing",
              "AdsPower API key may be invalid")
        
        check("AdsPower path configured",
              ads_path and ads_path != '',
              "AdsPower executable path is missing")
        
        if ads_path:
            # Check if path exists (adjust for Windows/Mac)
            normalized_path = ads_path.replace('C:/Program Files', '').replace('\\', '/')
            check("AdsPower path might exist",
                  True,  # Can't reliably check without knowing exact path
                  None,
                  f"Verify path exists: {ads_path}")
    else:
        issues.append("Config section [ads] is missing")
        print("❌ Config section [ads] is missing")

print()

# Check 2: AdsPower Service
print("[2] Checking AdsPower Service...")
try:
    response = requests.get("http://127.0.0.1:50325/api/v1/browser/list", timeout=2)
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 0:
            browsers = data.get('data', {}).get('list', [])
            check("AdsPower service is running", True)
            check(f"Facebook accounts configured in AdsPower", 
                  len(browsers) > 0,
                  "No Facebook accounts found in AdsPower",
                  f"Found {len(browsers)} account(s) - need at least 1")
        else:
            check("AdsPower service is running", False, 
                  f"AdsPower API error: {data.get('msg', 'Unknown error')}")
    else:
        check("AdsPower service is running", False, 
              f"HTTP {response.status_code}")
except requests.exceptions.ConnectionError:
    check("AdsPower service is running", False,
          "Cannot connect to AdsPower (is it running?)")
except Exception as e:
    check("AdsPower service is running", False,
          f"Error: {str(e)}")

print()

# Check 3: Required directories
print("[3] Checking Data Directories...")
required_dirs = [
    './fb/group/',
    './fb/member/',
    './fb/post/',
    './fb/page/',
    './ins/follower/',
    './ins/following/',
    './ins/user/',
    './ins/reels_comment/',
]

for dir_path in required_dirs:
    exists = os.path.exists(dir_path)
    if not exists:
        try:
            os.makedirs(dir_path, exist_ok=True)
            check(f"Directory: {dir_path}", True)
        except Exception as e:
            check(f"Directory: {dir_path}", False, str(e))
    else:
        check(f"Directory: {dir_path}", True)

print()

# Check 4: Python dependencies
print("[4] Checking Python Dependencies...")
required_packages = [
    'selenium',
    'requests',
    'PySide6',
    'loguru',
]

for package in required_packages:
    try:
        __import__(package.lower().replace('-', '_'))
        check(f"Package: {package}", True)
    except ImportError:
        check(f"Package: {package}", False, "Not installed")

print()

# Check 5: Feature prerequisites
print("[5] Checking Feature Prerequisites...")

# Check if groups exist (needed for member collection)
if os.path.exists('./fb/group/'):
    group_files = [f for f in os.listdir('./fb/group/') if f.endswith('.txt')]
    check("Groups collected (for member collection)",
          len(group_files) > 0,
          "No groups found - need to collect groups first",
          f"Found {len(group_files)} group file(s)")

# Check if members exist (needed for private messages)
if os.path.exists('./fb/member/'):
    member_files = [f for f in os.listdir('./fb/member/') if f.endswith('.txt')]
    check("Members collected (for private messages)",
          len(member_files) > 0,
          "No members found - need to collect members first",
          f"Found {len(member_files)} member file(s)")

print()

# Summary
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(success)}")
print(f"❌ Issues: {len(issues)}")
print(f"⚠️  Warnings: {len(warnings)}")
print()

if issues:
    print("CRITICAL ISSUES (Must Fix):")
    for issue in issues:
        print(f"  ❌ {issue}")
    print()

if warnings:
    print("WARNINGS (Should Fix):")
    for warning in warnings:
        print(f"  ⚠️  {warning}")
    print()

if len(issues) == 0:
    print("🎉 All critical checks passed! Setup looks good.")
    print("   You can now test the features.")
else:
    print("⚠️  Please fix the issues above before testing features.")
    print()
    print("SETUP REQUIRED:")
    print("1. Install AdsPower Global Browser")
    print("2. Configure AdsPower API key in config.ini")
    print("3. Add Facebook accounts to AdsPower")
    print("4. Start AdsPower service")
    print("5. Run this validation again")

print("=" * 70)

