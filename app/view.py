# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import sys


class _MainWindow(QMainWindow):
    """Main window to manage all widgets and how to swap them out
    """

    main_layout: QLayout
    main_left: QWidget
    main_right: QWidget
    current_widget: QWidget
    main_display: bool
    detail_widgets: dict[str, QWidget]

    # translations: dict

    def __init__(self, tables, *args, **kwargs):
        """Initialize the main window with the main widgets.
        Load all table specific widgets into a dictionary to easily swap them out at runtime.

        :param tables: name of tables that correspond to widgets which need to be loaded
        :param args: arguments tuple
        :param kwargs: keywords dictionary
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
        """Switch the main widget to a table specific widget if given - else switch back to the initial main widget

        :param table: name of table that corresponds to a specific widget
        :return: None
        """

        if self.main_display:
            self.main_layout.removeWidget(self.main_left)
            self.main_left.hide()
            self.main_layout.removeWidget(self.main_right)
            self.main_right.hide()

            self.current_widget = self.detail_widgets[table]
            self.main_layout.addWidget(self.current_widget)
            self.current_widget.show()

            self.setWindowTitle('sportApp - main')
            self.main_display = False
        else:
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.hide()

            self.main_left.show()
            self.main_layout.addWidget(self.main_left)
            self.main_right.show()
            self.main_layout.addWidget(self.main_right)

            self.setWindowTitle(f'sportApp - {table}')
            self.main_display = True


class MainApplication(QApplication):
    """Main application that manages the main window with all its widgets.
    Also manages all calls from outside the display.
    """

    _main_window: _MainWindow

    def __init__(self, tables, *args, **kwargs):
        """Initialize the MainApplication and set the main window

        :param tables: name of tables that correspond to widgets which will be loaded in the main window
        :param args: arguments tuple
        :param kwargs: keywords dictionary
        """

        super(MainApplication, self).__init__(sys.argv, *args, **kwargs)
        self._main_window = _MainWindow(tables)
        self._main_window.show()

    def connect_create(self, action):
        """Connect the create button of the main widget to the corresponding method

        :param action: method to be connected to the create button
        :return: None
        """

        self._main_window.main_left.pushButton_create.clicked.connect(action)

    def connect_search(self, action):
        """Connect the search button of the main widget to the corresponding method

        :param action: method to be connected to the search button
        :return: None
        """

        self._main_window.main_left.pushButton_search.clicked.connect(action)

    def connect_commit(self, action):
        """Connect the commit button of the main widget to the corresponding method

        :param action: method to be connected to the commit button
        :return: None
        """

        self._main_window.pushButton_save_db.clicked.connect(action)

    def connect_revert(self, action):
        """Connect the cancel button of the main widget to the corresponding method

        :param action: method to be connected to the revert button
        :return: None
        """

        self._main_window.pushButton_revert_db.clicked.connect(action)

    def connect_cancel(self, tables, action):
        """Connect the cancel button of all table widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the cancel button
        :return: None
        """

        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_cancel.clicked.connect(action)

    def connect_save(self, tables, action):
        """Connect the save button of all table widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the save button
        :return: None
        """

        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_save.clicked.connect(action)

    def get_main_window(self) -> _MainWindow:
        """Get the main window

        :return: main_window object
        """

        return self._main_window

    def get_main_left(self) -> QWidget:
        """Get the main_left widget of the main window

        :return: main_left widget
        """

        return self._main_window.main_left

    def get_current_widget(self) -> QWidget:
        """Get the currently stored widget

        :return: currently stored widget
        """

        return self._main_window.current_widget

    def get_main_display(self) -> bool:
        """Return whether the main_display is active

        :return: main_display (bool)
        """

        return self._main_window.main_display

    def init_main_widget(self, combobox, tree_view):
        """Initialize the main widget with values

        :param combobox: values of tables that need to be added to the main combobox
        :param tree_view:
        :return: None
        """

        # Set Table Combobox
        self._main_window.main_left.comboBox_tables.addItems(combobox)
        # Set Widget Config
        # Set Tree Overview
        pass

    def switch_main_widget(self, table=None):
        """Switch the main widget to a table specific one or back to the initial main widget

        :param table: name of the table/widget to be loaded - will switch back to main if None is given
        :return: None
        """

        if table is None:
            self._main_window.switch_main_widget()
        else:
            self._main_window.switch_main_widget(table)

    def set_relation_table(self, table, table_data):
        """Set the contents of a relation table in the corresponding widget

        :param table_data: data of the relation table
        :param table: name of the relation table
        :return: None
        """
        table_widget = self._main_window.current_widget.findChildr(QTableWidget, f'table_{table}')
        table_widget.setRowCount(len(table_data))
        index = 0
        for key, row in table_data.iterrows():
            table_widget.setItem(index, 0, QTableWidgetItem(row['ID']))
            index += 1

    def start_application(self):
        """Start the application

        :return: None
        """
        self.exec_()
