from fastapi import FastAPI
import migrate
from config.config import settings

def main():
    migrate.migrate_database()        
    app = FastAPI()

if __name__ == "__main__":
    main()
