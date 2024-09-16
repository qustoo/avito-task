from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    echo: bool = True
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class DatabaseData(BaseModel):
    user: str
    password: str
    name: str
    port: int


class Settings(BaseSettings):
    db: DatabaseData
    api: ApiPrefix = ApiPrefix()
    db_config: DatabaseConfig = DatabaseConfig()
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="_",
        env_file=(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.db.user}:{self.db.password}@db:{self.db.port}/{self.db.name}"


settings = Settings()
