from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtPrintSupport import QPrinter  # QPrintDialog, QPrintPreviewDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
import xml.etree.ElementTree as ElTr
import error
import sys
import os


class _MainWindow(QMainWindow):
    """Main window to manage all widgets and how to swap them out
    """

    main_layout: QLayout
    main_left: QWidget
    main_right: QWidget
    current_widget: QWidget
    main_display: bool
    detail_widgets: dict[str, QWidget]

    def __init__(self, widgets, path, *args, **kwargs):
        """Initialize the main window with the main widgets.
        Load all table specific widgets into a dictionary to easily swap them out at runtime.

        :param widgets: name of widgets which need to be loaded
        :param path: current path of the application
        :param args: arguments tuple
        :param kwargs: keywords dictionary
        """

        super(_MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(path, 'view\\main.ui'), self)  # load main layout
        self.setWindowTitle('sportApp - main')  # set the main window title

        self.main_layout = self.horizontalLayout_main_widget
        # self.main_left = uic.loadUi(os.path.join(path, 'view\\main_left.ui'))  # load left main widget
        # self.main_left_2 = uic.loadUi(os.path.join(path, 'view\\main_left_2.ui'))  # load left main widget
        self.main_left = uic.loadUi(os.path.join(path, 'view\\main_left_2.ui'))  # load left main widget
        self.main_right = uic.loadUi(os.path.join(path, 'view\\main_right.ui'))  # load right main widget
        self.main_layout.addWidget(self.main_left)  # add left main widget to the layout
        # self.main_layout.addWidget(self.main_left_2)  # add left main widget to the layout
        self.main_layout.addWidget(self.main_right)  # add right main widget to the layout
        self.main_display = True  # main display is active

        self.detail_widgets = {}  # create dict for the detail widgets
        for name in widgets:  # iterate through the given widget names
            try:
                # load the widget into the dict and hide it
                self.detail_widgets[name] = uic.loadUi(os.path.join(path, 'view/' + name + '_widget.ui'))
                self.detail_widgets[name].hide()
            except FileNotFoundError:
                # file could not be found, so widget cannot be loaded
                continue

            # set the icon for all buttons of the detail widgets
            for button in self.detail_widgets[name].findChildren(QPushButton):
                self.__set_button_icon(button)

        # set the icon for all buttons on the main widget
        for button in self.findChildren(QPushButton):
            self.__set_button_icon(button)

    def __set_button_icon(self, button):
        """Set the icon of a button corresponding to the button name

        :param button: pushButton for that the icon needs to be set
        :return: None
        """

        if 'create' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileIcon')))
        elif 'cancel' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCancelButton')))
        elif 'display' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileLinkIcon')))
        elif 'search' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogContentsView')))
        elif 'edit' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogResetButton')))
        elif 'export' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DriveFDIcon')))
        elif 'print' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DriveFDIcon')))
        elif 'save' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))
        elif 'revert' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
        elif 'delete' in button.objectName():
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogDiscardButton')))

    def switch_main_widget(self, name=None):
        """Switch the main widget to a table specific widget if given - else switch back to the initial main widget

        :param name: name of the specific widget
        :return: None
        """

        if name is not None:
            if self.main_display:
                # main display is active, so remove and hide the main widgets
                self.main_layout.removeWidget(self.main_left)
                self.main_left.hide()
                self.main_layout.removeWidget(self.main_right)
                self.main_right.hide()
            else:
                # main display is inactive, so switch between current widgets
                self.main_layout.removeWidget(self.current_widget)
                self.current_widget.hide()

            # set the current widget to the chosen detail widget
            self.current_widget = self.detail_widgets[name]
            self.main_layout.addWidget(self.current_widget)
            self.current_widget.show()

            self.setWindowTitle(f'sportApp - {name}')  # set the window title to the specific widget name
            self.main_display = False  # main display is inactive
        else:
            # no table name is given, so switch back to main widget
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.hide()

            # add the main widgets back
            self.main_left.show()
            self.main_layout.addWidget(self.main_left)
            self.main_right.show()
            self.main_layout.addWidget(self.main_right)

            self.setWindowTitle('sportApp - main')  # set the window title back to main
            self.main_display = True  # main display is active

    def get_current_widget_name(self) -> str:
        """Get the name of the currently stored widget

        :return: name of the currently stored widget
        """

        # iterate through all widgets to find the name of the currently displayed widget
        for name, widget in self.detail_widgets.items():
            if widget == self.current_widget:
                return name
        return ''  # empty String


