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

        # TODO: assert error.DataMismatchError

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

        # TODO: assert error.DataMismatchError
        # TODO: assert error.NoDataFoundError

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

        # TODO: assert error.DataMismatchError
        # TODO: assert error.NoDataFoundError

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

        # TODO: assert error.DataMismatchError

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

        # TODO: assert error.DataMismatchError

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

        # TODO: assert error.DataMismatchError
        # TODO: assert error.NoDataFoundError

        data_con.rollback_changes()

    def test_commit_changes(self):
        pass

    def test_rollback_changes(self):
        pass

    def test_lookup_entry_in_table(self):
        pass

    def test_lookup_table_by_relation(self):
        pass

    def test_singleton_database_connector(self):
        data_con1 = data.DatabaseConnector(DATABASE, DB_DEF)
        data_con2 = data.DatabaseConnector(DATABASE, DB_DEF)

        self.assertEqual(data_con1, data_con2)


if __name__ == '__main__':
    data_con = data.DatabaseConnector(DATABASE, DB_DEF)
    unittest.main()

"""elif __name__ != '__main__':
    print('Test run of data module')

    database = 'data/test.db'
    db_def = 'data/db_def.xml'

    data_con = data.DatabaseConnector(database, db_def)

    test_exercise = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                              data=['', 'Test Übung', 'Dies ist ein Test', 30.0, ''])
    test_exercise2 = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                               data=['', 'Test Übung 2', 'Dies ist ein Test 2', 600.0,
                                     'https://www.youtube.com/watch?v=dQw4w9WgXcQ'])

    # print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise2)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.delete_entry_from_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.commit_changes(data.NAME_EXERCISE)
    # data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    print(data_con.get_table_content(data.NAME_EXERCISE))

    # test_exercise['NAME'] = 'Banane'
    # data_con.modify_entry_in_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.commit_changes(data.NAME_EXERCISE)

    # data_con.rollback_changes(data.NAME_EXERCISE)

    test_category = pd.Series(index=data_con.get_table_columns(data.NAME_CATEGORY),
                              data=['', 'FUN', 'Spiel und Spaß', 'GREEN'])
    data_con.add_entry_to_table(data.NAME_CATEGORY, test_category)
    print(data_con.get_table_content(data.NAME_CATEGORY))
    test_exercise_category = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_CATEGORY),
                                       data=[test_exercise['ID'], test_category['ID']])
    data_con.add_entry_to_table(data.NAME_EXERCISE_CATEGORY, test_exercise_category)
    print(data_con.get_table_content(data.NAME_EXERCISE_CATEGORY))

    # print(data_con.lookup_entry_in_table(data.NAME_EXERCISE, (data.NAME_CATEGORY + '_ID'), [1]))

    test_unit = pd.Series(index=data_con.get_table_columns(data.NAME_UNIT),
                          data=['', 'Test Einheit 2', 'Weiterer Text', 60.0])
    data_con.add_entry_to_table(data.NAME_UNIT, test_unit)
    test_exercise_unit = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_UNIT),
                                   data=[test_exercise2['ID'], test_unit['ID']])
    data_con.add_entry_to_table(data.NAME_EXERCISE_UNIT, test_exercise_unit)
    data_con.commit_changes()
    print(data_con.get_table_content(data.NAME_EXERCISE))
    print(data_con.get_table_content(data.NAME_UNIT))
    print(data_con.get_table_content(data.NAME_EXERCISE_UNIT))

    # print(data_con.lookup_entry_in_table(data.NAME_UNIT, (data.NAME_CATEGORY + '_ID'), [2]))
    for index, row in data_con.lookup_entry_in_table(data.NAME_CATEGORY, 'NAME', ['FUN']).iterrows():
        data_con.add_entry_to_table(data.NAME_UNIT_CATEGORY,
                                    pd.Series(index=data_con.get_table_columns(data.NAME_UNIT_CATEGORY),
                                              data=[test_unit['ID'], index]))
    data_con.commit_changes(data.NAME_UNIT_CATEGORY)
    print(data_con.get_table_content(data.NAME_UNIT_CATEGORY))

    print(data_con.get_table_content(data.NAME_CATEGORY))
    data_con.delete_entry_from_table(data.NAME_CATEGORY, test_category)
    print(data_con.get_table_content(data.NAME_CATEGORY))
    print(data_con.get_table_content(data.NAME_UNIT_CATEGORY))
    data_con.commit_changes()
    # print(data_con.get_table_content(data.NAME_EXERCISE_UNIT))

    print(data_con.get_table_relations(data.NAME_UNIT))"""
