from pydantic import BaseModel, model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import platform
import os

ROOT_DIRECTORY: Path = Path(__file__).resolve().parent.parent


def get_default_download_dir() -> Path:
    system = platform.system()
    home = Path.home()

    if system == "Linux":
        xdg = Path(os.environ["XDG_DOWNLOAD_DIR"]) if "XDG_DOWNLOAD_DIR" in os.environ else None
        return xdg or home / "Downloads"

    return home / "Downloads"


DEFAULT_DOWNLOAD_DIR = get_default_download_dir()


class CertificateSettings(BaseModel):
    PROD_CA_CERT: Path = Path("/temp_path_until_distrib_configured/ca.crt")
    PROD_CA_KEY: Path = Path("/temp_path_until_distrib_configured/ca.key")
    ca_cert_path: Path | None = None
    ca_key_path: Path | None = None

    @model_validator(mode="after")
    def resolve_ca_paths(self) -> "CertificateSettings":
        dev_cert = ROOT_DIRECTORY / "localdev" / "root_ca.crt"
        dev_key = ROOT_DIRECTORY / "localdev" / "root_ca.key"

        if self.PROD_CA_CERT.exists() and self.PROD_CA_KEY.exists():
            self.ca_cert_path = self.PROD_CA_CERT
            self.ca_key_path = self.PROD_CA_KEY
        elif dev_cert.exists() and dev_key.exists():
            self.ca_cert_path = dev_cert
            self.ca_key_path = dev_key
        else:
            raise ValueError("No CA cert/key found in prod or dev paths")
        return self


class DatabaseSettings(BaseModel):
    database_name: str = "windrop"

    @property
    def database_path(self) -> Path:
        return ROOT_DIRECTORY / "database" / (self.database_name + ".db")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(json_file="app_config.json", populate_by_name=True)
    root_directory: Path = ROOT_DIRECTORY
    config_path:Path = ROOT_DIRECTORY / "config" / "app_config.json"
    app_name: str = "WinDrop"
    download_directory: Path | None = Field(default=None, alias="download_path")

    @property
    def migration_directory_path(self) -> Path:
        return ROOT_DIRECTORY / "migrations"

    database: DatabaseSettings = DatabaseSettings()
    certificate_authority: CertificateSettings = CertificateSettings()

    @model_validator(mode="after")
    def resolve_download_dir(self) -> "Settings":
        if self.download_directory is None:
            self.download_directory = DEFAULT_DOWNLOAD_DIR
        return self


settings = Settings()
