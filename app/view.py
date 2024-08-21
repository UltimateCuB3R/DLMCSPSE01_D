# from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import xml.etree.ElementTree as ElTr
import error

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

        if table is not None:
            if self.main_display:
                # main display is active, so remove and hide the widgets
                self.main_layout.removeWidget(self.main_left)
                self.main_left.hide()
                self.main_layout.removeWidget(self.main_right)
                self.main_right.hide()
            else:
                # main display is inactive, so switch between current widgets
                self.main_layout.removeWidget(self.current_widget)
                self.current_widget.hide()

            self.current_widget = self.detail_widgets[table]
            self.main_layout.addWidget(self.current_widget)
            self.current_widget.show()

            self.setWindowTitle(f'sportApp - {table}')
            self.main_display = False
        else:
            # no table name is given, so switch back to main widget
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.hide()

            self.main_left.show()
            self.main_layout.addWidget(self.main_left)
            self.main_right.show()
            self.main_layout.addWidget(self.main_right)

            self.setWindowTitle('sportApp - main')
            self.main_display = True


class MainApplication(QApplication):
    """Main application that manages the main window with all its widgets.
    Also manages all calls from outside the display.
    """

    _main_window: _MainWindow
    _gui_def: dict[str, list]

    def __init__(self, tables, gui_def, *args, **kwargs):
        """Initialize the MainApplication and set the main window

        :param tables: name of tables that correspond to widgets which will be loaded in the main window
        :param args: arguments tuple
        :param kwargs: keywords dictionary
        """

        super(MainApplication, self).__init__(sys.argv, *args, **kwargs)
        self._main_window = _MainWindow(tables)
        self._main_window.show()
        self._gui_def = _read_gui_definition(gui_def)

    def connect_create(self, action):
        """Connect the create button of the main widget to the corresponding method

        :param action: method to be connected to the create button
        :return: None
        """

        self.get_main_left().pushButton_create.clicked.connect(action)

    def connect_display(self, tables, action):
        """Connect the display button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the display button
        :return: None
        """
        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_display.clicked.connect(action)

    def connect_edit(self, tables, action):
        """Connect the edit button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the edit button
        :return: None
        """
        for table in tables:
            if table in self._main_window.detail_widgets.keys():
                self._main_window.detail_widgets[table].pushButton_edit.clicked.connect(action)

    def connect_search(self, action):
        """Connect the search button of the main widget to the corresponding method

        :param action: method to be connected to the search button
        :return: None
        """

        self.get_main_left().pushButton_search.clicked.connect(action)

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

    def get_gui_definition(self):
        """Get the gui definition from xml

        :return: dict of gui definition
        """

        return self._gui_def

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

    def get_displayed_table(self) -> str:
        """Get the name of the currently displayed table.
        Returns empty string if no table is currently displayed.

        :return: currently displayed table as string
        """

        try:
            return self.get_current_widget().label_table_name.text()
        except AttributeError:
            self.send_critical_message('Fehler beim Lesen der aktuell angezeigten Tabelle (label_table_name)')

    def get_main_display(self) -> bool:
        """Return whether the main_display is active

        :return: main_display (bool)
        """

        return self._main_window.main_display

    @staticmethod
    def _get_selection_of_widget(table_widget) -> list:
        """Retrieve the selected row indices of a given table widget.

        :return: list of row indices that are selected
        """

        selected_rows = []
        for selection in table_widget.selectedRanges():
            if selection.topRow() == selection.bottomRow():
                selected_rows.append(selection.topRow())
            else:
                for row in range(selection.topRow(), selection.bottomRow()):
                    selected_rows.append(row)
        return selected_rows

    def get_selected_rows_of_current_widget(self) -> list:
        """Retrieve the selected row indices of the current table widget.

        :return: list of row indices that are selected
        """
        table_widget = self.get_current_widget().findChild(QTableWidget)
        rows = self._get_selection_of_widget(table_widget)
        return rows

    def init_main_widget(self, combobox, tree_view):
        """Initialize the main widget with values

        :param combobox: values of tables that need to be added to the main combobox
        :param tree_view:
        :return: None
        """

        # Set Table Combobox
        self.get_main_left().comboBox_tables.addItems(combobox)
        # Set Widget Config
        # Set Tree Overview
        pass

    def send_critical_message(self, message):
        """Send a critical message to the user and block the current widget until the message is confirmed

        :param message: text of the message to be displayed
        :return: None
        """
        QMessageBox.critical(self.get_current_widget(), 'ERROR', message)

    def send_information_message(self, message):
        """Send an information message to the user and block the current widget until the message is confirmed

        :param message: text of the message to be displayed
        :return: None
        """
        QMessageBox.information(self.get_current_widget(), 'INFORMATION', message)

    @staticmethod
    def _set_table_widget(table_widget, table_data):
        table_widget.setRowCount(len(table_data.index))
        table_widget.setColumnCount(len(table_data.columns))
        table_widget.setHorizontalHeaderLabels(table_data.columns.to_list())
        index = 0
        for key, row in table_data.iterrows():
            print(f'index: {index}, key: {key}, row: {row}')
            col_index = 0
            for column in table_data.columns:
                table_widget.setItem(index, col_index, QTableWidgetItem(str(row[column])))
                col_index += 1
            index += 1

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
        for table_widget in self.get_current_widget().findChildren(QTableWidget):
            print(table_widget, table_widget.objectName())
            if table_widget.objectName().lower() == f'table_{table}'.lower():
                try:
                    self._set_table_widget(table_widget, table_data)
                except AttributeError:
                    self.send_critical_message('Fehler beim Setzen der Beziehungstabellen!')

    def set_search_table(self, table_name, table_data):
        """Set the contents of the search widget

        :param table_name: name of the table that the search is executed for
        :param table_data: content of the searched table
        :return: None
        """
        table_widget = self.get_current_widget().findChild(QTableWidget)
        print(table_widget, table_widget.objectName())
        self._set_table_widget(table_widget, table_data)
        self.get_current_widget().label_table_name.setText(table_name)

    def get_field_of_current_widget(self, field_name) -> str:
        """Get the value of a field in the current widget

        :param field_name: name of the PyQt field
        :return: value of the field as string
        """
        field = self.get_current_widget().findChild(QObject, field_name)

        if isinstance(field, QLineEdit):
            return field.text()
        elif isinstance(field, QTextEdit):
            return field.toPlainText()
        elif isinstance(field, QTimeEdit):
            return str(field.time().toPyTime())
        else:
            self.send_critical_message('Fehler beim Lesen der Felder im aktuellen Widget!')

    def set_field_in_current_widget(self, field_name, field_data):
        """Set a field in the current widget to the corresponding data

        :param field_name: name of the PyQt field
        :param field_data: value to be set for the field
        :return: None
        """
        field = self.get_current_widget().findChild(QObject, field_name)
        if isinstance(field, QLineEdit):
            field.setText(str(field_data))
        elif isinstance(field, QTextEdit):
            field.setPlainText(field_data)
        elif isinstance(field, QTimeEdit):
            if field_data == '':
                field.setTime(QTime().fromString('00:00'))
            else:
                field.setTime(QTime().fromString(field_data))
        else:
            self.send_critical_message('Fehler beim Setzen der Felder im aktuellen Widget!')

    def start_application(self):
        """Start the application

        :return: None
        """
        self.exec_()


def _read_gui_definition(gui_def) -> dict:
    """Read GUI definition out of xml file.

    :param gui_def: path to gui definition file
    :return: dictionary of gui definition
    """

    tree = ElTr.parse(gui_def)
    root = tree.getroot()
    def_gui = {}

    for item in root.findall('WIDGET'):
        name = item.attrib['NAME']
        table = item.attrib['TABLE']

        fields = {}
        for child in item:
            if child.tag == 'FIELD':
                fields[child.attrib['COLUMN']] = child.attrib['NAME']
            else:
                pass

        def_gui[table] = [name, fields]

    return def_gui
