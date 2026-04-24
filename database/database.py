import sqlite3

from config.config import settings


class Database:
    def __init__(self, database_path: str):
        self.__db = sqlite3.connect(database_path)
        self.__db.row_factory = sqlite3.Row

    def execute_sql(self, sql, params=()):
        cursor = self.__db.cursor()
        cursor.execute(sql, params)
        return cursor

    def execute_script(self, sql):
        cursor = self.__db.cursor()
        cursor.executescript(sql)
        return cursor

    def commit(self):
        self.__db.commit()

    def rollback(self):
        self.__db.rollback()

    def close(self):
        self.__db.close()


database = Database(settings.database.database_path)
