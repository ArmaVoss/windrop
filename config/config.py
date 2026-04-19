from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIRECTORY: Path = Path(__file__).resolve().parent.parent

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
        return ROOT_DIRECTORY / "database" / (self. database_name + ".db")

class Settings(BaseSettings):
    # app conf
    app_name: str = "WinDrop"
    
    @property
    def migration_directory_path(self) -> Path:
        return ROOT_DIRECTORY / "migrations"

    database: DatabaseSettings = DatabaseSettings()
    certificate_authority: CertificateSettings = CertificateSettings()

settings = Settings()
