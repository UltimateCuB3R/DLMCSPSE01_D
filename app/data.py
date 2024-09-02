import pandas as pd
import sqlite3
import xml.etree.ElementTree as ElTr
import error

NAME_UNIT = 'UNIT'
NAME_EXERCISE = 'EXERCISE'
NAME_PLAN = 'PLAN'
NAME_CALENDAR = 'PLAN_CALENDAR'
NAME_CATEGORY = 'CATEGORY'
NAME_RESOURCE = 'RESOURCE'
NAME_UNIT_PLAN = 'UNIT_PLAN'
NAME_UNIT_CATEGORY = 'UNIT_CATEGORY'
NAME_EXERCISE_UNIT = 'EXERCISE_UNIT'
NAME_EXERCISE_RESOURCE = 'EXERCISE_RESOURCE'
NAME_EXERCISE_CATEGORY = 'EXERCISE_CATEGORY'
NAME_TYPE_MAIN = 'MAIN'
NAME_TYPE_RELATION = 'RELATION'
NAME_TYPE_SUB = 'SUB'


class _DataTableDefinition:
    """Class to hold definitions of Datatables, so every table can hold its own definition
    """

    _table_name: str
    _table_type: str
    _top_table: str
    _column_names = []
    _column_types = {}
    _column_relations = {}
    _table_relations = {}
    _table_keys = []

    def __init__(self, name, definition):
        """Construct a definition object out of the definitions read from XML

        :param name: name of the Datatable
        :param definition: definition as list of dictionaries/lists
        """

        self._table_name = name
        self._column_names = definition[0]
        self._column_types = definition[1]
        self._column_relations = definition[2]
        self._table_relations = definition[3]
        self._table_keys = definition[4]
        self._table_type = definition[5]
        self._top_table = definition[6]

    def get_name(self):
        """Get the name of the table

        :return: name of the table
        """

        return self._table_name

    def get_column_names(self):
        """Get all the columns of the table, including column ID

        :return: all columns of the table
        """

        return self._column_names

    def get_column_types(self):
        """Get all type definitions of the columns, excluding column ID

        :return: all type definitions w/o ID
        """

        return self._column_types

    def get_column_relations(self):
        """Get all relation definitions of the columns

        :return: all relation definitions of the columns
        """

        return self._column_relations

    def get_table_relations(self):
        """Get all the relations to other tables

        :return: relations to other tables
        """

        return self._table_relations

    def get_table_keys(self):
        """Get all key fields of the table

        :return: all key fields
        """

        return self._table_keys

    def get_table_type(self):
        """Get the type of the table, either MAIN or RELATION

        :return: type of table
        """

        return self._table_type

    def get_top_table(self):
        """Get the top table of the table.

        :return: name of the top table
        """

        return self._top_table

    def has_table_keys(self) -> bool:
        """Check if table has table keys defined

        :return: True if table keys are existent, False if not.
        """

        return len(self._table_keys) > 0

    def is_relation_table(self) -> bool:
        """Check if table is a relation table

        :return: True if table is relation table
        """

        return self.get_table_type() == NAME_TYPE_RELATION

    def is_main_table(self) -> bool:
        """Check if table is a main table

        :return: True if table is main table
        """

        return self.get_table_type() == NAME_TYPE_MAIN

    def is_sub_table(self) -> bool:
        """Check if table is a subordinate table

        :return: True if table is subordinate table
        """

        return self.get_table_type() == NAME_TYPE_SUB


