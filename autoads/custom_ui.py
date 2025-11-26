# Import compatibility layer for PySide6 before any PySide2 imports
import pyside2_compat
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, Signal


class TableWidget(QWidget):
    control_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(TableWidget, self).__init__(*args, **kwargs)
        self.__init_ui()
        self.total_page = None
        self.changeTableContentFlag = False
        self.init_table_fun=None

    def __init_ui(self):
        style_sheet = """
            QTableWidget {
                border: none;
                background-color:rgb(240,240,240)
            }
            QPushButton{
                max-width: 18ex;
                max-height: 6ex;
                font-size: 11px;
            }
            QLineEdit{
                max-width: 30px
            }
        """
        self.table = QTableWidget()  # 3 行 5 列的表格
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应宽度
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.table)
        self.setLayout(self.__layout)
        self.setStyleSheet(style_sheet)

    def setPageController(self, page):
        """自定义页码控制器"""
        if hasattr(self, 'totalPage'):
            if not self.changeTableContentFlag:
                self.curPage.setText('1')
            self.totalPage.setText("共" + str(page) + "页")
        else:
            control_layout = QHBoxLayout()
            homePage = QPushButton("首页")
            prePage = QPushButton("<上一页")
            self.curPage = QLabel("1")
            nextPage = QPushButton("下一页>")
            finalPage = QPushButton("尾页")
            self.totalPage = QLabel("共" + str(page) + "页")
            skipLable_0 = QLabel("跳到")
            self.skipPage = QLineEdit()
            skipLabel_1 = QLabel("页")
            confirmSkip = QPushButton("确定")
            homePage.clicked.connect(self.__home_page)
            prePage.clicked.connect(self.__pre_page)
            nextPage.clicked.connect(self.__next_page)
            finalPage.clicked.connect(self.__final_page)
            confirmSkip.clicked.connect(self.__confirm_skip)
            control_layout.addStretch(1)
            control_layout.addWidget(homePage)
            control_layout.addWidget(prePage)
            control_layout.addWidget(self.curPage)
            control_layout.addWidget(nextPage)
            control_layout.addWidget(finalPage)
            control_layout.addWidget(self.totalPage)
            control_layout.addWidget(skipLable_0)
            control_layout.addWidget(self.skipPage)
            control_layout.addWidget(skipLabel_1)
            control_layout.addWidget(confirmSkip)
            control_layout.addStretch(1)
            self.__layout.addLayout(control_layout)

    def __home_page(self):
        """点击首页信号"""
        self.control_signal.emit(["home", self.curPage.text(),self])

    def __pre_page(self):
        """点击上一页信号"""
        self.control_signal.emit(["pre", self.curPage.text(),self])

    def __next_page(self):
        """点击下一页信号"""
        self.control_signal.emit(["next", self.curPage.text(),self])

    def __final_page(self):
        """尾页点击信号"""
        self.control_signal.emit(["final", self.curPage.text(),self])

    def __confirm_skip(self):
        """跳转页码确定"""
        self.control_signal.emit(["confirm", self.skipPage.text(),self])

    def showTotalPage(self):
        """返回当前总页数"""
        return int(self.totalPage.text()[1:-1])


class ComboCheckBox(QComboBox):
    signa = Signal(list)

    def __init__(self, items):  # items==[str,str...]
        super(ComboCheckBox, self).__init__()
        self.split_char=';'
        self.items = items
        self.items.insert(0, '全部')

        self.row_num = len(self.items)
        self.Selectedrow_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        self.addQCheckBox(0)
        self.qCheckBox[0].clicked.connect(self.select_all_click)
        for i in range(1, self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].clicked.connect(self.single_checkbox_click)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)
        self.setMaxVisibleItems(100)  # 避免滑条的出现引起滑条偷吃标签的问题

    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        qItem = QListWidgetItem(self.qListWidget)
        self.qCheckBox[i].setText(self.items[i])
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    def update_box_text(self):
        show0 = ''

        Outputlist = []
        for i in range(1, self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
        self.Selectedrow_num = len(Outputlist)

        self.signa.emit(Outputlist)
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in Outputlist:
            show0 += i + self.split_char

        self.qLineEdit.setText(show0)
        self.qLineEdit.setReadOnly(True)

    def single_checkbox_click(self):
        self.update_box_text()
        if self.Selectedrow_num == self.row_num - 1:
            self.qCheckBox[0].setCheckState(Qt.CheckState.Checked)
        else:
            self.qCheckBox[0].setCheckState(Qt.CheckState.Unchecked)

    def select_all_click(self, checkState):
        if checkState:
            for i in range(1, self.row_num):
                self.qCheckBox[i].setChecked(True)
        else:
            self.clear()
        self.update_box_text()

    def clear(self):
        for i in range(self.row_num):
            self.qCheckBox[i].setChecked(False)

    def changeitemlist(self, itemlist):

        self.items = itemlist
        self.items.insert(0, '全部')
        self.row_num = len(self.items)

        self.Selectedrow_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        self.addQCheckBox(0)
        self.qCheckBox[0].stateChanged.connect(self.All)
        for i in range(1, self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(self.show0)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)