class MainApplication(QApplication):
    """Main application that manages the main window with all its widgets.
    Also manages all calls from outside the display.
    """

    _main_window: _MainWindow
    _gui_def: dict[str, list]

    def __init__(self, tables, gui_def, path, *args, **kwargs):
        """Initialize the MainApplication and set the main window

        :param tables: name of tables that correspond to widgets which will be loaded in the main window
        :param gui_def: path to the GUI definition file
        :param path: current path of the application
        :param args: arguments tuple
        :param kwargs: keywords dictionary
        """

        super(MainApplication, self).__init__(sys.argv, *args, **kwargs)
        self._main_window = _MainWindow(tables, path)  # create the main window
        self._main_window.show()  # show the main window and all its content
        self._gui_def = _read_gui_definition(gui_def)  # read the GUI definition from the xml file
        self.setStyle('Fusion')  # different style for better readability

    def _set_field_editable(self, field_name, editable):
        """Set a given field to be editable or not

        :param field_name: name of the field in the current widget
        :param editable: bool if the field should be editable
        :return: None
        """

        # find the field with the given name in the current widget and set it editable
        field = self.get_current_widget().findChild(QObject, field_name)
        field.setReadOnly(not editable)

    def connect_table_click(self, action):
        table_widgets = self.get_main_left().findChildren(QTableWidget)
        for widget in table_widgets:
            widget_clicked = widget.objectName()
            if 'tableMain' in widget_clicked:
                widget.doubleClicked.connect(self._make_widget_action(action, widget_clicked))

        # connect search table click
        widget = self._main_window.detail_widgets['search'].tableWidget_search
        widget_clicked = widget.objectName()
        widget.doubleClicked.connect(self._make_widget_action(action, widget_clicked))

    def connect_create(self, action):
        """Connect the create button of the main widget to the corresponding method

        :param action: method to be connected to the create button
        :return: None
        """

        buttons = self.get_main_left().findChildren(QPushButton)
        for button in buttons:
            button_clicked = button.objectName()
            if 'create' in button_clicked:
                button.clicked.connect(self._make_widget_action(action, button_clicked))

    @staticmethod
    def _make_widget_action(action, name):
        # function factory to give the widget name into the given function
        def widget_action():
            action(name)

        return widget_action

    def connect_display(self, tables, action):
        """Connect the display button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the display button
        :return: None
        """

        for table in tables:  # iterate through all given table
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_display.clicked.connect(action)

    def connect_edit(self, tables, action):
        """Connect the edit button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the edit button
        :return: None
        """

        for table in tables:  # iterate through all given table
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_edit.clicked.connect(action)

    def connect_export(self, tables, action):
        """Connect the export button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the export button
        :return: None
        """

        for table in tables:  # iterate through all given table
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_export.clicked.connect(action)

    def connect_print(self, tables, action):
        """Connect the print button of all specified widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the print button
        :return: None
        """

        for table in tables:  # iterate through all given tables
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_print.clicked.connect(action)

    def connect_search(self, action):
        """Connect the search button of the main widget to the corresponding method

        :param action: method to be connected to the search button
        :return: None
        """

        buttons = self.get_main_window().findChildren(QPushButton)
        for button in buttons:
            button_clicked = button.objectName()
            if 'search' in button_clicked:
                button.clicked.connect(self._make_widget_action(action, button_clicked))

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

        for table in tables:  # iterate through all given tables
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_cancel.clicked.connect(action)

    def connect_save(self, tables, action):
        """Connect the save button of all table widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the save button
        :return: None
        """

        for table in tables:  # iterate through all given tables
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_save.clicked.connect(action)

    def connect_delete(self, tables, action):
        """Connect the delete button of all table widgets to the corresponding method

        :param tables: list of table names that correspond to widgets
        :param action: method to be connected to the delete button
        :return: None
        """

        for table in tables:  # iterate through all given tables
            if table in self._main_window.detail_widgets.keys():  # check if table has a widget defined
                self._main_window.detail_widgets[table].pushButton_delete.clicked.connect(action)

    def enable_save_button(self, enabled):
        """Enable or disable the save button of the current widget

        :param enabled: state of the save button
        :return: None
        """

        if not self.get_main_display():  # check if the main display is not active
            # enable the save button of the current widget
            self.get_current_widget().pushButton_save.setEnabled(enabled)

    def enable_delete_button(self, enabled):
        """Enable or disable the delete button of the current widget

        :param enabled: state of the delete button
        :return: None
        """

        if not self.get_main_display():  # check if the main display is not active
            # enable the delete button of the current widget
            self.get_current_widget().pushButton_delete.setEnabled(enabled)

    def _enable_global_buttons(self, enabled):
        """Enable or disable the global buttons

        :param enabled: state of the buttons
        :return: None
        """

        # enable the commit button
        self._main_window.findChild(QPushButton, 'pushButton_save_db').setEnabled(enabled)
        # enable the revert button
        self._main_window.findChild(QPushButton, 'pushButton_revert_db').setEnabled(enabled)

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

    def get_current_widget_name(self) -> str:
        """Get the name of the currently stored widget

        :return: name of the currently stored widget
        """

        return self._main_window.get_current_widget_name()

    def get_displayed_table(self) -> str:
        """Get the name of the currently displayed table.
        Returns empty string and calls an error message if no table is currently displayed.

        :return: currently displayed table as string
        """

        try:
            # retrieve the name of the currently displayed table
            return self.get_current_widget().label_table_name.text()
        except AttributeError:
            # label is not available in the current widget
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
        for selection in table_widget.selectedRanges():  # iterate the selection of the given table widget
            if selection.topRow() == selection.bottomRow():  # check if only one row is selected
                selected_rows.append(selection.topRow())  # append the single row
            else:
                # more than one row is selected, so append all rows in the selected range
                for row in range(selection.topRow(), selection.bottomRow() + 1):
                    selected_rows.append(row)
        return selected_rows

    def get_selected_rows_of_current_widget(self) -> dict:
        """Retrieve the selected row indices of the current table widget.

        :return: dict of row indices that are selected
        """
        # find all table widgets in the current widget
        table_widgets = self.get_current_widget().findChildren(QTableWidget)

        tables = {}
        for table_widget in table_widgets:  # iterate through all table widgets
            rows = self._get_selection_of_widget(table_widget)  # retrieve the selected rows
            tables[table_widget.objectName()] = rows  # add the selected rows to the dict
        return tables

    def get_selected_rows_of_widget(self, table_widget_name) -> list:
        """Retrieve the selected row indices of the given table widget.

        :return: list of row indices that are selected
        """

        # find the table widget in the current widget with the given name
        table_widget = self._main_window.findChild(QTableWidget, table_widget_name)

        if table_widget is not None:  # check if a table widget was found
            rows = self._get_selection_of_widget(table_widget)  # retrieve the selected rows
            return rows
        else:
            # no table widget with the given name could be found
            raise error.WidgetNotKnownError(f'Widget {table_widget_name} is not known in current widget!')

    def get_unselected_rows_of_widget(self, table_widget_name) -> list:
        """Retrieve the unselected row indices of the given table widget.

        :return: list of row indices that are unselected
        """

        # find the table widget in the current widget with the given name
        table_widget = self.get_current_widget().findChild(QTableWidget, table_widget_name)

        if table_widget is not None:  # check if a table widget was found
            unselected_rows = []
            rows = self._get_selection_of_widget(table_widget)  # retrieve the selected rows
            for row in range(0, table_widget.rowCount()):  # iterate through all rows
                if row not in rows:  # check if the current row is selected
                    unselected_rows.append(row)  # append if the row is not selected
            return unselected_rows
        else:
            # no table widget with the given name could be found
            raise error.WidgetNotKnownError(f'Widget {table_widget_name} is not known in current widget!')

    def init_main_widget(self, tables, table_data):
        """Initialize the main widget with values

        :param tables: values of tables that need to be processed
        :param table_data: dictionary of table data
        :return: None
        """

        for table in tables:
            table_widget = self.get_main_left().findChild(QTableWidget, 'tableMain_' + table.lower())
            self._set_table_widget(table_widget, table_data[table], 2)
            self._set_table_widget_selection(table_widget, [])

    def ask_user_confirmation(self, title, message):
        """Ask the user for confirmation of a message

        :param title: header title of the dialog
        :param message: text to be displayed
        :return: True if answer_yes was chosen
        """

        answer = QMessageBox.question(self.get_current_widget(), title, message,
                                      QMessageBox.Yes | QMessageBox.No)

        if answer == QMessageBox.Yes:
            return True
        else:
            return False

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
    def _set_table_widget(table_widget, table_data, max_columns=0):
        """Set the contents of the table widget to the given table data

        :param table_widget: QTableWidget object
        :param table_data: data as Dataframe
        :return: None
        """

        # set the main settings of the table widget corresponding to the given data
        table_widget.setRowCount(len(table_data.index))
        if max_columns == 0:
            table_widget.setColumnCount(len(table_data.columns))
        else:
            table_widget.setColumnCount(max_columns)

        table_widget.setHorizontalHeaderLabels(table_data.columns.to_list())
        """index = 0
        for column in table_data.columns.to_list():
            header_item = QTableWidgetItem(column)
            header_item.setBackground(QColor(211, 211, 211))
            table_widget.setHorizontalHeaderItem(index, header_item)
            index += 1
        """

        index = 0
        for key, row in table_data.iterrows():  # iterate through the given data
            col_index = 0
            for column in table_data.columns:  # iterate through the columns
                if max_columns == 0 or col_index < max_columns:
                    # create a widget item and set it to the corresponding row/column
                    table_widget.setItem(index, col_index, QTableWidgetItem(str(row[column])))
                    col_index += 1
            index += 1
        table_widget.resizeColumnsToContents()

    @staticmethod
    def _set_table_widget_selection(table_widget, table_rows):
        """Set the contents of the table widget to the given table data

        :param table_widget: QTableWidget object
        :param table_rows: selected rows of the table
        :return: None
        """

        for row in range(0, table_widget.rowCount()):  # iterate through all rows of the table widget
            selection = QTableWidgetSelectionRange(row, 0, row, table_widget.columnCount() - 1)
            if row in table_rows:  # check if this row is selected
                table_widget.setRangeSelected(selection, True)  # set this row selected
            else:
                table_widget.setRangeSelected(selection, False)  # set this row unselected

    def switch_main_widget(self, name=None):
        """Switch the main widget to a table specific one or back to the initial main widget

        :param name: name of the table/widget to be loaded - will switch back to main if None is given
        :return: None
        """

        if name is None:  # check if a widget name was given
            # switch back to the main widget
            self._main_window.switch_main_widget()
            self._enable_global_buttons(True)  # enable the global buttons (revert/commit)
        else:
            # switch to the specified widget
            self._main_window.switch_main_widget(name)
            self._enable_global_buttons(False)  # disable the global buttons (revert/commit)

    def set_relation_table(self, table, table_data, editable) -> bool:
        """Set the contents of a relation table in the corresponding widget

        :param table_data: data of the relation table
        :param table: name of the relation table
        :param editable: bool to set the table widget editable
        :return: True if a relation table was set
        """

        for table_widget in self.get_current_widget().findChildren(QTableWidget):  # iterate through all table widgets
            if table_widget.objectName().lower() == f'table_{table}'.lower():
                # if the table widget name matches the given table name, the given table data can be set
                try:
                    self._set_table_widget(table_widget, table_data)
                    # table_widget.setEnabled(editable)  # enable that the widget can be edited
                    if editable:
                        table_widget.setSelectionMode(QAbstractItemView.MultiSelection)
                    else:
                        table_widget.setSelectionMode(QAbstractItemView.NoSelection)
                except AttributeError:
                    # an error occurred when trying to set the table widget
                    self.send_critical_message('Fehler beim Setzen der Beziehungstabellen!')
                else:
                    return True  # a relation table was set

        return False  # no relation table was set

    def set_relation_table_selection(self, table, selected_rows):
        """Set the contents of a relation table in the corresponding widget

        :param selected_rows: selected rows of the table
        :param table: name of the relation table
        :return: None
        """

        for table_widget in self.get_current_widget().findChildren(QTableWidget):  # iterate through all table widgets
            if table_widget.objectName().lower() == f'table_{table}'.lower():
                # if the table widget name matches the given table name, the given selection can be set
                try:
                    self._set_table_widget_selection(table_widget, selected_rows)
                except AttributeError:
                    # an error occurred when trying to set the table widget selection
                    self.send_critical_message('Fehler beim Setzen der Beziehungstabellen!')

    def set_search_table(self, table_name, table_data):
        """Set the contents of the search widget

        :param table_name: name of the table that the search is executed for
        :param table_data: content of the searched table
        :return: None
        """

        # find the table widget in the current widget - the search table may only have one
        table_widget = self.get_current_widget().findChild(QTableWidget)

        self._set_table_widget(table_widget, table_data)  # set the table widget to the given data
        self._set_table_widget_selection(table_widget, [])  # clear the table widget selection
        self.get_current_widget().label_table_name.setText(table_name)  # set the table name

    def get_item_of_table_widget(self, widget_name, row, column) -> str:
        """Get the item of a table widget in a specific row and column as text

        :param widget_name: name of the table widget
        :param row: item position row
        :param column: item position column
        :return: text of specified item in table widget
        """

        # find the table widget with the given name in the current widget
        table_widget = self.get_current_widget().findChild(QTableWidget, widget_name)
        # return the text of the specified item of the table widget
        return table_widget.item(row, column).text()

    def get_field_of_current_widget(self, field_name) -> str:
        """Get the value of a field in the current widget

        :param field_name: name of the PyQt field
        :return: value of the field as string
        """

        # find the field with the given name in the current widget
        field = self.get_current_widget().findChild(QObject, field_name)

        # get the field data corresponding to the field type
        if isinstance(field, QLineEdit):
            return field.text()
        elif isinstance(field, QTextEdit):
            return field.toPlainText()
        elif isinstance(field, QTimeEdit):
            return str(field.time().toPyTime())
        else:
            # field type is unknown, so no data can be retrieved
            self.send_critical_message('Fehler beim Lesen der Felder im aktuellen Widget!')

    def set_fields_of_current_widget(self, table_name, row_data=None, editable=True):
        """Set all fields of the current widget to the corresponding value from the given data

        :param table_name: name of the table that is currently displayed
        :param row_data: values that should be set into the current widget
        :param editable: bool if a field should be editable
        :return: None
        """

        fields = self.get_gui_definition()[table_name][1]  # get the fields of the given table
        for field in fields.keys():  # iterate through all fields and set the data
            if row_data is not None:
                self.set_field_in_current_widget(fields[field], row_data[field])
            self._set_field_editable(fields[field], editable)

    def set_field_in_current_widget(self, field_name, field_data):
        """Set a field in the current widget to the corresponding data

        :param field_name: name of the PyQt field
        :param field_data: value to be set for the field
        :return: None
        """

        # find the field with the given name in the current widget
        field = self.get_current_widget().findChild(QObject, field_name)

        # set the field data corresponding to the field type
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
            # field type is unknown, so no data can be set
            self.send_critical_message('Fehler beim Setzen der Felder im aktuellen Widget!')

    @staticmethod
    def _set_tree_structure(tree_widget: QTreeWidget, tree_items, header_labels, column_count=6, expand_all=False):
        """Set the tree structure of the given QTreeWidget.

        :param tree_widget: QTreeWidget that shall be changed
        :param tree_items: QTreeWidgetItems to be inserted into the tree widget
        :param header_labels: labels of the header columns
        :param column_count: count of columns to be displayed
        :return: None
        """

        tree_widget.setColumnCount(column_count)
        tree_widget.setHeaderLabels(header_labels)
        tree_widget.clear()  # remove all items that are currently stored
        tree_widget.insertTopLevelItems(0, tree_items)
        tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  # activate auto-resize
        if expand_all:
            tree_widget.expandAll()  # auto-expand the tree

    @staticmethod
    def create_tree_item(name, item_data, child_items):
        """Create and return a tree item with the given item data and the child items.

        :param name: name of the table for which a tree item should be created
        :param item_data: data of the tree item to be displayed
        :param child_items: items that are children of this item
        :return: QTreeWidgetItem with the given data
        """

        value_list = [name]  # name is the first value of the item
        for value in item_data:  # iterate through the given data to append to the value list
            if isinstance(value, str):
                # if the value is already a str, it can be appended
                value_list.append(value)
            else:
                # if the value is not a str, it must be converted to a str first
                value_list.append(str(value))

        tree_item = QTreeWidgetItem(value_list)  # create the tree item

        # add all given children to the item
        for child in child_items:
            tree_item.addChild(child)

        return tree_item

    def set_current_tree_widget(self, tree_items, header, expand_all: bool):
        """Set the tree widget in the currently displayed widget (not main widget)

        :param expand_all: expand all items of the tree if True
        :param tree_items: top level items that define the tree structure
        :param header: labels of the header columns
        :return: None
        """

        header_labels = ['Objekt'] + header
        self._set_tree_structure(self.get_current_widget().treeWidget, tree_items, header_labels, 6, expand_all)

    def get_current_tree_widget(self):
        """Retrieve the tree widget of the currently displayed widget

        :return: tree widget that is currently displayed
        """

        return self.get_current_widget().treeWidget

    def set_main_tree_widget(self, tree_items):
        """Set the main tree widget with the given tree items

        :param tree_items: top level items that define the tree structure
        :return: None
        """

        header_labels = ['Objekt', 'ID', '', '', '', '']
        self._set_tree_structure(self._main_window.main_right.treeWidget, tree_items, header_labels, 6, False)

    def set_html(self, html):
        tree_widget = self.get_current_tree_widget()
        self.get_current_widget().contentLayout.removeWidget(tree_widget)
        tree_widget.hide()
        html_view = QWebEngineView(self.get_current_widget())
        self.get_current_widget().contentLayout.addWidget(html_view)
        html_view.setHtml(html)
        html_view.show()
        pass

    def print_widget(self):
        """Print the current widget as a viewable file

        :return: None
        """

        filename, _ = QFileDialog.getSaveFileName(self._main_window, 'Export PDF', None,
                                                  'PDF files (.pdf);;All Files()')
        if filename != '':
            if QFileInfo(filename).suffix() == '':
                filename += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            # self.get_current_widget().document().print_(printer)
            self.primaryScreen().grabWindow(self.get_current_tree_widget().winId()).save(f'{filename}.jpg', 'jpg')
            # self.get_current_widget().render(QPainter(printer))

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

    # parse given file into ElementTree
    tree = ElTr.parse(gui_def)
    root = tree.getroot()
    def_gui = {}  # create empty dictionary for return

    for item in root.findall('WIDGET'):
        name = item.attrib['NAME']  # name of the widget
        table = item.attrib['TABLE']  # table that corresponds to the widget

        fields = {}  # fields of this widget
        tables = {}  # table widgets of this widget
        for child in item:
            if child.tag == 'FIELD':
                # child is a field, so the column name and the field name should be linked
                fields[child.attrib['COLUMN']] = child.attrib['NAME']
            elif child.tag == 'TABLE':
                # child is a table widget, so the widget name should be linked to the relation table and its keys
                tables[child.attrib['NAME']] = [child.attrib['REL_TABLE'], child.attrib['PK'], child.attrib['FK']]
            else:
                # new child tag that is not yet defined
                raise error.DataMismatchError(f'Error in _read_gui_definition: {child.tag} is unknown!')

        # save the data in the dictionary to the corresponding table name
        def_gui[table] = [name, fields, tables]

    return def_gui
