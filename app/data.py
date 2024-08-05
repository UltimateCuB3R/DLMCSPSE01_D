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


class DataTable:
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
            self._read_table(sql_con)
        except ValueError:
            # table does not exist
            self._data = pd.DataFrame(columns=def_tables[name])
            self._create_table(sql_con)

    def _read_table(self, sql_con) -> pd.DataFrame:
        """Read table from database
        Raises ValueError when table does not exist

        :param sql_con: sqlite connection to database
        :return: table from database
        """

        self._data = pd.read_sql(f'select * from {self._name}', sql_con)
        return self._data

    def _create_table(self, sql_con):
        """Create table on database with current contents of _data
        Raises ValueError if table already exists

        :param sql_con: sqlite connection to database
        :return: None
        """

        self._data.to_sql(self._name, con=sql_con, if_exists='fail', index=True)

    def _modify_table(self, sql_con):
        """Write current contents of _data to database

        :param sql_con: sqlite connection to database
        :return: None
        """

        self._data.to_sql(self._name, con=sql_con, if_exists='replace', index=True)


class DataTableExercise(DataTable):
    """Class for data table EXERCISE
    """


class DataTableUnit(DataTable):
    """Class for data table UNIT
    """


class DataTablePlan(DataTable):
    """Class for data table PLAN
    """


class DataTableCalendar(DataTable):
    """Class for data table PLAN_CALENDAR
    """


class DataTableCategory(DataTable):
    """Class for data table CATEGORY
    """


class DataTableResource(DataTable):
    """Class for data table RESOURCE
    """


class DatabaseConnector:
    """Base class to handle the database connection
    """
    _sql_con: sqlite3.Connection
    # _db_def: str
    _data_tables: dict[str, DataTable]
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
        self._data_tables = {NAME_EXERCISE: DataTableExercise(self._sql_con, NAME_EXERCISE),
                             NAME_UNIT: DataTableUnit(self._sql_con, NAME_UNIT),
                             NAME_PLAN: DataTablePlan(self._sql_con, NAME_PLAN),
                             NAME_CALENDAR: DataTableCalendar(self._sql_con, NAME_CALENDAR),
                             NAME_CATEGORY: DataTableCategory(self._sql_con, NAME_CATEGORY),
                             NAME_RESOURCE: DataTableResource(self._sql_con, NAME_RESOURCE)}

    def __new__(cls, database: str, db_def: str):
        """Override method to create Singleton pattern.
        Only one instance of DatabaseConnector shall be created as only one database connection is needed.

        :param database: path to database file
        :param db_def: path to database definition file
        """

        if not cls._instance:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance


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
        for child in item:
            columns.append(child.text)
        def_tables[name] = columns
