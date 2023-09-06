from typing import Optional
from pydantic import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    DB_DRIVERNAME: str = "postgresql+asyncpg"
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_DATABASE: str

    @property
    def db_connection_string(self):
        return URL.create(
            drivername=self.DB_DRIVERNAME,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_DATABASE,
        )
