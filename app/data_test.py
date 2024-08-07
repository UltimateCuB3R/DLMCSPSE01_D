import data
import pandas as pd

if __name__ == '__main__':
    print('Test run of data module')

    database = 'data/test.db'
    db_def = 'data/db_def.xml'

    data_con = data.DatabaseConnector(database, db_def)

    test_exercise = pd.Series(index=data.get_table_definition(data.NAME_EXERCISE),
                              data=['', 'Test Übung', 'Dies ist ein Test', '3 min', 2, ''])
    test_exercise2 = pd.Series(index=data.get_table_definition(data.NAME_EXERCISE),
                               data=['', 'Test Übung 2', 'Dies ist ein Test 2', '5 min', 1,
                                     'https://www.youtube.com/watch?v=dQw4w9WgXcQ'])

    print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise2)
    print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.delete_entry_from_table(data.NAME_EXERCISE, test_exercise)
    print(data_con.get_table_content(data.NAME_EXERCISE))
    data_con.commit_changes(data.NAME_EXERCISE)
    data_con.add_entry_to_table(data.NAME_EXERCISE, test_exercise)
    print(data_con.get_table_content(data.NAME_EXERCISE))

    test_exercise['NAME'] = 'Banane'
    data_con.modify_entry_in_table(data.NAME_EXERCISE, test_exercise)
    print(data_con.get_table_content(data.NAME_EXERCISE))
#    data_con.commit_changes(data.NAME_EXERCISE)

    data_con.rollback_changes(data.NAME_EXERCISE)
    print(data_con.get_table_content(data.NAME_EXERCISE))

    df = data_con.lookup_entry_in_table_by_relation(data.NAME_EXERCISE, data.NAME_CATEGORY, [1])
    print(df)
