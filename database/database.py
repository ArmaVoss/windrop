import sqlite3
from config.config import settings

class Database():
    def __init__(self, database_path: str):
        self.__db = sqlite3.connect(database_path)

    
    def execute_sql(self, sql, params=()):
        with self.__db:
            cursor = self.__db.cursor()
            cursor.execute(sql, params)
            return cursor



database = Database(settings.database.database_path)