class _DataTable:
    """Base class for definition of general database actions
    """

    _name: str
    _data: pd.DataFrame
    _definition: _DataTableDefinition

    def __init__(self, sql_con, name, definition):
        """Constructor for table object

        :param sql_con: sqlite connection to database
        :param name: name of table
        :param definition: definition of this table
        """

        self._name = name
        self._definition = _DataTableDefinition(name, definition)

        try:
            # try to read table from database
            self.read_table_sql(sql_con)
        except (ValueError, pd.errors.DatabaseError):
            # table does not exist
            self._data = pd.DataFrame(columns=self._definition.get_column_names())

            if self._definition.has_table_keys():
                # table has column ID, so index of the dataframe needs to be set
                self._data.set_index(keys=self._definition.get_table_keys(), inplace=True, verify_integrity=True)

            self._create_table_sql(sql_con)  # create the table in the database

    def read_table_sql(self, sql_con):
        """Read table from database
        Raises ValueError when table does not exist

        :param sql_con: sqlite connection to database
        :return: None
        """

        self._data = pd.read_sql(f'select * from {self._name}', sql_con)
        if self._definition.has_table_keys():
            # table has column 'ID', so ID is the index
            self._data.set_index(keys=self._definition.get_table_keys(), inplace=True, verify_integrity=True)

    def _create_table_sql(self, sql_con):
        """Create table on database with current contents of _data
        Raises ValueError if table already exists

        :param sql_con: sqlite connection to database
        :return: None
        """

        if self._definition.has_table_keys():
            # table has column 'ID', so ID is the index
            self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=True,
                              index_label=self._definition.get_table_keys(),
                              dtype=self._definition.get_column_types())
        else:
            # no column ID, so no special index
            self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=False,
                              dtype=self._definition.get_column_types())

    def modify_table_sql(self, sql_con, sort=True):
        """Write current contents of _data to database

        :param sort: sort the table by index before writing to SQL
        :param sql_con: sqlite connection to database
        :return: None
        """

        if sort:
            # sort the dataframe if necessary
            self._data.sort_index(axis=0, ascending=True, kind='quicksort', inplace=True)

        if self._definition.has_table_keys():
            # table has column 'ID', so ID is the index
            self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=True,
                              index_label=self._definition.get_table_keys(),
                              dtype=self._definition.get_column_types())
        else:
            # no column ID, so no special index
            self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=False,
                              dtype=self._definition.get_column_types())

    def delete_entry(self, entry: pd.Series) -> int:
        """Delete specific entry of table

        :param entry: Series element to be deleted from the Dataframe
        :return: complete Dataframe after modification
        """

        if not self.__check_columns(entry):  # check if the columns of the entry match the data table
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        elif self._definition.is_main_table():
            # table is main table, so it has a column ID
            if entry['ID'] in self._data.index:  # check if ID is in table
                self._data.drop(self._data[self._data.index == entry['ID']].index, axis='rows', inplace=True)
            else:
                # no entry with this ID was found
                raise error.NoDataFoundError(f'Error! Entry {entry} was not found in table!')
            return_id = entry['ID']
        else:
            # table is relation table, so it has no column ID
            selected_rows = self._data[self._data == entry].dropna(how='any').index
            if len(selected_rows) > 0:  # check if values are in table
                self._data.drop(selected_rows, axis='rows', inplace=True)
                return_id = -1
            else:
                # no entry with these values was found
                raise error.NoDataFoundError(f'Error! Entry {entry} was not found in table!')
        return return_id

    def add_entry(self, entry: pd.Series) -> int:
        """Add single entry to the table

        :param entry: Series element to be added to the Dataframe
        :return: ID of added entry
        """

        if not self.__check_columns(entry):  # check if the columns of the entry match the data table
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        else:
            if self._definition.has_table_keys():
                # ID will be determined dynamically
                if len(self._data.index) == 0:  # check if dataframe is empty
                    entry['ID'] = return_id = 0  # first ID is set to zero
                else:
                    entry['ID'] = return_id = self._data.index.max() + 1  # all subsequent IDs are +1 of the max index
                self._data.loc[entry['ID']] = entry
            else:
                # check if keys already exist in the Dataframe
                if len(self._data[self._data == entry].dropna(how='any').index) > 0:
                    raise error.KeyAlreadyExistError(f'Key {list(entry)} already exists in Dataframe!')
                else:
                    # if table has no ID, just add the entry to the end of the Dataframe
                    return_id = len(self._data.index)
                    self._data.loc[return_id] = entry
        return return_id

    def modify_entry(self, entry: pd.Series) -> int:
        """Modify a single entry of the table

        :param entry: Series element to be modified
        :return: ID of modified entry
        """

        if not self.__check_columns(entry):  # check if the columns of the entry match the data table
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        elif self._definition.has_table_keys():
            # table is main table, so column ID exists
            if entry['ID'] in self._data.index:  # check if ID is in table
                for col in self._data.columns:
                    self._data.at[entry['ID'], col] = entry[col]
            else:
                # no entry with this ID was found
                raise error.NoDataFoundError(f'Error! Entry {entry} was not found in table!')
        else:
            # relation table entries cannot be modified, only deleted and added
            raise error.ForbiddenActionError(f'Modify is not allowed on this type of table!')

        return entry['ID']

    def lookup_table_by_column(self, name, values) -> pd.DataFrame:
        """Lookup all entries in a table where the column values match the given values

        :param name: column name of table
        :param values: list of values to search for
        :return: resulting data as Dataframe
        """

        if name not in self._definition.get_column_names():
            # column is not existent in definition
            raise error.ColumnNotKnownError(f'column {name} is not known for table {self._name}!')
        else:
            if self.get_definition().has_table_keys():
                # main or sub tables have the column ID as index
                result_data = self._data.reset_index().loc[self._data.reset_index()[name].isin(values)]
            else:
                # relation tables do not have the column ID
                result_data = self._data.loc[self._data[name].isin(values)]
            return result_data

    def get_table(self) -> pd.DataFrame:
        """Get dataframe of table

        :return: Dataframe
        """

        return self._data

    def get_definition(self) -> _DataTableDefinition:
        """Get the definition of this DataTable

        :return: definition of this DataTable
        """

        return self._definition

    def __check_columns(self, row: pd.Series):
        """Check if the columns of a row have the same definition as the Dataframe

        :param row: Series to check the columns
        :return: True if column definitions match, False if not
        """

        if self._definition.has_table_keys():
            # if the table has table keys, reset_index() is necessary as the ID field is present in row,
            # but normally not in the dataframe because it is defined as the index.
            if not len(self._data.reset_index().columns.difference(row.index)) == 0:
                return False
            else:
                return True
        else:
            # if the table has no table keys, just compare the indices of the columns.
            if not len(self._data.columns.difference(row.index)) == 0:
                return False
            else:
                return True


