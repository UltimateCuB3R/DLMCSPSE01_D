# Jan Sauerland

import control

DATABASE = 'data/main.db'
DB_DEF = 'data/db_def.xml'
GUI_DEF = 'view/gui_def.xml'

if __name__ == '__main__':
    print('Jan Sauerland')
    main_control = control.MainControl(DATABASE, DB_DEF, GUI_DEF)
    main_control.start_application()

