import data
import pandas as pd

if __name__ == '__main__':
    print('Test run of data module')

    database = 'data/test.db'
    db_def = 'data/db_def.xml'

    data_con = data.DatabaseConnector(database, db_def)

    test_exercise = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                              data=['', 'Test Übung', 'Dies ist ein Test', 30.0, 2, ''])
    test_exercise2 = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE),
                               data=['', 'Test Übung 2', 'Dies ist ein Test 2', 600.0, 1,
                                     'https://www.youtube.com/watch?v=dQw4w9WgXcQ'])

    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise2)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.delete_entry_from_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.commit_changes(data.NAME_EXERCISE)
    # data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))

    # test_exercise['NAME'] = 'Banane'
    # data_con.modify_entry_in_table(data.NAME_EXERCISE, test_exercise)
    # print(data_con.get_table_content(data.NAME_EXERCISE))
    # data_con.commit_changes(data.NAME_EXERCISE)

    # data_con.rollback_changes(data.NAME_EXERCISE)

    print(data_con.lookup_entry_in_table(data.NAME_EXERCISE, (data.NAME_CATEGORY + '_ID'), [1]))

    test_unit = pd.Series(index=data_con.get_table_columns(data.NAME_UNIT),
                          data=['', 'Test Einheit 2', 'Weiterer Text', 60.0, 2])
    data_con.add_entry_to_table(data.NAME_UNIT, test_unit)
    test_exercise_unit = pd.Series(index=data_con.get_table_columns(data.NAME_EXERCISE_UNIT),
                                   data=[test_exercise2['ID'], test_unit['ID']])
    data_con.add_entry_to_table(data.NAME_EXERCISE_UNIT, test_exercise_unit)
    data_con.commit_changes()
    print(data_con.get_table_content(data.NAME_EXERCISE))
    print(data_con.get_table_content(data.NAME_UNIT))
    print(data_con.get_table_content(data.NAME_EXERCISE_UNIT))

    print(data_con.lookup_entry_in_table(data.NAME_UNIT, (data.NAME_CATEGORY + '_ID'), [2]))

    data_con.delete_entry_from_table(data.NAME_EXERCISE_UNIT, test_exercise_unit)
    data_con.commit_changes()
    print(data_con.get_table_content(data.NAME_EXERCISE_UNIT))
