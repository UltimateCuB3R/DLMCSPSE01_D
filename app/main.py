# Jan Sauerland
# Kurs DLMCSPSE01_D
# IU Internationale Hochschule

import control
import os

DATABASE = 'data\\main.db'
DB_DEF = 'data\\db_def.xml'
GUI_DEF = 'view\\gui_def.xml'

if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))  # get the current path
    main_control = control.MainControl(DATABASE, DB_DEF, GUI_DEF, path)  # create the main control
    main_control.start_application()  # start the application

