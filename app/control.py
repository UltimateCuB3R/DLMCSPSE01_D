import data
import view
import error
import os
from jinja2 import Environment, FileSystemLoader

NAME_SEARCH = 'search'
NAME_PRINT = 'print'


class MainControl:
    """Main controller class to handle the user interactions and data modifications.
    """

    data_con: data.DatabaseConnector
    main_app: view.MainApplication
    main_tables: []

    def __init__(self, database, db_def, gui_def, path):
        """Initialize the main control by giving the paths of the database and the definition file.
        The main application is created and loaded with all necessary widgets.

        :param database: path to the database file
        :param db_def: path to the database definition file
        :param gui_def: path to the GUI definition file
        :param path: current path of the application
        """

        self.app_path = path
        db_path = str(os.path.join(path, database))
        db_def_path = str(os.path.join(path, db_def))
        gui_def_path = str(os.path.join(path, gui_def))

        self.data_con = data.DatabaseConnector(db_path, db_def_path)
        self.main_tables = [data.NAME_PLAN, data.NAME_UNIT, data.NAME_EXERCISE, data.NAME_CATEGORY,
                            data.NAME_RESOURCE]  # data.NAME_CALENDAR is not yet implemented
        self.main_app = view.MainApplication(self.main_tables + [NAME_SEARCH, NAME_PRINT], gui_def_path, path)
        self.main_app.init_main_widget(self.main_tables, self._get_data_of_tables(self.main_tables))
        self.main_app.set_main_tree_widget(self._get_tree_structure())
        self._init_connectors()

    def _init_connectors(self):
        """Initialize all button connections to the corresponding action methods when they are clicked.

        :return: None
        """

        # create, search, commit and revert are only accessible from the main widget
        self.main_app.connect_create(self._button_create)
        self.main_app.connect_search(self._button_search)
        self.main_app.connect_commit(self._button_commit)
        self.main_app.connect_revert(self._button_revert)
        self.main_app.connect_table_click(self._table_clicked)

        # save and delete are only accessible from the detail widgets
        self.main_app.connect_save(self.main_tables, self._button_save)
        self.main_app.connect_delete(self.main_tables, self._button_delete)
        # cancel is accessible from all detail and additional widgets, but not the main widget
        self.main_app.connect_cancel(self.main_tables + [NAME_SEARCH, NAME_PRINT], self._button_cancel)
        # display, edit and export are only accessible from the search widget
        self.main_app.connect_display([NAME_SEARCH], self._button_display)
        self.main_app.connect_edit([NAME_SEARCH], self._button_edit)
        self.main_app.connect_export([NAME_SEARCH], self._button_export)
        # print is only accessible from the export/print widget
        self.main_app.connect_print([NAME_PRINT], self._button_print)

    def _switch_main_widget(self, name=None):
        """Switch the main widget to a table specific one or back to the initial main widget.
        If it is switched back to the initial main widget, the main tree widget is calculated again.

        :param name: name of the table/widget to be loaded - will switch back to main if None is given
        :return: None
        """
        if name is None:
            # switch back to the main widget
            self.main_app.switch_main_widget()
            # calculate the new tree structure and set the main tree widget
            self.main_app.set_main_tree_widget(self._get_tree_structure())
            self.main_app.init_main_widget(self.main_tables, self._get_data_of_tables(self.main_tables))
        else:
            # switch to the given widget
            self.main_app.switch_main_widget(name)

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
                    selected_rows = sub_table_data[
                        sub_table_data['ID'].isin(selected_sub_table_data['ID'])].index.to_list()
                    # set the selection in the table widget
                    self.main_app.set_relation_table_selection(sub_table, selected_rows)
                else:
                    # clear the selection in the table widget
                    self.main_app.set_relation_table_selection(sub_table, [])

            else:
                # table name contains two underscores, logic cannot apply
                self.main_app.send_critical_message(
                    f'Fehler! Datenbankschema oder Programmierung falsch für {table}!')

    def __show_widget(self, table_name, table_rows, edit_mode=True):
        """Show the chosen widget and fill the widget fields with data.
        Set edit_mode to define if data should be editable or not.

        :param edit_mode: True if data should be editable and save button enabled.
        :return: None
        """

        # check if only one row was selected
        if len(table_rows) == 0:
            # too few lines selected
            self.main_app.send_critical_message('Fehler! Keine Zeile ausgewählt! Bitte genau eine Zeile auswählen!')
        elif len(table_rows) > 1:
            # too many lines selected
            self.main_app.send_critical_message('Fehler! Zu viele Zeilen ausgewählt! Bitte genau eine Zeile auswählen!')
        else:
            self._switch_main_widget(table_name)  # switch to chosen table widget
            # get row data corresponding to chosen row
            table_data = self.data_con.get_table_content(table_name)
            row = table_data.iloc[table_rows[0]]
            # fill the widget with data and enable the save and delete buttons
            self.main_app.set_fields_of_current_widget(table_name, row, edit_mode)
            self.main_app.enable_save_button(edit_mode)
            self.main_app.enable_delete_button(True)
            # fill the relation tables with data
            self._fill_relation_tables(table_name, row['ID'], edit_mode)

    def _table_clicked(self, widget_name):
        """This action is called when a main table is double-clicked.
        The item according to the clicked table is loaded in display mode.

        :return: None
        """

        if self.main_app.get_main_display() or NAME_SEARCH in widget_name:  # check if main display is active
            if NAME_SEARCH in widget_name:  # search table was clicked
                table_name = self.main_app.get_displayed_table()
            else:  # main table was clicked
                # table name is found in the widget name
                table_name = widget_name.split('_')[1].upper()

            table_rows = self.main_app.get_selected_rows_of_widget(widget_name)  # get selection
            self.__show_widget(table_name, table_rows, False)  # show the widget in display mode
        else:
            # function cannot be called here
            self.main_app.send_critical_message('Fehler! Funktion kann hier nicht ausgeführt werden!')

    def _button_create(self, button_name):
        """This action is called when the create button is pressed.
        The widget according to the chosen table is loaded in creation mode.
        Any existing relation tables to the chosen table are loaded into the widget.

        :return: None
        """

        if self.main_app.get_main_display():  # check if main display is active
            # table = self.main_app.get_main_left().comboBox_tables.currentText()  # get chosen table
            table = button_name.split('_')[1].upper()
            self._switch_main_widget(table)  # switch to chosen table widget
            self.main_app.enable_save_button(True)  # enable the save button
            self.main_app.enable_delete_button(False)  # disable the delete button
            self.main_app.set_fields_of_current_widget(table, editable=True)  # set fields editable
            self._fill_relation_tables(table)  # fill the relation table widgets in the current widget
        else:
            # if main display is not active, creation process cannot be started
            self.main_app.send_critical_message('Fehler! Funktion kann hier nicht ausgeführt werden!')

    def _button_display(self):
        """This action calls the detail widget of the chosen table with the selected entry.
        The widget is set to display mode, so no changes can be done.

        :return: None
        """

        table_name = self.main_app.get_displayed_table()  # get current table
        table_rows = list(self.main_app.get_selected_rows_of_current_widget().values())[0]  # get selection

        self.__show_widget(table_name, table_rows, False)  # show the widget in display mode

    def _button_edit(self):
        """This action calls the detail widget of the chosen table with the selected entry.
        The widget is set to edit mode, so changes can be done and saved.

        :return: None
        """

        table_name = self.main_app.get_displayed_table()  # get current table
        table_rows = list(self.main_app.get_selected_rows_of_current_widget().values())[0]  # get selection

        self.__show_widget(table_name, table_rows, True)  # show the widget in edit mode

    def _button_export(self, table_name):
        """This action calls the print widget of the chosen table with the selected entry.

        :param table_name: name of the chosen table
        :return: None
        """
        if self.main_app.get_main_display():
            # main screen is displayed, so get table rows from corresponding table
            table_rows = self.main_app.get_selected_rows_of_widget('tableMain_' + table_name)  # get selection
            table_name = table_name.upper()
        else:
            # search screen is displayed, so get table rows from current widget
            table_rows = list(self.main_app.get_selected_rows_of_current_widget().values())[0]  # get selection
            table_name = self.main_app.get_displayed_table()

        # check if only one row was selected
        if len(table_rows) == 0:
            # too few lines selected
            self.main_app.send_critical_message('Fehler! Keine Zeile ausgewählt! Bitte genau eine Zeile auswählen!')
        elif len(table_rows) > 1:
            # too many lines selected
            self.main_app.send_critical_message('Fehler! Zu viele Zeilen ausgewählt! Bitte genau eine Zeile auswählen!')
        else:
            self._switch_main_widget(NAME_PRINT)  # switch to export widget
            self.main_app.set_label_table_name(table_name)  # set the table name
            # get row data corresponding to chosen row
            table_data = self.data_con.get_table_content(table_name)
            row = table_data.iloc[table_rows[0]]
            # build the tree structure and set the tree widget with the selected data
            self.main_app.set_current_tree_widget(self._get_tree_structure(main_id=row['ID'], table=table_name),
                                                  self.data_con.get_table_columns(table_name), True)

            #  build the html view or show the tree widget again
            if table_name == data.NAME_PLAN:
                # retrieve the top-down data to create the html view
                top_down_data = self.data_con.get_data_top_down(table_name, [row['ID']])
                # create the html code from the data and set it in the application
                self.main_app.set_html_view(self._create_html_from_template(table_name, top_down_data))
            else:
                self.main_app.clear_html_view()
                self.main_app.get_current_tree_widget().show()  # tree widget was hidden if html view was active before

    def _create_html_from_template(self, table_name, table_data):
        """Create html code from a jinja template.
        The given data is parsed and then used in the template.

        :param table_name: name of the table
        :param table_data: all data to be displayed
        :return: html code as string
        """

        # create a jinja environment to load the template file
        env = Environment(loader=FileSystemLoader(str(os.path.join(self.app_path, 'templates'))))
        template_file = table_name + '.jinja'
        # load the template file
        template = env.get_template(template_file.lower())

        # parse the table_data into the needed split_data for the jinja template
        split_data = self._split_data_for_html(table_data)
        # table_data is now split into:
        # plan_id, plan_name, plan_description, unit_data
        # unit[ID, NAME, DESCRIPTION, DURATION, EXERCISE, CATEGORY]
        # exercise[ID, NAME, DESCRIPTION, DURATION, URL, CATEGORY, RESOURCE]

        # render the html template with the given data
        html = template.render(plan_name=split_data[1], plan_description=split_data[2], unit_data=split_data[3])

        return html

    @staticmethod
    def _split_data_for_html(table_data):
        """Parse the given data that comes from _get_data_top_down into the needed format for html rendering.
        Each table has to have its own implementation.

        :param table_data: top-down data of the table
        :return: list of values
        """
        return_data = []

        for main_id, main_content in table_data.items():
            table_name = main_content[0]  # object (table) name
            if table_name == data.NAME_PLAN:  # only parse the data for PLAN
                item_data = main_content[1]  # data contents of this item (columns)
                return_data.append(item_data['ID'])  # plan_id - 0
                return_data.append(item_data['NAME'])  # plan_name - 1
                return_data.append(item_data['DESCRIPTION'].split('\n'))  # plan_description - 2
                main_children = main_content[2]  # children of this item
                unit_list = []

                for c1 in main_children:  # iterate through all children (UNIT)
                    for c1_id, c1_content in c1.items():
                        c1_name = c1_content[0]
                        c1_data = c1_content[1]
                        c1_children = c1_content[2]
                        if c1_name == data.NAME_UNIT:
                            unit_data = {}
                            unit_data['ID'] = c1_data['ID']
                            unit_data['NAME'] = c1_data['NAME']
                            unit_data['DESCRIPTION'] = c1_data['DESCRIPTION'].split('\n')
                            unit_data['DURATION'] = c1_data['DURATION']
                            unit_data['EXERCISE'] = []
                            unit_data['CATEGORY'] = []

                            for c2 in c1_children:  # iterate through all children (EXERCISE, CATEGORY)
                                for c2_id, c2_content in c2.items():
                                    c2_name = c2_content[0]
                                    c2_data = c2_content[1]
                                    c2_children = c2_content[2]
                                    if c2_name == data.NAME_EXERCISE:
                                        exercise_data = {}
                                        exercise_data['ID'] = c2_data['ID']
                                        exercise_data['NAME'] = c2_data['NAME']
                                        exercise_data['DESCRIPTION'] = c2_data['DESCRIPTION'].split('\n')
                                        exercise_data['DURATION'] = c2_data['DURATION']
                                        exercise_data['VIDEO_URL'] = c2_data['VIDEO_URL']
                                        exercise_data['CATEGORY'] = []
                                        exercise_data['RESOURCE'] = []

                                        for c3 in c2_children:  # iterate through all children (CATEGORY, RESOURCE)
                                            for c3_id, c3_content in c3.items():
                                                c3_name = c3_content[0]
                                                c3_data = c3_content[1]
                                                if c3_name == data.NAME_CATEGORY:
                                                    exercise_data['CATEGORY'].append(c3_data['NAME'])
                                                elif c3_name == data.NAME_RESOURCE:
                                                    exercise_data['RESOURCE'].append(c3_data['NAME'])
                                        unit_data['EXERCISE'].append(exercise_data)
                                    elif c2_name == data.NAME_CATEGORY:
                                        unit_data['CATEGORY'].append(c2_data['NAME'])

                            unit_list.append(unit_data)
                return_data.append(unit_list)  # unit_data - 3

        return return_data

    def _button_print(self):
        """This action prints the currently displayed widget.
        Regarding the displayed table, the widget is either printed as pdf (from html) or as jpg (from screenshot).

        :return: None
        """

        if self.main_app.get_displayed_table() == data.NAME_PLAN:
            self.main_app.print_widget_pdf()  # call the print dialog to pdf via html
        else:
            self.main_app.print_widget_jpg()  # call the print dialog to jpg
        self._switch_main_widget()  # switch back to the main widget

    def _button_search(self, button_name):
        """This action is called when the search button is pressed.
        The central search widget is loaded with the corresponding table data of the chosen table.
        Additionally, the tree structure for the chosen table is also loaded.

        :return: None
        """

        if self.main_app.get_main_display():
            # search can only be accessed via the main widget
            # table_name = self.main_app.get_main_left().comboBox_tables.currentText()  # get chosen table name
            table_name = button_name.split('_')[1].upper()
            self._switch_main_widget(NAME_SEARCH)  # switch to search widget
            # set up the search table with the right data
            self.main_app.set_search_table(table_name, self.data_con.get_table_content(table_name))
            # set up the tree widget in the search table with the tree structure
            self.main_app.set_current_tree_widget(self._get_tree_structure(table=table_name),
                                                  self.data_con.get_table_columns(table_name), False)
        else:
            # fallback if action was improperly connected
            self.main_app.send_critical_message('Diese Funktion kann hier nicht ausgeführt werden!')

    def _button_commit(self):
        """This action commits all table changes to the database.

        :return: None
        """

        self.data_con.commit_changes()  # commit all changes to the database

    def _button_revert(self):
        """This action reverts all changes made to the tables and loads them back from the database.

        :return: None
        """

        self.data_con.rollback_changes()  # revert all changes, read data again from database
        self.main_app.set_main_tree_widget(self._get_tree_structure())  # reset the main tree widget
        self.main_app.init_main_widget(self.main_tables, self._get_data_of_tables(self.main_tables))  # reset all tables

    def _button_cancel(self):
        """This action cancels the current widget.
        All fields are cleared and the main widget is switched back.

        :return: None
        """

        if self.main_app.get_current_widget_name() not in [NAME_SEARCH, NAME_PRINT]:
            # clear all fields of the current widget if it's not the search or print widget
            table_name = self.main_app.get_displayed_table()  # name of the currently displayed table
            fields = self.main_app.get_gui_definition()[table_name][1]  # fields of the GUI definition of this table
            for field in fields.keys():  # iterate through all fields
                self.main_app.set_field_in_current_widget(fields[field], '')  # set empty data

        self._switch_main_widget()  # switch back to the main widget

    def _button_save(self):
        """This action saves the currently displayed entry.
        All GUI fields are read according to the GUI definition.
        The selected rows of the related tables are also saved to the relation tables.
        The unselected rows are deleted in the relation tables, if existing.

        :return: None
        """

        # retrieve the table name from GUI and the GUI definition from the main app
        table_name = self.main_app.get_displayed_table()
        fields = self.main_app.get_gui_definition()[table_name][1]
        table_data = []  # setup empty list to fill

        # iterate through all fields and retrieve the values
        for field_name in fields.keys():
            if field_name == 'ID':
                # ID needs to be converted into int
                try:
                    value = int(self.main_app.get_field_of_current_widget(fields[field_name]))
                except ValueError:
                    # ID could not be converted
                    if self.main_app.get_field_of_current_widget(fields[field_name]) == '':
                        # if the ID is an empty string, it is OK to set in the table data
                        value = self.main_app.get_field_of_current_widget(fields[field_name])
                    else:
                        # if the ID has any other value that can't be converted, the process needs to be stopped.
                        self.main_app.send_critical_message('Fehler! ID konnte nicht verarbeitet werden!')
                        return
            else:
                # if it's not an ID, just get the field value from the GUI
                value = self.main_app.get_field_of_current_widget(fields[field_name])

            table_data.append(value)  # add the value to the list

        entry_id = self._save_entry(table_name, table_data)  # save the resulting entry to the data table

        # also build and save relation table data
        relation_tables = self.main_app.get_gui_definition()[table_name][2]  # retrieve the GUI definition for relations

        for relation_widget_name in relation_tables.keys():  # iterate through all relation widgets
            # get selected rows of widget with name relation_widget_name
            selected_rows = self.main_app.get_selected_rows_of_current_widget()[relation_widget_name]
            # build relation table entries
            rel_table_name = relation_tables[relation_widget_name][0]  # name of relation table
            main_id_name = relation_tables[relation_widget_name][1]  # primary key name
            sub_id_name = relation_tables[relation_widget_name][2]  # foreign key name

            for row in selected_rows:
                # to get the right ID of the foreign key, the corresponding ID has to be read from the table widget
                # ID needs to be converted into int
                try:
                    sub_table_id = int(self.main_app.get_item_of_table_widget(relation_widget_name, row, 0))
                except ValueError:
                    # ID could not be converted
                    self.main_app.send_critical_message('Fehler beim Schreiben der Beziehungsdaten!')
                    return

                # build the entry for the relation data as a dict with the key names
                # because the right column order is not known at this point
                relation_data = {main_id_name: entry_id,
                                 sub_id_name: sub_table_id}
                self._save_entry(rel_table_name, relation_data)  # save the resulting entry to the data table

            # get unselected rows of widget with name relation_widget_name
            unselected_rows = self.main_app.get_unselected_rows_of_widget(relation_widget_name)
            for row in unselected_rows:
                # to get the right ID of the foreign key, the corresponding ID has to be read from the table widget
                # ID needs to be converted into int
                try:
                    sub_table_id = int(self.main_app.get_item_of_table_widget(relation_widget_name, row, 0))
                except ValueError:
                    # ID could not be converted
                    self.main_app.send_critical_message('Fehler beim Schreiben der Beziehungsdaten!')
                    return

                # build the entry for the relation data as a dict with the key names
                # because the right column order is not known at this point
                relation_data = {main_id_name: entry_id,
                                 sub_id_name: sub_table_id}
                self._delete_entry(rel_table_name, relation_data)  # delete the entry from the data table

        # reset all fields to the initial values
        for field_name in fields.keys():
            self.main_app.set_field_in_current_widget(fields[field_name], '')  # set empty data

        self._switch_main_widget()  # switch back to the main widget after saving is completed

    def _button_delete(self):
        """This action deletes the currently displayed entry.

        :return: None
        """

        # retrieve the table name from GUI and the GUI definition from the main app
        table_name = self.main_app.get_displayed_table()
        fields = self.main_app.get_gui_definition()[table_name][1]
        table_data = []  # setup empty list to fill

        # iterate through all fields and retrieve the values
        for field_name in fields.keys():
            if field_name == 'ID':
                # ID needs to be converted into int
                try:
                    value = int(self.main_app.get_field_of_current_widget(fields[field_name]))
                except ValueError:
                    # ID could not be converted
                    if self.main_app.get_field_of_current_widget(fields[field_name]) == '':
                        # if the ID is an empty string, it is OK to set in the table data
                        value = self.main_app.get_field_of_current_widget(fields[field_name])
                    else:
                        # if the ID has any other value that can't be converted, the process needs to be stopped.
                        self.main_app.send_critical_message('Fehler! ID konnte nicht verarbeitet werden!')
                        return
            else:
                # if it's not an ID, just get the field value from the GUI
                value = self.main_app.get_field_of_current_widget(fields[field_name])

            table_data.append(value)  # add the value to the list

        if self.main_app.ask_user_confirmation('Löschen', 'Möchten Sie den gewählten Eintrag wirklich löschen?'):
            entry_id = self._delete_entry(table_name, table_data)  # delete the entry from the data table

            # reset all fields to the initial values
            for field_name in fields.keys():
                self.main_app.set_field_in_current_widget(fields[field_name], '')  # set empty data

            self._switch_main_widget()  # switch back to the main widget after saving is completed

            # send information about deleted entry to user
            self.main_app.send_information_message(f'ID {entry_id} aus Tabelle {table_name} erfolgreich gelöscht!')
        else:
            # do not delete the entry
            pass

    def _get_data_of_tables(self, table_names: list) -> dict:
        """Retrieve all the data of the given list of table names.
        All table data will be stored in a dictionary that is returned.

        :param table_names: list of table names
        :return: dictionary of table names and corresponding table data
        """

        return_data = {}

        for table in table_names:
            # retrieve table data and insert into dict
            table_data = self.data_con.get_table_content(table)
            return_data[table] = table_data

        return return_data

    def _get_tree_structure(self, main_id=None, table=None) -> list:
        """Retrieve the tree structure of the data of one or all tables and one or all IDs of a table.
        This calculated the top-down data of the table and

        :param main_id: optional ID of an entry to be retrieved as a tree structure
        :param table: optional name of the table
        :return: list of items that can be displayed in a tree widget
        """

        # get all table contents and display connections in tree structure for TreeView
        if table is None:
            # iterate through all tables and append list of items
            tree = []
            for table_name in self.main_tables:
                tree += self._get_tree_structure(table=table_name)
            return tree

        elif self.data_con.is_relation_table(table):
            # relation tables are not allowed to be listed in TreeView
            self.main_app.send_critical_message('Fehler! Tabelle für TreeView ist eine Beziehungstabelle!')
        else:
            # table name is given, so begin to retrieve the data
            if main_id is None:
                # no ID is given, so all entries of this table should be retrieved
                table_data = self.data_con.get_table_content(table)
                all_data = self.data_con.get_data_top_down(table, table_data['ID'].to_list())
            else:
                # ID is given, so only the related entries should be retrieved
                all_data = self.data_con.get_data_top_down(table, [main_id])

            main_items = []
            # build a main item for each retrieved main entry of this table
            for main_id, contents in all_data.items():
                main_items.append(self._build_tree_item(contents))

            return main_items

    def _build_tree_item(self, contents):
        """Build a tree item out of the given data contents.

        :param contents: list of data to be built as a tree item
        :return: corresponding tree item created from the data contents
        """

        name = contents[0]  # object (table) name
        item_data = contents[1]  # data contents of this item (columns)
        children = contents[2]  # children of this item

        child_items = []  # create list to fill later
        if children is not None:  # check if this item has children
            # children need to be created too, so iterate through them and recursively build the items
            for child in children:
                for child_id, child_content in child.items():
                    if len(child_items) == 0:
                        # first entry
                        child_items = [self._build_tree_item(child_content)]
                    else:
                        child_items.append(self._build_tree_item(child_content))

        # finally create the top item with all child items and return
        return self.main_app.create_tree_item(self.main_app.translate_text(name), item_data.to_list(), child_items)

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
                # build entry for non-relation table normally
                entry = self.data_con.build_entry_for_table(table_name, data_entry)
                # delete the entry from the table, including relation table entries
                return self.data_con.delete_entry_from_table(table_name, entry)
        except error.DataMismatchError:  # entry data does not match the data table
            self.main_app.send_critical_message('Fehler beim Aufbau des Tabelleneintrags! DataMismatchError')
        except error.NoDataFoundError:  # existing entry could not be found and deleted
            if self.data_con.is_relation_table(table_name):
                return -1
            else:
                self.main_app.send_critical_message('Fehler beim Löschen eines Tabelleneintrags! NoDataFoundError')

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
                # build entry for non-relation table normally
                entry = self.data_con.build_entry_for_table(table_name, data_entry)
                if data_entry[0] == '':
                    # new entry without ID needs to be added
                    return self.data_con.add_entry_to_table(table_name, entry)
                else:
                    # existing entry with ID needs to be modified
                    return self.data_con.modify_entry_in_table(table_name, entry)
        except error.DataMismatchError:  # entry data does not match the data table
            self.main_app.send_critical_message('Fehler beim Aufbau des Tabelleneintrags! DataMismatchError')
        except error.NoDataFoundError:  # existing entry could not be found and modified
            self.main_app.send_critical_message('Fehler beim Modifizieren eines Tabelleneintrags! NoDataFoundError')
        except error.ForbiddenActionError:  # a relation table was tried to be modified
            self.main_app.send_critical_message('Fehler beim Speichern des Tabelleneintrags! ForbiddenActionError')

    def start_application(self):
        """Start the main application.

        :return: None
        """

        self.main_app.start_application()
