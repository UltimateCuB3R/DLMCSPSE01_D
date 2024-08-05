# Jan Sauerland

import data

DATABASE = 'app/data/main.db'
DB_DEF = 'app/data/db_def.xml'

if __name__ == '__main__':
    print('Jan Sauerland')
    data_con = data.DatabaseConnector(DATABASE, DB_DEF)
