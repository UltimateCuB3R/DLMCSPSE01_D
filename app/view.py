from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import sys


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('view/main.ui', self)
        self.setWindowTitle('sportApp')


app = QApplication(sys.argv)

main_window = MainWindow()
main_window.show()

app.exec_()
