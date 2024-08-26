# Jan Sauerland

# import data
# import view
import control

DATABASE = 'data/main.db'
DB_DEF = 'data/db_def.xml'
GUI_DEF = 'view/gui_def.xml'

if __name__ == '__main__':
    print('Jan Sauerland')
    # data_con = data.DatabaseConnector(DATABASE, DB_DEF)
    # main_view = view.create_main_application([data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN])
    main_control = control.MainControl(DATABASE, DB_DEF, GUI_DEF)
    main_control.start_application()

