import data
import view
import error

NAME_SEARCH = 'search'


class MainControl:
    """Main controller class to handle the user interactions and data modifications.

    """
    data_con: data.DatabaseConnector
    main_app: view.MainApplication
    main_tables: []

    def __init__(self, database, db_def, gui_def):
        """Initialize the main control by giving the paths of the database and the definition file.
        The main application is created and loaded with all necessary widgets.

        :param database: path to the database file
        :param db_def: path to the database definition file
        """
        self.data_con = data.DatabaseConnector(database, db_def)
        self.main_tables = [data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN, data.NAME_CALENDAR, data.NAME_CATEGORY,
                            data.NAME_RESOURCE]
        self.main_app = view.MainApplication(self.main_tables + [NAME_SEARCH], gui_def)
        self.main_app.init_main_widget(self.main_tables, self._get_tree_structure())
        self._init_connectors()

    def _init_connectors(self):
        """Initialize all button connections to the corresponding action methods when they are clicked.

        :return: None
        """
        self.main_app.connect_create(self._button_create)
        self.main_app.connect_search(self._button_search)
        self.main_app.connect_commit(self._button_commit)
        self.main_app.connect_revert(self._button_revert)
        self.main_app.connect_save(self.main_tables, self._button_save)
        self.main_app.connect_cancel(self.main_tables + [NAME_SEARCH], self._button_cancel)
        self.main_app.connect_display([NAME_SEARCH], self._button_display)
        self.main_app.connect_edit([NAME_SEARCH], self._button_edit)

    def _button_create(self):
        """This action is called when the create button is pressed.
        The widget according to the chosen table is loaded in creation mode.
        Any existing relation tables to the chosen table are loaded into the widget.

        :return: None
        """
        print('create:', self)

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

    def _button_display(self):
        """

        :return:
        """

        print('display:', self)
        pass

    def _button_edit(self):
        """

        :return: None
        """

        print('edit:', self)
        table_name = self.main_app.get_current_widget().label_table_name.text()
        table_rows = self.main_app.get_selected_rows_of_current_widget()
        if len(table_rows) == 0:
            self.main_app.send_critical_message('Fehler! Keine Zeile ausgewählt! Bitte genau eine Zeile auswählen!')
        elif len(table_rows) > 1:
            self.main_app.send_critical_message('Fehler! Zu viele Zeilen ausgewählt! Bitte genau eine Zeile auswählen!')
        else:
            # switch to chosen table widget and fill the widget with data
            self.main_app.switch_main_widget(table_name)
            table_data = self.data_con.get_table_content(table_name)
            row = table_data.iloc[table_rows[0]]
            print(row)
            fields = self.main_app.get_gui_definition()[table_name][1]
            for field in fields.keys():
                self.main_app.set_field_in_current_widget(fields[field], row[field])

    def _button_search(self):
        """This action is called when the search button is pressed.
        The central search widget is loaded with the corresponding table data of the chosen table.

        :return: None
        """
        print('search:', self)

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            print(table)
            self.main_app.switch_main_widget('search')
            self.main_app.set_search_table(table, self.data_con.get_table_content(table))
            # TODO: implement search for table
        else:
            pass
            # TODO: Error message: Function should not be available

    def _button_commit(self):
        """This action commits all table changes to the database

        :return: None
        """
        print('commit', self)

        self.data_con.commit_changes()

    def _button_revert(self):
        """This action reverts all changes made to the tables and loads them back from the database.

        :return: None
        """
        print('revert', self)

        # TODO: Revert all changes, read data again from database

        self.data_con.rollback_changes()

    def _button_cancel(self):
        """This action cancels the current widget.
        All fields are cleared and the main widget is switched back.

        :return: None
        """
        print('cancel', self)

        # clear all fields of the current widget
        table_name = self.main_app.get_displayed_table()
        fields = self.main_app.get_gui_definition()[table_name][1]
        for field in fields.keys():
            self.main_app.set_field_in_current_widget(fields[field], '')

        # switch back to the main widget
        self.main_app.switch_main_widget()

    def _button_save(self):
        """

        :return: None
        """
        print('save', self)

        # collect all field values into a list and save it to the current table
        table_name = self.main_app.get_displayed_table()
        fields = self.main_app.get_gui_definition()[table_name][1]
        table_data = []
        for field_name in fields.keys():
            if field_name == 'ID':
                value = int(self.main_app.get_field_of_current_widget(fields[field_name]))
            else:
                value = self.main_app.get_field_of_current_widget(fields[field_name])
            table_data.append(value)
        print(table_name, table_data)
        self._save_entry(table_name, table_data)

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
        """Save an entry to the table.
        If an ID is given, the existing entry in the table is modified.
        If the ID is empty, a new entry is created in the table.

        :param table_name: name of the table
        :param data_entry: list of values for the table
        :return: None
        """
        try:
            entry = self.data_con.build_entry_for_table(table_name, data_entry)
            if data_entry[0] == '':
                self.data_con.add_entry_to_table(table_name, entry)
            else:
                self.data_con.modify_entry_in_table(table_name, entry)
        except error.DataMismatchError:
            self.main_app.send_critical_message('Fehler beim Aufbau des Tabelleneintrags! DataMismatchError')
        except error.NoDataFoundError:
            self.main_app.send_critical_message('Fehler beim Modifizieren eines Tabelleneintrags! NoDataFoundError')
        except error.ForbiddenActionError:
            self.main_app.send_critical_message('Fehler beim Speichern des Tabelleneintrags! ForbiddenActionError')

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
        """Start the main application

        :return: None
        """

        self.main_app.start_application()
