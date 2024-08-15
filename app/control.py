import data
import view


class MainControl:
    data_con: data.DatabaseConnector
    main_app: view.MainApplication
    main_tables: []

    def __init__(self, database, db_def):
        self.data_con = data.DatabaseConnector(database, db_def)
        self.main_tables = [data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN, data.NAME_CALENDAR, data.NAME_CATEGORY,
                            data.NAME_RESOURCE]
        self.main_app = view.MainApplication('view/main.ui', self.main_tables)
        self.main_app.init_main_window(self.main_tables, self.get_tree_structure())
        self._init_connectors()

    def _init_connectors(self):
        self.main_app.connect_main(self._button_main)
        self.main_app.connect_save(self.main_tables, self._button_save)
        self.main_app.connect_cancel(self.main_tables, self._button_cancel)

    def _button_main(self, s):
        """

        :param s:
        :return:
        """
        print('button_main:', s, self)

        # path = 'view/' + self.main_app.get_main_left().comboBox_tables.currentText() + '_widget.ui'

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            print(table)
            self.main_app.switch_main_widget(table)
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_cancel(self, s):
        """

        :param s:
        :return:
        """
        print('cancel', s, self)

        # TODO: Cancel this widget

        self.main_app.switch_main_widget()

    def _button_save(self, s):
        """

        :param s:
        :return:
        """
        print('save', s, self)

        # TODO: Save the data
        current_table = self.main_app.get_current_widget().label_table_name.text()
        print(self.main_app.get_current_widget().label_table_name.text())
        if current_table == data.NAME_EXERCISE:
            """data_exercise = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.text(),
                             self.main_app.get_current_widget().timeEdit_duration.text(),
                             self.main_app.get_current_widget().lineEdit_video_url.text()]"""
            data_exercise = ['', 'Test Übung 2', 'Dies ist ein Test 2', 600.0,
                             'https://www.youtube.com/watch?v=dQw4w9WgXcQ']
            print(data_exercise)
            self.save_exercise(self.main_app.get_widget_fields(data.NAME_EXERCISE), data_exercise)

        self.main_app.switch_main_widget()

    def get_tree_structure(self, table=None):
        # get all table contents and display connections in tree structure for TreeView
        # TODO: build tree structure for pyqt tree view
        pass

    def save_exercise(self, table_name, data_exercise):
        entry = self.data_con.build_entry_for_table(table_name, data_exercise)
        if data_exercise[0] == '':
            self.data_con.add_entry_to_table(table_name, entry)
        else:
            self.data_con.modify_entry_in_table(table_name, entry)

    def start_application(self):
        self.main_app.start_application()
