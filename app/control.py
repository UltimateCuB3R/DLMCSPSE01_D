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
        self.main_tables = [data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN, data.NAME_CATEGORY,
                            data.NAME_RESOURCE]  # data.NAME_CALENDAR is not yet implemented
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

    def _fill_relation_tables(self, table, main_id='', editable=True):
        """Fill the relation tables of the current widget according to the data related to the given table.
        Tables can optionally be set to disabled, so no changes can be done.
        If a main ID is given, the relation tables are selected according to the current data.

        :param table: name of the currently displayed table
        :param main_id: ID of the currently displayed entry (empty if creation dialog)
        :param editable: optional switch to set tables to disabled, so no changes can be done
        :return: None
        """

        # retrieve the defined relation table settings
        relation_tables = self.data_con.get_table_relations(table)
        # iterate all relation tables
        for table_name in relation_tables.keys():
            # relation table name consists of the two main tables joined together
            sub_tables = table_name.split('_')
            if len(sub_tables) == 2:
                if table == sub_tables[0]:
                    # first part is main table, so second part is sub_table
                    sub_table = sub_tables[1]
                elif table == sub_tables[1]:
                    # second part is main table, so first part is sub_table
                    sub_table = sub_tables[0]
                else:
                    # given table name is not existent in relation table name
                    self.main_app.send_critical_message(
                        f'Fehler! Beziehungen in Datenbankschema falsch gesetzt für {table}')
                    return

                # retrieve the data of the sub_table and set the relation table in the current widget
                sub_table_data = self.data_con.get_table_content(sub_table)
                relation_was_set = self.main_app.set_relation_table(sub_table, sub_table_data, editable)

                # set the selected entries of the sub_table only if a main ID is given and a relation was set
                if main_id != '' and relation_was_set:
                    # search for the entries in the relation table that match the main ID
                    relation_data = self.data_con.lookup_entry_in_table(table_name, relation_tables[table_name],
                                                                        [main_id])
                    # get the key name of the sub table
                    sub_table_key = self.data_con.get_table_relations(sub_table)[table_name]
                    # search for the entries in the sub table that match the entries of the selected relation table data
                    selected_sub_table_data = self.data_con.lookup_entry_in_table(sub_table, 'ID', relation_data[
                        sub_table_key].to_list())

                    # build the list of selected rows for the table widget
                    selected_rows = sub_table_data[sub_table_data['ID'].isin(selected_sub_table_data['ID'])].index.to_list()
                    # set the selection in the table widget
                    self.main_app.set_relation_table_selection(sub_table, selected_rows)

            else:
                # table name contains two underscores, logic cannot apply
                self.main_app.send_critical_message(
                    f'Fehler! Datenbankschema oder Programmierung falsch für {table}!')

    def _button_create(self):
        """This action is called when the create button is pressed.
        The widget according to the chosen table is loaded in creation mode.
        Any existing relation tables to the chosen table are loaded into the widget.

        :return: None
        """

        if self.main_app.get_main_display():
            table = self.main_app.get_main_left().comboBox_tables.currentText()
            self.main_app.switch_main_widget(table)
            self.main_app.enable_save_button(True)

            # fill the relation table widgets in the current widget
            self._fill_relation_tables(table)
        else:
            self.main_app.send_critical_message('Fehler! Funktion kann hier nicht ausgeführt werden!')

    def _button_display(self):
        """his action calls the detail widget of the chosen table with the selected entry.
        The widget is set to display mode, so no changes can be done.

        :return: None
        """

        table_name = self.main_app.get_current_widget().label_table_name.text()
        table_rows = list(self.main_app.get_selected_rows_of_current_widget().values())
        if len(table_rows) == 0:
            self.main_app.send_critical_message('Fehler! Keine Zeile ausgewählt! Bitte genau eine Zeile auswählen!')
        elif len(table_rows) > 1:
            self.main_app.send_critical_message('Fehler! Zu viele Zeilen ausgewählt! Bitte genau eine Zeile auswählen!')
        else:
            # switch to chosen table widget and fill the widget with data
            self.main_app.switch_main_widget(table_name)
            table_data = self.data_con.get_table_content(table_name)

            row = table_data.iloc[table_rows[0][0]]
            self.main_app.set_fields_of_current_widget(table_name, row, False)
            self.main_app.enable_save_button(False)

            self._fill_relation_tables(table_name, row['ID'], False)

    def _button_edit(self):
        """This action calls the detail widget of the chosen table with the selected entry.
        The widget is set to edit mode, so changes can be done and saved.

        :return: None
        """

        table_name = self.main_app.get_current_widget().label_table_name.text()
        table_rows = list(self.main_app.get_selected_rows_of_current_widget().values())

        # check if only one row was selected
        if len(table_rows) == 0:
            # too few lines selected
            self.main_app.send_critical_message('Fehler! Keine Zeile ausgewählt! Bitte genau eine Zeile auswählen!')
        elif len(table_rows) > 1:
            # too many lines selected
            self.main_app.send_critical_message('Fehler! Zu viele Zeilen ausgewählt! Bitte genau eine Zeile auswählen!')
        else:
            # switch to chosen table widget
            self.main_app.switch_main_widget(table_name)
            # get row data corresponding to chosen row
            table_data = self.data_con.get_table_content(table_name)
            row = table_data.iloc[table_rows[0][0]]
            # fill the widget with data
            self.main_app.set_fields_of_current_widget(table_name, row, True)
            self.main_app.enable_save_button(True)
            # fill the relation tables with data
            self._fill_relation_tables(table_name, row['ID'], True)

    def _button_search(self):
        """This action is called when the search button is pressed.
        The central search widget is loaded with the corresponding table data of the chosen table.

        :return: None
        """

        if self.main_app.get_main_display():
            # search can only be accessed via the main widget
            table_name = self.main_app.get_main_left().comboBox_tables.currentText()
            self.main_app.switch_main_widget('search')
            self.main_app.set_search_table(table_name, self.data_con.get_table_content(table_name))
        else:
            # fallback if action was improperly connected
            self.main_app.send_critical_message('Diese Funktion kann hier nicht ausgeführt werden!')

    def _button_commit(self):
        """This action commits all table changes to the database.

        :return: None
        """

        # commit all changes to the database
        self.data_con.commit_changes()

    def _button_revert(self):
        """This action reverts all changes made to the tables and loads them back from the database.

        :return: None
        """

        # revert all changes, read data again from database
        self.data_con.rollback_changes()

    def _button_cancel(self):
        """This action cancels the current widget.
        All fields are cleared and the main widget is switched back.

        :return: None
        """

        if self.main_app.get_current_widget_name() != 'search':
            # clear all fields of the current widget if it's not the search widget
            table_name = self.main_app.get_displayed_table()
            fields = self.main_app.get_gui_definition()[table_name][1]
            for field in fields.keys():
                self.main_app.set_field_in_current_widget(fields[field], '')

        # switch back to the main widget
        self.main_app.switch_main_widget()

    def _button_save(self):
        """This action saves the currently displayed entry.
        All GUI fields are read according to the GUI definition.
        The selected rows of the related tables are also saved to the relation tables.
        The unselected rows are deleted in the relation tables, if existing.

        :return: None
        """

        # collect all field values into a list and save it to the current table
        table_name = self.main_app.get_displayed_table()
        fields = self.main_app.get_gui_definition()[table_name][1]
        table_data = []
        for field_name in fields.keys():
            if field_name == 'ID':
                try:
                    value = int(self.main_app.get_field_of_current_widget(fields[field_name]))
                except ValueError:
                    if self.main_app.get_field_of_current_widget(fields[field_name]) == '':
                        value = self.main_app.get_field_of_current_widget(fields[field_name])
                    else:
                        self.main_app.send_critical_message('Fehler! ID konnte nicht verarbeitet werden!')
                        return
            else:
                value = self.main_app.get_field_of_current_widget(fields[field_name])
            table_data.append(value)
        entry_id = self._save_entry(table_name, table_data)

        # also build and save relation table data
        relation_tables = self.main_app.get_gui_definition()[table_name][2]
        for relation_widget_name in relation_tables.keys():
            # get selected rows of widget with name relation_widget_name
            selected_rows = self.main_app.get_selected_rows_of_widget(relation_widget_name)
            # build relation table entries
            rel_table_name = relation_tables[relation_widget_name][0]  # name of relation table
            main_id_name = relation_tables[relation_widget_name][1]  # primary key name
            sub_id_name = relation_tables[relation_widget_name][2]  # foreign key name

            selected_sub_ids = []
            for row in selected_rows:
                # to get the right ID of the foreign key, the corresponding ID has to be read from the table widget
                try:
                    sub_table_id = int(self.main_app.get_item_of_table_widget(relation_widget_name, row, 0))
                except ValueError:
                    self.main_app.send_critical_message('Fehler beim Schreiben der Beziehungsdaten!')
                    return

                relation_data = {main_id_name: entry_id,
                                 sub_id_name: sub_table_id}
                self._save_entry(rel_table_name, relation_data)

            unselected_rows = self.main_app.get_unselected_rows_of_widget(relation_widget_name)
            for row in unselected_rows:
                try:
                    sub_table_id = int(self.main_app.get_item_of_table_widget(relation_widget_name, row, 0))
                except ValueError:
                    self.main_app.send_critical_message('Fehler beim Schreiben der Beziehungsdaten!')
                    return

                relation_data = {main_id_name: entry_id,
                                 sub_id_name: sub_table_id}
                self._delete_entry(rel_table_name, relation_data)

        self.main_app.switch_main_widget()

    def _get_tree_structure(self, table=None):
        """

        :param table:
        :return:
        """

        # get all table contents and display connections in tree structure for TreeView
        # TODO: build tree structure for pyqt tree view
        pass

    def _delete_entry(self, table_name, data_entry) -> int:
        """Delete an entry from the table.
        If the table is a relation table, the entry will be built differently.

        :param table_name: name of the table
        :param data_entry: list (or dict) of values for the table
        :return: ID of entry that was deleted
        """

        try:
            if self.data_con.is_relation_table(table_name):
                # build entry for relation table differently as it's a combination of IDs
                entry = self.data_con.build_entry_for_relation_table(table_name, data_entry)
                # delete the entry from the table
                return self.data_con.delete_entry_from_table(table_name, entry)
            else:
                # build the entry for the table
                entry = self.data_con.build_entry_for_table(table_name, data_entry)
                # delete the entry from the table, including relation table entries
                return self.data_con.delete_entry_from_table(table_name, entry)
        except error.DataMismatchError:
            self.main_app.send_critical_message('Fehler beim Aufbau des Tabelleneintrags! DataMismatchError')
        except error.NoDataFoundError:
            self.main_app.send_critical_message('Fehler beim Modifizieren eines Tabelleneintrags! NoDataFoundError')
        except error.ForbiddenActionError:
            self.main_app.send_critical_message('Fehler beim Speichern des Tabelleneintrags! ForbiddenActionError')

    def _save_entry(self, table_name, data_entry) -> int:
        """Save an entry to the table.
        If an ID is given, the existing entry in the table is modified.
        If the ID is empty, a new entry is created in the table.

        :param table_name: name of the table
        :param data_entry: list of values for the table
        :return: ID of entry that was saved
        """

        try:
            if self.data_con.is_relation_table(table_name):
                # build entry for relation table differently as it's a combination of IDs
                entry = self.data_con.build_entry_for_relation_table(table_name, data_entry)
                try:
                    # add the entry to the table - this inhibits a check whether the entry is already existing
                    self.data_con.add_entry_to_table(table_name, entry)
                except error.KeyAlreadyExistError:
                    # return negative int to show no entry was added
                    return -1
            else:
                entry = self.data_con.build_entry_for_table(table_name, data_entry)
                if data_entry[0] == '':
                    return self.data_con.add_entry_to_table(table_name, entry)
                else:
                    return self.data_con.modify_entry_in_table(table_name, entry)
        except error.DataMismatchError:
            self.main_app.send_critical_message('Fehler beim Aufbau des Tabelleneintrags! DataMismatchError')
        except error.NoDataFoundError:
            self.main_app.send_critical_message('Fehler beim Modifizieren eines Tabelleneintrags! NoDataFoundError')
        except error.ForbiddenActionError:
            self.main_app.send_critical_message('Fehler beim Speichern des Tabelleneintrags! ForbiddenActionError')

    def start_application(self):
        """Start the main application

        :return: None
        """

        self.main_app.start_application()
