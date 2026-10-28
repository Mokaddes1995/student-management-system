from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    debug: bool = False
    database_url: str = str(
        URL.create(
            "sqlite",
            database=str(PROJECT_ROOT / "student.db"),
        )
    )


settings = Settings()

DATABASE_URL = make_url(settings.database_url)

if DATABASE_URL.get_backend_name() == "sqlite":
    database = DATABASE_URL.database

    if database and database != ":memory:":
        database_path = Path(database)

        if not database_path.is_absolute():
            database_path = PROJECT_ROOT / database_path

        DATABASE_URL = DATABASE_URL.set(database=str(database_path.resolve()))
