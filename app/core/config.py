from pydantic import BaseSettings, PostgresDsn
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # DATABASE CONNECTION
    DATABASE_URL: PostgresDsn


settings = Settings()  # type: ignore
