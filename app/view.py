from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import sys


class MainWindow(QMainWindow):
    main_layout: QLayout
    main_left: QWidget
    main_right: QWidget
    current_widget: QWidget

    def __init__(self, ui_file, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(ui_file, self)
        self.setWindowTitle('sportApp - main')

        self.main_layout = self.horizontalLayout_main_widget
        self.main_left = uic.loadUi('view/main_left.ui')
        self.main_right = uic.loadUi('view/main_right.ui')
        self.main_layout.addWidget(self.main_left)
        self.main_layout.addWidget(self.main_right)

        self.main_left.pushButton_create.clicked.connect(self.button_create)

    def button_create(self, s):
        print('create', s)

        self.current_widget = uic.loadUi('view/exercise_widget.ui')
        # self.current_widget = MainWidget('view/exercise_widget.ui')
        self.main_layout.removeWidget(self.main_left)
        self.main_left.close()
        self.main_layout.removeWidget(self.main_right)
        self.main_right.close()
        self.main_layout.addWidget(self.current_widget)
        # self.current_widget.buttonBox.accepted.connect(lambda: print('accepted'))
        # self.current_widget.buttonBox.rejected.connect(lambda: print('rejected'))
        # print(self.current_widget.buttonBox)
        self.current_widget.pushButton_save.clicked.connect(self.button_save)
        self.current_widget.pushButton_cancel.clicked.connect(self.button_cancel)

    def button_cancel(self, s):
        print('cancel', s)
        print(f'main_layout children: {self.main_layout.children()}')

        for widget in self.main_layout.findChildren():
            print(f'found widget to remove: {widget}')
            self.main_layout.removeWidget(widget)
            widget.close()

        self.main_layout.addWidget(self.main_left)
        self.main_layout.addWidget(self.main_right)

    def button_save(self, s):
        print('save', s)

        # TODO: Save the data

        for widget in self.main_layout.findChildren():
            self.main_layout.removeWidget(widget)
            widget.close()

        self.main_layout.addWidget(self.main_left)
        self.main_layout.addWidget(self.main_right)


class MainWidget(QWidget):
    def __init__(self, ui_file, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        uic.loadUi(ui_file, self)

        # self.buttonBox.accepted.connect(lambda: print('accepted'))
        self.buttonBox.accepted.connect(self.button_save)
        # self.buttonBox.rejected.connect(lambda: print('rejected'))
        self.buttonBox.rejected.connect(self.button_cancel)

    def button_save(self, s):
        print('widget save:', self)

    def button_cancel(self, s):
        print('widget cancel:', self)


app = QApplication(sys.argv)

main_window = MainWindow('view/main.ui')
main_window.show()

app.exec_()
