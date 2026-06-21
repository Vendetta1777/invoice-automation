from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg2://invoice_admin:dev_password_change_me@localhost:5432/invoice_automation"

    # Directory of the built React app to serve in production (set in Docker/Render).
    static_dir: str = ""

    @field_validator("database_url")
    @classmethod
    def _normalize_db_url(cls, value: str) -> str:
        # Managed hosts (Render/Railway) often hand out "postgres://..." which
        # SQLAlchemy 2.0 no longer accepts; pin the psycopg2 driver.
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg2://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg2://", 1)
        return value

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "invoices@example.com"
    smtp_from_name: str = "Invoice Automation"

    business_name: str = "Your Business Name"
    business_address: str = ""
    business_email: str = ""
    business_phone: str = ""

    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
