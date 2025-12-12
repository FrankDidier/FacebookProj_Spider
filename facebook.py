#!/anaconda3/bin python3.7
# -*- coding: utf-8 -*-
# ---
# @Software: PyCharm
# @File: main.py
# @Author: James.Zhou
# @E-mail: 407360491@163.com
# @Site: 
# @Time: 七月 22, 2022
# ---
import sys, os, pyDes, base64
# Import compatibility layer for PySide6 before any PySide2 imports
import pyside2_compat
import time
import json
import requests
from PySide2.QtWidgets import QTextBrowser, QMainWindow, QGridLayout, QApplication, QTabWidget, QPushButton, \
    QMessageBox, QFileDialog
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QIntValidator, QTextDocument, QTextBlock, QIcon
from autoads.triple_des import des
from autoads.config import config

config.name = 'config.ini'
from PySide2.QtCore import Signal, QObject
import threading
from threading import Thread
import multiprocessing as mp
from autoads import tools
from spider.fb_group import GroupSpider
from spider.fb_members import MembersSpider
from spider.fb_greets import GreetsSpider
from spider.fb_group_specified import GroupSpecifiedSpider
from spider.fb_members_rapid import MembersRapidSpider
from spider.fb_posts import PostsSpider
from spider.fb_pages import PagesSpider
from spider.ins_followers import InstagramFollowersSpider
from spider.ins_following import InstagramFollowingSpider
from spider.ins_profile import InstagramProfileSpider
from spider.ins_reels_comments import InstagramReelsCommentsSpider
from urllib import parse
from autoads.log import log
from autoads.app_logger import app_logger, log_button
from fb_main import Ui_MainWindow
from functools import partial
from autoads import ads_api

MACHINE = tools.getCombinNumber()


class MySignals(QObject):
    text_print = Signal(QTextBrowser, str)
    update_control_status = Signal(list)
    update_activate = Signal(bool)


