# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import sys


class _MainWindow(QMainWindow):
    """

    """
    main_layout: QLayout
    main_left: QWidget
    main_right: QWidget
    current_widget: QWidget
    main_display: bool
    detail_widgets: dict[str, QWidget]

    # translations: dict

    def __init__(self, tables, *args, **kwargs):
        """

        :param tables:
        :param args:
        :param kwargs:
        """
        super(_MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('view/main.ui', self)
        self.setWindowTitle('sportApp - main')

        self.main_layout = self.horizontalLayout_main_widget
        self.main_left = uic.loadUi('view/main_left.ui')
        self.main_right = uic.loadUi('view/main_right.ui')
        self.main_layout.addWidget(self.main_left)
        self.main_layout.addWidget(self.main_right)
        self.main_display = True

        self.detail_widgets = {}
        for table in tables:
            try:
                self.detail_widgets[table] = uic.loadUi('view/' + table + '_widget.ui')
                self.detail_widgets[table].hide()
            except FileNotFoundError:
                continue

    def switch_main_widget(self, table=None):
        """

        :param table:
        :return:
        """
        if self.main_display:
            self.main_layout.removeWidget(self.main_left)
            self.main_left.hide()
            self.main_layout.removeWidget(self.main_right)
            self.main_right.hide()

            self.current_widget = self.detail_widgets[table]
            self.main_layout.addWidget(self.current_widget)
            self.current_widget.show()

            # self.current_widget.pushButton_save.clicked.connect(self._button_save)
            # self.current_widget.pushButton_cancel.clicked.connect(self._button_cancel)
            self.main_display = False
        else:
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.hide()

            self.main_left.show()
            self.main_layout.addWidget(self.main_left)
            self.main_right.show()
            self.main_layout.addWidget(self.main_right)
            self.main_display = True


class MainApplication(QApplication):
    """

    """
    _main_window: _MainWindow

    def __init__(self, tables, *args, **kwargs):
        """

        :param tables:
        :param args:
        :param kwargs:
        """
        super(MainApplication, self).__init__(sys.argv, *args, **kwargs)
        self._main_window = _MainWindow(tables)
        self._main_window.show()

    def connect_main(self, s):
        """

        :param s:
        :return:
        """
        self._main_window.main_left.pushButton_create.clicked.connect(s)

    def connect_commit(self, s):
        """

        :param s:
        :return:
        """
        self._main_window.pushButton_save_db.clicked.connect(s)

    def connect_revert(self, s):
        """

        :param s:
        :return:
        """
        self._main_window.pushButton_revert_db.clicked.connect(s)

    def connect_cancel(self, tables, s):
        """

        :param tables:
        :param s:
        :return:
        """
        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_cancel.clicked.connect(s)

    def connect_save(self, tables, s):
        """

        :param tables:
        :param s:
        :return:
        """
        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_save.clicked.connect(s)

    def get_main_window(self) -> _MainWindow:
        """

        :return:
        """
        return self._main_window

    def get_main_left(self) -> QWidget:
        """

        :return:
        """
        return self._main_window.main_left

    def get_current_widget(self) -> QWidget:
        """

        :return:
        """
        return self._main_window.current_widget

    def get_main_display(self) -> bool:
        """

        :return:
        """
        return self._main_window.main_display

    def init_main_window(self, combobox, tree_view):
        """

        :param combobox:
        :param tree_view:
        :return:
        """
        # Set Table Combobox
        self._main_window.main_left.comboBox_tables.addItems(combobox)
        # Set Widget Config
        # Set Tree Overview
        pass

    def switch_main_widget(self, table=None):
        """

        :param table:
        :return:
        """
        if table is None:
            self._main_window.switch_main_widget()
        else:
            self._main_window.switch_main_widget(table)

    def start_application(self):
        """

        :return:
        """
        self.exec_()
