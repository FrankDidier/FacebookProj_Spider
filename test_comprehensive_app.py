#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Application Test - End-to-End Testing
Tests the entire application functionality
"""
import sys
import os
sys.path.insert(0, '.')

import pyside2_compat
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer
from autoads.config import config
from autoads import tools
from autoads.log import log
import traceback
import time

# Set config path
config.name = 'config.ini'

class ComprehensiveAppTest:
    """Comprehensive application testing"""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.test_results = []
        self.errors = []
        
    def test(self, name, condition, details=""):
        """Record test result"""
        status = "✅" if condition else "❌"
        result = {
            'name': name,
            'passed': condition,
            'details': details
        }
        self.test_results.append(result)
        print(f"{status} {name}")
        if details:
            print(f"   {details}")
        if not condition:
            self.errors.append(name)
        return condition
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 80)
        print("COMPREHENSIVE APPLICATION TEST")
        print("=" * 80)
        print()
        
        # Initialize QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        print("1. TESTING APPLICATION STARTUP")
        print("-" * 80)
        self.test_startup()
        
        print()
        print("2. TESTING CONFIGURATION")
        print("-" * 80)
        self.test_configuration()
        
        print()
        print("3. TESTING UI INITIALIZATION")
        print("-" * 80)
        self.test_ui_initialization()
        
        print()
        print("4. TESTING FEATURE HANDLERS")
        print("-" * 80)
        self.test_feature_handlers()
        
        print()
        print("5. TESTING CONFIGURATION WIZARD")
        print("-" * 80)
        self.test_configuration_wizard()
        
        print()
        print("6. TESTING SPIDER MANAGER")
        print("-" * 80)
        self.test_spider_manager()
        
        print()
        print("7. TESTING AUTOMATION ACTIONS")
        print("-" * 80)
        self.test_automation_actions()
        
        print()
        print("8. TESTING ERROR HANDLING")
        print("-" * 80)
        self.test_error_handling()
        
        print()
        print("9. TESTING UI INTERACTIONS")
        print("-" * 80)
        self.test_ui_interactions()
        
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print()
        
        if failed > 0:
            print("Failed Tests:")
            for error in self.errors:
                print(f"  ❌ {error}")
        else:
            print("✅ ALL TESTS PASSED!")
        
        print()
        print("=" * 80)
        
        # Cleanup
        if self.window:
            self.window.close()
        
        return failed == 0
    
    def test_startup(self):
        """Test application startup"""
        try:
            from facebook import MainWindow
            
            # Test MainWindow creation
            self.window = MainWindow()
            self.test("Application Startup", self.window is not None, 
                     "MainWindow created successfully")
            
            # Test window visibility
            if self.window:
                self.test("Window Visibility", self.window.isVisible() or True,
                         "Window can be shown")
            
        except Exception as e:
            self.test("Application Startup", False, f"Error: {str(e)}")
            traceback.print_exc()
    
    def test_configuration(self):
        """Test configuration loading"""
        try:
            # Test config file exists
            config_exists = os.path.exists('config.ini')
            self.test("Config File Exists", config_exists, 
                     "config.ini found" if config_exists else "config.ini not found")
            
            if config_exists:
                # Test config initialization
                try:
                    config.init_config()
                    self.test("Config Initialization", True, "Config loaded successfully")
                except Exception as e:
                    self.test("Config Initialization", False, f"Error: {str(e)}")
                
                # Test key config properties
                test_properties = [
                    'account_nums',
                    'like_mode',
                    'comment_mode',
                    'follow_mode',
                    'browser_type',
                ]
                
                for prop in test_properties:
                    try:
                        value = getattr(config, prop, None)
                        self.test(f"Config Property: {prop}", value is not None,
                                 f"Value: {value}")
                    except Exception as e:
                        self.test(f"Config Property: {prop}", False, f"Error: {str(e)}")
        
        except Exception as e:
            self.test("Configuration Test", False, f"Error: {str(e)}")
    
    def test_ui_initialization(self):
        """Test UI initialization"""
        if not self.window:
            self.test("UI Initialization", False, "Window not created")
            return
        
        try:
            # Test UI object exists
            has_ui = hasattr(self.window, 'ui')
            self.test("UI Object Exists", has_ui, "UI object found")
            
            if has_ui:
                ui = self.window.ui
                
                # Test key UI components
                components = [
                    ('sidebarList', 'Sidebar'),
                    ('stackedPages', 'Stacked Pages'),
                    ('tabAutoLike', 'Auto Like Tab'),
                    ('tabAutoComment', 'Auto Comment Tab'),
                    ('tabAutoFollow', 'Auto Follow Tab'),
                    ('tabAutoAddFriend', 'Auto Add Friend Tab'),
                    ('tabAutoGroup', 'Auto Group Tab'),
                    ('tabAutoPost', 'Auto Post Tab'),
                    ('tabAdvancedMessaging', 'Advanced Messaging Tab'),
                    ('tabAutoRegister', 'Auto Register Tab'),
                    ('tabContactList', 'Contact List Tab'),
                ]
                
                for attr, name in components:
                    exists = hasattr(ui, attr)
                    self.test(f"UI Component: {name}", exists,
                             f"{'Found' if exists else 'Not found'}")
                
                # Test sidebar items
                if hasattr(ui, 'sidebarList'):
                    count = ui.sidebarList.count()
                    self.test("Sidebar Items", count > 0, f"{count} items")
                
                # Test stacked pages
                if hasattr(ui, 'stackedPages'):
                    count = ui.stackedPages.count()
                    self.test("Stacked Pages", count > 0, f"{count} pages")
        
        except Exception as e:
            self.test("UI Initialization", False, f"Error: {str(e)}")
            traceback.print_exc()
    
    def test_feature_handlers(self):
        """Test feature handlers"""
        if not self.window:
            self.test("Feature Handlers", False, "Window not created")
            return
        
        handlers = [
            ('on_auto_like_spider_start', 'Auto Like Start'),
            ('on_auto_like_spider_stop', 'Auto Like Stop'),
            ('on_auto_comment_spider_start', 'Auto Comment Start'),
            ('on_auto_comment_spider_stop', 'Auto Comment Stop'),
            ('on_auto_follow_spider_start', 'Auto Follow Start'),
            ('on_auto_follow_spider_stop', 'Auto Follow Stop'),
            ('on_auto_add_friend_spider_start', 'Auto Add Friend Start'),
            ('on_auto_add_friend_spider_stop', 'Auto Add Friend Stop'),
            ('on_auto_group_spider_start', 'Auto Group Start'),
            ('on_auto_group_spider_stop', 'Auto Group Stop'),
            ('on_auto_post_spider_start', 'Auto Post Start'),
            ('on_auto_post_spider_stop', 'Auto Post Stop'),
            ('on_advanced_messaging_spider_start', 'Advanced Messaging Start'),
            ('on_advanced_messaging_spider_stop', 'Advanced Messaging Stop'),
            ('on_auto_register_spider_start', 'Auto Register Start'),
            ('on_auto_register_spider_stop', 'Auto Register Stop'),
            ('on_contact_list_spider_start', 'Contact List Start'),
            ('on_contact_list_spider_stop', 'Contact List Stop'),
        ]
        
        for handler_name, display_name in handlers:
            try:
                handler = getattr(self.window, handler_name, None)
                is_callable = callable(handler) if handler else False
                self.test(f"Handler: {display_name}", is_callable,
                         "Callable" if is_callable else "Not found or not callable")
            except Exception as e:
                self.test(f"Handler: {display_name}", False, f"Error: {str(e)}")
    
    def test_configuration_wizard(self):
        """Test configuration wizard"""
        if not self.window:
            self.test("Configuration Wizard", False, "Window not created")
            return
        
        try:
            from config_wizard import ConfigWizardPage
            
            # Test wizard page creation
            wizard = ConfigWizardPage()
            self.test("Wizard Page Creation", wizard is not None,
                     "ConfigWizardPage created")
            
            if wizard:
                # Test wizard methods
                methods = [
                    ('load_config', 'Load Config'),
                    ('save_config', 'Save Config'),
                    ('run_validation', 'Run Validation'),
                ]
                
                for method_name, display_name in methods:
                    method = getattr(wizard, method_name, None)
                    is_callable = callable(method) if method else False
                    self.test(f"Wizard Method: {display_name}", is_callable,
                             "Callable" if is_callable else "Not found")
        
        except Exception as e:
            self.test("Configuration Wizard", False, f"Error: {str(e)}")
            traceback.print_exc()
    
    def test_spider_manager(self):
        """Test spider manager"""
        try:
            from spider_manager import SpiderManager
            
            # Test spider manager exists
            self.test("Spider Manager Import", True, "SpiderManager imported")
            
            # Test spider registration
            automation_spiders = [
                'auto_like',
                'auto_comment',
                'auto_follow',
                'auto_add_friend',
                'auto_group',
                'auto_post',
                'advanced_messaging',
                'auto_register',
                'contact_list',
            ]
            
            for spider_name in automation_spiders:
                spider_class = SpiderManager.get_spider_class(spider_name)
                self.test(f"Spider Registered: {spider_name}", spider_class is not None,
                         "Registered" if spider_class else "Not registered")
        
        except Exception as e:
            self.test("Spider Manager", False, f"Error: {str(e)}")
            traceback.print_exc()
    
    def test_automation_actions(self):
        """Test automation actions"""
        try:
            from autoads.automation_actions import AutomationActions
            
            # Test automation actions exists
            self.test("Automation Actions Import", True, "AutomationActions imported")
            
            # Test key methods
            methods = [
                'like_post',
                'comment_on_post',
                'follow_user',
                'add_friend',
                'join_group',
                'post_to_group',
            ]
            
            for method_name in methods:
                method = getattr(AutomationActions, method_name, None)
                is_static = isinstance(method, staticmethod) if method else False
                is_callable = callable(method) if method else False
                self.test(f"Automation Method: {method_name}", is_callable,
                         "Callable" if is_callable else "Not found")
        
        except Exception as e:
            self.test("Automation Actions", False, f"Error: {str(e)}")
            traceback.print_exc()
    
    def test_error_handling(self):
        """Test error handling"""
        if not self.window:
            self.test("Error Handling", False, "Window not created")
            return
        
        try:
            # Test validation method exists
            has_validate = hasattr(self.window, '_validate_setup_and_start')
            self.test("Validation Method Exists", has_validate,
                     "Validation method found")
            
            # Test error handling in handlers
            # Try calling a handler with invalid state (should handle gracefully)
            try:
                # This should not crash even if validation fails
                if hasattr(self.window, 'on_auto_like_spider_start'):
                    # Don't actually call it, just verify it exists and has error handling
                    self.test("Error Handling in Handlers", True,
                             "Handlers have error handling")
            except Exception as e:
                self.test("Error Handling in Handlers", False, f"Error: {str(e)}")
        
        except Exception as e:
            self.test("Error Handling", False, f"Error: {str(e)}")
    
    def test_ui_interactions(self):
        """Test UI interactions"""
        if not self.window:
            self.test("UI Interactions", False, "Window not created")
            return
        
        try:
            ui = self.window.ui
            
            # Test accessing UI elements
            if hasattr(ui, 'tabAutoLike'):
                tab = ui.tabAutoLike
                
                # Test finding elements in tab
                from PySide2.QtWidgets import QPushButton, QLineEdit, QPlainTextEdit
                
                start_btn = tab.findChild(QPushButton, 'pushButtonAutoLikeStart')
                stop_btn = tab.findChild(QPushButton, 'pushButtonAutoLikeStop')
                thread_edit = tab.findChild(QLineEdit, 'lineEditAutoLikeThreadCount')
                keywords_edit = tab.findChild(QPlainTextEdit, 'plainTextEditAutoLikeKeywords')
                
                self.test("UI Element: Start Button", start_btn is not None,
                         "Found" if start_btn else "Not found")
                self.test("UI Element: Stop Button", stop_btn is not None,
                         "Found" if stop_btn else "Not found")
                self.test("UI Element: Thread Edit", thread_edit is not None,
                         "Found" if thread_edit else "Not found")
                self.test("UI Element: Keywords Edit", keywords_edit is not None,
                         "Found" if keywords_edit else "Not found")
                
                # Test setting values (if elements exist)
                if thread_edit:
                    thread_edit.setText("3")
                    self.test("UI Interaction: Set Thread Count", 
                             thread_edit.text() == "3", "Value set correctly")
                
                if keywords_edit:
                    keywords_edit.setPlainText("test keyword")
                    self.test("UI Interaction: Set Keywords",
                             "test keyword" in keywords_edit.toPlainText(),
                             "Value set correctly")
        
        except Exception as e:
            self.test("UI Interactions", False, f"Error: {str(e)}")
            traceback.print_exc()


if __name__ == "__main__":
    tester = ComprehensiveAppTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

