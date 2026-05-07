from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIRECTORY: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    tray_icon_path: Path = ROOT_DIRECTORY / "resources" / "tray_icon.png"


settings = Settings()