class DatabaseConnector:
    """Base class to handle the database connection
    """

    _sql_con: sqlite3.Connection
    _data_tables: dict[str, _DataTable]
    _instance = None

    def __init__(self, database: str, db_def: str):
        """Create a sqlite3 connection to a SQL database.
        If the database is not existing, it will be automatically generated as an empty database.
        Definition file as XML will be read and used to create the DataTable objects.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        self._sql_con = sqlite3.connect(database)  # connect to given database
        def_tables = _read_db_definition(db_def)  # read the db definition out of the xml file
        self._data_tables = {}  # create the dictionary for the data tables

        for name in def_tables.keys():  # iterate through all tables that are defined in the xml file
            self.__add_datatable(name, def_tables[name])

    def __new__(cls, database: str, db_def: str):
        """Override method to create Singleton pattern.
        Only one instance of DatabaseConnector shall be created as only one database connection is needed.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        if not cls._instance:  # no instance exists yet -> create new instance
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance  # stored instance

    def __add_datatable(self, name, definition):
        """Create a new DataTable and link it in the dict
        Additionally save columns of table in another dict to access from outside

        :param name: table name
        :param definition: table definitions from XML file
        :return: None
        """

        # create a new DataTable instance with the given definition
        self._data_tables[name] = _DataTable(self._sql_con, name, definition)

    def _delete_relation_tables(self, name, entry: pd.Series):
        """Delete all entries that relate to the given entry and are safe to delete

        :param name: Name of table
        :param entry: Series element to be deleted, contains key for relation lookup
        :return:
        """

        # iterate through all relation tables where the given ID is mentioned and delete it
        for table, key in self._data_tables[name].get_definition().get_table_relations().items():
            relation_table = self.lookup_table_by_relation([entry['ID']], name, table)
            for index, row in relation_table.iterrows():
                self._data_tables[table].delete_entry(row)

    def get_table_content(self, name) -> pd.DataFrame:
        """Get Dataframe of a table

        :param name: Name of table
        :return: Dataframe of specified table
        """

        if self._data_tables[name].get_definition().has_table_keys():
            # reset index only if it's a main table
            return self._data_tables[name].get_table().copy().reset_index()
        else:
            # do not reset the index for relation tables
            return self._data_tables[name].get_table().copy()

    def get_table_relations(self, name) -> dict:
        """Get the relations to other tables

        :param name: Name of table
        :return: relations to other tables
        """
        return self._data_tables[name].get_definition().get_table_relations()

    def get_column_relations(self, name) -> dict:
        """Get the column relations of a table

        :param name: Name of the table
        :return: relations to other tables via columns
        """

        return self._data_tables[name].get_definition().get_column_relations()

    def get_table_columns(self, name):
        """Get column names of a table

        :param name: Name of table
        :return: List of column names
        """

        return self._data_tables[name].get_definition().get_column_names()

    def add_entry_to_table(self, name, entry: pd.Series) -> int:
        """Add single entry to specific table

        :param name: Name of table
        :param entry: Series element to be added
        :return: ID of added entry
        """

        return self._data_tables[name].add_entry(entry)

    def delete_entry_from_table(self, name, entry: pd.Series) -> int:
        """Delete single entry from specific table

        :param name: Name of table
        :param entry: Series element to be deleted
        :return: None
        """

        # first delete possible entries in relation tables
        self._delete_relation_tables(name, entry)

        # then delete the entry in the table itself
        return self._data_tables[name].delete_entry(entry)

    def modify_entry_in_table(self, name, entry: pd.Series) -> int:
        """Modify single entry in specific table

        :param name: Name of table
        :param entry: Series element to be modified
        :return: ID of modified entry
        """

        return self._data_tables[name].modify_entry(entry)

    def lookup_entry_in_table(self, name, column, values) -> pd.DataFrame:
        """Search for entries in a table by a specific column.

        :param name: name of the table
        :param column: name of the column to be searched
        :param values: list of values to be matched in the column
        :return: Dataframe of corresponding entries
        """

        return self._data_tables[name].lookup_table_by_column(column, values)

    def lookup_table_by_relation(self, values, source_table, search_table) -> pd.DataFrame:
        """Search for relation table corresponding to given ID values

        :param values: list of IDs to be searched for
        :param source_table: name of the source (main) table
        :param search_table: name of the table (relation) to be searched
        :return: Dataframe of the corresponding entries in the search table
        """

        # retrieve the table relations of the given source table where the search table is mentioned
        tables = [(key, value) for key, value in
                  self._data_tables[source_table].get_definition().get_table_relations().items() if key == search_table]

        if len(tables) == 1:  # search table is a relation table of the source table
            for table, key_id in tables:
                return self._data_tables[table].lookup_table_by_column(key_id, values)
        elif len(tables) > 1:  # more than one entry has been found - this should not occur
            raise error.DataMismatchError(f'Multiple table entries have been found!')
        else:  # search table has no relation to the source table
            raise error.TableNotKnownError(f'Table {source_table} is not connected to table {search_table}')

    def commit_changes(self, name=None):
        """Commit changes made to Dataframes.
        If no name is given, the changes to all tables are committed.

        :param name: name of table
        :return: None
        """

        if name is None:
            # commit all changes
            for key in self._data_tables.keys():
                self._data_tables[key].modify_table_sql(self._sql_con)
        else:
            # only commit the changes to a specific table
            self._data_tables[name].modify_table_sql(self._sql_con)

    def rollback_changes(self, name=None):
        """Rollback changes made to Dataframes.
        If no name is given, the changes to all tables are reverted.

        :param name: name of table
        :return: None
        """

        if name is None:
            # rollback all changes to what is saved on the database
            for key in self._data_tables.keys():
                self._data_tables[key].read_table_sql(self._sql_con)
        else:
            # only rollback the changes to a specific table
            self._data_tables[name].read_table_sql(self._sql_con)

    def build_entry_for_table(self, table_name, table_data) -> pd.Series:
        """Build the entry for the datatable from the stored definition as a Series object

        :param table_name: name of table
        :param table_data: data of table to be built into a Series object
        :return: Series element that matches the columns of the table
        """

        if len(self.get_table_columns(table_name)) == len(table_data):
            return pd.Series(index=self.get_table_columns(table_name), data=table_data)
        else:
            # given table data does not match the amount of columns of the table
            raise error.DataMismatchError(f'Length of given data does not match number of columns for this table!')

    def build_entry_for_relation_table(self, table_name, table_data: dict) -> pd.Series:
        """Build the relation table entry for the datatable from the stored definition as a Series object.
        The table data is a dictionary as the column order is unknown when calling.

        :param table_name: name of table
        :param table_data: data of table as dict to be built into a Series object
        :return: Series element that matches the columns of the table
        """

        if len(self.get_table_columns(table_name)) == len(table_data):
            entry = []
            # match the right data to the column
            for column in self.get_table_columns(table_name):
                try:
                    entry.append(table_data[column])
                except KeyError:
                    # column is missing in the dictionary
                    raise error.DataMismatchError(f'Column {column} missing in table data!')
            return pd.Series(index=self.get_table_columns(table_name), data=entry)
        else:
            # given table data does not match the amount of columns of the table
            raise error.DataMismatchError(f'Length of given data does not match number of columns for this table!')

    def is_relation_table(self, table_name) -> bool:
        """Check if a table is a relation table

        :param table_name: name of table
        :return: True if table is relation table
        """

        return self._data_tables[table_name].get_definition().is_relation_table()

    def is_main_table(self, table_name) -> bool:
        """Check if a table is a main table

        :param table_name: name of table
        :return: True if table is main table
        """

        return self._data_tables[table_name].get_definition().is_main_table()

    def is_sub_table(self, table_name) -> bool:
        """Check if a table is a subordinate table

        :param table_name: name of table
        :return: True if table is subordinate table
        """

        return self._data_tables[table_name].get_definition().is_sub_table()

    def is_top_table(self, relation_table, top_table) -> bool:
        """Check if a table is the top table of a given relation table

        :param relation_table: name of the relation table
        :param top_table: name of the top table to check for
        :return: True if table is the top table of the relation table
        """

        return self._data_tables[relation_table].get_definition().get_top_table() == top_table

    def get_top_table_key(self, table_name) -> str:
        """Retrieve the key of the top table

        :param table_name: name of table
        :return: column name of the top table key if existent, empty string if not
        """

        top_table = self._data_tables[table_name].get_definition().get_top_table()
        if top_table == '':  # given table has no top table

            return ''
        else:  # given table has a top table
            column_relations = self._data_tables[table_name].get_definition().get_column_relations()
            # check for the right key name in the column relations
            for column, relation_table in column_relations.items():
                if top_table == relation_table:
                    return column
        return ''


