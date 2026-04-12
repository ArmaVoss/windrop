from config.config import settings
from database.database import database 
from pathlib import Path
import sys 
MIGRATION_DIR_PATH: Path = settings.migration_directory_path

def add_schema_table():

    try:
        database.execute_sql(    
            """CREATE TABLE IF NOT EXISTS schema_migrations(
            version INTEGER NOT NULL PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );"""
        )
    except:
        print("Error starting database")
        sys.exit(1)  

def apply_migration(migration_file_path, version):
    with open(migration_file_path, "r") as sql_script:
        script = sql_script.read()

    try:
        database.execute_script(script)
        database.execute_sql(
            """
            INSERT INTO schema_migrations (version)
            VALUES (?);
            """,
            (version,)
        )
        database.commit()
    except Exception:
        database.rollback()
        raise

def migrate_database():
    add_schema_table()
    
    migration_files = sorted(list(MIGRATION_DIR_PATH.glob("**/*.sql")))
    num_migration_files = len(migration_files)

    if num_migration_files < 1:
        print("No migrations to run")
        return
    
    database_cursor = database.execute_sql(
        "SELECT COUNT(*) AS count FROM schema_migrations"
    )

    number_migrated_rows = database_cursor.fetchone()["count"]

    if number_migrated_rows == num_migration_files:
        print("Migrations up to date")
        return

    for migration_number, migration in enumerate(
        migration_files[number_migrated_rows:],
        start=number_migrated_rows + 1
    ):
        apply_migration(migration, migration_number)

