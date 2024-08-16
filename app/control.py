import data
import view


class MainControl:
    """

    """
    data_con: data.DatabaseConnector
    main_app: view.MainApplication
    main_tables: []

    def __init__(self, database, db_def):
        """

        :param database:
        :param db_def:
        """
        self.data_con = data.DatabaseConnector(database, db_def)
        self.main_tables = [data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN, data.NAME_CALENDAR, data.NAME_CATEGORY,
                            data.NAME_RESOURCE]
        self.main_app = view.MainApplication(self.main_tables)
        self.main_app.init_main_window(self.main_tables, self.get_tree_structure())
        self._init_connectors()

    def _init_connectors(self):
        """

        :return:
        """
        self.main_app.connect_main(self._button_main)
        self.main_app.connect_commit(self._button_commit)
        self.main_app.connect_revert(self._button_revert)
        self.main_app.connect_save(self.main_tables, self._button_save)
        self.main_app.connect_cancel(self.main_tables, self._button_cancel)

    def _button_main(self, s):
        """

        :param s:
        :return:
        """
        print('button_main:', s, self)

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            print(table)
            self.main_app.switch_main_widget(table)
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_commit(self, s):
        """

        :param s:
        :return:
        """
        print('commit', s, self)

        # TODO: Commit all saved data

        self.data_con.commit_changes()

    def _button_revert(self, s):
        """

        :param s:
        :return:
        """
        print('revert', s, self)

        # TODO: Revert all changes, read data again from database

        self.data_con.rollback_changes()

    def _button_cancel(self, s):
        """

        :param s:
        :return:
        """
        print('cancel', s, self)

        # TODO: Cancel this widget - clear all fields?

        self.main_app.switch_main_widget()

    def _button_save(self, s):
        """

        :param s:
        :return:
        """
        print('save', s, self)

        current_table = self.main_app.get_current_widget().label_table_name.text()
        print(self.main_app.get_current_widget().label_table_name.text())
        if current_table == data.NAME_EXERCISE:
            data_exercise = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText(),
                             str(self.main_app.get_current_widget().timeEdit_duration.time().toPyTime()),
                             self.main_app.get_current_widget().lineEdit_video_url.text()]
            print(data_exercise)
            self.save_entry(data.NAME_EXERCISE, data_exercise)
        elif current_table == data.NAME_UNIT:
            data_unit = [self.main_app.get_current_widget().lineEdit_id.text(),
                         self.main_app.get_current_widget().lineEdit_name.text(),
                         self.main_app.get_current_widget().textEdit_description.toPlainText(),
                         str(self.main_app.get_current_widget().timeEdit_duration.time().toPyTime())]
            print(data_unit)
            self.save_entry(data.NAME_UNIT, data_unit)
        elif current_table == data.NAME_PLAN:
            data_plan = [self.main_app.get_current_widget().lineEdit_id.text(),
                         self.main_app.get_current_widget().lineEdit_name.text(),
                         self.main_app.get_current_widget().textEdit_description.toPlainText()]
            print(data_plan)
            self.save_entry(data.NAME_PLAN, data_plan)
        elif current_table == data.NAME_CATEGORY:
            data_category = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText(),
                             self.main_app.get_current_widget().lineEdit_color.text()]
            print(data_category)
            self.save_entry(data.NAME_CATEGORY, data_category)
        elif current_table == data.NAME_RESOURCE:
            data_resource = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText()]
            print(data_resource)
            self.save_entry(data.NAME_RESOURCE, data_resource)

        # TODO: also build and save related tables

        self.main_app.switch_main_widget()

    def get_tree_structure(self, table=None):
        """

        :param table:
        :return:
        """
        # get all table contents and display connections in tree structure for TreeView
        # TODO: build tree structure for pyqt tree view
        pass

    def save_entry(self, table_name, data_entry):
        """

        :param table_name:
        :param data_entry:
        :return:
        """
        entry = self.data_con.build_entry_for_table(table_name, data_entry)
        if data_entry[0] == '':
            self.data_con.add_entry_to_table(table_name, entry)
        else:
            self.data_con.modify_entry_in_table(table_name, entry)

    def save_related_table(self, table_name, data_relation):
        """

        :param table_name:
        :param data_relation:
        :return:
        """
        entry = self.data_con.build_entry_for_table(table_name, data_relation)
        if data_relation[0] == '':
            self.data_con.add_entry_to_table(table_name, entry)
        else:
            # TODO: do nothing for relation tables?
            pass
            # self.data_con.modify_entry_in_table(table_name, entry)

    def start_application(self):
        """

        :return:
        """

        self.main_app.start_application()
