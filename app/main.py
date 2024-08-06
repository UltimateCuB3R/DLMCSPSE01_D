# Jan Sauerland

import data

DATABASE = 'data/main.db'
DB_DEF = 'data/db_def.xml'

if __name__ == '__main__':
    print('Jan Sauerland')
    data_con = data.DatabaseConnector(DATABASE, DB_DEF)