def _read_db_definition(db_def):
    """Read database definition out of xml file.

    :param db_def: path to database definition file
    :return: None
    """

    # parse given file into ElementTree
    tree = ElTr.parse(db_def)
    root = tree.getroot()
    def_tables = {}  # create empty dictionary for return

    for item in root.findall('TABLE'):
        name = item.attrib['NAME']  # name of the table
        table_type = item.attrib['TYPE']  # type of the table (MAIN/SUB/RELATION)
        try:
            top = item.attrib['TOP']  # name of the top table of a relation table
        except KeyError:  # if the table isn't a relation table, no top table is defined
            top = ''

        # create the lists and dictionaries for the different definitions
        column_names = []  # names of the columns
        column_types = {}  # data types of the columns
        column_relations = {}  # relations to other tables via columns
        table_relations = {}  # relations to other tables via relation tables
        table_keys = []  # columns that are defined as keys

        for child in item:
            if child.tag == 'COLUMN':
                # get the column name
                column_names.append(child.text)

                # check the column type
                if child.attrib['TYPE'] == 'ID':
                    # column ID should not be added to Dataframe definition, as it is defined automatically.
                    # but it needs to be added to the table keys
                    table_keys.append(child.text)
                    continue  # ID has no other settings, so go to next child
                else:
                    column_types[child.text] = child.attrib['TYPE']

                # read the column relation attribute
                try:
                    column_relations[child.text] = child.attrib['RELATION']
                except KeyError:
                    column_relations[child.text] = ''

            elif child.tag == 'RELATION':
                # read the item for table relations
                table_relations[child.text] = child.attrib['KEY']
            else:
                # new child tag that is not yet defined
                raise error.DataMismatchError(f'Error in _read_db_definition: {child.tag} is unknown!')

        # save the data in the dictionary to the corresponding table name
        def_tables[name] = (column_names, column_types, column_relations, table_relations, table_keys, table_type, top)

    return def_tables
