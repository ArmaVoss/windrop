from fastapi import FastAPI
from migrate import migrate_database
from config.config import settings

def main():
    migrate_database()        
    app = FastAPI()

if __name__ == "__main__":
    main()
