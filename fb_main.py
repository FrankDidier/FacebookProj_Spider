# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fb_main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

# Import compatibility layer for PySide6 before any PySide2 imports
import pyside2_compat
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1086, 907)
        MainWindow.setStyleSheet(u"QLabel{\n"
"	font:10pt \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"}\n"
"\n"
"QTabBar::tab:first{\n"
"	font: 11pt \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"	border: 1px  solid ;\n"
"	border-top-left-radius:8px;\n"
"	border-top-right-radius:8px;\n"
"	border-color: #ecf1f2;\n"
"	width: 200px;\n"
" 	height: 35px;\n"
"	margin-left:2px;\n"
"	color: rgb(102, 102, 102);\n"
"\n"
"	background-color: rgb(236, 241, 242);\n"
"\n"
"\n"
"}\n"
"QTabBar::tab{\n"
"	font: 11pt \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"	border: 1px  solid ;\n"
"	border-top-left-radius:8px;\n"
"	border-top-right-radius:8px;\n"
"	border-color: rgb(236, 241, 242);\n"
"	width: 200px;\n"
" 	height: 35px;\n"
"	color: rgb(102, 102, 102);\n"
"	background-color: rgb(236, 241, 242);\n"
"	\n"
"}\n"
"QTabBar::tab:selected {\n"
"	font: 11pt \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"	font-weight:bold;\n"
"	background: #5e98ea;\n"
"	color: white;\n"
"	border-top-left-radius:8px;\n"
"	border-top-right-radius:8px;\n"
"	width: 200px;\n"
" 	height: 35px;\n"
"	background-color: #5e98ea;\n"
"	border"
                        "-color: #5e98ea;\n"
