import data
import error
import pandas as pd
import unittest
from datetime import datetime

DATABASE = 'data/test.db'
DB_DEF = 'data/db_def.xml'


class MyTestCase(unittest.TestCase):
    def test_add_entry_to_main_table(self):
        entry = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                          data=['', 'Test Übung', 'Dies ist ein Test', '00:00:00', 'http://www.google.de'])
        data_before = data_con.get_table_content(data.NAME_EXERCISE)
        added_id = data_con.add_entry_to_table(data.NAME_EXERCISE, entry)
        data_after = data_con.get_table_content(data.NAME_EXERCISE)

        # assert that one entry was added
        self.assertEqual(len(data_before.index) + 1, len(data_after.index))
        # assert that the added ID is in the table
        self.assertEqual(data_after['ID'].isin([added_id]).any(), True)

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.add_entry_to_table(data.NAME_EXERCISE, entry_mismatch)

        data_con.rollback_changes()

    def test_delete_entry_from_main_table(self):
        entry = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                          data=[0, 'Test', 'Test', '00:00:00', 'http://www.google.de'])
        data_before = data_con.get_table_content(data.NAME_EXERCISE)
        deleted_id = data_con.delete_entry_from_table(data.NAME_EXERCISE, entry)
        data_after = data_con.get_table_content(data.NAME_EXERCISE)

        # assert that one entry was deleted
        self.assertEqual(len(data_before.index) - 1, len(data_after.index))
        # assert that the deleted ID is no longer in the table
        self.assertEqual(data_after['ID'].isin([deleted_id]).any(), False)

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.delete_entry_from_table(data.NAME_EXERCISE, entry_mismatch)

        # check if NoDataFoundError is raised if a not existing entry is tried to be deleted
        entry_not_found = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                                    data=[-1, 'ERROR', 'ERROR', '00:00:00', 'http...'])
        with self.assertRaises(error.NoDataFoundError):
            data_con.delete_entry_from_table(data.NAME_EXERCISE, entry_not_found)

        data_con.rollback_changes()

    def test_modify_entry_in_main_table(self):
        entry = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                          data=[0, f'Test Modify {datetime.now()}', 'Test Modify', '00:00:00', 'http://www.google.de'])
        data_before = data_con.get_table_content(data.NAME_EXERCISE)
        modified_id = data_con.modify_entry_in_table(data.NAME_EXERCISE, entry)
        data_after = data_con.get_table_content(data.NAME_EXERCISE)

        # assert that no entry was deleted or added
        self.assertEqual(len(data_before.index), len(data_after.index))
        # assert that the modified ID is in the table
        self.assertEqual(data_after['ID'].isin([modified_id]).any(), True)
        # assert that the changed column is in the table
        self.assertEqual(data_after['NAME'].isin([entry['NAME']]).any(), True)

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.modify_entry_in_table(data.NAME_EXERCISE, entry_mismatch)

        # check if NoDataFoundError is raised if a not existing entry is tried to be modified
        entry_not_found = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                                    data=[-1, 'ERROR', 'ERROR', '00:00:00', 'http...'])
        with (self.assertRaises(error.NoDataFoundError)):
            data_con.modify_entry_in_table(data.NAME_EXERCISE, entry_not_found)

        data_con.rollback_changes()

    def test_add_entry_to_relation_table(self):
        entry_new = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                              data=[0, 1])  # new ID combination
        data_before = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)
        added_id = data_con.add_entry_to_table(data.NAME_EXERCISE_CATEGORY, entry_new)
        data_after = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)

        # assert that one entry was added
        self.assertEqual(len(data_before.index) + 1, len(data_after.index))
        # assert that the added row index is in the table
        self.assertEqual(data_after.index.isin([added_id]).any(), True)

        entry_existing = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                                   data=[0, 0])  # existing ID combination

        data_before = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)
        with self.assertRaises(error.KeyAlreadyExistError):
            data_con.add_entry_to_table(data.NAME_EXERCISE_CATEGORY, entry_existing)
        data_after = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)

        # assert that no entry was added
        self.assertEqual(len(data_before.index), len(data_after.index))

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.add_entry_to_table(data.NAME_EXERCISE_CATEGORY, entry_mismatch)

        data_con.rollback_changes()

    def test_modify_entry_in_relation_table(self):
        entry_existing = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                                   data=[0, 0])  # existing ID combination

        data_before = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)
        with self.assertRaises(error.ForbiddenActionError):
            data_con.modify_entry_in_table(data.NAME_EXERCISE_CATEGORY, entry_existing)
        data_after = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)

        # assert that no entry was added
        self.assertEqual(len(data_before.index), len(data_after.index))

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.modify_entry_in_table(data.NAME_EXERCISE_CATEGORY, entry_mismatch)

        data_con.rollback_changes()

    def test_delete_entry_from_relation_table(self):
        entry_existing = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                                   data=[0, 0])  # existing ID combination

        data_before = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)
        deleted_id = data_con.delete_entry_from_table(data.NAME_EXERCISE_CATEGORY, entry_existing)
        data_after = data_con.get_table_content(data.NAME_EXERCISE_CATEGORY)

        # assert that one entry was deleted
        self.assertEqual(len(data_before.index) - 1, len(data_after.index))
        # assert that the deleted ID combination is no longer in the table
        self.assertEqual(len(data_after.loc[(data_after['EXERCISE_ID'] == 0) & (data_after['CATEGORY_ID'] == 0)].index),
                         0)

        # check if DataMismatchError is raised if the entry does not match the needed data format
        entry_mismatch = pd.Series(index=['ID', 'NAME'], data=[100, 'ERROR'])
        with self.assertRaises(error.DataMismatchError):
            data_con.delete_entry_from_table(data.NAME_EXERCISE_CATEGORY, entry_mismatch)

        # check if NoDataFoundError is raised if a not existing entry is tried to be modified
        entry_not_found = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                                    data=[-1, -1])
        with (self.assertRaises(error.NoDataFoundError)):
            data_con.delete_entry_from_table(data.NAME_EXERCISE_CATEGORY, entry_not_found)

        data_con.rollback_changes()

    def test_commit_changes(self):
        # TODO: test commit
        pass

    def test_rollback_changes(self):
        # TODO: test rollback
        pass

    def test_lookup_entry_in_table(self):
        # TODO: test lookup entry
        pass

    def test_lookup_table_by_relation(self):
        # TODO: test lookup relation
        pass

    def test_singleton_database_connector(self):
        data_con1 = data.DatabaseConnector(DATABASE, DB_DEF)
        data_con2 = data.DatabaseConnector(DATABASE, DB_DEF)

        # check if no additional instance of the database connector was created
        self.assertEqual(data_con1, data_con2)


if __name__ == '__main__':
    data_con = data.DatabaseConnector(DATABASE, DB_DEF)
    unittest.main()
