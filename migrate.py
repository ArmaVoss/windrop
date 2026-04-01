import sqlite3
from config import settings
import pathlib

MIGRATION_DIR_PATH = settings.migration_dir_path

def read_migration_file(file):
    with open(file, "r") as f:
        file_content = f.read()
        

def migrate_database():
    migration_files = sorted(list(MIGRATION_DIR_PATH.glob('**/*.sql')))
    
    num_migrataions = len(migration_files)
    if len(num_migrataions) < 0:
        print("No migrations to run")
    elif len(num_migrataions) == 1:
        read_migration_file(num_migrataions[0])
    else:
         pass
    # read files in within the ./migrations path