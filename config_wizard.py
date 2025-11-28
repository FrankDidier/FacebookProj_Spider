# -*- coding: utf-8 -*-
"""
Configuration Wizard - Setup and validation page
"""
# Import compatibility layer for PySide6
import pyside2_compat
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QLineEdit, QTextEdit, QFileDialog,
                                QMessageBox, QGroupBox, QProgressBar, QFrame,
                                QScrollArea, QComboBox)
from PySide2.QtCore import Qt, QThread, Signal
from PySide2.QtGui import QFont, QIcon
import os
import requests
import configparser
from autoads import ads_api
from autoads.config import config
from autoads import tools
from loguru import logger as log


class ValidationThread(QThread):
    """Thread for running validation checks"""
    status_update = Signal(str, str)  # message, status_type (success/error/warning)
    finished = Signal(dict)  # validation results
    
    def __init__(self):
        super().__init__()
        self.results = {}
    
    def run(self):
        """Run all validation checks"""
        results = {
            'ads_power': {'status': 'unknown', 'message': ''},
            'api_key': {'status': 'unknown', 'message': ''},
            'accounts': {'status': 'unknown', 'message': ''},
            'directories': {'status': 'unknown', 'message': ''},
            'dependencies': {'status': 'unknown', 'message': ''},
        }
        
        # Check browser service (AdsPower or BitBrowser)
        browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
        browser_name = 'AdsPower' if browser_type == 'adspower' else 'BitBrowser' if browser_type == 'bitbrowser' else '指纹浏览器'
        
        self.status_update.emit(f"检查 {browser_name} 服务...", "info")
        
        # Try AdsPower first (port 50325)
        ads_power_ok = False
        try:
            response = requests.get("http://127.0.0.1:50325/api/v1/browser/list", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    browsers = data.get('data', {}).get('list', [])
                    if len(browsers) > 0:
                        results['ads_power'] = {'status': 'success', 'message': f'AdsPower 运行正常，找到 {len(browsers)} 个账户'}
                        results['accounts'] = {'status': 'success', 'message': f'{len(browsers)} 个 Facebook 账户已配置'}
                    else:
                        results['ads_power'] = {'status': 'success', 'message': 'AdsPower 运行正常'}
                        results['accounts'] = {'status': 'warning', 'message': '未找到 Facebook 账户，请添加账户'}
                    ads_power_ok = True
        except:
            pass
        
        # Try BitBrowser (port 54345 or custom)
        if not ads_power_ok:
            bitbrowser_port = getattr(config, 'bitbrowser_port', '54345') if hasattr(config, 'bitbrowser_port') else '54345'
            bitbrowser_api_url = getattr(config, 'bitbrowser_api_url', f'http://127.0.0.1:{bitbrowser_port}') if hasattr(config, 'bitbrowser_api_url') else f'http://127.0.0.1:{bitbrowser_port}'
            
            try:
                # BitBrowser API endpoint (may vary, try common ones)
                for endpoint in ['/api/v1/browser/list', '/api/browser/list', '/browser/list']:
                    try:
                        response = requests.get(f"{bitbrowser_api_url}{endpoint}", timeout=2)
                        if response.status_code == 200:
                            data = response.json()
                            browsers = data.get('data', {}).get('list', []) if isinstance(data.get('data'), dict) else data.get('list', [])
                            if isinstance(browsers, list) and len(browsers) > 0:
                                results['ads_power'] = {'status': 'success', 'message': f'BitBrowser 运行正常，找到 {len(browsers)} 个账户'}
                                results['accounts'] = {'status': 'success', 'message': f'{len(browsers)} 个 Facebook 账户已配置'}
                                ads_power_ok = True
                                break
                    except:
                        continue
                
                if not ads_power_ok:
                    # Just check if service is reachable
                    try:
                        response = requests.get(bitbrowser_api_url, timeout=2)
                        results['ads_power'] = {'status': 'success', 'message': f'BitBrowser 服务可访问 (API 密钥配置后即可使用)'}
                        results['accounts'] = {'status': 'warning', 'message': '请配置 API 密钥并添加账户'}
                        ads_power_ok = True
                    except:
                        pass
            except:
                pass
        
        # If neither works, make it a warning instead of error
        if not ads_power_ok:
            results['ads_power'] = {'status': 'warning', 'message': f'{browser_name} 服务未检测到，但只要有 API 密钥和浏览器打开即可使用'}
            results['accounts'] = {'status': 'warning', 'message': '请确保浏览器已打开并配置 API 密钥'}
        
        # Check API key
        self.status_update.emit("检查 API 密钥...", "info")
        api_key = config.ads_key if hasattr(config, 'ads_key') else ''
        if api_key and api_key.strip():
            results['api_key'] = {'status': 'success', 'message': 'API 密钥已配置'}
        else:
            results['api_key'] = {'status': 'error', 'message': 'API 密钥未配置'}
        
        # Check directories
        self.status_update.emit("检查数据目录...", "info")
        required_dirs = ['./fb/group/', './fb/member/', './fb/post/', './fb/page/',
                        './ins/follower/', './ins/following/', './ins/user/', './ins/reels_comment/']
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            results['directories'] = {'status': 'warning', 'message': f'缺少 {len(missing_dirs)} 个目录，将自动创建'}
        else:
            results['directories'] = {'status': 'success', 'message': '所有数据目录已就绪'}
        
        # Check dependencies
        self.status_update.emit("检查依赖包...", "info")
        missing_packages = []
        for package in ['selenium', 'requests', 'loguru']:
            try:
                __import__(package.lower().replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            results['dependencies'] = {'status': 'error', 'message': f'缺少依赖包: {", ".join(missing_packages)}'}
        else:
            results['dependencies'] = {'status': 'success', 'message': '所有依赖包已安装'}
        
        self.finished.emit(results)


class ConfigWizardPage(QWidget):
    """Configuration wizard page with validation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.validation_thread = None
        self.setup_ui()
        self.load_config()
        self.run_validation()
    
    def setup_ui(self):
        """Setup the UI"""
        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ 配置向导 - 系统设置与验证")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Configuration Section
        config_group = QGroupBox("📋 基本配置")
        config_layout = QVBoxLayout()
        
        # Browser Type Selection
        browser_type_layout = QVBoxLayout()
        browser_type_row = QHBoxLayout()
        browser_type_label = QLabel("浏览器类型:")
        browser_type_label.setMinimumWidth(120)
        
        browser_type_info = QLabel("📌 <b>说明:</b> 选择您使用的指纹浏览器类型。支持 AdsPower、BitBrowser 或其他兼容的指纹浏览器。")
        browser_type_info.setWordWrap(True)
        browser_type_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.browser_type_combo = QComboBox()
        self.browser_type_combo.addItems(["AdsPower", "BitBrowser", "其他指纹浏览器"])
        self.browser_type_combo.currentTextChanged.connect(self.on_browser_type_changed)
        
        browser_type_row.addWidget(browser_type_label)
        browser_type_row.addWidget(self.browser_type_combo, 1)
        browser_type_layout.addWidget(browser_type_info)
        browser_type_layout.addLayout(browser_type_row)
        config_layout.addLayout(browser_type_layout)
        
        # Browser Path (works for any browser)
        path_layout = QVBoxLayout()
        path_row = QHBoxLayout()
        path_label = QLabel("浏览器路径:")
        path_label.setMinimumWidth(120)
        
        # Info box explaining why path is needed
        path_info = QLabel("📌 <b>为什么需要:</b> 应用程序可能需要通过此路径启动浏览器实例（可选）。如果浏览器已打开且 API 密钥已配置，通常不需要设置此路径。")
        path_info.setWordWrap(True)
        path_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择指纹浏览器安装路径（可选）")
        self.path_edit.setToolTip("这是指纹浏览器的安装路径（可选）。\n\n应用程序使用此路径来:\n• 启动浏览器实例\n• 管理多个账户\n• 控制浏览器自动化\n\n通常位于:\nAdsPower: C:/Program Files/AdsPower Global/AdsPower Global.exe\nBitBrowser: C:/Program Files/BitBrowser/BitBrowser.exe\n\n⚠️ 注意: 如果浏览器已打开且 API 密钥已配置，此路径可选")
        
        self.path_browse_btn = QPushButton("浏览...")
        self.path_browse_btn.clicked.connect(self.browse_ads_power_path)
        
        path_row.addWidget(path_label)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.path_browse_btn)
        path_layout.addWidget(path_info)
        path_layout.addLayout(path_row)
        config_layout.addLayout(path_layout)
        
        # API Key
        api_layout = QVBoxLayout()
        api_row = QHBoxLayout()
        api_label = QLabel("API 密钥:")
        api_label.setMinimumWidth(120)
        
        # Info box explaining why API key is needed
        api_info = QLabel("📌 <b>为什么需要:</b> API 密钥用于与指纹浏览器服务通信，获取账户列表、启动浏览器等操作。没有 API 密钥，应用程序无法与浏览器通信。")
        api_info.setWordWrap(True)
        api_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入指纹浏览器 API 密钥")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setToolTip("这是指纹浏览器的 API 密钥，用于:\n• 获取账户列表\n• 启动和管理浏览器实例\n• 控制浏览器自动化\n• 访问浏览器服务\n\n获取方法:\nAdsPower: 设置 → API → 复制密钥\nBitBrowser: 设置 → API → 复制密钥\n其他浏览器: 查看浏览器文档\n\n⚠️ 重要: 请妥善保管此密钥，不要泄露给他人")
        
        self.api_key_show_btn = QPushButton("显示")
        self.api_key_show_btn.clicked.connect(self.toggle_api_key_visibility)
        
        api_row.addWidget(api_label)
        api_row.addWidget(self.api_key_edit, 1)
        api_row.addWidget(self.api_key_show_btn)
        api_layout.addWidget(api_info)
        api_layout.addLayout(api_row)
        config_layout.addLayout(api_layout)
        
        # Account Numbers
        account_layout = QVBoxLayout()
        account_row = QHBoxLayout()
        account_label = QLabel("账户数量:")
        account_label.setMinimumWidth(120)
        
        # Info box explaining why account count is needed
        account_info = QLabel("📌 <b>为什么需要:</b> 指定同时使用的 Facebook 账户数量，用于并发采集和控制任务分配，提高效率并避免单个账户过度使用。")
        account_info.setWordWrap(True)
        account_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.account_count_edit = QLineEdit()
        self.account_count_edit.setPlaceholderText("同时使用的账户数量")
        self.account_count_edit.setToolTip("指定同时使用的 Facebook 账户数量。\n\n用途:\n• 控制并发任务数量\n• 分配采集任务到不同账户\n• 避免单个账户过度使用\n• 提高采集效率\n\n建议:\n根据您的 AdsPower 账户数量和任务需求设置。\n例如: 如果您有 5 个账户，可以设置为 3-5")
        
        account_row.addWidget(account_label)
        account_row.addWidget(self.account_count_edit, 1)
        account_layout.addWidget(account_info)
        account_layout.addLayout(account_row)
        config_layout.addLayout(account_layout)
        
        # Save button
        save_btn = QPushButton("💾 保存配置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e98ea;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a7bc8;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        config_layout.addWidget(save_btn)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Validation Section
        validation_group = QGroupBox("✅ 系统验证")
        validation_layout = QVBoxLayout()
        
        # Info about validation
        validation_info = QLabel("以下验证项确保系统可以正常工作。所有项显示 ✓ 后即可使用功能。")
        validation_info.setWordWrap(True)
        validation_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #e8f4f8; border-radius: 4px; margin-bottom: 10px;")
        validation_layout.addWidget(validation_info)
        
        # Validation status labels with descriptions
        self.status_labels = {}
        status_items = [
            ('ads_power', '浏览器服务', '检查指纹浏览器服务是否运行。如果浏览器已打开且 API 密钥已配置，通常可以正常使用。'),
            ('api_key', 'API 密钥', '验证 API 密钥是否正确配置。API 密钥用于与浏览器服务通信，是必需的。'),
            ('accounts', 'Facebook 账户', '检查浏览器中是否有可用的 Facebook 账户。至少需要一个账户才能执行采集任务。'),
            ('directories', '数据目录', '检查数据存储目录是否存在。用于保存采集的数据，如群组信息、成员信息等。'),
            ('dependencies', '依赖包', '检查必需的 Python 包是否已安装。缺少依赖包会导致功能无法正常使用。'),
        ]
        
        for key, label_text, description in status_items:
            status_container = QVBoxLayout()
            status_row = QHBoxLayout()
            label = QLabel(label_text + ":")
            label.setMinimumWidth(120)
            status_label = QLabel("检查中...")
            status_label.setWordWrap(True)
            self.status_labels[key] = status_label
            status_row.addWidget(label)
            status_row.addWidget(status_label, 1)
            
            # Add description
            desc_label = QLabel(f"   <small>{description}</small>")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #888; font-size: 10px; margin-left: 10px; margin-top: 2px;")
            
            status_container.addLayout(status_row)
            status_container.addWidget(desc_label)
            validation_layout.addLayout(status_container)
        
        # Validation progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        validation_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_message = QLabel("")
        self.status_message.setWordWrap(True)
        self.status_message.setStyleSheet("color: #666; font-style: italic;")
        validation_layout.addWidget(self.status_message)
        
        # Validate button
        validate_btn = QPushButton("🔄 重新验证")
        validate_btn.clicked.connect(self.run_validation)
        validation_layout.addWidget(validate_btn)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        # Help Section
        help_group = QGroupBox("📖 设置指南")
        help_layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(150)
        help_text.setHtml("""
        <b>📋 配置说明 - 为什么需要这些设置？</b><br><br>
        
        <b>1. 浏览器类型:</b><br>
        • <b>作用:</b> 选择您使用的指纹浏览器类型<br>
        • <b>支持:</b> AdsPower、BitBrowser（比特浏览器）或其他兼容的指纹浏览器<br>
        • <b>说明:</b> 应用程序支持多种指纹浏览器，不强制使用 AdsPower<br>
        • <b>如何选择:</b> 根据您实际使用的浏览器选择对应类型<br><br>
        
        <b>2. 浏览器路径:</b><br>
        • <b>作用:</b> 应用程序可能需要知道浏览器的安装位置（<b>可选</b>）<br>
        • <b>用途:</b> 启动浏览器实例、管理多个账户、控制自动化<br>
        • <b>如何获取:</b> 点击"浏览"按钮选择浏览器可执行文件<br>
        • <b>常见位置:</b><br>
          - AdsPower: C:/Program Files/AdsPower Global/AdsPower Global.exe<br>
          - BitBrowser: C:/Program Files/BitBrowser/BitBrowser.exe<br>
        • <b>⚠️ 注意:</b> 如果浏览器已打开且 API 密钥已配置，此路径通常不需要设置<br><br>
        
        <b>3. API 密钥:</b><br>
        • <b>作用:</b> 这是应用程序与指纹浏览器服务通信的"密码"<br>
        • <b>用途:</b> 获取账户列表、启动浏览器、控制自动化操作<br>
        • <b>如何获取:</b><br>
          - <b>AdsPower:</b> 设置 → API → 复制密钥<br>
          - <b>BitBrowser:</b> 设置 → API → 复制密钥<br>
          - <b>其他浏览器:</b> 查看浏览器文档获取 API 密钥<br>
        • <b>重要性:</b> ⚠️ 没有 API 密钥，应用程序无法与浏览器通信（<b>必需</b>）<br><br>
        
        <b>4. 账户数量:</b><br>
        • <b>作用:</b> 指定同时使用多少个 Facebook 账户<br>
        • <b>用途:</b> 控制并发任务、分配采集任务、提高效率<br>
        • <b>建议:</b> 根据您的账户数量和任务需求设置（通常 3-5 个）<br><br>
        
        <b>🚀 快速设置步骤:</b><br>
        1. <b>选择浏览器类型</b>（AdsPower/BitBrowser/其他）<br>
        2. <b>打开您的指纹浏览器</b>（确保浏览器正在运行）<br>
        3. <b>获取 API 密钥</b>（浏览器设置 → API → 复制密钥）<br>
        4. <b>在浏览器中添加 Facebook 账户</b>（至少添加一个账户）<br>
        5. <b>配置上方 API 密钥</b>（路径可选，如果浏览器已打开）<br>
        6. <b>点击"保存配置"并"重新验证"</b><br>
        7. <b>开始使用功能</b>（即使验证显示警告，只要 API 密钥配置即可使用）<br><br>
        
        <b>💡 重要提示:</b><br>
        • <b>API 密钥是必需的</b>，没有它无法使用功能<br>
        • <b>浏览器路径是可选的</b>，如果浏览器已打开通常不需要<br>
        • <b>验证显示警告是正常的</b>，只要 API 密钥已配置即可使用<br>
        • <b>支持 BitBrowser</b>，选择"BitBrowser"类型并输入对应 API 密钥即可<br><br>
        
        <b>⚠️ 常见问题:</b><br>
        • <b>"浏览器服务未检测到"</b> → 这是正常的！只要浏览器已打开且 API 密钥已配置即可使用<br>
        • <b>"API 密钥未配置"</b> → 请在浏览器中获取并输入 API 密钥（设置 → API）<br>
        • <b>"未找到账户"</b> → 请在浏览器中添加 Facebook 账户<br>
        • <b>"使用 BitBrowser"</b> → 选择"BitBrowser"类型，输入 BitBrowser API 密钥即可<br>
        • <b>"验证失败但想使用"</b> → 只要 API 密钥配置正确，功能仍然可以使用
        """)
        help_layout.addWidget(help_text)
        
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_edit.echoMode() == QLineEdit.Password:
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
            self.api_key_show_btn.setText("隐藏")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
            self.api_key_show_btn.setText("显示")
    
    def on_browser_type_changed(self, text):
        """Update UI when browser type changes"""
        # Update placeholder text based on browser type
        if text == "AdsPower":
            self.path_edit.setPlaceholderText("选择 AdsPower Global Browser 安装路径（可选）")
        elif text == "BitBrowser":
            self.path_edit.setPlaceholderText("选择 BitBrowser 安装路径（可选）")
        else:
            self.path_edit.setPlaceholderText("选择指纹浏览器安装路径（可选）")
    
    def browse_ads_power_path(self):
        """Browse for browser executable"""
        browser_type = self.browser_type_combo.currentText() if hasattr(self, 'browser_type_combo') else "AdsPower"
        if os.name == 'nt':  # Windows
            if browser_type == "AdsPower":
                default_path = "C:/Program Files/AdsPower Global/"
                title = "选择 AdsPower Global Browser"
            elif browser_type == "BitBrowser":
                default_path = "C:/Program Files/BitBrowser/"
                title = "选择 BitBrowser"
            else:
                default_path = "C:/Program Files/"
                title = "选择指纹浏览器"
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, title, 
                default_path,
                "Executable (*.exe);;All Files (*)"
            )
        else:  # macOS/Linux
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择指纹浏览器",
                "/Applications/",
                "All Files (*)"
            )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def load_config(self):
        """Load current configuration"""
        try:
            # Ensure config is initialized
            if not hasattr(config, 'name') or not config.name:
                config.name = 'config.ini'
            
            # Load browser type
            browser_type = config.get_option('ads', 'browser_type') if config.config.has_option('ads', 'browser_type') else 'adspower'
            browser_type_map = {
                'adspower': 'AdsPower',
                'bitbrowser': 'BitBrowser',
                'other': '其他指纹浏览器'
            }
            browser_type_text = browser_type_map.get(browser_type, 'AdsPower')
            index = self.browser_type_combo.findText(browser_type_text)
            if index >= 0:
                self.browser_type_combo.setCurrentIndex(index)
            
            # Load browser path
            try:
                ads_path = ads_api.get_service_exe()
                if ads_path:
                    self.path_edit.setText(ads_path)
            except:
                pass
            
            # Load API key
            try:
                if hasattr(config, 'ads_key') and config.ads_key:
                    self.api_key_edit.setText(config.ads_key)
            except:
                pass
            
            # Load account count
            try:
                if hasattr(config, 'account_nums'):
                    self.account_count_edit.setText(str(config.account_nums))
            except:
                pass
        except Exception as e:
            log.error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to config.ini"""
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read('config.ini', encoding='utf-8')
            
            # Save browser type
            try:
                if hasattr(self, 'browser_type_combo') and self.browser_type_combo:
                    browser_type_text = self.browser_type_combo.currentText()
                    browser_type_map = {
                        'AdsPower': 'adspower',
                        'BitBrowser': 'bitbrowser',
                        '其他指纹浏览器': 'other'
                    }
                    browser_type = browser_type_map.get(browser_type_text, 'adspower')
                    config.set_option('ads', 'browser_type', browser_type)
            except Exception as e:
                log.debug(f"Could not save browser type: {e}")
                pass
            
            # Save browser path
            path = self.path_edit.text().strip()
            if path:
                if not config_parser.has_section('ads'):
                    config_parser.add_section('ads')
                config_parser.set('ads', 'service_app_path', path)
            
            # Save API key
            api_key = self.api_key_edit.text().strip()
            if api_key:
                if not config_parser.has_section('ads'):
                    config_parser.add_section('ads')
                config_parser.set('ads', 'key', api_key)
            
            # Save account count
            account_count = self.account_count_edit.text().strip()
            if account_count:
                if not config_parser.has_section('main'):
                    config_parser.add_section('main')
                config_parser.set('main', 'account_nums', account_count)
            
            # Write to file
            with open('config.ini', 'w', encoding='utf-8') as f:
                config_parser.write(f)
            
            # Reload config
            config.name = 'config.ini'
            
            QMessageBox.information(self, "成功", "配置已保存！\n请点击「重新验证」检查设置。")
            
            # Run validation again
            self.run_validation()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
            log.error(f"Error saving config: {e}")
    
    def run_validation(self):
        """Run validation checks"""
        if self.validation_thread and self.validation_thread.isRunning():
            return
        
        # Reset status
        for label in self.status_labels.values():
            label.setText("检查中...")
            label.setStyleSheet("color: #666;")
        
        self.progress_bar.setVisible(True)
        self.status_message.setText("正在验证系统配置...")
        self.status_message.setStyleSheet("color: #666; font-style: italic;")
        
        # Start validation thread
        self.validation_thread = ValidationThread()
        self.validation_thread.status_update.connect(self.on_status_update)
        self.validation_thread.finished.connect(self.on_validation_finished)
        self.validation_thread.start()
        
        # Auto-run validation on page show if not already validated
        if not hasattr(self, '_validated_once'):
            self._validated_once = True
    
    def on_status_update(self, message, status_type):
        """Handle status update from validation thread"""
        self.status_message.setText(message)
    
    def on_validation_finished(self, results):
        """Handle validation finished"""
        self.progress_bar.setVisible(False)
        
        all_success = True
        has_warnings = False
        
        for key, result in results.items():
            status = result['status']
            message = result['message']
            label = self.status_labels.get(key)
            
            if label:
                if status == 'success':
                    label.setText(f"✓ {message}")
                    label.setStyleSheet("color: #28a745; font-weight: bold;")
                elif status == 'warning':
                    label.setText(f"⚠ {message}")
                    label.setStyleSheet("color: #ffc107; font-weight: bold;")
                    has_warnings = True
                elif status == 'error':
                    label.setText(f"✗ {message}")
                    label.setStyleSheet("color: #dc3545; font-weight: bold;")
                    all_success = False
        
        if all_success and not has_warnings:
            self.status_message.setText("✓ 所有检查通过！系统已准备就绪，可以开始使用功能。")
            self.status_message.setStyleSheet("color: #28a745; font-weight: bold;")
        elif all_success:
            self.status_message.setText("✓ 基本检查通过，但有一些警告。建议修复警告项以获得最佳体验。")
            self.status_message.setStyleSheet("color: #ffc107; font-weight: bold;")
        else:
            error_count = sum(1 for r in results.values() if r.get('status') == 'error')
            self.status_message.setText(f"✗ 发现 {error_count} 个问题，请根据上述提示修复后重新验证。修复后点击「重新验证」按钮。")
            self.status_message.setStyleSheet("color: #dc3545; font-weight: bold;")

