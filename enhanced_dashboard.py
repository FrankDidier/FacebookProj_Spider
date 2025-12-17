# -*- coding: utf-8 -*-
"""
Enhanced Dashboard - Matches reference app UI layout
Features:
- Account Management Panel (账号管理)
- User Management Panel (用户管理)
- Statistics Dashboard
- Thread Controls
- Network Settings
- Filter Settings (Country, Gender, Age, AI)
"""

import pyside2_compat
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os
import json
from datetime import datetime

# Import actual functionality modules
try:
    from autoads.account_manager import AccountManager
    from autoads.cloud_dedup import CloudDeduplication
    from autoads.config import config
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False
    print("Warning: Backend modules not available")


class StatsWidget(QFrame):
    """Statistics display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("""
            QFrame { 
                background: #f0f5ff; 
                border: 1px solid #5e98ea; 
                border-radius: 5px; 
                padding: 5px;
            }
            QLabel { font-size: 11px; }
        """)
        
        layout = QGridLayout(self)
        layout.setSpacing(5)
        
        # Row 1
        self.add_stat(layout, 0, 0, "提取", "0")
        self.add_stat(layout, 0, 1, "完成", "0")
        self.add_stat(layout, 0, 2, "线程容量", "1")
        
        # Row 2
        self.add_stat(layout, 1, 0, "代理剩余", "0")
        self.add_stat(layout, 1, 1, "时速", "0")
        self.add_stat(layout, 1, 2, "派发任务", "0")
        
        # Row 3
        self.add_stat(layout, 2, 0, "状态", "待机")
        self.add_stat(layout, 2, 1, "剩余", "0")
        self.add_stat(layout, 2, 2, "执行线程", "0")
        
        # Row 4
        self.add_stat(layout, 3, 0, "总提", "0")
        self.add_stat(layout, 3, 1, "运行时间", "00:00:00")
        self.add_stat(layout, 3, 2, "等待线程", "0")
        
    def add_stat(self, layout, row, col, label_text, value_text):
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(2, 2, 2, 2)
        h_layout.setSpacing(3)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #666; font-weight: bold;")
        
        value = QLabel(value_text)
        value.setObjectName(f"stat_{label_text}")
        value.setStyleSheet("color: #5e98ea; font-weight: bold;")
        
        h_layout.addWidget(label)
        h_layout.addWidget(value)
        h_layout.addStretch()
        
        layout.addWidget(container, row, col)
        
    def update_stat(self, name, value):
        label = self.findChild(QLabel, f"stat_{name}")
        if label:
            label.setText(str(value))


class AccountManagementPanel(QGroupBox):
    """Account Management Panel (账号管理)"""
    
    # Signals for parent to connect to
    account_imported = Signal(int)
    account_cleared = Signal()
    account_exported = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__("账号管理", parent)
        self.account_manager = AccountManager() if HAS_BACKEND else None
        self.setup_ui()
        self.connect_signals()
        self.load_accounts()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #5e98ea;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #5e98ea;
            }
            QPushButton {
                background: #5e98ea;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4a88da;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        
        self.btn_import = QPushButton("导入账号")
        self.btn_clear = QPushButton("清空账号")
        self.btn_export = QPushButton("导出未使用")
        self.chk_skip_used = QCheckBox("跳过已使用")
        
        self.btn_clear.setStyleSheet("background: #e74c3c;")
        self.btn_export.setStyleSheet("background: #27ae60;")
        
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.chk_skip_used)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "序号", "账号", "密码", "2FA", "cookie", "代理", "统计", "状态"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMaximumHeight(150)
        
        layout.addWidget(self.table)
        
    def connect_signals(self):
        """Connect button signals to actual functionality"""
        self.btn_import.clicked.connect(self.on_import_accounts)
        self.btn_clear.clicked.connect(self.on_clear_accounts)
        self.btn_export.clicked.connect(self.on_export_accounts)
        
    def load_accounts(self):
        """Load accounts from account manager"""
        if not self.account_manager:
            return
        try:
            accounts = self.account_manager.get_all_accounts()
            self.table.setRowCount(0)
            for acc in accounts:
                self.add_account(acc)
        except Exception as e:
            print(f"Error loading accounts: {e}")
            
    def on_import_accounts(self):
        """Import accounts from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择账号文件", "", "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            try:
                if self.account_manager:
                    result = self.account_manager.import_accounts(file_path)
                    self.load_accounts()
                    if result.get('success'):
                        QMessageBox.information(self, "导入成功", result.get('message', f"成功导入 {result.get('count', 0)} 个账号"))
                        self.account_imported.emit(result.get('count', 0))
                    else:
                        QMessageBox.warning(self, "导入警告", result.get('message', '导入失败'))
                else:
                    # Fallback: just read the file and display
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines):
                        parts = line.strip().split('\t') if '\t' in line else line.strip().split(',')
                        if parts:
                            self.add_account({
                                'username': parts[0] if len(parts) > 0 else '',
                                'password': parts[1] if len(parts) > 1 else '',
                                '2fa': parts[2] if len(parts) > 2 else '',
                                'cookie': parts[3] if len(parts) > 3 else '',
                                'proxy': parts[4] if len(parts) > 4 else '',
                                'stats': 0,
                                'status': '待机'
                            })
                    QMessageBox.information(self, "导入成功", f"成功导入 {len(lines)} 个账号")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入失败: {str(e)}")
                
    def on_clear_accounts(self):
        """Clear all accounts"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有账号吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.account_manager:
                self.account_manager.clear_all()
            self.table.setRowCount(0)
            self.account_cleared.emit()
            QMessageBox.information(self, "清空成功", "已清空所有账号")
            
    def on_export_accounts(self):
        """Export unused accounts"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出账号", "unused_accounts.txt", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                if self.account_manager:
                    self.account_manager.export_unused(file_path)
                else:
                    # Fallback: export from table
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for row in range(self.table.rowCount()):
                            status = self.table.item(row, 7).text() if self.table.item(row, 7) else ''
                            if '使用' not in status:
                                username = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
                                password = self.table.item(row, 2).text() if self.table.item(row, 2) else ''
                                f.write(f"{username}\t{password}\n")
                QMessageBox.information(self, "导出成功", f"已导出到 {file_path}")
                self.account_exported.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出失败: {str(e)}")
        
    def add_account(self, account_data):
        """Add account to table - handles both dict and Account objects"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Handle both Account objects and dicts
        if hasattr(account_data, 'to_dict'):
            # It's an Account object
            data = account_data.to_dict()
            username = data.get('username', '')
            password = '***'  # Don't show password
            two_fa = data.get('two_fa', '')
            cookie = data.get('cookie', '')[:20] + '...' if data.get('cookie') else ''
            proxy = data.get('proxy', '')
            stats = str(data.get('stats', {}))
            status = data.get('status', '待机')
        elif hasattr(account_data, 'username'):
            # It's an Account object without to_dict
            username = getattr(account_data, 'username', '')
            password = '***'
            two_fa = getattr(account_data, 'two_fa', '')
            cookie = getattr(account_data, 'cookie', '')[:20] + '...' if getattr(account_data, 'cookie', '') else ''
            proxy = getattr(account_data, 'proxy', '')
            stats = str(getattr(account_data, 'stats', {}))
            status = getattr(account_data, 'status', '待机')
        else:
            # It's a dict
            username = account_data.get('username', '')
            password = '***'
            two_fa = account_data.get('2fa', '') or account_data.get('two_fa', '')
            cookie = account_data.get('cookie', '')[:20] + '...' if account_data.get('cookie') else ''
            proxy = account_data.get('proxy', '')
            stats = str(account_data.get('stats', 0))
            status = account_data.get('status', '待机')
        
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(username))
        self.table.setItem(row, 2, QTableWidgetItem(password))
        self.table.setItem(row, 3, QTableWidgetItem(two_fa))
        self.table.setItem(row, 4, QTableWidgetItem(cookie))
        self.table.setItem(row, 5, QTableWidgetItem(proxy))
        self.table.setItem(row, 6, QTableWidgetItem(stats))
        self.table.setItem(row, 7, QTableWidgetItem(status))


class UserManagementPanel(QGroupBox):
    """User Management Panel (用户管理)"""
    
    # Signals
    data_imported = Signal(int)
    data_cleared = Signal()
    data_exported = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__("用户管理", parent)
        self.setup_ui()
        self.connect_signals()
        self.load_collected_users()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #27ae60;
            }
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        
        self.btn_import = QPushButton("导入数据")
        self.btn_clear = QPushButton("清空数据")
        self.btn_export = QPushButton("导出未使用")
        
        self.btn_clear.setStyleSheet("background: #e74c3c;")
        
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "序号", "用户昵称", "UID", "时间", "状态"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        
    def connect_signals(self):
        """Connect button signals"""
        self.btn_import.clicked.connect(self.on_import_data)
        self.btn_clear.clicked.connect(self.on_clear_data)
        self.btn_export.clicked.connect(self.on_export_data)
        
    def load_collected_users(self):
        """Load collected users from data directory"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'members')
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir)[:50]:  # Limit to 50 files
                    if filename.endswith('.json'):
                        filepath = os.path.join(data_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                users = json.load(f)
                                if isinstance(users, list):
                                    for user in users[:20]:  # Limit per file
                                        self.add_user(user)
                        except:
                            pass
        except Exception as e:
            print(f"Error loading users: {e}")
            
    def on_import_data(self):
        """Import user data from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择用户数据文件", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        users = json.load(f)
                    else:
                        users = [{'name': line.strip(), 'uid': '', 'time': '', 'status': ''} 
                                for line in f.readlines() if line.strip()]
                
                count = 0
                for user in users:
                    self.add_user(user)
                    count += 1
                    
                QMessageBox.information(self, "导入成功", f"成功导入 {count} 个用户")
                self.data_imported.emit(count)
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入失败: {str(e)}")
                
    def on_clear_data(self):
        """Clear all user data"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有用户数据吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table.setRowCount(0)
            self.data_cleared.emit()
            QMessageBox.information(self, "清空成功", "已清空所有用户数据")
            
    def on_export_data(self):
        """Export user data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出用户数据", "users.txt", "Text Files (*.txt);;JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                users = []
                for row in range(self.table.rowCount()):
                    users.append({
                        'name': self.table.item(row, 1).text() if self.table.item(row, 1) else '',
                        'uid': self.table.item(row, 2).text() if self.table.item(row, 2) else '',
                        'time': self.table.item(row, 3).text() if self.table.item(row, 3) else '',
                        'status': self.table.item(row, 4).text() if self.table.item(row, 4) else ''
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(users, f, ensure_ascii=False, indent=2)
                    else:
                        for user in users:
                            f.write(f"{user['name']}\t{user['uid']}\n")
                            
                QMessageBox.information(self, "导出成功", f"已导出到 {file_path}")
                self.data_exported.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出失败: {str(e)}")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
        
    def add_user(self, user_data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(user_data.get('name', '')))
        self.table.setItem(row, 2, QTableWidgetItem(user_data.get('uid', '')))
        self.table.setItem(row, 3, QTableWidgetItem(user_data.get('time', '')))
        self.table.setItem(row, 4, QTableWidgetItem(user_data.get('status', '')))


class CollectionControlPanel(QGroupBox):
    """Collection Control Panel (采集控制台)"""
    
    def __init__(self, parent=None):
        super().__init__("控制台", parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #9b59b6;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Keywords/Group ID input
        keywords_layout = QHBoxLayout()
        keywords_layout.addWidget(QLabel("关键词/群组ID:"))
        self.txt_keywords = QTextEdit()
        self.txt_keywords.setMaximumHeight(80)
        self.txt_keywords.setPlaceholderText("每行一个关键词或群组ID...")
        layout.addWidget(self.txt_keywords)
        
        # Settings grid
        settings_grid = QGridLayout()
        
        # Row 1
        settings_grid.addWidget(QLabel("单号采集数:"), 0, 0)
        self.spin_per_account = QSpinBox()
        self.spin_per_account.setRange(1, 100)
        self.spin_per_account.setValue(10)
        settings_grid.addWidget(self.spin_per_account, 0, 1)
        
        settings_grid.addWidget(QLabel("群组采集页:"), 0, 2)
        self.spin_group_pages = QSpinBox()
        self.spin_group_pages.setRange(1, 100)
        self.spin_group_pages.setValue(10)
        settings_grid.addWidget(self.spin_group_pages, 0, 3)
        
        # Row 2
        settings_grid.addWidget(QLabel("群成员采集页:"), 1, 0)
        self.spin_member_pages = QSpinBox()
        self.spin_member_pages.setRange(1, 100)
        self.spin_member_pages.setValue(10)
        settings_grid.addWidget(self.spin_member_pages, 1, 1)
        
        settings_grid.addWidget(QLabel("间隔延迟:"), 1, 2)
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 60)
        self.spin_delay.setValue(10)
        settings_grid.addWidget(self.spin_delay, 1, 3)
        settings_grid.addWidget(QLabel("毫秒"), 1, 4)
        
        layout.addLayout(settings_grid)
        
        # Radio buttons
        radio_layout = QHBoxLayout()
        self.radio_keyword = QRadioButton("关键词采集群组成员")
        self.radio_custom = QRadioButton("自定义群组采集")
        self.radio_keyword.setChecked(True)
        radio_layout.addWidget(self.radio_keyword)
        radio_layout.addWidget(self.radio_custom)
        radio_layout.addStretch()
        layout.addLayout(radio_layout)
        
        # Clear history button
        self.btn_clear_history = QPushButton("清理采集历史库")
        self.btn_clear_history.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.btn_clear_history)


class FilterSettingsPanel(QGroupBox):
    """Filter Settings Panel (功能设置)"""
    
    # Signals
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__("功能设置", parent)
        self.cloud_dedup = CloudDeduplication() if HAS_BACKEND else None
        self.setup_ui()
        self.connect_signals()
        
    def connect_signals(self):
        """Connect all filter controls"""
        self.btn_test_connection.clicked.connect(self.on_test_connection)
        
    def on_test_connection(self):
        """Test cloud deduplication connection"""
        try:
            if self.cloud_dedup:
                stats = self.cloud_dedup.get_stats()
                QMessageBox.information(
                    self, "连通测试成功", 
                    f"云端去重复连接正常!\n\n"
                    f"数据库: {self.txt_db_name.text()}\n"
                    f"总记录数: {stats.get('total_entries', 0)}\n"
                    f"成员数: {stats.get('members', 0)}\n"
                    f"群组数: {stats.get('groups', 0)}"
                )
            else:
                QMessageBox.warning(self, "连通测试", "云端去重复模块未加载")
        except Exception as e:
            QMessageBox.critical(self, "连通测试失败", f"连接失败: {str(e)}")
            
    def get_settings(self):
        """Get all filter settings as a dict"""
        return {
            'pm_after_add': self.chk_pm_after_add.isChecked(),
            'delete_request': self.chk_delete_request.isChecked(),
            'delete_unfit': self.chk_delete_unfit.isChecked(),
            'country': self.combo_country.currentText(),
            'gender': self.combo_gender.currentText(),
            'text_detect': self.chk_text_detect.isChecked(),
            'language': self.combo_language.currentText(),
            'ai_only': self.chk_ai_only.isChecked(),
            'ai_face': self.chk_ai_face.isChecked(),
            'friend_min': self.spin_friend_min.value(),
            'friend_max': self.spin_friend_max.value(),
            'age_min': self.spin_age_min.value(),
            'age_max': self.spin_age_max.value(),
            'delay_min': self.spin_delay_min.value(),
            'delay_max': self.spin_delay_max.value(),
            'quantity': self.spin_quantity.value(),
            'cloud_dedup': self.chk_cloud_dedup.isChecked(),
            'db_name': self.txt_db_name.text(),
            'no_age': self.chk_no_age.isChecked(),
            'no_gender': self.chk_no_gender.isChecked(),
            'no_location': self.chk_no_location.isChecked(),
            'name_only': self.chk_name_only.isChecked()
        }
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #e67e22;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Checkboxes row 1
        chk_layout1 = QHBoxLayout()
        self.chk_pm_after_add = QCheckBox("加好友后私信")
        self.chk_delete_request = QCheckBox("删除好友请求")
        self.chk_delete_unfit = QCheckBox("删除不符推荐好友")
        chk_layout1.addWidget(self.chk_pm_after_add)
        chk_layout1.addWidget(self.chk_delete_request)
        chk_layout1.addWidget(self.chk_delete_unfit)
        chk_layout1.addStretch()
        layout.addLayout(chk_layout1)
        
        # Country and Gender
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("国家选择:"))
        self.combo_country = QComboBox()
        self.combo_country.addItems(["全部", "中国", "日本", "韩国", "美国", "越南", "泰国", "菲律宾"])
        self.combo_country.setEditable(True)
        filter_layout.addWidget(self.combo_country)
        
        filter_layout.addWidget(QLabel("性别选择:"))
        self.combo_gender = QComboBox()
        self.combo_gender.addItems(["全部", "男", "女"])
        filter_layout.addWidget(self.combo_gender)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Language and AI
        ai_layout = QHBoxLayout()
        
        self.chk_text_detect = QCheckBox("页面文字检测:")
        self.combo_language = QComboBox()
        self.combo_language.addItems(["中文", "英文", "日文", "韩文", "越南语"])
        ai_layout.addWidget(self.chk_text_detect)
        ai_layout.addWidget(self.combo_language)
        
        self.chk_ai_only = QCheckBox("只用AI不看简介")
        ai_layout.addWidget(self.chk_ai_only)
        
        self.chk_ai_face = QCheckBox("AI头像识别")
        ai_layout.addWidget(self.chk_ai_face)
        
        ai_layout.addStretch()
        layout.addLayout(ai_layout)
        
        # Friend count and age range
        range_layout = QHBoxLayout()
        
        range_layout.addWidget(QLabel("好友量:"))
        self.spin_friend_min = QSpinBox()
        self.spin_friend_min.setRange(0, 10000)
        self.spin_friend_min.setValue(0)
        range_layout.addWidget(self.spin_friend_min)
        range_layout.addWidget(QLabel("~"))
        self.spin_friend_max = QSpinBox()
        self.spin_friend_max.setRange(0, 10000)
        self.spin_friend_max.setValue(5000)
        range_layout.addWidget(self.spin_friend_max)
        
        range_layout.addWidget(QLabel("年龄范围:"))
        self.spin_age_min = QSpinBox()
        self.spin_age_min.setRange(0, 100)
        self.spin_age_min.setValue(18)
        range_layout.addWidget(self.spin_age_min)
        range_layout.addWidget(QLabel("~"))
        self.spin_age_max = QSpinBox()
        self.spin_age_max.setRange(0, 100)
        self.spin_age_max.setValue(65)
        range_layout.addWidget(self.spin_age_max)
        
        range_layout.addStretch()
        layout.addLayout(range_layout)
        
        # Delay and quantity
        delay_layout = QHBoxLayout()
        
        delay_layout.addWidget(QLabel("延迟:"))
        self.spin_delay_min = QSpinBox()
        self.spin_delay_min.setRange(1, 60)
        self.spin_delay_min.setValue(5)
        delay_layout.addWidget(self.spin_delay_min)
        delay_layout.addWidget(QLabel("~"))
        self.spin_delay_max = QSpinBox()
        self.spin_delay_max.setRange(1, 60)
        self.spin_delay_max.setValue(10)
        delay_layout.addWidget(self.spin_delay_max)
        
        delay_layout.addWidget(QLabel("数量:"))
        self.spin_quantity = QSpinBox()
        self.spin_quantity.setRange(1, 1000)
        self.spin_quantity.setValue(10)
        delay_layout.addWidget(self.spin_quantity)
        
        delay_layout.addStretch()
        layout.addLayout(delay_layout)
        
        # Cloud deduplication
        dedup_layout = QHBoxLayout()
        self.chk_cloud_dedup = QCheckBox("云端去重复")
        self.chk_cloud_dedup.setChecked(True)
        dedup_layout.addWidget(self.chk_cloud_dedup)
        
        dedup_layout.addWidget(QLabel("数据库名:"))
        self.txt_db_name = QLineEdit("去重复用")
        self.txt_db_name.setMaximumWidth(150)
        dedup_layout.addWidget(self.txt_db_name)
        
        self.btn_test_connection = QPushButton("连通测试")
        self.btn_test_connection.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
        """)
        dedup_layout.addWidget(self.btn_test_connection)
        
        dedup_layout.addStretch()
        layout.addLayout(dedup_layout)
        
        # Additional checkboxes
        extra_layout = QHBoxLayout()
        self.chk_no_age = QCheckBox("加无年龄")
        self.chk_no_gender = QCheckBox("加无性别")
        self.chk_no_location = QCheckBox("加无位置")
        self.chk_name_only = QCheckBox("只识别名字")
        extra_layout.addWidget(self.chk_no_age)
        extra_layout.addWidget(self.chk_no_gender)
        extra_layout.addWidget(self.chk_no_location)
        extra_layout.addWidget(self.chk_name_only)
        extra_layout.addStretch()
        layout.addLayout(extra_layout)


