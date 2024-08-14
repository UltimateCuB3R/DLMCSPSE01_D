from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import sys
import data


class _MainWindow(QMainWindow):
    main_layout: QLayout
    main_left: QWidget
    main_right: QWidget
    current_widget: QWidget
    main_display: bool
    # translations: dict

    def __init__(self, ui_file, translations, *args, **kwargs):
        super(_MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(ui_file, self)
        self.setWindowTitle('sportApp - main')

        self.main_layout = self.horizontalLayout_main_widget
        self.main_left = uic.loadUi('view/main_left.ui')
        self.main_right = uic.loadUi('view/main_right.ui')
        self.main_layout.addWidget(self.main_left)
        self.main_layout.addWidget(self.main_right)
        self.main_display = True
        self.main_left.pushButton_create.clicked.connect(self._button_main)

        # self.translations = translations

        self.main_left.comboBox_tables.addItems(translations)

    def _button_main(self, s):
        print('button_main:', s, self)

        path = 'view/' + self.main_left.comboBox_tables.currentText() + '_widget.ui'

        if self.main_display:
            self._switch_main_widget(uic.loadUi(path))
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_cancel(self, s):
        print('cancel', s)

        self._switch_main_widget()

    def _button_save(self, s):
        print('save', s)

        # TODO: Save the data
        print(self.current_widget.label_table_name.text())

        self._switch_main_widget()

    def _switch_main_widget(self, widget=None):
        if self.main_display:
            self.main_layout.removeWidget(self.main_left)
            self.main_left.hide()
            self.main_layout.removeWidget(self.main_right)
            self.main_right.hide()

            self.current_widget = widget
            self.main_layout.addWidget(self.current_widget)

            self.current_widget.pushButton_save.clicked.connect(self._button_save)
            self.current_widget.pushButton_cancel.clicked.connect(self._button_cancel)
            self.main_display = False
        else:
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater()

            self.main_left.show()
            self.main_layout.addWidget(self.main_left)
            self.main_right.show()
            self.main_layout.addWidget(self.main_right)
            self.main_display = True


class MainApplication(QApplication):
    _main_window: _MainWindow

    def __init__(self, ui_file, translations, *args, **kwargs):
        super(MainApplication, self).__init__(sys.argv, *args, **kwargs)
        self._main_window = _MainWindow(ui_file, translations)
        self._main_window.show()

        self.exec_()

    def get_main_window(self) -> _MainWindow:
        return self._main_window

    def init_main_window(self):
        # Set Table Combobox
        # Set Widget Config
        # Set Tree Overview
        pass


def create_main_application(translations):
    app = QApplication(sys.argv)

    main_window = _MainWindow('view/main.ui', translations)
    main_window.show()

    app.exec_()
    return main_window