"}\n"
"\n"
"")
        MainWindow.setTabShape(QTabWidget.Rounded)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setFrameShape(QFrame.NoFrame)
        self.stackedWidget.setFrameShadow(QFrame.Plain)
        self.stackedWidget.setLineWidth(0)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setStyleSheet(u"")
        self.verticalLayout_3 = QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_12 = QLabel(self.page)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_16.addWidget(self.label_12)

        self.lineEditMyMachine = QLineEdit(self.page)
        self.lineEditMyMachine.setObjectName(u"lineEditMyMachine")
        self.lineEditMyMachine.setEnabled(True)
        self.lineEditMyMachine.setReadOnly(True)

        self.horizontalLayout_16.addWidget(self.lineEditMyMachine)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_15)

        self.horizontalLayout_16.setStretch(0, 3)
        self.horizontalLayout_16.setStretch(1, 10)
        self.horizontalLayout_16.setStretch(2, 19)

        self.verticalLayout_3.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_15 = QLabel(self.page)
        self.label_15.setObjectName(u"label_15")

        self.horizontalLayout_17.addWidget(self.label_15)

        self.lineEditAdsKey = QLineEdit(self.page)
        self.lineEditAdsKey.setObjectName(u"lineEditAdsKey")

        self.horizontalLayout_17.addWidget(self.lineEditAdsKey)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_22)

        self.horizontalLayout_17.setStretch(0, 3)
        self.horizontalLayout_17.setStretch(1, 12)
        self.horizontalLayout_17.setStretch(2, 17)

        self.verticalLayout_3.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_16 = QLabel(self.page)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_11.addWidget(self.label_16)

        self.lineEditInstallLocation = QLineEdit(self.page)
        self.lineEditInstallLocation.setObjectName(u"lineEditInstallLocation")

        self.horizontalLayout_11.addWidget(self.lineEditInstallLocation)

        self.pushButtonSelectInstallLocation = QPushButton(self.page)
        self.pushButtonSelectInstallLocation.setObjectName(u"pushButtonSelectInstallLocation")

        self.horizontalLayout_11.addWidget(self.pushButtonSelectInstallLocation)

        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_23)

        self.horizontalLayout_11.setStretch(0, 3)
        self.horizontalLayout_11.setStretch(1, 18)
        self.horizontalLayout_11.setStretch(2, 1)
        self.horizontalLayout_11.setStretch(3, 9)

        self.verticalLayout_3.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_10 = QLabel(self.page)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_9.addWidget(self.label_10)

        self.lineEditCode = QLineEdit(self.page)
        self.lineEditCode.setObjectName(u"lineEditCode")

        self.horizontalLayout_9.addWidget(self.lineEditCode)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_12)

        self.horizontalLayout_9.setStretch(0, 3)
        self.horizontalLayout_9.setStretch(1, 27)
        self.horizontalLayout_9.setStretch(2, 2)

        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_14)

        self.pushButtonVerify = QPushButton(self.page)
        self.pushButtonVerify.setObjectName(u"pushButtonVerify")

        self.horizontalLayout_10.addWidget(self.pushButtonVerify)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_13)


        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.line_7 = QFrame(self.page)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.HLine)
        self.line_7.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line_7)

        self.textBrowserVerifyMessage = QTextBrowser(self.page)
        self.textBrowserVerifyMessage.setObjectName(u"textBrowserVerifyMessage")
        self.textBrowserVerifyMessage.setEnabled(False)

        self.verticalLayout_3.addWidget(self.textBrowserVerifyMessage)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 1)
        self.verticalLayout_3.setStretch(3, 1)
        self.verticalLayout_3.setStretch(4, 1)
        self.verticalLayout_3.setStretch(5, 1)
        self.verticalLayout_3.setStretch(6, 25)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setStyleSheet(u"")
        self.horizontalLayout_main = QHBoxLayout(self.page_2)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_main.setSpacing(0)
        
        # Create sidebar list widget for vertical navigation
        self.sidebarList = QListWidget(self.page_2)
        self.sidebarList.setObjectName(u"sidebarList")
        self.sidebarList.setMaximumWidth(200)
        self.sidebarList.setMinimumWidth(180)
        self.sidebarList.setStyleSheet(u"""
            QListWidget {
                background-color: #2b2b2b;
                color: white;
                border: none;
                font-size: 12pt;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #5e98ea;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Create stacked widget to hold all pages
        self.stackedPages = QStackedWidget(self.page_2)
        self.stackedPages.setObjectName(u"stackedPages")
        
        self.horizontalLayout_main.addWidget(self.sidebarList, 0)
        self.horizontalLayout_main.addWidget(self.stackedPages, 1)
        
        # Keep tabWidget for compatibility but hide it
        self.tabWidget = QTabWidget(self.page_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.hide()  # Hide the tab widget, we'll use stacked widget instead
        self.tabGroupSpider = QWidget()
        self.tabGroupSpider.setObjectName(u"tabGroupSpider")
        self.verticalLayout_12 = QVBoxLayout(self.tabGroupSpider)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.tabGroupSpider)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label)

        self.lineEditGroupMaxThreadCount = QLineEdit(self.tabGroupSpider)
        self.lineEditGroupMaxThreadCount.setObjectName(u"lineEditGroupMaxThreadCount")
        self.lineEditGroupMaxThreadCount.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.lineEditGroupMaxThreadCount)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label_2 = QLabel(self.tabGroupSpider)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.plainTextEditGroupWords = QPlainTextEdit(self.tabGroupSpider)
        self.plainTextEditGroupWords.setObjectName(u"plainTextEditGroupWords")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEditGroupWords.sizePolicy().hasHeightForWidth())
        self.plainTextEditGroupWords.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.plainTextEditGroupWords)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_24)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.pushButtonGroupSpiderStart = QPushButton(self.tabGroupSpider)
        self.pushButtonGroupSpiderStart.setObjectName(u"pushButtonGroupSpiderStart")

        self.verticalLayout_9.addWidget(self.pushButtonGroupSpiderStart)

        self.pushButtonGroupSpiderStop = QPushButton(self.tabGroupSpider)
        self.pushButtonGroupSpiderStop.setObjectName(u"pushButtonGroupSpiderStop")

        self.verticalLayout_9.addWidget(self.pushButtonGroupSpiderStop)


        self.horizontalLayout_2.addLayout(self.verticalLayout_9)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 2)
        self.horizontalLayout_2.setStretch(3, 1)
        self.horizontalLayout_2.setStretch(4, 5)
        self.horizontalLayout_2.setStretch(6, 1)
        self.horizontalLayout_2.setStretch(7, 5)

        self.verticalLayout_12.addLayout(self.horizontalLayout_2)

        self.groupBox_2 = QGroupBox(self.tabGroupSpider)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.textBrowserGroupSpider = QTextBrowser(self.groupBox_2)
        self.textBrowserGroupSpider.setObjectName(u"textBrowserGroupSpider")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        # PySide6 compatibility: use QFont.Weight enum instead of integer
        try:
            font.setWeight(QFont.Weight.Bold)
        except (AttributeError, TypeError):
            # Fallback for PySide2 or if enum not available
            try:
                font.setWeight(75)
            except:
                pass
        self.textBrowserGroupSpider.setFont(font)

        self.horizontalLayout.addWidget(self.textBrowserGroupSpider)

        self.line_2 = QFrame(self.groupBox_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line_2)

        self.gridLayout_0 = QGridLayout()
        self.gridLayout_0.setObjectName(u"gridLayout_0")

        self.horizontalLayout.addLayout(self.gridLayout_0)

        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 11)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_12.addWidget(self.groupBox_2)

        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 16)
        self.tabWidget.addTab(self.tabGroupSpider, "")
        # Configuration Wizard Page (First item)
        try:
            from config_wizard import ConfigWizardPage
            self.configWizardPage = ConfigWizardPage()
            self.configWizardPage.setObjectName(u"configWizardPage")
            self.stackedPages.addWidget(self.configWizardPage)
            self.sidebarList.addItem("⚙️ 配置向导")
        except Exception as e:
            # If config wizard fails to load, skip it
            print(f"Warning: Could not load config wizard: {e}")
        
        self.stackedPages.addWidget(self.tabGroupSpider)
        self.sidebarList.addItem("采集群组")
        self.tabMembersSpider = QWidget()
        self.tabMembersSpider.setObjectName(u"tabMembersSpider")
        self.verticalLayout_10 = QVBoxLayout(self.tabMembersSpider)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        
        # File selector row for loading group links
        self.horizontalLayout_MemberFile = QHBoxLayout()
        self.horizontalLayout_MemberFile.setObjectName(u"horizontalLayout_MemberFile")
        self.label_MemberFile = QLabel(self.tabMembersSpider)
        self.label_MemberFile.setObjectName(u"label_MemberFile")
        self.label_MemberFile.setText("群组链接文件:")
        self.label_MemberFile.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.horizontalLayout_MemberFile.addWidget(self.label_MemberFile)
        
        self.comboBoxMemberGroupFile = QComboBox(self.tabMembersSpider)
        self.comboBoxMemberGroupFile.setObjectName(u"comboBoxMemberGroupFile")
        self.comboBoxMemberGroupFile.setMinimumWidth(200)
        self.horizontalLayout_MemberFile.addWidget(self.comboBoxMemberGroupFile)
        
        self.pushButtonMemberRefreshFiles = QPushButton(self.tabMembersSpider)
        self.pushButtonMemberRefreshFiles.setObjectName(u"pushButtonMemberRefreshFiles")
        self.pushButtonMemberRefreshFiles.setText("刷新")
        self.horizontalLayout_MemberFile.addWidget(self.pushButtonMemberRefreshFiles)
        
        self.pushButtonMemberBrowseFile = QPushButton(self.tabMembersSpider)
        self.pushButtonMemberBrowseFile.setObjectName(u"pushButtonMemberBrowseFile")
        self.pushButtonMemberBrowseFile.setText("浏览...")
        self.horizontalLayout_MemberFile.addWidget(self.pushButtonMemberBrowseFile)
        
        self.horizontalLayout_MemberFile.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.verticalLayout_10.addLayout(self.horizontalLayout_MemberFile)
        
        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_3 = QLabel(self.tabMembersSpider)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_18.addWidget(self.label_3)

        self.lineEditMemberMaxThreadCount = QLineEdit(self.tabMembersSpider)
        self.lineEditMemberMaxThreadCount.setObjectName(u"lineEditMemberMaxThreadCount")

        self.horizontalLayout_18.addWidget(self.lineEditMemberMaxThreadCount)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_9)

        self.label_4 = QLabel(self.tabMembersSpider)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_18.addWidget(self.label_4)

        self.lineEditGroupCount = QLineEdit(self.tabMembersSpider)
        self.lineEditGroupCount.setObjectName(u"lineEditGroupCount")

        self.horizontalLayout_18.addWidget(self.lineEditGroupCount)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_10)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButtonMembersSpiderStart = QPushButton(self.tabMembersSpider)
        self.pushButtonMembersSpiderStart.setObjectName(u"pushButtonMembersSpiderStart")

        self.verticalLayout_2.addWidget(self.pushButtonMembersSpiderStart)

        self.pushButtonMembersSpiderStop = QPushButton(self.tabMembersSpider)
        self.pushButtonMembersSpiderStop.setObjectName(u"pushButtonMembersSpiderStop")

        self.verticalLayout_2.addWidget(self.pushButtonMembersSpiderStop)


        self.horizontalLayout_18.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_11)

        self.horizontalLayout_18.setStretch(0, 1)
        self.horizontalLayout_18.setStretch(1, 2)
        self.horizontalLayout_18.setStretch(2, 1)
        self.horizontalLayout_18.setStretch(3, 1)
        self.horizontalLayout_18.setStretch(4, 2)
        self.horizontalLayout_18.setStretch(5, 1)
        self.horizontalLayout_18.setStretch(6, 1)
        self.horizontalLayout_18.setStretch(7, 3)

        self.verticalLayout_10.addLayout(self.horizontalLayout_18)

        self.groupBox_3 = QGroupBox(self.tabMembersSpider)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.textBrowserMembersSpider = QTextBrowser(self.groupBox_3)
        self.textBrowserMembersSpider.setObjectName(u"textBrowserMembersSpider")
        self.textBrowserMembersSpider.setFont(font)

        self.horizontalLayout_5.addWidget(self.textBrowserMembersSpider)

        self.line_4 = QFrame(self.groupBox_3)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_5.addWidget(self.line_4)

        self.gridLayout_1 = QGridLayout()
        self.gridLayout_1.setObjectName(u"gridLayout_1")

        self.horizontalLayout_5.addLayout(self.gridLayout_1)

        self.horizontalLayout_5.setStretch(0, 4)
        self.horizontalLayout_5.setStretch(1, 1)
        self.horizontalLayout_5.setStretch(2, 11)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_5)


        self.verticalLayout_10.addWidget(self.groupBox_3)

        self.verticalLayout_10.setStretch(0, 1)
        self.verticalLayout_10.setStretch(1, 16)
        self.tabWidget.addTab(self.tabMembersSpider, "")
        self.stackedPages.addWidget(self.tabMembersSpider)
        self.sidebarList.addItem("采集成员")
        self.tabGreetsSpider = QWidget()
        self.tabGreetsSpider.setObjectName(u"tabGreetsSpider")
        self.verticalLayout_11 = QVBoxLayout(self.tabGreetsSpider)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        
        # File selector row for loading member data
        self.horizontalLayout_GreetsFile = QHBoxLayout()
        self.horizontalLayout_GreetsFile.setObjectName(u"horizontalLayout_GreetsFile")
        self.label_GreetsFile = QLabel(self.tabGreetsSpider)
        self.label_GreetsFile.setObjectName(u"label_GreetsFile")
        self.label_GreetsFile.setText("成员数据文件:")
        self.label_GreetsFile.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.horizontalLayout_GreetsFile.addWidget(self.label_GreetsFile)
        
        self.comboBoxGreetsMemberFile = QComboBox(self.tabGreetsSpider)
        self.comboBoxGreetsMemberFile.setObjectName(u"comboBoxGreetsMemberFile")
        self.comboBoxGreetsMemberFile.setMinimumWidth(200)
        self.horizontalLayout_GreetsFile.addWidget(self.comboBoxGreetsMemberFile)
        
        self.pushButtonGreetsRefreshFiles = QPushButton(self.tabGreetsSpider)
        self.pushButtonGreetsRefreshFiles.setObjectName(u"pushButtonGreetsRefreshFiles")
        self.pushButtonGreetsRefreshFiles.setText("刷新")
        self.horizontalLayout_GreetsFile.addWidget(self.pushButtonGreetsRefreshFiles)
        
        self.pushButtonGreetsBrowseFile = QPushButton(self.tabGreetsSpider)
        self.pushButtonGreetsBrowseFile.setObjectName(u"pushButtonGreetsBrowseFile")
        self.pushButtonGreetsBrowseFile.setText("浏览...")
        self.horizontalLayout_GreetsFile.addWidget(self.pushButtonGreetsBrowseFile)
        
        self.horizontalLayout_GreetsFile.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.verticalLayout_11.addLayout(self.horizontalLayout_GreetsFile)
        
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_5 = QLabel(self.tabGreetsSpider)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_6.addWidget(self.label_5)

        self.lineEditGreetsMaxThreadCount = QLineEdit(self.tabGreetsSpider)
        self.lineEditGreetsMaxThreadCount.setObjectName(u"lineEditGreetsMaxThreadCount")

        self.horizontalLayout_6.addWidget(self.lineEditGreetsMaxThreadCount)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.label_6 = QLabel(self.tabGreetsSpider)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lineEditGreetsCount = QLineEdit(self.tabGreetsSpider)
        self.lineEditGreetsCount.setObjectName(u"lineEditGreetsCount")

        self.horizontalLayout_6.addWidget(self.lineEditGreetsCount)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)

        self.label_7 = QLabel(self.tabGreetsSpider)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_6.addWidget(self.label_7)

        self.lineEditGreetsTimeout = QLineEdit(self.tabGreetsSpider)
        self.lineEditGreetsTimeout.setObjectName(u"lineEditGreetsTimeout")

        self.horizontalLayout_6.addWidget(self.lineEditGreetsTimeout)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 2)
        self.horizontalLayout_6.setStretch(2, 1)
        self.horizontalLayout_6.setStretch(3, 2)
        self.horizontalLayout_6.setStretch(4, 2)
        self.horizontalLayout_6.setStretch(5, 1)
        self.horizontalLayout_6.setStretch(6, 3)
        self.horizontalLayout_6.setStretch(7, 3)
        self.horizontalLayout_6.setStretch(8, 10)

        self.verticalLayout_11.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_8 = QLabel(self.tabGreetsSpider)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)

        self.horizontalLayout_8.addWidget(self.label_8)

        self.plainTextEditGreetsContent = QPlainTextEdit(self.tabGreetsSpider)
        self.plainTextEditGreetsContent.setObjectName(u"plainTextEditGreetsContent")
        sizePolicy.setHeightForWidth(self.plainTextEditGreetsContent.sizePolicy().hasHeightForWidth())
        self.plainTextEditGreetsContent.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.plainTextEditGreetsContent)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_5)

        self.label_9 = QLabel(self.tabGreetsSpider)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)

        self.horizontalLayout_8.addWidget(self.label_9)

        self.plainTextEditGreetsImage = QPlainTextEdit(self.tabGreetsSpider)
        self.plainTextEditGreetsImage.setObjectName(u"plainTextEditGreetsImage")
        sizePolicy.setHeightForWidth(self.plainTextEditGreetsImage.sizePolicy().hasHeightForWidth())
        self.plainTextEditGreetsImage.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.plainTextEditGreetsImage)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_6)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.pushButtonGreetsSpiderStart = QPushButton(self.tabGreetsSpider)
        self.pushButtonGreetsSpiderStart.setObjectName(u"pushButtonGreetsSpiderStart")

        self.verticalLayout_4.addWidget(self.pushButtonGreetsSpiderStart)

        self.pushButtonGreetsSpiderStop = QPushButton(self.tabGreetsSpider)
        self.pushButtonGreetsSpiderStop.setObjectName(u"pushButtonGreetsSpiderStop")

        self.verticalLayout_4.addWidget(self.pushButtonGreetsSpiderStop)


        self.horizontalLayout_8.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_8)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 6)
        self.horizontalLayout_8.setStretch(2, 1)
        self.horizontalLayout_8.setStretch(3, 2)
        self.horizontalLayout_8.setStretch(4, 7)
        self.horizontalLayout_8.setStretch(5, 1)
        self.horizontalLayout_8.setStretch(6, 1)
        self.horizontalLayout_8.setStretch(7, 1)

        self.verticalLayout_11.addLayout(self.horizontalLayout_8)

        self.groupBox_4 = QGroupBox(self.tabGreetsSpider)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.textBrowserGreetsSpider = QTextBrowser(self.groupBox_4)
        self.textBrowserGreetsSpider.setObjectName(u"textBrowserGreetsSpider")
        self.textBrowserGreetsSpider.setFont(font)

        self.horizontalLayout_7.addWidget(self.textBrowserGreetsSpider)

        self.line_6 = QFrame(self.groupBox_4)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.VLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_7.addWidget(self.line_6)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.horizontalLayout_7.addLayout(self.gridLayout_2)

        self.horizontalLayout_7.setStretch(0, 4)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_7.setStretch(2, 11)

        self.verticalLayout_11.addWidget(self.groupBox_4)

        self.verticalLayout_11.setStretch(0, 1)
        self.verticalLayout_11.setStretch(1, 1)
        self.verticalLayout_11.setStretch(2, 10)
        self.tabWidget.addTab(self.tabGreetsSpider, "")
        self.stackedPages.addWidget(self.tabGreetsSpider)
        self.sidebarList.addItem("私信成员")
        
        # ========== NEW FEATURES TABS ==========
        # FB Group Specified Collection Tab
        self.tabGroupSpecified = self._create_spider_tab("tabGroupSpecified", "lineEditGroupSpecifiedThreadCount", "plainTextEditGroupSpecifiedWords", "pushButtonGroupSpecifiedStart", "pushButtonGroupSpecifiedStop", "textBrowserGroupSpecified", "gridLayout_3")
        self.tabWidget.addTab(self.tabGroupSpecified, "")
        self.stackedPages.addWidget(self.tabGroupSpecified)
        self.sidebarList.addItem("FB小组指定采集")
        
        # FB Members Rapid Collection Tab
        self.tabMembersRapid = self._create_spider_tab("tabMembersRapid", "lineEditMembersRapidThreadCount", "lineEditMembersRapidGroupCount", "pushButtonMembersRapidStart", "pushButtonMembersRapidStop", "textBrowserMembersRapid", "gridLayout_4")
        self.tabWidget.addTab(self.tabMembersRapid, "")
        self.stackedPages.addWidget(self.tabMembersRapid)
        self.sidebarList.addItem("FB小组成员极速采集")
        
        # FB Posts Collection Tab
        self.tabPosts = self._create_spider_tab("tabPosts", "lineEditPostsThreadCount", "lineEditPostsGroupCount", "pushButtonPostsStart", "pushButtonPostsStop", "textBrowserPosts", "gridLayout_5")
        self.tabWidget.addTab(self.tabPosts, "")
        self.stackedPages.addWidget(self.tabPosts)
        self.sidebarList.addItem("FB小组帖子采集")
        
        # FB Pages Collection Tab
        self.tabPages = self._create_spider_tab("tabPages", "lineEditPagesThreadCount", "plainTextEditPagesKeywords", "pushButtonPagesStart", "pushButtonPagesStop", "textBrowserPages", "gridLayout_6")
        self.tabWidget.addTab(self.tabPages, "")
        self.stackedPages.addWidget(self.tabPages)
        self.sidebarList.addItem("FB公共主页采集")
        
        # Instagram Followers Tab
        self.tabInsFollowers = self._create_spider_tab("tabInsFollowers", "lineEditInsFollowersThreadCount", "plainTextEditInsFollowersUsers", "pushButtonInsFollowersStart", "pushButtonInsFollowersStop", "textBrowserInsFollowers", "gridLayout_7")
        self.tabWidget.addTab(self.tabInsFollowers, "")
        self.stackedPages.addWidget(self.tabInsFollowers)
        self.sidebarList.addItem("INS用户粉丝采集")
        
        # Instagram Following Tab
        self.tabInsFollowing = self._create_spider_tab("tabInsFollowing", "lineEditInsFollowingThreadCount", "plainTextEditInsFollowingUsers", "pushButtonInsFollowingStart", "pushButtonInsFollowingStop", "textBrowserInsFollowing", "gridLayout_8")
        self.tabWidget.addTab(self.tabInsFollowing, "")
        self.stackedPages.addWidget(self.tabInsFollowing)
        self.sidebarList.addItem("INS用户关注采集")
        
        # Instagram Profile Tab
        self.tabInsProfile = self._create_spider_tab("tabInsProfile", "lineEditInsProfileThreadCount", "plainTextEditInsProfileUsers", "pushButtonInsProfileStart", "pushButtonInsProfileStop", "textBrowserInsProfile", "gridLayout_9")
        self.tabWidget.addTab(self.tabInsProfile, "")
        self.stackedPages.addWidget(self.tabInsProfile)
        self.sidebarList.addItem("INS用户简介采集")
        
        # Instagram Reels Comments Tab
        self.tabInsReelsComments = self._create_spider_tab("tabInsReelsComments", "lineEditInsReelsCommentsThreadCount", "plainTextEditInsReelsCommentsUrls", "pushButtonInsReelsCommentsStart", "pushButtonInsReelsCommentsStop", "textBrowserInsReelsComments", "gridLayout_10")
        self.tabWidget.addTab(self.tabInsReelsComments, "")
        self.stackedPages.addWidget(self.tabInsReelsComments)
        self.sidebarList.addItem("INS-reels评论采集")
        # ========== END NEW FEATURES TABS ==========
        
        # ========== AUTOMATION FEATURES TABS ==========
        # Auto Like Tab
        self.tabAutoLike = self._create_spider_tab("tabAutoLike", "lineEditAutoLikeThreadCount", "plainTextEditAutoLikeKeywords", "pushButtonAutoLikeStart", "pushButtonAutoLikeStop", "textBrowserAutoLike", "gridLayoutAutoLike")
        self.tabWidget.addTab(self.tabAutoLike, "")
        self.stackedPages.addWidget(self.tabAutoLike)
        self.sidebarList.addItem("🤍 自动点赞")
        
        # Auto Comment Tab
        self.tabAutoComment = self._create_spider_tab("tabAutoComment", "lineEditAutoCommentThreadCount", "plainTextEditAutoCommentKeywords", "pushButtonAutoCommentStart", "pushButtonAutoCommentStop", "textBrowserAutoComment", "gridLayoutAutoComment")
        self.tabWidget.addTab(self.tabAutoComment, "")
        self.stackedPages.addWidget(self.tabAutoComment)
        self.sidebarList.addItem("💬 自动评论")
        
        # Auto Follow Tab
        self.tabAutoFollow = self._create_spider_tab("tabAutoFollow", "lineEditAutoFollowThreadCount", "plainTextEditAutoFollowKeywords", "pushButtonAutoFollowStart", "pushButtonAutoFollowStop", "textBrowserAutoFollow", "gridLayoutAutoFollow")
        self.tabWidget.addTab(self.tabAutoFollow, "")
        self.stackedPages.addWidget(self.tabAutoFollow)
        self.sidebarList.addItem("👥 自动关注")
        
        # Auto Add Friend Tab
        self.tabAutoAddFriend = self._create_spider_tab("tabAutoAddFriend", "lineEditAutoAddFriendThreadCount", "plainTextEditAutoAddFriendSettings", "pushButtonAutoAddFriendStart", "pushButtonAutoAddFriendStop", "textBrowserAutoAddFriend", "gridLayoutAutoAddFriend")
        self.tabWidget.addTab(self.tabAutoAddFriend, "")
        self.stackedPages.addWidget(self.tabAutoAddFriend)
        self.sidebarList.addItem("➕ 自动添加好友")
        
        # Auto Group Tab
        self.tabAutoGroup = self._create_spider_tab("tabAutoGroup", "lineEditAutoGroupThreadCount", "plainTextEditAutoGroupKeywords", "pushButtonAutoGroupStart", "pushButtonAutoGroupStop", "textBrowserAutoGroup", "gridLayoutAutoGroup")
        self.tabWidget.addTab(self.tabAutoGroup, "")
        self.stackedPages.addWidget(self.tabAutoGroup)
        self.sidebarList.addItem("👥 群组自动化")
        
        # Auto Post Tab
        self.tabAutoPost = self._create_spider_tab("tabAutoPost", "lineEditAutoPostThreadCount", "plainTextEditAutoPostContent", "pushButtonAutoPostStart", "pushButtonAutoPostStop", "textBrowserAutoPost", "gridLayoutAutoPost")
        self.tabWidget.addTab(self.tabAutoPost, "")
        self.stackedPages.addWidget(self.tabAutoPost)
        self.sidebarList.addItem("📝 自动发帖")
        
        # Advanced Messaging Tab
        self.tabAdvancedMessaging = self._create_spider_tab("tabAdvancedMessaging", "lineEditAdvancedMessagingThreadCount", "plainTextEditAdvancedMessagingContent", "pushButtonAdvancedMessagingStart", "pushButtonAdvancedMessagingStop", "textBrowserAdvancedMessaging", "gridLayoutAdvancedMessaging")
        self.tabWidget.addTab(self.tabAdvancedMessaging, "")
        self.stackedPages.addWidget(self.tabAdvancedMessaging)
        self.sidebarList.addItem("💌 高级私信")
        
        # Auto Register Tab
        self.tabAutoRegister = self._create_spider_tab("tabAutoRegister", "lineEditAutoRegisterThreadCount", "plainTextEditAutoRegisterSettings", "pushButtonAutoRegisterStart", "pushButtonAutoRegisterStop", "textBrowserAutoRegister", "gridLayoutAutoRegister")
        self.tabWidget.addTab(self.tabAutoRegister, "")
        self.stackedPages.addWidget(self.tabAutoRegister)
        self.sidebarList.addItem("📝 自动注册")
        
        # Contact List Tab
        self.tabContactList = self._create_spider_tab("tabContactList", "lineEditContactListThreadCount", "plainTextEditContactListSettings", "pushButtonContactListStart", "pushButtonContactListStop", "textBrowserContactList", "gridLayoutContactList")
        self.tabWidget.addTab(self.tabContactList, "")
        self.stackedPages.addWidget(self.tabContactList)
        self.sidebarList.addItem("📋 联系人列表")
        # ========== END AUTOMATION FEATURES TABS ==========
        
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_7 = QVBoxLayout(self.tab)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalSpacer = QSpacerItem(20, 31, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_18)

        self.label_11 = QLabel(self.tab)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_12.addWidget(self.label_11)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_19)


        self.verticalLayout_7.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_16)

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_20)

        self.label_13 = QLabel(self.groupBox)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_14.addWidget(self.label_13)

        self.labelEmail = QLabel(self.groupBox)
        self.labelEmail.setObjectName(u"labelEmail")

        self.horizontalLayout_14.addWidget(self.labelEmail)

        self.horizontalLayout_14.setStretch(0, 1)
        self.horizontalLayout_14.setStretch(1, 3)
        self.horizontalLayout_14.setStretch(2, 10)

        self.verticalLayout_8.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_21)

        self.label_14 = QLabel(self.groupBox)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_15.addWidget(self.label_14)

        self.labelPhone = QLabel(self.groupBox)
        self.labelPhone.setObjectName(u"labelPhone")

        self.horizontalLayout_15.addWidget(self.labelPhone)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 3)
        self.horizontalLayout_15.setStretch(2, 10)

        self.verticalLayout_8.addLayout(self.horizontalLayout_15)


        self.horizontalLayout_13.addWidget(self.groupBox)

        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_17)

        self.horizontalLayout_13.setStretch(0, 1)
        self.horizontalLayout_13.setStretch(1, 2)
        self.horizontalLayout_13.setStretch(2, 1)

        self.verticalLayout_7.addLayout(self.horizontalLayout_13)

        self.verticalSpacer_2 = QSpacerItem(20, 342, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_2)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 5)
        self.verticalLayout_7.setStretch(2, 3)
        self.verticalLayout_7.setStretch(3, 12)
        self.tabWidget.addTab(self.tab, "")
        self.stackedPages.addWidget(self.tab)
        self.sidebarList.addItem("更多功能")
        
        # Connect sidebar list to stacked widget
        self.sidebarList.currentRowChanged.connect(self.stackedPages.setCurrentIndex)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_6.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.stackedPages.setCurrentIndex(0)
        self.sidebarList.setCurrentRow(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def _create_spider_tab(self, tab_name, thread_count_obj, input_obj, start_btn_obj, stop_btn_obj, text_browser_obj, grid_layout_obj):
        """Helper function to create a spider tab with standard layout"""
        tab = QWidget()
        tab.setObjectName(tab_name)
        vertical_layout = QVBoxLayout(tab)
        vertical_layout.setObjectName(f"verticalLayout_{tab_name}")
        
        # Top controls layout
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setObjectName(f"horizontalLayout_{tab_name}")
        
        # Thread count label and input
        label_thread = QLabel(tab)
        label_thread.setObjectName(f"label_{tab_name}_thread")
        label_thread.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        label_thread.setText("采集器数")
        horizontal_layout.addWidget(label_thread)
        
        line_edit_thread = QLineEdit(tab)
        line_edit_thread.setObjectName(thread_count_obj)
        line_edit_thread.setPlaceholderText("请输入整数")
        horizontal_layout.addWidget(line_edit_thread)
        
        horizontal_spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontal_layout.addItem(horizontal_spacer1)
        
        # Input field label and widget
        label_input = QLabel(tab)
        label_input.setObjectName(f"label_{tab_name}_input")
        label_input.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        horizontal_layout.addWidget(label_input)
        
        # Create appropriate input widget based on type
        if "plainTextEdit" in input_obj:
            input_widget = QPlainTextEdit(tab)
            input_widget.setObjectName(input_obj)
            size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            input_widget.setSizePolicy(size_policy)
        else:
            input_widget = QLineEdit(tab)
            input_widget.setObjectName(input_obj)
            input_widget.setPlaceholderText("请输入")
        
        horizontal_layout.addWidget(input_widget)
        
        horizontal_spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontal_layout.addItem(horizontal_spacer2)
        
        # Start/Stop buttons
        vertical_btn_layout = QVBoxLayout()
        vertical_btn_layout.setObjectName(f"verticalLayout_{tab_name}_buttons")
        
        push_button_start = QPushButton(tab)
        push_button_start.setObjectName(start_btn_obj)
        push_button_start.setText("启动")
        vertical_btn_layout.addWidget(push_button_start)
        
        push_button_stop = QPushButton(tab)
        push_button_stop.setObjectName(stop_btn_obj)
        push_button_stop.setText("停止")
        vertical_btn_layout.addWidget(push_button_stop)
        
        horizontal_layout.addLayout(vertical_btn_layout)
        
        horizontal_spacer3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontal_layout.addItem(horizontal_spacer3)
        
        horizontal_layout.setStretch(0, 1)
        horizontal_layout.setStretch(1, 2)
        horizontal_layout.setStretch(3, 1)
        horizontal_layout.setStretch(4, 5)
        horizontal_layout.setStretch(6, 1)
        horizontal_layout.setStretch(7, 5)
        
        vertical_layout.addLayout(horizontal_layout)
        
        # Log group box
        group_box = QGroupBox(tab)
        group_box.setObjectName(f"groupBox_{tab_name}")
        group_box.setTitle("运行日志")
        vertical_group_layout = QVBoxLayout(group_box)
        vertical_group_layout.setObjectName(f"verticalLayout_{tab_name}_group")
        
        horizontal_group_layout = QHBoxLayout()
        horizontal_group_layout.setObjectName(f"horizontalLayout_{tab_name}_group")
        
        text_browser = QTextBrowser(group_box)
        text_browser.setObjectName(text_browser_obj)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        try:
            font.setWeight(QFont.Weight.Bold)
        except (AttributeError, TypeError):
            try:
                font.setWeight(75)
            except:
                pass
        text_browser.setFont(font)
        horizontal_group_layout.addWidget(text_browser)
        
        line = QFrame(group_box)
        line.setObjectName(f"line_{tab_name}")
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        horizontal_group_layout.addWidget(line)
        
        grid_layout = QGridLayout()
        grid_layout.setObjectName(grid_layout_obj)
        horizontal_group_layout.addLayout(grid_layout)
        
        horizontal_group_layout.setStretch(0, 4)
        horizontal_group_layout.setStretch(1, 1)
        horizontal_group_layout.setStretch(2, 11)
        
        vertical_group_layout.addLayout(horizontal_group_layout)
        vertical_layout.addWidget(group_box)
        
        vertical_layout.setStretch(0, 1)
        vertical_layout.setStretch(1, 16)
        
        return tab

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Facebook\u8425\u9500", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"\u673a\u5668\u7801", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8\u5668KEY", None))
        self.lineEditAdsKey.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165adsPower Global\u6d4f\u89c8\u5668KEY", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8\u5668EXE\u5730\u5740", None))
        self.lineEditInstallLocation.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9adsPower Global\u6d4f\u89c8\u5668\u53ef\u6267\u884c\u6587\u4ef6\uff0c\u4f8b\u5982 C:\\Program Files\\AdsPower Global\\AdsPower Global.exe", None))
        self.pushButtonSelectInstallLocation.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u6fc0\u6d3b\u7801", None))
        self.lineEditCode.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8f93\u5165\u6fc0\u6d3b\u7801", None))
        self.pushButtonVerify.setText(QCoreApplication.translate("MainWindow", u"\u6fc0\u6d3b", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u5668\u6570", None))
#if QT_CONFIG(tooltip)
        self.lineEditGroupMaxThreadCount.setToolTip(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6700\u5927\u53ef\u540c\u65f6\u5f00\u542f\u6d4f\u89c8\u5668\u6570", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditGroupMaxThreadCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u7fa4\u5173\u952e\u8bcd", None))
        self.plainTextEditGroupWords.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u7fa4\u7ec4", None))
        self.pushButtonGroupSpiderStart.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
        self.pushButtonGroupSpiderStop.setText(QCoreApplication.translate("MainWindow", u"\u505c\u6b62", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c\u65e5\u5fd7", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGroupSpider), QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u7fa4\u7ec4", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u5668\u6570", None))
        self.lineEditMemberMaxThreadCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u7ec4\u6570", None))
        self.lineEditGroupCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.pushButtonMembersSpiderStart.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
        self.pushButtonMembersSpiderStop.setText(QCoreApplication.translate("MainWindow", u"\u505c\u6b62", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c\u65e5\u5fd7", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMembersSpider), QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u6210\u5458", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u96c6\u5668\u6570", None))
        self.lineEditGreetsMaxThreadCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u5355\u91c7\u96c6\u5668\u79c1\u4fe1\u6570", None))
        self.lineEditGreetsCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u79c1\u4fe1\u95f4\u9694(\u79d2)", None))
        self.lineEditGreetsTimeout.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u6574\u6570", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u79c1\u4fe1\u6587\u672c", None))
        self.plainTextEditGreetsContent.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u79c1\u4fe1\u5185\u5bb9\uff0c\u6bcf\u4e00\u884c\u662f\u4e00\u6761\u4fe1\u606f\uff0c\u968f\u673a\u4ece\u591a\u6761\u4e2d\u9009\u4e00\u6761\u53d1\u9001", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>\u53d1\u9001\u56fe\u7247</p></body></html>", None))
        self.plainTextEditGreetsImage.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u56fe\u7247\u7684\u771f\u5b9e\u7269\u7406\u5730\u5740,\u6bcf\u4e00\u884c\u662f\u4e00\u5f20\u56fe\u7247\u4f8b\u5982\uff1aD:/temp/1jpg", None))
        self.pushButtonGreetsSpiderStart.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
        self.pushButtonGreetsSpiderStop.setText(QCoreApplication.translate("MainWindow", u"\u505c\u6b62", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c\u65e5\u5fd7", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGreetsSpider), QCoreApplication.translate("MainWindow", u"\u79c1\u4fe1\u6210\u5458", None))
        
        # New features tab labels
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGroupSpecified), QCoreApplication.translate("MainWindow", u"FB小组指定采集", None))
        label = self.tabGroupSpecified.findChild(QLabel, "label_tabGroupSpecified_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词", None))
        plain_text = self.tabGroupSpecified.findChild(QPlainTextEdit, "plainTextEditGroupSpecifiedWords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入关键词，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMembersRapid), QCoreApplication.translate("MainWindow", u"FB小组成员极速采集", None))
        label = self.tabMembersRapid.findChild(QLabel, "label_tabMembersRapid_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"采集组数", None))
        line_edit = self.tabMembersRapid.findChild(QLineEdit, "lineEditMembersRapidGroupCount")
        if line_edit:
            line_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入整数", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPosts), QCoreApplication.translate("MainWindow", u"FB小组帖子采集", None))
        label = self.tabPosts.findChild(QLabel, "label_tabPosts_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"采集组数", None))
        line_edit = self.tabPosts.findChild(QLineEdit, "lineEditPostsGroupCount")
        if line_edit:
            line_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入整数", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPages), QCoreApplication.translate("MainWindow", u"FB公共主页采集", None))
        label = self.tabPages.findChild(QLabel, "label_tabPages_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词/URL", None))
        plain_text = self.tabPages.findChild(QPlainTextEdit, "plainTextEditPagesKeywords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入关键词或URL，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInsFollowers), QCoreApplication.translate("MainWindow", u"INS用户粉丝采集", None))
        label = self.tabInsFollowers.findChild(QLabel, "label_tabInsFollowers_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"用户名", None))
        plain_text = self.tabInsFollowers.findChild(QPlainTextEdit, "plainTextEditInsFollowersUsers")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入Instagram用户名，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInsFollowing), QCoreApplication.translate("MainWindow", u"INS用户关注采集", None))
        label = self.tabInsFollowing.findChild(QLabel, "label_tabInsFollowing_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"用户名", None))
        plain_text = self.tabInsFollowing.findChild(QPlainTextEdit, "plainTextEditInsFollowingUsers")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入Instagram用户名，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInsProfile), QCoreApplication.translate("MainWindow", u"INS用户简介采集", None))
        label = self.tabInsProfile.findChild(QLabel, "label_tabInsProfile_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"用户名", None))
        plain_text = self.tabInsProfile.findChild(QPlainTextEdit, "plainTextEditInsProfileUsers")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入Instagram用户名，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInsReelsComments), QCoreApplication.translate("MainWindow", u"INS-reels评论采集", None))
        label = self.tabInsReelsComments.findChild(QLabel, "label_tabInsReelsComments_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"Reels URL", None))
        plain_text = self.tabInsReelsComments.findChild(QPlainTextEdit, "plainTextEditInsReelsCommentsUrls")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入Instagram Reels URL，每行一个", None))
        
        # Automation features tab labels
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoLike), QCoreApplication.translate("MainWindow", u"自动点赞", None))
        label = self.tabAutoLike.findChild(QLabel, "label_tabAutoLike_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词", None))
        plain_text = self.tabAutoLike.findChild(QPlainTextEdit, "plainTextEditAutoLikeKeywords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入关键词（可选），每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoComment), QCoreApplication.translate("MainWindow", u"自动评论", None))
        label = self.tabAutoComment.findChild(QLabel, "label_tabAutoComment_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词", None))
        plain_text = self.tabAutoComment.findChild(QPlainTextEdit, "plainTextEditAutoCommentKeywords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入关键词，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoFollow), QCoreApplication.translate("MainWindow", u"自动关注", None))
        label = self.tabAutoFollow.findChild(QLabel, "label_tabAutoFollow_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词", None))
        plain_text = self.tabAutoFollow.findChild(QPlainTextEdit, "plainTextEditAutoFollowKeywords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入搜索关键词（可选），每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoAddFriend), QCoreApplication.translate("MainWindow", u"自动添加好友", None))
        label = self.tabAutoAddFriend.findChild(QLabel, "label_tabAutoAddFriend_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"设置", None))
        plain_text = self.tabAutoAddFriend.findChild(QPlainTextEdit, "plainTextEditAutoAddFriendSettings")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"配置在config.ini中设置", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoGroup), QCoreApplication.translate("MainWindow", u"群组自动化", None))
        label = self.tabAutoGroup.findChild(QLabel, "label_tabAutoGroup_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"关键词", None))
        plain_text = self.tabAutoGroup.findChild(QPlainTextEdit, "plainTextEditAutoGroupKeywords")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入群组关键词，每行一个", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoPost), QCoreApplication.translate("MainWindow", u"自动发帖", None))
        label = self.tabAutoPost.findChild(QLabel, "label_tabAutoPost_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"内容", None))
        plain_text = self.tabAutoPost.findChild(QPlainTextEdit, "plainTextEditAutoPostContent")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入发帖内容，每行一条", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdvancedMessaging), QCoreApplication.translate("MainWindow", u"高级私信", None))
        label = self.tabAdvancedMessaging.findChild(QLabel, "label_tabAdvancedMessaging_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"内容", None))
        plain_text = self.tabAdvancedMessaging.findChild(QPlainTextEdit, "plainTextEditAdvancedMessagingContent")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"请输入私信内容，每行一条", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutoRegister), QCoreApplication.translate("MainWindow", u"自动注册", None))
        label = self.tabAutoRegister.findChild(QLabel, "label_tabAutoRegister_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"设置", None))
        plain_text = self.tabAutoRegister.findChild(QPlainTextEdit, "plainTextEditAutoRegisterSettings")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"配置在config.ini中设置", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabContactList), QCoreApplication.translate("MainWindow", u"联系人列表", None))
        label = self.tabContactList.findChild(QLabel, "label_tabContactList_input")
        if label:
            label.setText(QCoreApplication.translate("MainWindow", u"设置", None))
        plain_text = self.tabContactList.findChild(QPlainTextEdit, "plainTextEditContactListSettings")
        if plain_text:
            plain_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"配置在config.ini中设置", None))
        
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u591a\u529f\u80fd\uff0c\u656c\u8bf7\u671f\u5f85", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u8054\u7cfb\u6211\u4eec", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u7535\u5b50\u90ae\u7bb1\uff1a", None))
        self.labelEmail.setText(QCoreApplication.translate("MainWindow", u"c3708888@gmail.com", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Telegram\uff1a", None))
        self.labelPhone.setText(QCoreApplication.translate("MainWindow", u"@TTG88", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\u66f4\u591a\u529f\u80fd", None))
    # retranslateUi

