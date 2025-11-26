# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building Facebook Marketing Tool demo version
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files
datas = [
    ('config.ini', '.'),
    ('fb_main.ui', '.'),
]

# Collect hidden imports
hiddenimports = [
    'PySide2',
    'PySide2.QtCore',
    'PySide2.QtGui',
    'PySide2.QtWidgets',
    'PySide2.QtUiTools',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtUiTools',
    'pyside2_compat',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.wait',
    'loguru',
    'configparser',
    'json',
    'threading',
    'multiprocessing',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'autoads',
    'autoads.air_spider',
    'autoads.item',
    'autoads.items',
    'autoads.items.group_item',
    'autoads.items.member_item',
    'autoads.items.post_item',
    'autoads.items.page_item',
    'autoads.items.ins_user_item',
    'autoads.config',
    'autoads.log',
    'autoads.tools',
    'autoads.action_control',
    'autoads.item_buffer',
    'autoads.parser_control',
    'autoads.request',
    'autoads.memory_db',
    'autoads.ads_api',
    'spider',
    'spider.fb_group_specified',
    'spider.fb_members_rapid',
    'spider.fb_posts',
    'spider.fb_pages',
    'spider.ins_followers',
    'spider.ins_following',
    'spider.ins_profile',
    'spider.ins_reels_comments',
    'spider_manager',
]

# Collect submodules
try:
    hiddenimports += collect_submodules('autoads')
    hiddenimports += collect_submodules('spider')
except:
    pass

a = Analysis(
    ['facebook.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FacebookMarketingTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

