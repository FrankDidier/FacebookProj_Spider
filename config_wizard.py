# -*- coding: utf-8 -*-
"""
Configuration Wizard - Setup and validation page
"""
# Import compatibility layer for PySide6
import pyside2_compat
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QLineEdit, QTextEdit, QFileDialog,
                                QMessageBox, QGroupBox, QProgressBar, QFrame,
                                QScrollArea)
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
        
        # Check AdsPower service
        self.status_update.emit("检查 AdsPower 服务...", "info")
        try:
            response = requests.get("http://127.0.0.1:50325/api/v1/browser/list", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    browsers = data.get('data', {}).get('list', [])
                    if len(browsers) > 0:
                        results['ads_power'] = {'status': 'success', 'message': f'AdsPower 运行正常，找到 {len(browsers)} 个账户'}
                        results['accounts'] = {'status': 'success', 'message': f'{len(browsers)} 个 Facebook 账户已配置'}
                    else:
                        results['ads_power'] = {'status': 'success', 'message': 'AdsPower 运行正常'}
                        results['accounts'] = {'status': 'warning', 'message': '未找到 Facebook 账户，请在 AdsPower 中添加账户'}
                else:
                    results['ads_power'] = {'status': 'error', 'message': f'AdsPower API 错误: {data.get("msg", "未知错误")}'}
            else:
                results['ads_power'] = {'status': 'error', 'message': f'无法连接到 AdsPower (HTTP {response.status_code})'}
        except requests.exceptions.ConnectionError:
            results['ads_power'] = {'status': 'error', 'message': 'AdsPower 服务未运行，请启动 AdsPower Global Browser'}
        except Exception as e:
            results['ads_power'] = {'status': 'error', 'message': f'检查失败: {str(e)}'}
        
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
        
        # AdsPower Path
        path_layout = QVBoxLayout()
        path_row = QHBoxLayout()
        path_label = QLabel("AdsPower 路径:")
        path_label.setMinimumWidth(120)
        
        # Info box explaining why path is needed
        path_info = QLabel("📌 <b>为什么需要:</b> 应用程序需要通过此路径启动和管理浏览器实例，控制自动化操作。")
        path_info.setWordWrap(True)
        path_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择 AdsPower Global Browser 安装路径")
        self.path_edit.setToolTip("这是 AdsPower Global Browser 的安装路径。\n\n应用程序使用此路径来:\n• 启动浏览器实例\n• 管理多个账户\n• 控制浏览器自动化\n\n通常位于:\nWindows: C:/Program Files/AdsPower Global/AdsPower Global.exe\nmacOS: /Applications/AdsPower Global.app")
        
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
        api_info = QLabel("📌 <b>为什么需要:</b> API 密钥用于与 AdsPower 服务通信，获取账户列表、启动浏览器等操作。没有 API 密钥，应用程序无法与 AdsPower 通信。")
        api_info.setWordWrap(True)
        api_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 5px;")
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入 AdsPower API 密钥")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setToolTip("这是 AdsPower 的 API 密钥，用于:\n• 获取账户列表\n• 启动和管理浏览器实例\n• 控制浏览器自动化\n• 访问 AdsPower 服务\n\n获取方法:\nAdsPower → 设置 → API → 复制密钥\n\n⚠️ 重要: 请妥善保管此密钥，不要泄露给他人")
        
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
            ('ads_power', 'AdsPower 服务', '检查 AdsPower 服务是否运行。服务必须运行才能启动浏览器和控制自动化。'),
            ('api_key', 'API 密钥', '验证 API 密钥是否正确配置。API 密钥用于与 AdsPower 服务通信，是必需的。'),
            ('accounts', 'Facebook 账户', '检查 AdsPower 中是否有可用的 Facebook 账户。至少需要一个账户才能执行采集任务。'),
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
        
        <b>1. AdsPower 路径:</b><br>
        • <b>作用:</b> 应用程序需要知道 AdsPower 的安装位置<br>
        • <b>用途:</b> 启动浏览器实例、管理多个账户、控制自动化<br>
        • <b>如何获取:</b> 点击"浏览"按钮选择 AdsPower Global.exe 文件<br>
        • <b>常见位置:</b> C:/Program Files/AdsPower Global/ (Windows)<br><br>
        
        <b>2. API 密钥:</b><br>
        • <b>作用:</b> 这是应用程序与 AdsPower 服务通信的"密码"<br>
        • <b>用途:</b> 获取账户列表、启动浏览器、控制自动化操作<br>
        • <b>如何获取:</b> AdsPower → 设置 → API → 复制密钥<br>
        • <b>重要性:</b> ⚠️ 没有 API 密钥，应用程序无法与 AdsPower 通信<br><br>
        
        <b>3. 账户数量:</b><br>
        • <b>作用:</b> 指定同时使用多少个 Facebook 账户<br>
        • <b>用途:</b> 控制并发任务、分配采集任务、提高效率<br>
        • <b>建议:</b> 根据您的账户数量和任务需求设置（通常 3-5 个）<br><br>
        
        <b>🚀 快速设置步骤:</b><br>
        1. 安装并启动 AdsPower Global Browser<br>
        2. 获取 API 密钥（设置 → API）<br>
        3. 在 AdsPower 中添加 Facebook 账户<br>
        4. 配置上方路径和 API 密钥<br>
        5. 点击"保存配置"并"重新验证"<br>
        6. 所有验证项显示 ✓ 后即可使用功能<br><br>
        
        <b>⚠️ 常见问题:</b><br>
        • "AdsPower 服务未运行" → 请启动 AdsPower Global Browser<br>
        • "API 密钥未配置" → 请在 AdsPower 中获取并输入密钥<br>
        • "未找到账户" → 请在 AdsPower 中添加 Facebook 账户
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
    
    def browse_ads_power_path(self):
        """Browse for AdsPower executable"""
        if os.name == 'nt':  # Windows
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 AdsPower Global Browser", 
                "C:/Program Files/AdsPower Global/",
                "Executable (*.exe);;All Files (*)"
            )
        else:  # macOS/Linux
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 AdsPower Global Browser",
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
            
            # Load AdsPower path
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
            
            # Save AdsPower path
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