class PrivateMessagePanel(QGroupBox):
    """Private Message Content Panel (私信内容)"""
    
    def __init__(self, parent=None):
        super().__init__("私信内容", parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1abc9c;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Options
        opt_layout = QHBoxLayout()
        self.chk_send_image = QCheckBox("私信发送图片")
        self.chk_random_emoji = QCheckBox("私信随机表情")
        self.chk_random_emoji.setChecked(True)
        opt_layout.addWidget(self.chk_send_image)
        opt_layout.addWidget(self.chk_random_emoji)
        opt_layout.addStretch()
        layout.addLayout(opt_layout)
        
        # Message content
        layout.addWidget(QLabel("随机私信内容:"))
        self.txt_messages = QTextEdit()
        self.txt_messages.setPlaceholderText("每行一条消息，系统会随机选择发送...\n例如:\n你好，很高兴认识你！\n嗨，想和你交个朋友\n...")
        self.txt_messages.setMaximumHeight(120)
        layout.addWidget(self.txt_messages)


class RunLogPanel(QGroupBox):
    """Run Log Panel (运行日志)"""
    
    def __init__(self, parent=None):
        super().__init__("运行日志", parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #34495e;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #00ff00;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)
        
    def add_log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": "#00ff00",
            "SUCCESS": "#00ffff",
            "WARNING": "#ffff00",
            "ERROR": "#ff0000"
        }.get(level, "#ffffff")
        
        self.log_text.append(f'<span style="color:{color}">{timestamp}: {message}</span>')
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )


class ThreadControlPanel(QWidget):
    """Thread Control Panel"""
    
    # Signals
    stop_requested = Signal()
    pause_requested = Signal()
    thread_count_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_paused = False
        self.setup_ui()
        self.connect_signals()
        
    def connect_signals(self):
        """Connect button signals"""
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_pause.clicked.connect(self.on_pause_clicked)
        self.spin_threads.valueChanged.connect(self.on_thread_count_changed)
        
    def on_stop_clicked(self):
        """Handle stop button click"""
        reply = QMessageBox.question(
            self, "确认停止", "确定要停止所有运行中的任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.stop_requested.emit()
            QMessageBox.information(self, "已停止", "已发送停止信号到所有任务")
            
    def on_pause_clicked(self):
        """Handle pause button click"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.setText("继续")
            self.btn_pause.setStyleSheet("""
                QPushButton {
                    background: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                }
            """)
        else:
            self.btn_pause.setText("暂停")
            self.btn_pause.setStyleSheet("""
                QPushButton {
                    background: #f39c12;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                }
            """)
        self.pause_requested.emit()
        
    def on_thread_count_changed(self, value):
        """Handle thread count change"""
        self.thread_count_changed.emit(value)
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("线程数:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 10)
        self.spin_threads.setValue(1)
        layout.addWidget(self.spin_threads)
        
        self.btn_stop = QPushButton("停止运行")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        layout.addWidget(self.btn_stop)
        
        self.btn_pause = QPushButton("暂停")
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background: #f39c12;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #d68910;
            }
        """)
        layout.addWidget(self.btn_pause)
        
        layout.addStretch()


class EnhancedDashboard(QWidget):
    """Main Enhanced Dashboard Widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left side - Account and User Management
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.account_panel = AccountManagementPanel()
        left_layout.addWidget(self.account_panel)
        
        self.user_panel = UserManagementPanel()
        left_layout.addWidget(self.user_panel)
        
        # Right side - Controls and Stats
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stats_widget = StatsWidget()
        right_layout.addWidget(self.stats_widget)
        
        self.control_panel = CollectionControlPanel()
        right_layout.addWidget(self.control_panel)
        
        # Tab widget for settings
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #5e98ea;
                color: white;
            }
        """)
        
        # Settings tabs
        self.filter_panel = FilterSettingsPanel()
        self.pm_panel = PrivateMessagePanel()
        
        self.settings_tabs.addTab(self.filter_panel, "功能设置")
        self.settings_tabs.addTab(self.pm_panel, "私信内容")
        self.settings_tabs.addTab(QWidget(), "网络设置")
        self.settings_tabs.addTab(QWidget(), "公告")
        self.settings_tabs.addTab(QWidget(), "关于")
        
        right_layout.addWidget(self.settings_tabs)
        
        # Thread control
        self.thread_control = ThreadControlPanel()
        right_layout.addWidget(self.thread_control)
        
        # Run log
        self.log_panel = RunLogPanel()
        right_layout.addWidget(self.log_panel)
        
        # Add to main layout
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)
        
    def log(self, message, level="INFO"):
        self.log_panel.add_log(message, level)