class ProcessCheckCode(object):

    @staticmethod
    def code_is_valid():
        params = parse.urlencode({
            'machine': MACHINE,
            'verify_code': config.app_code,
            'status': 'valid'

        })
        url = f'{config.activator_service}/valid?{params}'
        try:
            res = requests.get(url)
            # log.info(res.text)
            res = json.loads(res.text)
        except Exception as e:
            log.error(e)
            res = {'code': -1, 'data_len': 1, 'delay_times': 7}

        flag = False
        delay_times = 5
        # if res['code'] == 0:
        # print(len(res['datas']))
        if res['data_len'] > 0:
            flag = True
            delay_times = res['delay_times']

        # 先验证是不是当前激活码和机器码在可用的状态
        # print(f'flag={flag}')
        return (flag, delay_times)

    @classmethod
    def main(cls, queue_receiver):
        flag, delay_times = cls.code_is_valid()
        # print(flag)
        while flag:
            tools.delay_time(delay_times)
            flag, delay_times = cls.code_is_valid()
        queue_receiver.put(flag)
        # print(f'flag={flag}')
        return flag


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # 使用ui文件导入定义界面类
        # qfile_main = QFile('main.ui')
        # qfile_main.open(QFile.ReadOnly)
        # qfile_main.close()

        # 加载UI控件
        # self.ui = QUiLoader().load(qfile_main)

        # 加载UI控件
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("facebook.ico"))

        # self.ui.setWindowIcon(QIcon("facebook.ico"))

        # 创建定时器
        self.Timer = QTimer()
        # 定时器每1000ms工作一次
        self.Timer.start(1000)
        # 建立定时器连接通道  注意这里调用update_window_title方法，不是方法返回的的结果，所以不能带括号
        self.Timer.timeout.connect(self.update_window_title)

        self.invalidate_seconds = None
        self.expiried = None

        # self.ui.tabWidget.setTabIcon(0, QIcon("ui/group.ico"))
        # self.ui.tabWidget.setTabIcon(1, QIcon("ui/member.ico"))
        # self.ui.tabWidget.setTabIcon(2, QIcon("ui/greet.ico"))

        # 加载自定义信号对象，这里就是给界面中输出信息
        self.ms = MySignals()
        self.ms.text_print.connect(self.print_to_tui)
        self.ms.update_control_status.connect(self.update_control_enabled)
        self.ms.update_activate.connect(self.on_verify)

        # 定义每个爬虫停止的事件标志
        self.group_stop_event = None
        self.member_stop_event = None
        self.greets_stop_event = None
        self.group_specified_stop_event = None
        self.members_rapid_stop_event = None
        self.posts_stop_event = None
        self.pages_stop_event = None
        self.ins_followers_stop_event = None
        self.ins_following_stop_event = None
        self.ins_profile_stop_event = None
        self.ins_reels_comments_stop_event = None

        # 页面中的参数，都会保存到配置文件中，下次启动的时候，有些参数可以就使用上次的了

        self.queue = mp.Queue()

        self.check_queue_data()

        # 开启一个线程去更新配置信息
        # self.update_config()

        # 设置校验器
        self.ui.lineEditGroupMaxThreadCount.setValidator(QIntValidator())
        self.ui.lineEditMemberMaxThreadCount.setValidator(QIntValidator())
        self.ui.lineEditGroupCount.setValidator(QIntValidator())
        self.ui.lineEditGreetsMaxThreadCount.setValidator(QIntValidator())
        self.ui.lineEditGreetsCount.setValidator(QIntValidator())
        self.ui.lineEditGreetsTimeout.setValidator(QIntValidator())
        
        # New features validators (with error handling in case UI elements don't exist yet)
        try:
            self.ui.lineEditGroupSpecifiedThreadCount.setValidator(QIntValidator())
            self.ui.lineEditMembersRapidThreadCount.setValidator(QIntValidator())
            self.ui.lineEditMembersRapidGroupCount.setValidator(QIntValidator())
            self.ui.lineEditPostsThreadCount.setValidator(QIntValidator())
            self.ui.lineEditPostsGroupCount.setValidator(QIntValidator())
            self.ui.lineEditPagesThreadCount.setValidator(QIntValidator())
            self.ui.lineEditInsFollowersThreadCount.setValidator(QIntValidator())
            self.ui.lineEditInsFollowingThreadCount.setValidator(QIntValidator())
            self.ui.lineEditInsProfileThreadCount.setValidator(QIntValidator())
            self.ui.lineEditInsReelsCommentsThreadCount.setValidator(QIntValidator())
        except AttributeError:
            pass  # UI elements will be created dynamically

        # 加载上次设置的参数
        self.ui.lineEditGroupMaxThreadCount.setText(str(config.account_nums))
        self.ui.lineEditMemberMaxThreadCount.setText(str(config.account_nums))
        self.ui.lineEditGreetsMaxThreadCount.setText(str(config.account_nums))

        self.ui.lineEditGroupCount.setText(str(config.groups_nums))
        self.ui.lineEditGreetsCount.setText(str(config.members_nums))
        self.ui.lineEditGreetsTimeout.setText(str(config.member_timeout))
        
        # Load new features default values (with error handling)
        try:
            self.ui.lineEditGroupSpecifiedThreadCount.setText(str(config.account_nums))
            self.ui.lineEditMembersRapidThreadCount.setText(str(config.account_nums))
            self.ui.lineEditMembersRapidGroupCount.setText(str(config.groups_nums))
            self.ui.lineEditPostsThreadCount.setText(str(config.account_nums))
            self.ui.lineEditPostsGroupCount.setText(str(getattr(config, 'post_groups_nums', 10)))
            self.ui.lineEditPagesThreadCount.setText(str(config.account_nums))
            self.ui.lineEditInsFollowersThreadCount.setText(str(config.account_nums))
            self.ui.lineEditInsFollowingThreadCount.setText(str(config.account_nums))
            self.ui.lineEditInsProfileThreadCount.setText(str(config.account_nums))
            self.ui.lineEditInsReelsCommentsThreadCount.setText(str(config.account_nums))
            
            # Load Instagram usernames if any
            try:
                for username in config.ins_target_users:
                    self.ui.plainTextEditInsFollowersUsers.appendPlainText(username)
                    self.ui.plainTextEditInsFollowingUsers.appendPlainText(username)
                    self.ui.plainTextEditInsProfileUsers.appendPlainText(username)
            except:
                pass
            
            # Load Reels URLs if any
            try:
                for url in config.ins_reels_urls:
                    self.ui.plainTextEditInsReelsCommentsUrls.appendPlainText(url)
            except:
                pass
        except AttributeError:
            pass  # UI elements will be created dynamically

        self.ui.lineEditCode.setText(str(config.app_code))
        self.ui.lineEditMyMachine.setText(MACHINE)
        self.ui.lineEditAdsKey.setText(config.ads_key)

        ads_install_location = ads_api.get_service_exe()
        if ads_install_location:
            self.ui.lineEditInstallLocation.setText(ads_install_location)

        self.ui.pushButtonSelectInstallLocation.clicked.connect(self.on_select_file)

        for text in config.members_texts:
            self.ui.plainTextEditGreetsContent.appendPlainText(text)

        for image in config.members_images:
            self.ui.plainTextEditGreetsImage.appendPlainText(image)

        for text in config.groups_words:
            self.ui.plainTextEditGroupWords.appendPlainText(text)

        # 按钮绑定点击事件
        self.ui.pushButtonGroupSpiderStart.clicked.connect(self.on_group_spider_start)
        self.ui.pushButtonGroupSpiderStop.clicked.connect(self.on_group_spider_stop)

        self.ui.pushButtonMembersSpiderStart.clicked.connect(self.on_member_spider_start)
        self.ui.pushButtonMembersSpiderStop.clicked.connect(self.on_member_spider_stop)

        self.ui.pushButtonGreetsSpiderStart.clicked.connect(self.on_greets_spider_start)
        self.ui.pushButtonGreetsSpiderStop.clicked.connect(self.on_greets_spider_stop)
        
        # New features button connections (with error handling)
        try:
            self.ui.pushButtonGroupSpecifiedStart.clicked.connect(self.on_group_specified_spider_start)
            self.ui.pushButtonGroupSpecifiedStop.clicked.connect(self.on_group_specified_spider_stop)
            
            self.ui.pushButtonMembersRapidStart.clicked.connect(self.on_members_rapid_spider_start)
            self.ui.pushButtonMembersRapidStop.clicked.connect(self.on_members_rapid_spider_stop)
            
            self.ui.pushButtonPostsStart.clicked.connect(self.on_posts_spider_start)
            self.ui.pushButtonPostsStop.clicked.connect(self.on_posts_spider_stop)
            
            self.ui.pushButtonPagesStart.clicked.connect(self.on_pages_spider_start)
            self.ui.pushButtonPagesStop.clicked.connect(self.on_pages_spider_stop)
            
            self.ui.pushButtonInsFollowersStart.clicked.connect(self.on_ins_followers_spider_start)
            self.ui.pushButtonInsFollowersStop.clicked.connect(self.on_ins_followers_spider_stop)
            
            self.ui.pushButtonInsFollowingStart.clicked.connect(self.on_ins_following_spider_start)
            self.ui.pushButtonInsFollowingStop.clicked.connect(self.on_ins_following_spider_stop)
            
            self.ui.pushButtonInsProfileStart.clicked.connect(self.on_ins_profile_spider_start)
            self.ui.pushButtonInsProfileStop.clicked.connect(self.on_ins_profile_spider_stop)
            
            self.ui.pushButtonInsReelsCommentsStart.clicked.connect(self.on_ins_reels_comments_spider_start)
            self.ui.pushButtonInsReelsCommentsStop.clicked.connect(self.on_ins_reels_comments_spider_stop)
            
            # Automation features button connections
            self.ui.pushButtonAutoLikeStart.clicked.connect(self.on_auto_like_spider_start)
            self.ui.pushButtonAutoLikeStop.clicked.connect(self.on_auto_like_spider_stop)
            
            self.ui.pushButtonAutoCommentStart.clicked.connect(self.on_auto_comment_spider_start)
            self.ui.pushButtonAutoCommentStop.clicked.connect(self.on_auto_comment_spider_stop)
            
            self.ui.pushButtonAutoFollowStart.clicked.connect(self.on_auto_follow_spider_start)
            self.ui.pushButtonAutoFollowStop.clicked.connect(self.on_auto_follow_spider_stop)
            
            self.ui.pushButtonAutoAddFriendStart.clicked.connect(self.on_auto_add_friend_spider_start)
            self.ui.pushButtonAutoAddFriendStop.clicked.connect(self.on_auto_add_friend_spider_stop)
            
            self.ui.pushButtonAutoGroupStart.clicked.connect(self.on_auto_group_spider_start)
            self.ui.pushButtonAutoGroupStop.clicked.connect(self.on_auto_group_spider_stop)
            
            self.ui.pushButtonAutoPostStart.clicked.connect(self.on_auto_post_spider_start)
            self.ui.pushButtonAutoPostStop.clicked.connect(self.on_auto_post_spider_stop)
            
            self.ui.pushButtonAdvancedMessagingStart.clicked.connect(self.on_advanced_messaging_spider_start)
            self.ui.pushButtonAdvancedMessagingStop.clicked.connect(self.on_advanced_messaging_spider_stop)
            
            self.ui.pushButtonAutoRegisterStart.clicked.connect(self.on_auto_register_spider_start)
            self.ui.pushButtonAutoRegisterStop.clicked.connect(self.on_auto_register_spider_stop)
            
            self.ui.pushButtonContactListStart.clicked.connect(self.on_contact_list_spider_start)
            self.ui.pushButtonContactListStop.clicked.connect(self.on_contact_list_spider_stop)
        except AttributeError as e:
            log.warning(f"Some UI elements not found: {e}. They will be created when tabs are accessed.")

        self.ui.pushButtonVerify.clicked.connect(partial(self.on_verify, False))

        self.ui.tabWidget.currentChanged.connect(self.tab_change)  # 绑定标签点击时的信号与槽函数

        self.ui.tabWidget.tabBarClicked.connect(self.tab_clicked)
        
        # Connect sidebar list to tab change handler
        self.ui.sidebarList.currentRowChanged.connect(self.on_sidebar_changed)
        
        # Initialize configuration wizard (if not already added in fb_main.py)
        try:
            from config_wizard import ConfigWizardPage
            # Check if config wizard already exists in stackedPages
            config_wizard_exists = False
            if hasattr(self.ui, 'stackedPages') and self.ui.stackedPages.count() > 0:
                # Check if first widget is already the config wizard
                first_widget = self.ui.stackedPages.widget(0)
                if first_widget:
                    obj_name = first_widget.objectName() if hasattr(first_widget, 'objectName') else ''
                    if obj_name == "configWizardPage" or isinstance(first_widget, ConfigWizardPage):
                        # Already exists, just reference it
                        self.ui.configWizardPage = first_widget
                        if hasattr(first_widget, 'main_window'):
                            first_widget.main_window = self
                        config_wizard_exists = True
            
            # If config wizard doesn't exist, check if we need to create it
            if not config_wizard_exists:
                if hasattr(self.ui, 'configWizardPage') and self.ui.configWizardPage:
                    # Config wizard object exists but not in stackedPages, add it
                    self.ui.stackedPages.insertWidget(0, self.ui.configWizardPage)
                elif hasattr(self.ui, 'stackedPages'):
                    # Check for placeholder
                    if self.ui.stackedPages.count() > 0:
                        first_widget = self.ui.stackedPages.widget(0)
                        if first_widget and hasattr(first_widget, 'objectName') and first_widget.objectName() == "configWizardPlaceholder":
                            self.ui.stackedPages.removeWidget(first_widget)
                            first_widget.deleteLater()
                    
                    # Create and add config wizard
                    self.ui.configWizardPage = ConfigWizardPage(self)
                    self.ui.configWizardPage.setObjectName(u"configWizardPage")
                    self.ui.stackedPages.insertWidget(0, self.ui.configWizardPage)
        except Exception as e:
            log.warning(f"Could not initialize config wizard: {e}")
            import traceback
            traceback.print_exc()

        # self.on_verify()  # 初始化的时候页面需要进行验证
        self.update_control_enabled([True, 0])

        self.current_tab_index = 0
        # 每次启动的时候，清理ads_user中的配置信息，去重新获取新的配置信息
        self.clear_ads_user()
        
        # BYPASS ACTIVATION: Automatically skip to main app page
        self.bypass_activation()
        
        # Initialize file selectors
        self._init_file_selectors()

    def _init_file_selectors(self):
        """Initialize file selector comboboxes and connect buttons"""
        try:
            # Member page - select group files
            if hasattr(self.ui, 'comboBoxMemberGroupFile'):
                self._refresh_member_group_files()
                if hasattr(self.ui, 'pushButtonMemberRefreshFiles'):
                    self.ui.pushButtonMemberRefreshFiles.clicked.connect(self._refresh_member_group_files)
                if hasattr(self.ui, 'pushButtonMemberBrowseFile'):
                    self.ui.pushButtonMemberBrowseFile.clicked.connect(self._browse_member_group_file)
            
            # Greets page - select member files  
            if hasattr(self.ui, 'comboBoxGreetsMemberFile'):
                self._refresh_greets_member_files()
                if hasattr(self.ui, 'pushButtonGreetsRefreshFiles'):
                    self.ui.pushButtonGreetsRefreshFiles.clicked.connect(self._refresh_greets_member_files)
                if hasattr(self.ui, 'pushButtonGreetsBrowseFile'):
                    self.ui.pushButtonGreetsBrowseFile.clicked.connect(self._browse_greets_member_file)
        except Exception as e:
            log.warning(f"File selector init warning: {e}")

    def _refresh_member_group_files(self):
        """Refresh the group files list for member collection"""
        try:
            combo = self.ui.comboBoxMemberGroupFile
            combo.clear()
            combo.addItem("使用默认采集结果")  # Default option
            
            group_dir = './group'
            if os.path.exists(group_dir):
                for f in sorted(os.listdir(group_dir)):
                    if f.endswith('.txt') or f.endswith('.csv') or f.endswith('.json'):
                        combo.addItem(f"group/{f}")
            
            # Also check for any txt files in current directory
            for f in sorted(os.listdir('.')):
                if f.endswith('.txt') and 'group' in f.lower():
                    combo.addItem(f)
        except Exception as e:
            log.warning(f"Error refreshing group files: {e}")

    def _browse_member_group_file(self):
        """Browse for a group links file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, '选择群组链接文件', '.', 
            '文本文件 (*.txt);;CSV文件 (*.csv);;JSON文件 (*.json);;所有文件 (*.*)'
        )
        if file_name:
            combo = self.ui.comboBoxMemberGroupFile
            combo.addItem(file_name)
            combo.setCurrentText(file_name)

    def _refresh_greets_member_files(self):
        """Refresh the member files list for private messaging"""
        try:
            combo = self.ui.comboBoxGreetsMemberFile
            combo.clear()
            combo.addItem("使用默认采集结果")  # Default option
            
            member_dir = './member'
            if os.path.exists(member_dir):
                for f in sorted(os.listdir(member_dir)):
                    if f.endswith('.txt') or f.endswith('.csv') or f.endswith('.json'):
                        combo.addItem(f"member/{f}")
            
            # Also check for any txt files in current directory
            for f in sorted(os.listdir('.')):
                if f.endswith('.txt') and 'member' in f.lower():
                    combo.addItem(f)
        except Exception as e:
            log.warning(f"Error refreshing member files: {e}")

    def _browse_greets_member_file(self):
        """Browse for a member data file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, '选择成员数据文件', '.', 
            '文本文件 (*.txt);;CSV文件 (*.csv);;JSON文件 (*.json);;所有文件 (*.*)'
        )
        if file_name:
            combo = self.ui.comboBoxGreetsMemberFile
            combo.addItem(file_name)
            combo.setCurrentText(file_name)

    def get_selected_group_file(self):
        """Get the selected group file path, or None for default"""
        try:
            if hasattr(self.ui, 'comboBoxMemberGroupFile'):
                text = self.ui.comboBoxMemberGroupFile.currentText()
                if text and text != "使用默认采集结果":
                    return text
        except:
            pass
        return None

    def get_selected_member_file(self):
        """Get the selected member file path, or None for default"""
        try:
            if hasattr(self.ui, 'comboBoxGreetsMemberFile'):
                text = self.ui.comboBoxGreetsMemberFile.currentText()
                if text and text != "使用默认采集结果":
                    return text
        except:
            pass
        return None

    def on_select_file(self):
        file_name = QFileDialog.getOpenFileName(self, caption='选择文件', dir='.', filter='*.exe')
        if file_name and len(file_name) > 0 and file_name[0]:
            self.ui.lineEditInstallLocation.setText(file_name[0])

    def is_exists_ads_key(self):
        key = config.ads_key
        if key:
            return True
        return False

    def is_exists_ads_path(self):
        key = config.service_app_path
        if key:
            return True
        return False

    def print_to_tui(self, fb, text):
        str_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        format_text = f'<font color="#66CC00">{str_time}</font><font color="#CD0000"> | </font>{text}'
        fb.append(format_text)
        # fb.moveCursor(QTextCursor.Start)
        fb.ensureCursorVisible()

    def update_config(self):
        def run():
            url = f'{config.activator_service}/config'
            try:
                res = requests.get(url).json()
                if res['flag'] and res['version'] != config.version:
                    config.set_option('main', 'version', res['version'])
                    json_config = res['config']
                    for key in json_config.keys():
                        for item in json_config[key]:
                            for key_item in item.keys():
                                config.set_option(key, key_item, item[key_item])
            except Exception as e:
                log.error(e)

        # 开启一个线程来更新配置
        Thread(target=run).start()

    @staticmethod
    def clear_ads_user():
        def run():
            _file = './ads-users.txt'
            if os.path.exists(_file):
                os.remove(_file)

        # 开启一个线程来更新配置
        Thread(target=run).start()

    def update_control_enabled(self, args):
        # 获取当前index的tab
        # 如果stop参数为True，让启动按钮可用，停止按钮不可用，同时检查group文件夹和member文件夹是否有文件，控制是不是要让tab可用
        # 如果stop参数为False,让启动按钮不可用，停止按钮可用，同时其他的tab不可用

        # 获取当前tab和tab对应的启动和停止按钮
        stop, index = args
        tabs: QTabWidget = self.ui.tabWidget
        
        log.info(f"update_control_enabled called: stop={stop}, index={index}")
        app_logger.log_action("CONTROL_UPDATE", f"更新控件状态", {"stop": stop, "index": index})
        
        # IMPORTANT: If stop=True, always call reset to ensure buttons work
        if stop:
            # Use QTimer to delay the reset slightly to ensure spider has finished
            QTimer.singleShot(500, lambda: self._force_re_enable_buttons(index))
        
        # Get tab widget, use stacked widget if tab widget doesn't have it
        tab = tabs.widget(index)
        if not tab and hasattr(self.ui, 'stackedPages'):
            tab = self.ui.stackedPages.widget(index)
        
        if not tab:
            log.warning(f"No tab found for index {index}")
            return
            
        spider_name = tab.objectName().replace('tab', '')
        log.info(f"Spider name from tab: {spider_name}")
        
        # Map tab names to button names - extended list
        button_name_map = {
            'GroupSpider': 'GroupSpider',
            'MembersSpider': 'MembersSpider',
            'GreetsSpider': 'GreetsSpider',
            'GroupSpecified': 'GroupSpecified',
            'MembersRapid': 'MembersRapid',
            'Posts': 'Posts',
            'Pages': 'Pages',
            'InsFollowers': 'InsFollowers',
            'InsFollowing': 'InsFollowing',
            'InsProfile': 'InsProfile',
            'InsReelsComments': 'InsReelsComments',
            'AutoLike': 'AutoLike',
            'AutoComment': 'AutoComment',
            'AutoFollow': 'AutoFollow',
            'AutoAddFriend': 'AutoAddFriend',
            'AutoGroup': 'AutoGroup',
            'AutoPost': 'AutoPost',
            'AdvancedMessaging': 'AdvancedMessaging',
            'AutoRegister': 'AutoRegister',
            'ContactList': 'ContactList',
        }
        
        button_base = button_name_map.get(spider_name, spider_name)
        buttons_start = self.findChildren(QPushButton, f'pushButton{button_base}Start')
        buttons_stop = self.findChildren(QPushButton, f'pushButton{button_base}Stop')
        
        log.info(f"Looking for buttons: pushButton{button_base}Start, pushButton{button_base}Stop")
        log.info(f"Found start buttons: {len(buttons_start)}, stop buttons: {len(buttons_stop)}")
        
        if not buttons_start or not buttons_stop:
            # Try to find buttons within the current tab widget
            if tab:
                buttons_start = tab.findChildren(QPushButton)
                for btn in buttons_start:
                    if 'start' in btn.objectName().lower() or btn.text() == '启动':
                        buttons_start = [btn]
                        break
                for btn in tab.findChildren(QPushButton):
                    if 'stop' in btn.objectName().lower() or btn.text() == '停止':
                        buttons_stop = [btn]
                        break
            
            if not buttons_start or not buttons_stop:
                log.warning(f"Buttons not found for {spider_name}, but trying to re-enable all buttons")
                # If stop=True and buttons not found, try to enable all relevant buttons
                if stop:
                    # Re-enable all start buttons on the page
                    if tab:
                        for btn in tab.findChildren(QPushButton):
                            btn_name = btn.objectName().lower()
                            if 'start' in btn_name or btn.text() == '启动':
                                btn.setEnabled(True)
                            elif 'stop' in btn_name or btn.text() == '停止':
                                btn.setEnabled(False)
                return
        
        button_start: QPushButton = buttons_start[0]
        button_stop: QPushButton = buttons_stop[0]
        
        log.info(f"Setting button states: start.enabled={stop}, stop.enabled={not stop}")
        
        if stop:
            # 让启动按钮可用，停止按钮不可用
            button_start.setEnabled(True)
            button_stop.setEnabled(False)

            tabs.setTabEnabled(0, True)
            
            # Update sidebar list item state if available
            if hasattr(self.ui, 'sidebarList'):
                item = self.ui.sidebarList.item(0)
                if item:
                    item.setFlags(item.flags() | Qt.ItemIsEnabled)

            # 判断是不是group文件夹下有文件，有文件那么tab1就可以点击
            if os.path.exists('group') and len(os.listdir('group')) > 0:
                tabs.setTabEnabled(1, True)
                if hasattr(self.ui, 'sidebarList'):
                    item = self.ui.sidebarList.item(1)
                    if item:
                        item.setFlags(item.flags() | Qt.ItemIsEnabled)
            else:
                # tabs.setTabEnabled(1, False)
                tabs.setTabToolTip(1, '请先采集群组')
                if hasattr(self.ui, 'sidebarList'):
                    item = self.ui.sidebarList.item(1)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

            # 如果member文件夹下有文件，那tab2就可以点击
            if os.path.exists('member') and len(os.listdir('member')) > 0:
                tabs.setTabEnabled(2, True)
                if hasattr(self.ui, 'sidebarList'):
                    item = self.ui.sidebarList.item(2)
                    if item:
                        item.setFlags(item.flags() | Qt.ItemIsEnabled)
            else:
                # tabs.setTabEnabled(2, False)
                tabs.setTabToolTip(2, '请先采集群成员')
                if hasattr(self.ui, 'sidebarList'):
                    item = self.ui.sidebarList.item(2)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        else:
            # 让启动按钮不可用，停止按钮可用
            button_start.setEnabled(False)
            button_stop.setEnabled(True)

            text_browsers = self.findChildren(QTextBrowser, f'textBrowser{button_base}')
            if text_browsers:
                main_text_browser: QTextBrowser = text_browsers[0]
                main_text_browser.clear()

    def validate_setup(self, feature_name="功能"):
        """Validate setup before starting any feature - Flexible for multiple browsers"""
        app_logger.log_action("VALIDATION", f"开始验证配置 - {feature_name}")
        issues = []
        
        # Check browser type
        browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
        browser_name = 'AdsPower' if browser_type == 'adspower' else 'BitBrowser' if browser_type == 'bitbrowser' else '指纹浏览器'
        app_logger.log_action("VALIDATION", f"浏览器类型: {browser_name}", {"browser_type": browser_type})
        
        # Check API key - ONLY required for AdsPower, NOT for BitBrowser
        if browser_type == 'bitbrowser':
            # BitBrowser doesn't need API key - just check if service is running
            # Don't do additional checks to avoid rate limiting
            try:
                from autoads import bitbrowser_api
                service_ok = bitbrowser_api.test_connection()
                if not service_ok:
                    issues.append("BitBrowser 服务未检测到，请确保 BitBrowser 已打开并登录")
                # Skip login check to avoid rate limiting - service running is enough
            except Exception as e:
                # If we can't check, just try to proceed
                log.warning(f"BitBrowser connection check failed: {e}")
                pass
        elif browser_type == 'adspower':
            # AdsPower requires API key
            if not hasattr(config, 'ads_key') or not config.ads_key or config.ads_key.strip() == '':
                issues.append(f"API 密钥未配置，请在配置向导中设置 AdsPower API 密钥")
            else:
                # Check AdsPower service
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:50325/api/v1/browser/list", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('code') != 0:
                            issues.append("AdsPower API 返回错误，请检查 API 密钥")
                except:
                    # Don't block if service check fails
                    pass
        else:
            # Other browsers - API key optional, just check if service is available
            pass
        
        # Check accounts (only if we can connect)
        # Add delay for BitBrowser to avoid rate limiting
        if browser_type == 'bitbrowser':
            import time
            time.sleep(0.7)  # Wait to avoid API rate limiting
        
        try:
            ads_ids = tools.get_ads_id(1)  # Just check if we can get at least 1
            if len(ads_ids) == 0:
                issues.append(f"未找到浏览器配置，请在 {browser_name} 中添加浏览器")
        except Exception as e:
            # Don't fail if we can't get accounts - might just need browser to be open
            if browser_type != 'bitbrowser':  # Only show API key error for non-BitBrowser
                if "API" in str(e) or "key" in str(e).lower():
                    issues.append(f"无法获取账户列表，请检查 {browser_name} API 密钥配置")
            else:
                # For BitBrowser, just log the error but don't block
                log.warning(f"BitBrowser account check: {e}")
        
        if issues:
            browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
            browser_name = 'AdsPower' if browser_type == 'adspower' else 'BitBrowser' if browser_type == 'bitbrowser' else '指纹浏览器'
            
            msg = f"无法启动 {feature_name}:\n\n" + "\n".join(f"• {issue}" for issue in issues)
            
            # Different tips for different browsers
            if browser_type == 'bitbrowser':
                msg += f"\n\n请前往「配置向导」页面完成设置。\n\n💡 提示: 使用 BitBrowser 请确保:\n• BitBrowser 已打开并登录\n• 至少有一个浏览器配置\n• 至少有一个 Facebook 账户"
            else:
                msg += f"\n\n请前往「配置向导」页面完成设置。\n\n💡 提示: 使用 {browser_name} 请确保:\n• 浏览器已打开\n• API 密钥已配置\n• 至少有一个 Facebook 账户"
            
            reply = QMessageBox.warning(self, "配置不完整", msg, 
                                       QMessageBox.Ok | QMessageBox.Cancel)
            
            # Switch to config wizard if user clicks OK
            if reply == QMessageBox.Ok:
                if hasattr(self.ui, 'sidebarList'):
                    # Find config wizard index
                    for i in range(self.ui.sidebarList.count()):
                        item = self.ui.sidebarList.item(i)
                        if item and ("配置向导" in item.text() or "⚙️" in item.text()):
                            self.ui.sidebarList.setCurrentRow(i)
                            break
                if hasattr(self.ui, 'stackedPages'):
                    # Find config wizard page
                    for i in range(self.ui.stackedPages.count()):
                        widget = self.ui.stackedPages.widget(i)
                        if widget and (hasattr(widget, 'objectName') and 'config' in widget.objectName().lower()):
                            self.ui.stackedPages.setCurrentIndex(i)
                            break
                # Run validation in wizard if it exists
                if hasattr(self.ui, 'configWizardPage') and self.ui.configWizardPage:
                    try:
                        self.ui.configWizardPage.run_validation()
                    except:
                        pass
            return False
        
        return True
    
    def on_group_spider_start(self):
        """
        启动采集群组按钮
        获取界面中的参数保存到config中
        判断关键词是不是已经保存过了，如果都保存过了就不再启动线程了
        动态添加每个采集器对应的信息展示控件
        :return:
        """
        app_logger.log_button_click("采集群组-启动", "GroupSpider页面")
        
        # Validate setup first
        if not self.validate_setup("采集群组"):
            app_logger.log_validation("采集群组-配置检查", False, "配置验证失败")
            return
        app_logger.log_validation("采集群组-配置检查", True)
        doc: QTextDocument = self.ui.plainTextEditGroupWords.document()
        words = []
        # 搜集采集的关键词，如果采集过了，就不再采集了
        for i in range(self.ui.plainTextEditGroupWords.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            word = row.text()
            if word:
                # 检查此关键词是否已经采集过
                file_name = config.groups_table + tools.make_safe_filename(word) + '.txt'
                if os.path.exists(file_name):
                    self.print_to_tui(self.ui.textBrowserGroupSpider, f'关键词{word}已经采集过了！')
                    continue
                words.append(word)

        # 当每个关键词都采集过了，就不要再启动线程了，让重新输入关键词
        config.set_option('groups', 'words', json.dumps(words, ensure_ascii=False))
        if len(words) == 0:
            self.print_to_tui(self.ui.textBrowserGroupSpider, '所有关键词都采集过了，请重新输入群关键词')
            self.ui.plainTextEditGroupWords.clear()
            return

        # 收集页面中输入的参数，并保存到配置文件中
        config.set_option('main', 'account_nums', self.ui.lineEditGroupMaxThreadCount.text())

        # 获取可用的外部浏览器个数
        ads_ids = tools.get_ads_id(config.account_nums)
        # if len(ads_ids) == 0:
        #     QMessageBox.critical(self, '配置错误', 'facebook账号配置有误，国内IP不可用，请打开ads power客户端检查配置信息')
        #     return

        # elif len(ads_ids) < len(config.groups_words):
        #     QMessageBox.warning(self, '配置', f'没有足够的账号同时开启，配置同时开启[{config.groups_words}]个,可用账号[{len(ads_ids)}]个')
        # 确定需要开启多少个线程来处理请求
        thread_count = len(ads_ids) if len(ads_ids) < len(config.groups_words) else len(config.groups_words)

        # Calculate grid index: subtract 2 for ConfigWizardPage and EnhancedDashboard
        # Page 0 = ConfigWizard, Page 1 = Dashboard, Page 2 = Groups (gridLayout_0)
        current_page = self.ui.stackedPages.currentIndex()
        grid_index = current_page - 2  # Groups page is index 2, maps to gridLayout_0
        
        # Direct mapping for group spider
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_0')
        
        if not grid_layout:
            log.warning(f"Grid layout gridLayout_0 not found")
            QMessageBox.warning(self, "错误", "无法找到布局组件，请重启应用")
            return

        # Clear existing widgets from grid layout
        while grid_layout[0].count():
            item = grid_layout[0].takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 给每个处理请求的线程配置对应的流程展示控件，实时监控到请求被处理到哪一步了
        for i in range(thread_count):
            row = i // 2
            column = i % 2
            item = QTextBrowser()
            grid_layout[0].addWidget(item, row, column)

        self.group_stop_event = threading.Event()

        self.ms.update_control_status.emit([False, self.ui.stackedPages.currentIndex()])

        GroupSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=self.ui.stackedPages.currentIndex(),
            stop_event=self.group_stop_event, grid_layout=grid_layout[0]).start()

    def on_member_spider_start(self):
        app_logger.log_button_click("采集成员-启动", "MembersSpider页面")
        
        # Validate setup first
        if not self.validate_setup("采集成员"):
            app_logger.log_validation("采集成员-配置检查", False, "配置验证失败")
            return
        app_logger.log_validation("采集成员-配置检查", True)
        
        # 收集页面中输入的参数，并保存到配置文件中
        config.set_option('main', 'account_nums', self.ui.lineEditMemberMaxThreadCount.text())
        config.set_option('main', 'group_nums', self.ui.lineEditGroupCount.text())
        app_logger.log_config_change('main', 'account_nums', '', self.ui.lineEditMemberMaxThreadCount.text())
        app_logger.log_config_change('main', 'group_nums', '', self.ui.lineEditGroupCount.text())

        # 获取可用的外部浏览器个数
        # ads_ids = tools.get_ads_id(config.account_nums)

        # 确定需要开启多少个线程来处理请求
        thread_count = tools.get_greet_threading_count(config_from_newest=config)
        
        # Direct mapping for member spider - use gridLayout_1
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_1')
        
        if not grid_layout:
            log.warning(f"Grid layout gridLayout_1 not found")
            QMessageBox.warning(self, "错误", "无法找到布局组件，请重启应用")
            return
        
        # Clear existing widgets from grid layout
        while grid_layout[0].count():
            item = grid_layout[0].takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 给每个处理请求的线程配置对应的流程展示控件，实时监控到请求被处理到哪一步了
        for i in range(thread_count):
            row = i // 2
            column = i % 2
            item = QTextBrowser()
            grid_layout[0].addWidget(item, row, column)

        self.member_stop_event = threading.Event()
        self.ms.update_control_status.emit([False, self.ui.stackedPages.currentIndex()])

        MembersSpider(
            thread_count=thread_count, config=config, ui=self, ms=self.ms,
            tab_index=self.ui.stackedPages.currentIndex(),
            stop_event=self.member_stop_event, grid_layout=grid_layout[0]).start()

    def on_greets_spider_start(self):
        app_logger.log_button_click("私信成员-启动", "GreetsSpider页面")
        
        # Validate setup first
        if not self.validate_setup("私信成员"):
            app_logger.log_validation("私信成员-配置检查", False, "配置验证失败")
            return
        app_logger.log_validation("私信成员-配置检查", True)
        
        doc: QTextDocument = self.ui.plainTextEditGreetsContent.document()
        greets_content = []
        for i in range(self.ui.plainTextEditGreetsContent.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            if row.text():
                greets_content.append(row.text())
            # print(row.text())

        doc: QTextDocument = self.ui.plainTextEditGreetsImage.document()
        greets_image = []
        for i in range(self.ui.plainTextEditGreetsImage.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            if row.text():
                greets_image.append(row.text())
            # print(row.text())

        # 收集页面中输入的参数，并保存到配置文件中
        config.set_option('members', 'texts', json.dumps(greets_content, ensure_ascii=False))
        config.set_option('members', 'images', json.dumps(greets_image, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditGreetsMaxThreadCount.text())
        config.set_option('main', 'members_nums', self.ui.lineEditGreetsCount.text())
        config.set_option('main', 'member_timeout', self.ui.lineEditGreetsTimeout.text())
        
        # Get selected member file from UI
        selected_member_file = self.get_selected_member_file()
        if selected_member_file:
            # Save the selected file path to config for spider to use
            config.set_option('members', 'selected_file', selected_member_file)
            self.print_to_tui(self.ui.textBrowserGreetsSpider, f'使用选择的成员文件: {selected_member_file}')
        else:
            config.set_option('members', 'selected_file', '')

        # 确定需要开启多少个线程来处理请求
        thread_count = tools.get_greet_threading_count(config_from_newest=config)

        # Direct mapping for greets spider - use gridLayout_2
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_2')
        
        if not grid_layout:
            log.warning(f"Grid layout gridLayout_2 not found")
            QMessageBox.warning(self, "错误", "无法找到布局组件，请重启应用")
            return

        # Clear existing widgets from grid layout
        while grid_layout[0].count():
            item = grid_layout[0].takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 给每个处理请求的线程配置对应的流程展示控件，实时监控到请求被处理到哪一步了
        for i in range(thread_count):
            row = i // 2
            column = i % 2
            item = QTextBrowser()
            grid_layout[0].addWidget(item, row, column)

        self.greets_stop_event = threading.Event()
        self.ms.update_control_status.emit([False, self.ui.stackedPages.currentIndex()])

        GreetsSpider(
            thread_count=thread_count, config=config, ui=self, ms=self.ms,
            tab_index=self.ui.stackedPages.currentIndex(),
            stop_event=self.greets_stop_event, grid_layout=grid_layout[0], is_use_interval_timeout=True).start()

    def on_group_spider_stop(self):
        app_logger.log_button_click("采集群组-停止", "GroupSpider页面")
        if self.group_stop_event:
            self.group_stop_event.set()
            app_logger.log_spider_stop("GroupSpider", "用户点击停止")
            self.print_to_tui(self.ui.textBrowserGroupSpider, '正在停止...')
            # Delay re-enable to allow spider to finish, then clear stop_event
            QTimer.singleShot(1000, lambda: self._cleanup_after_stop(1, 'group'))
        else:
            app_logger.log_error("BUTTON_ERROR", "group_stop_event 为 None，无法停止")

    def on_member_spider_stop(self):
        app_logger.log_button_click("采集成员-停止", "MembersSpider页面")
        if self.member_stop_event:
            self.member_stop_event.set()
            app_logger.log_spider_stop("MembersSpider", "用户点击停止")
            self.print_to_tui(self.ui.textBrowserMembersSpider, '正在停止...')
            # Delay re-enable to allow spider to finish, then clear stop_event
            QTimer.singleShot(1000, lambda: self._cleanup_after_stop(2, 'member'))
        else:
            app_logger.log_error("BUTTON_ERROR", "member_stop_event 为 None，无法停止")

    def on_greets_spider_stop(self):
        app_logger.log_button_click("私信成员-停止", "GreetsSpider页面")
        if self.greets_stop_event:
            self.greets_stop_event.set()
            app_logger.log_spider_stop("GreetsSpider", "用户点击停止")
            self.print_to_tui(self.ui.textBrowserGreetsSpider, '正在停止...')
            # Delay re-enable to allow spider to finish, then clear stop_event
            QTimer.singleShot(1000, lambda: self._cleanup_after_stop(3, 'greets'))
        else:
            app_logger.log_error("BUTTON_ERROR", "greets_stop_event 为 None，无法停止")
    
    def _cleanup_after_stop(self, tab_index, spider_type):
        """Cleanup after spider stop - re-enable buttons and clear stop_event"""
        app_logger.log_action("CLEANUP", f"开始清理 {spider_type} spider", {"tab_index": tab_index})
        try:
            # Clear the stop_event so spider can start again
            if spider_type == 'group' and self.group_stop_event:
                self.group_stop_event.clear()
                self.group_stop_event = None
                app_logger.log_action("CLEANUP", "已清理 group_stop_event")
            elif spider_type == 'member' and self.member_stop_event:
                self.member_stop_event.clear()
                self.member_stop_event = None
                app_logger.log_action("CLEANUP", "已清理 member_stop_event")
            elif spider_type == 'greets' and self.greets_stop_event:
                self.greets_stop_event.clear()
                self.greets_stop_event = None
                app_logger.log_action("CLEANUP", "已清理 greets_stop_event")
            
            # Clear grid layout widgets
            self._clear_grid_layout(tab_index)
            
            # Re-enable buttons
            self._force_re_enable_buttons(tab_index)
            
            app_logger.log_action("CLEANUP", f"清理完成 {spider_type} spider", {"success": True})
        except Exception as e:
            app_logger.log_error("CLEANUP_ERROR", f"清理 {spider_type} 失败", e, {"tab_index": tab_index})
    
    def _clear_grid_layout(self, tab_index):
        """Clear all widgets from grid layout"""
        try:
            # Calculate grid index (subtract 1 for ConfigWizardPage at index 0)
            grid_index = tab_index - 1 if tab_index > 0 else 0
            grid_layouts = self.findChildren(QGridLayout, f'gridLayout_{grid_index}')
            
            if grid_layouts:
                grid_layout = grid_layouts[0]
                # Remove all widgets from grid layout
                while grid_layout.count():
                    item = grid_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                log.info(f"Cleared grid layout {grid_index}")
        except Exception as e:
            log.error(f"Error clearing grid layout: {e}")
    
    def _force_re_enable_buttons(self, tab_index):
        """Force re-enable buttons after stop is clicked"""
        app_logger.log_action("BUTTON_REENABLE", f"开始重新启用按钮", {"tab_index": tab_index})
        
        try:
            # Re-enable ALL start buttons across ALL pages/tabs
            # This ensures no button gets stuck disabled
            
            # Method 1: Re-enable buttons on the specific tab
            if hasattr(self.ui, 'stackedPages'):
                tab = self.ui.stackedPages.widget(tab_index)
                if tab:
                    for btn in tab.findChildren(QPushButton):
                        btn_name = btn.objectName().lower()
                        btn_text = btn.text()
                        if 'start' in btn_name or btn_text == '启动':
                            btn.setEnabled(True)
                            app_logger.log_action("BUTTON_ENABLED", f"启用按钮: {btn.objectName()}")
                        elif 'stop' in btn_name or btn_text == '停止':
                            btn.setEnabled(False)
            
            # Method 2: Also re-enable specific known buttons by name
            known_start_buttons = [
                'pushButtonGroupSpiderStart',
                'pushButtonMembersSpiderStart', 
                'pushButtonGreetsSpiderStart',
                'pushButtonGroupSpecifiedStart',
                'pushButtonMembersRapidStart',
                'pushButtonPostsSpiderStart',
                'pushButtonPagesSpiderStart',
            ]
            
            for btn_name in known_start_buttons:
                btn = self.findChild(QPushButton, btn_name)
                if btn:
                    btn.setEnabled(True)
                    app_logger.log_action("BUTTON_ENABLED", f"启用按钮: {btn_name}")
            
            # Method 3: Re-enable all sidebar items
            if hasattr(self.ui, 'sidebarList'):
                self.ui.sidebarList.setEnabled(True)
                for i in range(self.ui.sidebarList.count()):
                    item = self.ui.sidebarList.item(i)
                    if item:
                        item.setFlags(item.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                app_logger.log_action("SIDEBAR_ENABLED", "侧边栏已启用")
            
            # Method 4: Enable tab widget
            if hasattr(self.ui, 'tabWidget'):
                self.ui.tabWidget.setEnabled(True)
                for i in range(self.ui.tabWidget.count()):
                    self.ui.tabWidget.setTabEnabled(i, True)
            
            # Method 5: Enable stacked pages
            if hasattr(self.ui, 'stackedPages'):
                self.ui.stackedPages.setEnabled(True)
            
            app_logger.log_action("BUTTON_REENABLE", f"按钮重新启用完成", {"tab_index": tab_index, "success": True})
            log.info(f"Force re-enabled buttons for tab index {tab_index}")
            
        except Exception as e:
            app_logger.log_error("BUTTON_ERROR", f"重新启用按钮失败", e, {"tab_index": tab_index})
            log.error(f"Error re-enabling buttons: {e}")
    
    def reset_all_ui_controls(self):
        """Reset all UI controls to enabled state - emergency reset"""
        app_logger.log_action("UI_RESET", "开始重置所有UI控件")
        
        try:
            # Clear all stop events
            if hasattr(self, 'group_stop_event') and self.group_stop_event:
                self.group_stop_event.clear()
                self.group_stop_event = None
            if hasattr(self, 'member_stop_event') and self.member_stop_event:
                self.member_stop_event.clear()
                self.member_stop_event = None
            if hasattr(self, 'greets_stop_event') and self.greets_stop_event:
                self.greets_stop_event.clear()
                self.greets_stop_event = None
            
            # Enable all QPushButtons in the window
            for btn in self.findChildren(QPushButton):
                btn_name = btn.objectName().lower()
                if 'stop' in btn_name or btn.text() == '停止':
                    btn.setEnabled(False)
                else:
                    btn.setEnabled(True)
            
            # Enable sidebar
            if hasattr(self.ui, 'sidebarList'):
                self.ui.sidebarList.setEnabled(True)
                for i in range(self.ui.sidebarList.count()):
                    item = self.ui.sidebarList.item(i)
                    if item:
                        item.setFlags(item.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            # Enable tabs
            if hasattr(self.ui, 'tabWidget'):
                self.ui.tabWidget.setEnabled(True)
                for i in range(self.ui.tabWidget.count()):
                    self.ui.tabWidget.setTabEnabled(i, True)
            
            # Enable stacked pages
            if hasattr(self.ui, 'stackedPages'):
                self.ui.stackedPages.setEnabled(True)
            
            app_logger.log_action("UI_RESET", "UI控件重置完成", {"success": True})
            
        except Exception as e:
            app_logger.log_error("UI_RESET_ERROR", "UI重置失败", e)

    # New spider handlers
    def on_group_specified_spider_start(self):
        """Start FB Group Specified Collection"""
        # Validate setup first
        if not self.validate_setup("FB小组指定采集"):
            return
        
        # Get keywords from UI
        doc: QTextDocument = self.ui.plainTextEditGroupSpecifiedWords.document()
        words = []
        for i in range(self.ui.plainTextEditGroupSpecifiedWords.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            word = row.text().strip()
            if word:
                words.append(word)
        
        if not words:
            self.print_to_tui(self.ui.textBrowserGroupSpecified, '请输入关键词')
            return
        
        config.set_option('groups', 'words', json.dumps(words, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditGroupSpecifiedThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids) if len(ads_ids) < len(words) else len(words)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_3')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.group_specified_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabGroupSpecified)
        self.ms.update_control_status.emit([False, tab_index])
        
        GroupSpecifiedSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.group_specified_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_members_rapid_spider_start(self):
        """Start FB Group Member Rapid Collection"""
        # Validate setup first
        if not self.validate_setup("FB小组成员极速采集"):
            return
        
        config.set_option('main', 'account_nums', self.ui.lineEditMembersRapidThreadCount.text())
        config.set_option('main', 'group_nums', self.ui.lineEditMembersRapidGroupCount.text())
        thread_count = tools.get_greet_threading_count(config_from_newest=config)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_4')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.members_rapid_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabMembersRapid)
        self.ms.update_control_status.emit([False, tab_index])
        
        MembersRapidSpider(
            thread_count=thread_count, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.members_rapid_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_posts_spider_start(self):
        """Start FB Group Post Collection"""
        # Validate setup first
        if not self.validate_setup("FB小组帖子采集"):
            return
        
        config.set_option('main', 'account_nums', self.ui.lineEditPostsThreadCount.text())
        config.set_option('posts', 'groups_nums', self.ui.lineEditPostsGroupCount.text())
        thread_count = tools.get_greet_threading_count(config_from_newest=config)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_5')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.posts_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabPosts)
        self.ms.update_control_status.emit([False, tab_index])
        
        PostsSpider(
            thread_count=thread_count, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.posts_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_pages_spider_start(self):
        """Start FB Public Page Collection"""
        # Validate setup first
        if not self.validate_setup("FB公共主页采集"):
            return
        
        # Get keywords/URLs from UI
        doc: QTextDocument = self.ui.plainTextEditPagesKeywords.document()
        keywords = []
        urls = []
        for i in range(self.ui.plainTextEditPagesKeywords.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            text = row.text().strip()
            if text:
                if text.startswith('http'):
                    urls.append(text)
                else:
                    keywords.append(text)
        
        config.set_option('pages', 'keywords', json.dumps(keywords, ensure_ascii=False))
        config.set_option('pages', 'urls', json.dumps(urls, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditPagesThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_6')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.pages_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabPages)
        self.ms.update_control_status.emit([False, tab_index])
        
        PagesSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.pages_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_ins_followers_spider_start(self):
        """Start Instagram Follower Collection"""
        # Validate setup first
        if not self.validate_setup("INS用户粉丝采集"):
            return
        
        # Get usernames from UI
        doc: QTextDocument = self.ui.plainTextEditInsFollowersUsers.document()
        usernames = []
        for i in range(self.ui.plainTextEditInsFollowersUsers.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            username = row.text().strip().replace('@', '')
            if username:
                usernames.append(username)
        
        if not usernames:
            self.print_to_tui(self.ui.textBrowserInsFollowers, '请输入Instagram用户名')
            return
        
        config.set_option('instagram', 'target_users', json.dumps(usernames, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditInsFollowersThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids) if len(ads_ids) < len(usernames) else len(usernames)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_7')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.ins_followers_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabInsFollowers)
        self.ms.update_control_status.emit([False, tab_index])
        
        InstagramFollowersSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.ins_followers_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_ins_following_spider_start(self):
        """Start Instagram Following Collection"""
        # Validate setup first
        if not self.validate_setup("INS用户关注采集"):
            return
        # Get usernames from UI
        doc: QTextDocument = self.ui.plainTextEditInsFollowingUsers.document()
        usernames = []
        for i in range(self.ui.plainTextEditInsFollowingUsers.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            username = row.text().strip().replace('@', '')
            if username:
                usernames.append(username)
        
        if not usernames:
            self.print_to_tui(self.ui.textBrowserInsFollowing, '请输入Instagram用户名')
            return
        
        config.set_option('instagram', 'target_users', json.dumps(usernames, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditInsFollowingThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids) if len(ads_ids) < len(usernames) else len(usernames)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_8')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.ins_following_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabInsFollowing)
        self.ms.update_control_status.emit([False, tab_index])
        
        InstagramFollowingSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.ins_following_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_ins_profile_spider_start(self):
        """Start Instagram Profile Collection"""
        # Validate setup first
        if not self.validate_setup("INS用户简介采集"):
            return
        # Get usernames from UI
        doc: QTextDocument = self.ui.plainTextEditInsProfileUsers.document()
        usernames = []
        for i in range(self.ui.plainTextEditInsProfileUsers.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            username = row.text().strip().replace('@', '')
            if username:
                usernames.append(username)
        
        if not usernames:
            self.print_to_tui(self.ui.textBrowserInsProfile, '请输入Instagram用户名')
            return
        
        config.set_option('instagram', 'target_users', json.dumps(usernames, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditInsProfileThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids) if len(ads_ids) < len(usernames) else len(usernames)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_9')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.ins_profile_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabInsProfile)
        self.ms.update_control_status.emit([False, tab_index])
        
        InstagramProfileSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.ins_profile_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    def on_ins_reels_comments_spider_start(self):
        """Start Instagram Reels Comment Collection"""
        # Validate setup first
        if not self.validate_setup("INS-reels评论采集"):
            return
        # Get Reels URLs from UI
        doc: QTextDocument = self.ui.plainTextEditInsReelsCommentsUrls.document()
        urls = []
        for i in range(self.ui.plainTextEditInsReelsCommentsUrls.blockCount()):
            row: QTextBlock = doc.findBlockByLineNumber(i)
            url = row.text().strip()
            if url and 'instagram.com/reel/' in url:
                urls.append(url)
        
        if not urls:
            self.print_to_tui(self.ui.textBrowserInsReelsComments, '请输入Instagram Reels URL')
            return
        
        config.set_option('instagram', 'reels_urls', json.dumps(urls, ensure_ascii=False))
        config.set_option('main', 'account_nums', self.ui.lineEditInsReelsCommentsThreadCount.text())
        
        ads_ids = tools.get_ads_id(config.account_nums)
        thread_count = len(ads_ids) if len(ads_ids) < len(urls) else len(urls)
        
        grid_layout = self.findChildren(QGridLayout, 'gridLayout_10')
        if grid_layout:
            for i in range(thread_count):
                row = i // 2
                column = i % 2
                item = QTextBrowser()
                grid_layout[0].addWidget(item, row, column)
        
        self.ins_reels_comments_stop_event = threading.Event()
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabInsReelsComments)
        self.ms.update_control_status.emit([False, tab_index])
        
        InstagramReelsCommentsSpider(
            thread_count=thread_count, ads_ids=ads_ids, config=config, ui=self, ms=self.ms,
            tab_index=tab_index,
            stop_event=self.ins_reels_comments_stop_event, grid_layout=grid_layout[0] if grid_layout else None).start()

    # Stop handlers
    def on_group_specified_spider_stop(self):
        if self.group_specified_stop_event:
            self.group_specified_stop_event.set()

    def on_members_rapid_spider_stop(self):
        if self.members_rapid_stop_event:
            self.members_rapid_stop_event.set()

    def on_posts_spider_stop(self):
        if self.posts_stop_event:
            self.posts_stop_event.set()

    def on_pages_spider_stop(self):
        if self.pages_stop_event:
            self.pages_stop_event.set()

    def on_ins_followers_spider_stop(self):
        if self.ins_followers_stop_event:
            self.ins_followers_stop_event.set()

    def on_ins_following_spider_stop(self):
        if self.ins_following_stop_event:
            self.ins_following_stop_event.set()

    def on_ins_profile_spider_stop(self):
        if self.ins_profile_stop_event:
            self.ins_profile_stop_event.set()

    def on_ins_reels_comments_spider_stop(self):
        if self.ins_reels_comments_stop_event:
            self.ins_reels_comments_stop_event.set()

    # Automation feature handlers
    def on_auto_like_spider_start(self):
        """Start Auto Like"""
        feature_name = "自动点赞"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_like import AutoLikeSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_like_stop_event = threading.Event()
            self.auto_like_spider = AutoLikeSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_like_stop_event
            )
            self.auto_like_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动点赞已启动")
        except Exception as e:
            log.error(f"Error starting auto like: {e}")
            QMessageBox.critical(self, "错误", f"启动自动点赞失败: {str(e)}")
    
    def on_auto_like_spider_stop(self):
        if hasattr(self, 'auto_like_stop_event') and self.auto_like_stop_event:
            self.auto_like_stop_event.set()
    
    def on_auto_comment_spider_start(self):
        """Start Auto Comment"""
        feature_name = "自动评论"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_comment import AutoCommentSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_comment_stop_event = threading.Event()
            self.auto_comment_spider = AutoCommentSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_comment_stop_event
            )
            self.auto_comment_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动评论已启动")
        except Exception as e:
            log.error(f"Error starting auto comment: {e}")
            QMessageBox.critical(self, "错误", f"启动自动评论失败: {str(e)}")
    
    def on_auto_comment_spider_stop(self):
        if hasattr(self, 'auto_comment_stop_event') and self.auto_comment_stop_event:
            self.auto_comment_stop_event.set()
    
    def on_auto_follow_spider_start(self):
        """Start Auto Follow"""
        feature_name = "自动关注"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_follow import AutoFollowSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_follow_stop_event = threading.Event()
            self.auto_follow_spider = AutoFollowSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_follow_stop_event
            )
            self.auto_follow_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动关注已启动")
        except Exception as e:
            log.error(f"Error starting auto follow: {e}")
            QMessageBox.critical(self, "错误", f"启动自动关注失败: {str(e)}")
    
    def on_auto_follow_spider_stop(self):
        if hasattr(self, 'auto_follow_stop_event') and self.auto_follow_stop_event:
            self.auto_follow_stop_event.set()
    
    def on_auto_add_friend_spider_start(self):
        """Start Auto Add Friend"""
        feature_name = "自动添加好友"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_add_friend import AutoAddFriendSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_add_friend_stop_event = threading.Event()
            self.auto_add_friend_spider = AutoAddFriendSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_add_friend_stop_event
            )
            self.auto_add_friend_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动添加好友已启动")
        except Exception as e:
            log.error(f"Error starting auto add friend: {e}")
            QMessageBox.critical(self, "错误", f"启动自动添加好友失败: {str(e)}")
    
    def on_auto_add_friend_spider_stop(self):
        if hasattr(self, 'auto_add_friend_stop_event') and self.auto_add_friend_stop_event:
            self.auto_add_friend_stop_event.set()
    
    def on_auto_group_spider_start(self):
        """Start Auto Group"""
        feature_name = "群组自动化"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_group import AutoGroupSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_group_stop_event = threading.Event()
            self.auto_group_spider = AutoGroupSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_group_stop_event
            )
            self.auto_group_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "群组自动化已启动")
        except Exception as e:
            log.error(f"Error starting auto group: {e}")
            QMessageBox.critical(self, "错误", f"启动群组自动化失败: {str(e)}")
    
    def on_auto_group_spider_stop(self):
        if hasattr(self, 'auto_group_stop_event') and self.auto_group_stop_event:
            self.auto_group_stop_event.set()
    
    def on_auto_post_spider_start(self):
        """Start Auto Post"""
        feature_name = "自动发帖"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_auto_post import AutoPostSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_post_stop_event = threading.Event()
            self.auto_post_spider = AutoPostSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_post_stop_event
            )
            self.auto_post_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动发帖已启动")
        except Exception as e:
            log.error(f"Error starting auto post: {e}")
            QMessageBox.critical(self, "错误", f"启动自动发帖失败: {str(e)}")
    
    def on_auto_post_spider_stop(self):
        if hasattr(self, 'auto_post_stop_event') and self.auto_post_stop_event:
            self.auto_post_stop_event.set()
    
    def on_advanced_messaging_spider_start(self):
        """Start Advanced Messaging"""
        feature_name = "高级私信"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=True):
            return
        
        try:
            from spider.fb_advanced_messaging import AdvancedMessagingSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.advanced_messaging_stop_event = threading.Event()
            self.advanced_messaging_spider = AdvancedMessagingSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.advanced_messaging_stop_event
            )
            self.advanced_messaging_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "高级私信已启动")
        except Exception as e:
            log.error(f"Error starting advanced messaging: {e}")
            QMessageBox.critical(self, "错误", f"启动高级私信失败: {str(e)}")
    
    def on_advanced_messaging_spider_stop(self):
        if hasattr(self, 'advanced_messaging_stop_event') and self.advanced_messaging_stop_event:
            self.advanced_messaging_stop_event.set()
    
    def on_auto_register_spider_start(self):
        """Start Auto Register"""
        feature_name = "自动注册"
        if not self._validate_setup_and_start(feature_name, check_ads_power=True, check_accounts=False):
            return
        
        try:
            from spider.fb_auto_register import AutoRegisterSpider
            ads_ids = tools.get_ads_id(config.account_nums)
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
            
            self.auto_register_stop_event = threading.Event()
            self.auto_register_spider = AutoRegisterSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.auto_register_stop_event
            )
            self.auto_register_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "自动注册已启动")
        except Exception as e:
            log.error(f"Error starting auto register: {e}")
            QMessageBox.critical(self, "错误", f"启动自动注册失败: {str(e)}")
    
    def on_auto_register_spider_stop(self):
        if hasattr(self, 'auto_register_stop_event') and self.auto_register_stop_event:
            self.auto_register_stop_event.set()
    
    def on_contact_list_spider_start(self):
        """Start Contact List Generation"""
        feature_name = "联系人列表"
        # Contact list doesn't need AdsPower or accounts
        try:
            from spider.fb_contact_list import ContactListSpider
            ads_ids = tools.get_ads_id(1)  # Just need one for initialization
            thread_count = 1
            
            self.contact_list_stop_event = threading.Event()
            self.contact_list_spider = ContactListSpider(
                thread_count=thread_count,
                ads_ids=ads_ids,
                config=config,
                ui=self,
                ms=self.ms,
                tab_index=0,
                stop_event=self.contact_list_stop_event
            )
            self.contact_list_spider.start()
            tools.send_message_to_ui(self.ms, self.ui, "联系人列表生成已启动")
        except Exception as e:
            log.error(f"Error starting contact list: {e}")
            QMessageBox.critical(self, "错误", f"启动联系人列表生成失败: {str(e)}")
    
    def on_contact_list_spider_stop(self):
        if hasattr(self, 'contact_list_stop_event') and self.contact_list_stop_event:
            self.contact_list_stop_event.set()

    def bypass_activation(self):
        """Bypass activation and go directly to main app"""
        # Set a fake activation code to prevent errors
        if not config.app_code:
            config.set_option('main', 'app_code', 'BYPASSED')
        
        # Skip directly to main app (page 1)
        self.switch_page(1)
        self.invalidate_seconds = None  # No expiration
        self.update_window_title()
        log.info("Activation bypassed - Application unlocked")
    
    def on_verify(self, check_pass):
        # BYPASS: Always allow access
        self.bypass_activation()
        return True
        
        # Original code below (disabled)
        code = (self.ui.lineEditCode.text()).strip()
        if not check_pass:
            self.ms.text_print.emit(self.ui.textBrowserVerifyMessage, '验证中...')
            # self.print_to_tui(self.ui.textBrowserVerifyMessage, '验证中...')

            ads_key = (self.ui.lineEditAdsKey.text()).strip()
            if not ads_key:
                self.print_to_tui(self.ui.textBrowserVerifyMessage, '请输入adsPower Global浏览器KEY')
                QMessageBox.critical(self, '必填', '请输入adsPower Global浏览器key')
                return False

            config.set_option('ads', 'key', ads_key)

            # 输入框是否为空
            if not code:
                self.print_to_tui(self.ui.textBrowserVerifyMessage, '请输入激活码')
                QMessageBox.critical(self, '必填', '请输入激活码')
                return False

            install_location = self.ui.lineEditInstallLocation.text().strip()
            if not install_location:
                self.print_to_tui(self.ui.textBrowserVerifyMessage, '请选择adsPower Global浏览器程序地址')
                QMessageBox.critical(self, '必填', '请选择adsPower Global浏览器程序地址')
                return False

            if not os.path.exists(install_location):
                self.print_to_tui(self.ui.textBrowserVerifyMessage, 'adsPower Global浏览器程序不存在')
                QMessageBox.critical(self, '验证', 'adsPower Global浏览器程序不存在，请重新选择')
                return False

            config.set_option('ads', 'service_app_path', install_location)

            # 执行shell指令
            def run():
                check_pass = True
                try:
                    res = requests.get(url=config.activator_service, timeout=5)
                    if not (res.status_code == 200):
                        self.ms.text_print.emit(self.ui.textBrowserVerifyMessage,
                                                f'本机连接服务器网络不通，请使用浏览器访问地址{config.activator_service},检查本机网络')
                        check_pass = False
                    else:
                        self.ms.text_print.emit(self.ui.textBrowserVerifyMessage,
                                                f'请求{config.activator_service}成功')
                except Exception as e:
                    log.error(e)
                    self.ms.text_print.emit(self.ui.textBrowserVerifyMessage,
                                            f'本机连接服务器网络不通，请使用浏览器访问地址{config.activator_service},检查本机网络')
                    check_pass = False

                is_valid_key = tools.valid_ads_service_key()
                if is_valid_key['status'] == -1:
                    self.ms.text_print.emit(self.ui.textBrowserVerifyMessage,
                                            f'请输入可用的adsPower Global浏览器KEY，{is_valid_key["message"]}')
                    check_pass = False
                else:
                    self.ms.text_print.emit(self.ui.textBrowserVerifyMessage, is_valid_key["message"])

                if check_pass:
                    self.ms.text_print.emit(self.ui.textBrowserVerifyMessage, '连接服务器中...')
                    self.ms.update_activate.emit(check_pass)

            # 创建线程执行函数
            t1 = Thread(target=run)
            print("start")
            t1.start()
        else:
            # 获取机器码和激活码，拼接之后访问接口验证激活码状态
            params = parse.urlencode({
                'machine': des.encryption(self.ui.lineEditMyMachine.text()),
                'verify_code': code
            })

            url = f'{config.activator_service}/verify?{params}'
            try:
                res = requests.get(url).json()
            except Exception as e:
                log.error(e)
                self.print_to_tui(self.ui.textBrowserVerifyMessage, '服务器请求异常,请检查网络')
                return False

            if res['code'] == -1:
                # 验证信息打印
                self.print_to_tui(self.ui.textBrowserVerifyMessage, res['message'])
                self.switch_page(0)
            elif res['code'] == -2:
                # 弹出信息，确认是否换绑，并发送请求
                self.print_to_tui(self.ui.textBrowserVerifyMessage, '服务器请求是否解绑当前激活码，并绑定到本机...')
                ret = QMessageBox().question(self, '解绑', res['message'])
                if ret == QMessageBox.Yes:
                    url = f'{url}&op=1'  # 点击了是按钮，确认换绑
                    res = requests.get(url).json()

                    if res['code'] == 0:
                        self.invalidate_seconds = int(res['invalid_seconds'])

                    # 保存验证码，方便下次使用
                    config.set_option('main', 'app_code', code)
                    # 验证成功就直接跳转页面
                    self.switch_page(1)

                    self.update_window_title()

                    process = mp.Process(target=ProcessCheckCode.main, args=(self.queue,))
                    process.daemon = True
                    process.start()
                    log.info(f'当前启动的子进程id:{process.pid}')
            else:
                if res['code'] == 0:
                    self.invalidate_seconds = res['invalid_seconds']

                # 保存验证码，方便下次使用
                config.set_option('main', 'app_code', code)
                # 验证成功就直接跳转页面
                self.switch_page(1)

                self.update_window_title()

                process = mp.Process(target=ProcessCheckCode.main, args=(self.queue,))
                process.daemon = True
                process.start()
                log.info(f'当前启动的子进程id:{process.pid}')

        return

    def update_window_title(self):
        # BYPASS: Always show unlocked title
        self.setWindowTitle('Facebook营销  (已激活)')
        
        # Original code below (disabled)
        # if config.app_code:
        #     if self.invalidate_seconds:
        #         # 每秒减去一秒，获得最新的相差的秒数
        #         self.invalidate_seconds -= 1
        #         # 更新时间 剩余可用 X时X分X秒
        #         m, s = divmod(self.invalidate_seconds, 60)
        #         h, m = divmod(m, 60)
        #
        #         self.setWindowTitle(f'Facebook营销  (剩余可用 {"%02d:%02d:%02d" % (h, m, s)})')
        #         if self.invalidate_seconds <= 0:
        #             self.Timer.stop()
        #             # 验证信息打印
        #             self.print_to_tui(self.ui.textBrowserVerifyMessage, '激活码已经过期，请联系管理员重新获取！')
        #             self.switch_page(0)
        #     else:
        #         self.setWindowTitle('Facebook营销  (未注册)')
        # else:
        #     self.setWindowTitle('Facebook营销  (未注册)')

    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

    def on_sidebar_changed(self, index):
        """Handle sidebar list selection change"""
        # Get page name for logging
        page_name = "Unknown"
        if hasattr(self.ui, 'sidebarList') and self.ui.sidebarList.item(index):
            page_name = self.ui.sidebarList.item(index).text()
        app_logger.log_ui_event("PAGE_CHANGE", page_name, {"index": index})
        
        # Update both stacked widget and tab widget for compatibility
        if hasattr(self.ui, 'stackedPages'):
            self.ui.stackedPages.setCurrentIndex(index)
        self.ui.tabWidget.setCurrentIndex(index)
        self.tab_change(index)

    def tab_change(self, index):
        # print(f'pre tab index:{str(index)}')
        tooltip = self.ui.tabWidget.tabToolTip(index)
        if tooltip:
            self.ui.tabWidget.setCurrentIndex(self.current_tab_index)
            if hasattr(self.ui, 'sidebarList'):
                self.ui.sidebarList.setCurrentRow(self.current_tab_index)
        else:
            self.current_tab_index = index

        # print(f'current_index:{str(self.ui.stackedPages.currentIndex())}')
        if self.ui.stackedPages.currentIndex() == 2:
            # 执行清理重复成员链接的功能
            def run():
                tools.unique_member(dir=config.members_table, unique_key='member_link')

            # 使用单独的线程来做这个清理的事情
            Thread(target=run).start()

    def tab_clicked(self, index):
        # print(f'clicked tab index:{str(index)}')

        if index == 1 or index == 2:
            if not (os.path.exists(config.groups_table) and len(os.listdir(config.groups_table)) > 0):
                self.warning('请先采集群组！')
                return
            else:
                self.ui.tabWidget.setTabToolTip(1, '')

            if index == 2:
                # 如果member文件夹下有文件，那tab2就可以点击
                if not (os.path.exists(config.members_table) and len(os.listdir(config.members_table)) > 0):
                    self.warning('请先采集群成员！')
                    return
                else:
                    self.ui.tabWidget.setTabToolTip(2, '')

    def warning(self, message):
        messagebox = QMessageBox(self)
        messagebox.setWindowTitle("请稍等2秒")
        # messagebox.setText("wait (closing automatically in {0} secondes.)".format(3))
        messagebox.setText(message)
        messagebox.setStandardButtons(messagebox.NoButton)
        self.timer2 = QTimer()
        self.time_to_wait = 0

        def close_messagebox(e):
            e.accept()
            self.timer2.stop()
            self.time_to_wait = 0

        def decompte():
            # messagebox.setText("wait (closing automatically in {0} secondes.)".format(self.time_to_wait))
            # messagebox.setText(message)
            if self.time_to_wait <= 0:
                messagebox.closeEvent = close_messagebox
                messagebox.close()
            self.time_to_wait -= 1

        self.timer2.timeout.connect(decompte)
        self.timer2.start(1000)
        messagebox.exec_()

    def check_queue_data(self):
        # BYPASS: Disable activation check queue
        # Original code disabled to bypass activation validation
        pass
        
        # Original code below (disabled)
        # def check_data():
        #     while True:
        #         tools.delay_time(0.002)  # 防止cpu占用率太高
        #         try:
        #             if not self.queue.empty():
        #                 flag = self.queue.get()
        #                 if not flag:
        #                     # 提示当前机器绑定的激活码已经不可用，请检查是否换绑机器或直接联系管理员
        #                     # QMessageBox.critical(self, '验证', '当前机器绑定的激活码已经不可用，请检查是否换绑机器或直接联系管理员')
        #                     self.Timer.stop()
        #                     self.on_group_spider_stop()
        #                     self.on_member_spider_stop()
        #                     self.on_greets_spider_stop()
        #                     # 验证信息打印
        #                     self.print_to_tui(self.ui.textBrowserVerifyMessage, '当前机器绑定的激活码已经不可用，请检查是否换绑机器或直接联系管理员')
        #                     self.switch_page(0)
        #                     break
        #         except BaseException as e:
        #             print('# Queue Receiver Exception:', e)
        #
        # if self.queue is not None:
        #     Thread(target=check_data, daemon=True).start()

    def closeEvent(self, event):
        """Handle application close - auto-save logs and notify user"""
        app_logger.log_action("APP_CLOSE", "用户请求关闭应用")
        
        # AUTO-SAVE logs first (so they're never lost)
        try:
            log_file, json_file = app_logger.save_logs()
            
            # Get session summary
            summary = app_logger.get_session_summary()
            
            # Get absolute paths for display
            abs_log_dir = os.path.abspath(app_logger.default_log_dir)
            
            # Show info message with log location
            msg = QMessageBox(self)
            msg.setWindowTitle("📊 日志已保存 - Logs Saved")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"""
<h3>✅ 会话日志已自动保存</h3>

<p><b>会话信息:</b></p>
<ul>
<li>会话ID: {summary['session_id']}</li>
<li>运行时长: {summary['duration_formatted']}</li>
<li>总操作数: {summary['total_actions']}</li>
<li>错误数量: {summary['total_errors']}</li>
</ul>

<p><b>日志文件位置:</b></p>
<p style="background-color: #f0f0f0; padding: 10px; font-family: monospace;">
{abs_log_dir}
</p>

<p><b>如何发送日志给技术支持:</b></p>
<ol>
<li>打开文件夹: {abs_log_dir}</li>
<li>找到文件: session_{summary['session_id']}.log</li>
<li>将此文件发送给我们</li>
</ol>
""")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Open)
            msg.button(QMessageBox.Open).setText("📂 打开日志文件夹")
            msg.button(QMessageBox.Ok).setText("✓ 关闭应用")
            
            result = msg.exec_()
            
            # If user clicks "Open folder"
            if result == QMessageBox.Open:
                import subprocess
                import platform
                if platform.system() == 'Windows':
                    subprocess.Popen(['explorer', abs_log_dir])
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', abs_log_dir])
                else:
                    subprocess.Popen(['xdg-open', abs_log_dir])
            
        except Exception as e:
            # If saving fails, still allow close but show error
            QMessageBox.warning(
                self,
                "日志保存失败",
                f"无法保存日志文件:\n{str(e)}\n\n应用将继续关闭。"
            )
        
        event.accept()


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()
    # window.ui.show()
    window.show()
    # 运行应用，并监听事件
    sys.exit(app.exec_())
