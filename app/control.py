import data
import view


class MainControl:
    data_con: data.DatabaseConnector
    main_app: view.MainApplication

    def __init__(self, database, db_def):
        self.data_con = data.DatabaseConnector(database, db_def)
        self.main_app = view.MainApplication('view/main.ui', [data.NAME_EXERCISE, data.NAME_UNIT, data.NAME_PLAN])

        self.main_app.init_main_window()

    def get_tree_structure(self, table=None):
        # get all table contents and display connections in tree structure for TreeView
        pass
