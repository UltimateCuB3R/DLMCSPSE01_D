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


class _DataTableDefinition:
    """Class to hold definitions of Datatables, so every table can hold its own definition
    """
    _table_name: str
    _columns = []
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
        self._columns = definition[0]
        self._column_types = definition[1]
        self._column_relations = definition[2]
        self._table_relations = definition[3]
        self._table_keys = definition[4]

    def get_name(self):
        """Get the name of the table

        :return: name of the table
        """
        return self._table_name

    def get_columns(self):
        """Get all the columns of the table, including column ID

        :return: all columns of the table
        """
        return self._columns

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

    def has_table_keys(self):
        """Check if table has table keys defined

        :return: True if table keys are existent, False if not.
        """
        return len(self._table_keys) > 0


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
        """

        self._name = name
        self._definition = _DataTableDefinition(name, definition)

        try:
            # try to read table from database
            self.read_table_sql(sql_con)
        except (ValueError, pd.errors.DatabaseError):
            # table does not exist
            self._data = pd.DataFrame(columns=self._definition.get_columns())
            if self._definition.has_table_keys():
                self._data.set_index(keys=self._definition.get_table_keys(), inplace=True, verify_integrity=True)
            self._create_table_sql(sql_con)

    def read_table_sql(self, sql_con) -> pd.DataFrame:
        """Read table from database
        Raises ValueError when table does not exist

        :param sql_con: sqlite connection to database
        :return: table from database
        """

        self._data = pd.read_sql(f'select * from {self._name}', sql_con)
        if self._definition.has_table_keys():
            self._data.set_index(keys='ID', inplace=True, verify_integrity=True)
        return self._data

    def _create_table_sql(self, sql_con):
        """Create table on database with current contents of _data
        Raises ValueError if table already exists

        :param sql_con: sqlite connection to database
        :return: None
        """

        if self._definition.has_table_keys():
            self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=True,
                              index_label=self._definition.get_table_keys(),
                              dtype=self._definition.get_column_types())
        else:
            self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=False,
                              dtype=self._definition.get_column_types())

    def modify_table_sql(self, sql_con, sort=True):
        """Write current contents of _data to database

        :param sort: sort the table by index before writing to SQL
        :param sql_con: sqlite connection to database
        :return: None
        """

        if sort:
            self._data.sort_index(axis=0, ascending=True, kind='quicksort', inplace=True)

        if self._definition.has_table_keys():
            self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=True,
                              index_label=self._definition.get_table_keys(),
                              dtype=self._definition.get_column_types())
        else:
            self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=False,
                              dtype=self._definition.get_column_types())

    def delete_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Delete specific entry of table

        :param entry: Series element to be deleted from the Dataframe
        :return: complete Dataframe after modification
        """

        if not self.__check_columns(entry):
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        elif self._definition.has_table_keys():
            self._data.drop(self._data[self._data.index == entry['ID']].index, axis='rows', inplace=True)
        else:
            self._data.drop(self._data[self._data == entry].dropna(how='all').index, axis='rows', inplace=True)
        return self._data

    def add_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Add single entry to the table

        :param entry: Series element to be added to the Dataframe
        :return: complete Dataframe after modification
        """

        if not self.__check_columns(entry):
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        else:
            if self._definition.has_table_keys():
                # ID will be determined dynamically
                if len(self._data.index) == 0:
                    entry['ID'] = 0
                else:
                    entry['ID'] = self._data.index.max() + 1
                self._data.loc[entry['ID']] = entry
            else:
                # if table has no ID, just add the entry to the end of the Dataframe
                self._data.loc[len(self._data.index)] = entry
        return self._data

    def modify_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Modify a single entry of the table

        :param entry: Series element to be modified
        :return: complete Dataframe after modification
        """

        if not self.__check_columns(entry):
            raise error.DataMismatchError(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        elif self._definition.has_table_keys():
            raise error.ForbiddenActionError(f'Modify is not allowed on this type of table!')
        else:
            try:
                for col in self._data.columns:
                    self._data.at[entry['ID'], col] = entry[col]
            except KeyError:
                raise error.NoDataFoundError(f'KeyError in modify_entry for {entry}')

        return self._data

    def lookup_table_by_column(self, name, values) -> pd.DataFrame:
        """Lookup all entries in a table where the column values match the given values

        :param name: column name of table
        :param values: list of values to search for
        :return: resulting data as Dataframe
        """

        if name not in self._definition.get_columns():
            raise error.ColumnNotKnownError(f'column {name} is not known for table {self._name}!')
        else:
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

        # reset_index() is necessary as the ID field is present in row,
        # but normally not in the dataframe because it is defined as the index.
        if not len(row.index.difference(self._data.reset_index().columns)) == 0:
            return False
        else:
            return True


class DatabaseConnector:
    """Base class to handle the database connection
    """

    _sql_con: sqlite3.Connection
    _data_tables: dict[str, _DataTable]
    _instance = None
    _table_columns = {}

    def __init__(self, database: str, db_def: str):
        """Create a sqlite3 connection to a SQL database.
        If the database is not existing, it will be automatically generated as an empty database.
        Definition file as XML will be read and used to create the DataTable objects.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        self._sql_con = sqlite3.connect(database)
        def_tables = _read_db_definition(db_def)
        self._data_tables = {}

        for name in def_tables.keys():
            self.__add_datatable(name, def_tables[name])

    def __new__(cls, database: str, db_def: str):
        """Override method to create Singleton pattern.
        Only one instance of DatabaseConnector shall be created as only one database connection is needed.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        if not cls._instance:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance

    def __add_datatable(self, name, definition):
        """Create a new DataTable and link it in the dict
        Additionally save columns of table in another dict to access from outside

        :param name: table name
        :param definition: table definitions from XML file
        :return: None
        """

        self._data_tables[name] = _DataTable(self._sql_con, name, definition)
        self._table_columns[name] = definition[0]

    def _delete_relation_tables(self, name, entry: pd.Series):
        """Delete all entries that relate to the given entry and are safe to delete

        :param name: Name of table
        :param entry: Series element to be deleted, contains key for relation lookup
        :return:
        """

        for table, key in self._data_tables[name].get_definition().get_table_relations().items():
            relation_table = self.lookup_table_by_relation([entry['ID']], name, table)
            for index, row in relation_table.iterrows():
                self._data_tables[table].delete_entry(row)

    def get_table_content(self, name) -> pd.DataFrame:
        """Get Dataframe of a table

        :param name: Name of table
        :return: Dataframe of specified table
        """

        return self._data_tables[name].get_table().copy()

    def get_table_columns(self, name):
        """Get column names of a table

        :param name: Name of table
        :return: List of column names
        """

        return self._table_columns[name]

    def add_entry_to_table(self, name, entry: pd.Series):
        """Add single entry to specific table

        :param name: Name of table
        :param entry: Series element to be added
        :return: None
        """

        self._data_tables[name].add_entry(entry)

    def delete_entry_from_table(self, name, entry: pd.Series):
        """Delete single entry from specific table

        :param name: Name of table
        :param entry: Series element to be deleted
        :return: None
        """

        # first delete possible entries in relation tables
        self._delete_relation_tables(name, entry)

        # then delete the entry in the table itself
        self._data_tables[name].delete_entry(entry)

    def modify_entry_in_table(self, name, entry: pd.Series):
        """Modify single entry in specific table

        :param name: Name of table
        :param entry: Series element to be modified
        :return: None
        """

        self._data_tables[name].modify_entry(entry)

    def lookup_entry_in_table(self, name, column, values) -> pd.DataFrame:
        """Search for entries in a table regarding relations

        :param name:
        :param column:
        :param values:
        :return: Dataframe
        """

        return self._data_tables[name].lookup_table_by_column(column, values)

    def lookup_table_by_relation(self, values, source_table, search_table) -> pd.DataFrame:
        """

        :param values:
        :param source_table:
        :param search_table:
        :return:
        """

        tables = [(key, value) for key, value in
                  self._data_tables[source_table].get_definition().get_table_relations().items() if key == search_table]

        if len(tables) > 0:
            for table, key_id in tables:
                return self._data_tables[table].lookup_table_by_column(key_id, values)
        else:
            raise error.TableNotKnownError(f'table {source_table} is not connected to table {search_table}')

    def commit_changes(self, name=None):
        """Commit changes made to Dataframes

        :param name: Name of table
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
        """Rollback changes made to Dataframes

        :param name: Name of table
        :return: None
        """
        if name is None:
            # rollback all changes to what is saved on the database
            for key in self._data_tables.keys():
                self._data_tables[key].read_table_sql(self._sql_con)
        else:
            # only rollback the changes to a specific table
            self._data_tables[name].read_table_sql(self._sql_con)


def _read_db_definition(db_def):
    """Read database definition out of xml file.

    :param db_def: path to database definition file
    :return: None
    """

    tree = ElTr.parse(db_def)
    root = tree.getroot()
    def_tables = {}

    for item in root.findall('TABLE'):
        name = item.attrib['NAME']
        columns = []
        column_types = {}
        column_relations = {}
        table_relations = {}
        table_keys = []
        for child in item:
            if child.tag == 'COLUMN':
                columns.append(child.text)
                if child.attrib['TYPE'] == 'ID':
                    # column ID should not be added to Dataframe definition, as it is defined automatically
                    table_keys.append(child.text)
                    continue
                else:
                    column_types[child.text] = child.attrib['TYPE']
                try:
                    column_relations[child.text] = child.attrib['RELATION']
                except KeyError:
                    column_relations[child.text] = ''
            elif child.tag == 'RELATION':
                table_relations[child.text] = child.attrib['KEY']
            else:
                raise error.DataMismatchError(f'Error in _read_db_definition: {child.tag} is unknown!')

        def_tables[name] = (columns, column_types, column_relations, table_relations, table_keys)
    return def_tables
