from config.config import settings
from database.database import database 
from pathlib import Path

MIGRATION_DIR_PATH: Path = settings.migration_directory_path

def apply_migration(migration_file_path):
    with open(migration_file_path, "r") as sql_script:
        script = sql_script.read()
        database.execute_sql(script)

def migrate_database():
    migration_files = sorted(list(MIGRATION_DIR_PATH.glob('**/*.sql')))
    print(migration_files)
    num_migrations = len(migration_files)
    print(num_migrations)
    if num_migrations < 1:
        print("No migrations to run")
    elif num_migrations == 1:
        apply_migration(migration_files[0])
    else:
        for migration_file in migration_files[1:]:
            apply_migration(migration_file)