from fastapi import FastAPI
from migrate import migrate_database

def main():
    # app = FastAPI()
    migrate_database()
        
if __name__ == "__main__":
    main()
