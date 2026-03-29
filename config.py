from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Windrop"
    
    ROOT_DIR: Path = Path(__file__).resolve().parent




