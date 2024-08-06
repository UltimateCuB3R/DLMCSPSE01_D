import pandas as pd
import sqlite3
import xml.etree.ElementTree as ElTr

NAME_UNIT = 'UNIT'
NAME_EXERCISE = 'EXERCISE'
NAME_PLAN = 'PLAN'
NAME_CALENDAR = 'PLAN_CALENDAR'
NAME_CATEGORY = 'CATEGORY'
NAME_RESOURCE = 'RESOURCE'

def_tables = {}


class _DataTable:
    """Base class for definition of general database actions
    """

    _name: str
    _data: pd.DataFrame

    def __init__(self, sql_con, name):
        """Constructor for table object

        :param sql_con: sqlite connection to database
        :param name: name of table
        """

        self._name = name
        try:
            # try to read table from database
            self.read_table_sql(sql_con)
        except (ValueError, pd.errors.DatabaseError):
            # table does not exist
            self._data = pd.DataFrame(columns=def_tables[name][0])
            self.create_table_sql(sql_con)

    def read_table_sql(self, sql_con) -> pd.DataFrame:
        """Read table from database
        Raises ValueError when table does not exist

        :param sql_con: sqlite connection to database
        :return: table from database
        """

        self._data = pd.read_sql(f'select * from {self._name}', sql_con)
        self._data.set_index('ID')
        return self._data

    def create_table_sql(self, sql_con):
        """Create table on database with current contents of _data
        Raises ValueError if table already exists

        :param sql_con: sqlite connection to database
        :return: None
        """

        self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=False, dtype=def_tables[self._name][1])

    def modify_table_sql(self, sql_con):
        """Write current contents of _data to database

        :param sql_con: sqlite connection to database
        :return: None
        """

        self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=False, dtype=def_tables[self._name][1])

    def delete_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Delete specific entry of table

        :param entry: Series element to be deleted from the Dataframe
        :return:
        """

        if not self.__check_columns(entry):
            # TODO raise Error
            print(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        else:
            self._data.drop(self._data[self._data['ID'] == entry['ID']].index, axis='rows', inplace=True)
        return self._data

    def add_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Add single entry to the table

        :param entry: Series element to be added to the Dataframe
        :return:
        """

        if not self.__check_columns(entry):
            # TODO raise Error
            print(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        else:
            # ID wird dynamisch festgelegt
            if len(self._data.index) == 0:
                entry['ID'] = 0
            else:
                entry['ID'] = self._data['ID'].idxmax() + 1
            self._data.loc[entry['ID']] = entry
        return self._data

    def modify_entry(self, entry: pd.Series) -> pd.DataFrame:
        """Modify a single entry of the table

        :param entry:
        :return:
        """

        if not self.__check_columns(entry):
            # TODO raise Error
            print(f'Error in check_columns: {entry.index} does not match {self._data.columns}')
        else:
            try:
                self._data.loc[entry['ID']] = entry
            except KeyError:
                # TODO handle Error
                print(f'KeyError in modify_entry for {entry}')

        return self._data

    def get_table(self) -> pd.DataFrame:
        """Get dataframe of table

        :return:
        """

        return self._data

    def __check_columns(self, row: pd.Series):
        """Check if the columns of a row have the same definition as the Dataframe

        :param row: Series to check the columns
        :return: True if column definitions match, False if not
        """

        if not len(row.index.difference(self._data.columns)) == 0:
            return False
        else:
            return True


class _DataTableExercise(_DataTable):
    """Class for data table EXERCISE
    """


class _DataTableUnit(_DataTable):
    """Class for data table UNIT
    """


class _DataTablePlan(_DataTable):
    """Class for data table PLAN
    """


class _DataTableCalendar(_DataTable):
    """Class for data table PLAN_CALENDAR
    """


class _DataTableCategory(_DataTable):
    """Class for data table CATEGORY
    """


class _DataTableResource(_DataTable):
    """Class for data table RESOURCE
    """


class DatabaseConnector:
    """Base class to handle the database connection
    """

    _sql_con: sqlite3.Connection
    _data_tables: dict[str, _DataTable]
    _instance = None

    def __init__(self, database: str, db_def: str):
        """Create a sqlite3 connection to a SQL database.
        If the database is not existing, it will be automatically generated as an empty database.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        print(f'init - db:{database} - def:{db_def}')
        self._sql_con = sqlite3.connect(database)
        _read_db_definition(db_def)
        self._data_tables = {NAME_EXERCISE: _DataTableExercise(self._sql_con, NAME_EXERCISE),
                             NAME_UNIT: _DataTableUnit(self._sql_con, NAME_UNIT),
                             NAME_PLAN: _DataTablePlan(self._sql_con, NAME_PLAN),
                             NAME_CALENDAR: _DataTableCalendar(self._sql_con, NAME_CALENDAR),
                             NAME_CATEGORY: _DataTableCategory(self._sql_con, NAME_CATEGORY),
                             NAME_RESOURCE: _DataTableResource(self._sql_con, NAME_RESOURCE)}

    def __new__(cls, database: str, db_def: str):
        """Override method to create Singleton pattern.
        Only one instance of DatabaseConnector shall be created as only one database connection is needed.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        if not cls._instance:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance

    def get_table_content(self, name) -> pd.DataFrame:
        """Get Dataframe of a table

        :param name: Name of table
        :return: Dataframe of specified table
        """

        return self._data_tables[name].get_table().copy()

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

        self._data_tables[name].delete_entry(entry)

    def modify_entry_in_table(self, name, entry: pd.Series):
        """Modify single entry in specific table

        :param name: Name of table
        :param entry: Series element to be modified
        :return: None
        """

        self._data_tables[name].modify_entry(entry)

    def commit_changes(self, name=None):
        """Commit changes made to Dataframes

        :param name:
        :return:
        """
        if name is None:
            # commit all changes
            for key in self._data_tables.keys():
                self._data_tables[key].modify_table_sql(self._sql_con)
        else:
            # only commit changes to a specific table
            self._data_tables[name].modify_table_sql(self._sql_con)


def get_table_definition(name):
    """Get table definitions that were read from xml file

    :param name: Name of table
    :return: definitions of tables / SQL database
    """

    return def_tables[name][0]


def _read_db_definition(db_def):
    """Read database definition out of xml file.

    :param db_def: path to database definition file
    :return: None
    """

    global def_tables

    tree = ElTr.parse(db_def)
    root = tree.getroot()
    def_tables = {}

    for item in root.findall('TABLE'):
        name = item.attrib['NAME']
        columns = []
        column_types = {}
        for child in item:
            columns.append(child.text)
            column_types[child.text] = child.attrib['TYPE']
        def_tables[name] = (columns, column_types)