class ScriptSelectionPanel(QGroupBox):
    """Script Selection Panel (脚本选择) - for Add Friend tab"""
    
    def __init__(self, parent=None):
        super().__init__("脚本选择", parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Checkboxes row 1
        row1 = QHBoxLayout()
        self.chk_add_recommended = QCheckBox("加推荐好友")
        self.chk_add_friend_of_friend = QCheckBox("加好友的好友")
        self.chk_add_own_friend = QCheckBox("加自己好友的好友")
        row1.addWidget(self.chk_add_recommended)
        row1.addWidget(self.chk_add_friend_of_friend)
        row1.addWidget(self.chk_add_own_friend)
        row1.addStretch()
        layout.addLayout(row1)
        
        # Location based
        loc_layout = QHBoxLayout()
        self.chk_location_recommend = QCheckBox("定位推荐好友")
        loc_layout.addWidget(self.chk_location_recommend)
        loc_layout.addWidget(QLabel("定位位置:"))
        self.txt_location = QLineEdit()
        self.txt_location.setPlaceholderText("Tokyo")
        self.txt_location.setMaximumWidth(150)
        loc_layout.addWidget(self.txt_location)
        loc_layout.addStretch()
        layout.addLayout(loc_layout)
        
        # More options
        row2 = QHBoxLayout()
        self.chk_add_post_likers = QCheckBox("加贴子点赞用户好友")
        self.chk_add_group_members = QCheckBox("加小组成员好友")
        self.chk_add_friend_request = QCheckBox("加好友请求")
        row2.addWidget(self.chk_add_post_likers)
        row2.addWidget(self.chk_add_group_members)
        row2.addWidget(self.chk_add_friend_request)
        row2.addStretch()
        layout.addLayout(row2)
        
        # File selector
        file_layout = QHBoxLayout()
        self.chk_add_from_file = QCheckBox("个人链接加好友")
        file_layout.addWidget(self.chk_add_from_file)
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setPlaceholderText("文本路径")
        self.txt_file_path.setReadOnly(True)
        file_layout.addWidget(self.txt_file_path)
        self.btn_select_file = QPushButton("点击选择")
        self.btn_select_file.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
        """)
        file_layout.addWidget(self.btn_select_file)
        layout.addLayout(file_layout)


# Test the dashboard
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Enhanced Dashboard Test")
    window.resize(1200, 800)
    
    dashboard = EnhancedDashboard()
    window.setCentralWidget(dashboard)
    
    # Add some test data
    dashboard.account_panel.add_account({
        'username': '61574***',
        'password': '***',
        '2fa': 'PCCFX...',
        'cookie': 'c_use...',
        'proxy': '["proxy..."]',
        'stats': 40,
        'status': '采集[5]页'
    })
    
    dashboard.user_panel.add_user({
        'name': 'R X gaming',
        'uid': '1000795...',
        'time': '约 1 分...',
        'status': ''
    })
    
    dashboard.log("成功>当前已采集到用户昵称[Md Najmul Islam]用户uid:[61551759999610]", "SUCCESS")
    dashboard.log("成功>当前已采集到用户昵称[Shejan Shejan]用户uid:[61550819686435]", "SUCCESS")
    
    window.show()
    sys.exit(app.exec_())

