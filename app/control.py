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
        self.main_app.init_main_widget(self.main_tables, self._get_tree_structure())
        self._init_connectors()

    def _init_connectors(self):
        """

        :return:
        """
        self.main_app.connect_create(self._button_create)
        self.main_app.connect_search(self._button_search)
        self.main_app.connect_commit(self._button_commit)
        self.main_app.connect_revert(self._button_revert)
        self.main_app.connect_save(self.main_tables, self._button_save)
        self.main_app.connect_cancel(self.main_tables, self._button_cancel)

    def _button_create(self):
        """

        :return: None
        """
        print('button_create:', self)

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            print(table)
            self.main_app.switch_main_widget(table)
            # TODO: fill relation tables in widget
            relation_tables = self.data_con.get_table_content_relation(table)
            print(f'relation_tables: {relation_tables}')
            for table_name in relation_tables.keys():
                sub_tables = table_name.split('_')
                if len(sub_tables) == 2:
                    if table == sub_tables[0]:
                        self.main_app.set_relation_table(sub_tables[1], self.data_con.get_table_content(sub_tables[1]))
                    elif table == sub_tables[1]:
                        self.main_app.set_relation_table(sub_tables[0], self.data_con.get_table_content(sub_tables[0]))
                    else:
                        # TODO: Error message
                        pass
                else:
                    # TODO: Error message: wrong database scheme
                    pass
                pass
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_search(self):
        """

        :return: None
        """
        print('search:', self)

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            print(table)
            self.main_app.switch_main_widget(table)
            # TODO: implement search for table
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_commit(self):
        """

        :return: None
        """
        print('commit', self)

        self.data_con.commit_changes()

    def _button_revert(self):
        """

        :return:
        """
        print('revert', self)

        # TODO: Revert all changes, read data again from database

        self.data_con.rollback_changes()

    def _button_cancel(self):
        """

        :return:
        """
        print('cancel', self)

        # TODO: Cancel this widget - clear all fields

        self.main_app.switch_main_widget()

    def _button_save(self):
        """

        :return:
        """
        print('save', self)

        current_table = self.main_app.get_current_widget().label_table_name.text()
        print(self.main_app.get_current_widget().label_table_name.text())
        if current_table == data.NAME_EXERCISE:
            data_exercise = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText(),
                             str(self.main_app.get_current_widget().timeEdit_duration.time().toPyTime()),
                             self.main_app.get_current_widget().lineEdit_video_url.text()]
            print(data_exercise)
            self._save_entry(data.NAME_EXERCISE, data_exercise)
        elif current_table == data.NAME_UNIT:
            data_unit = [self.main_app.get_current_widget().lineEdit_id.text(),
                         self.main_app.get_current_widget().lineEdit_name.text(),
                         self.main_app.get_current_widget().textEdit_description.toPlainText(),
                         str(self.main_app.get_current_widget().timeEdit_duration.time().toPyTime())]
            print(data_unit)
            self._save_entry(data.NAME_UNIT, data_unit)
        elif current_table == data.NAME_PLAN:
            data_plan = [self.main_app.get_current_widget().lineEdit_id.text(),
                         self.main_app.get_current_widget().lineEdit_name.text(),
                         self.main_app.get_current_widget().textEdit_description.toPlainText()]
            print(data_plan)
            self._save_entry(data.NAME_PLAN, data_plan)
        elif current_table == data.NAME_CATEGORY:
            data_category = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText(),
                             self.main_app.get_current_widget().lineEdit_color.text()]
            print(data_category)
            self._save_entry(data.NAME_CATEGORY, data_category)
        elif current_table == data.NAME_RESOURCE:
            data_resource = [self.main_app.get_current_widget().lineEdit_id.text(),
                             self.main_app.get_current_widget().lineEdit_name.text(),
                             self.main_app.get_current_widget().textEdit_description.toPlainText()]
            print(data_resource)
            self._save_entry(data.NAME_RESOURCE, data_resource)

        # TODO: also build and save related tables

        self.main_app.switch_main_widget()

    def _get_tree_structure(self, table=None):
        """

        :param table:
        :return:
        """
        # get all table contents and display connections in tree structure for TreeView
        # TODO: build tree structure for pyqt tree view
        pass

    def _save_entry(self, table_name, data_entry):
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

    def _save_related_table(self, table_name, data_relation):
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
