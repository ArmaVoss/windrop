from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

class DatabaseSettings(BaseModel):
    root_path: Path 
    
    database_name: str = "windrop"
    
    @property
    def database_path(self) -> Path:
        return self.root_path / "database" / (self. database_name + ".db")

class Settings(BaseSettings):
    # app conf
    app_name: str = "WinDrop"
    
    # paths 
    root_directory: Path = Path(__file__).resolve().parent.parent
    
    @property
    def migration_directory_path(self) -> Path:
        return self.root_directory / "migrations"

    # database conf
    database: DatabaseSettings = DatabaseSettings(root_path=root_directory)


settings = Settings()
