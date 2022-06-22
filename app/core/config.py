from pydantic import BaseSettings, PostgresDsn
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # DATABASE CONNECTION
    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn
    GOOGLE_CLIENT_ID: str

    DEFAULT_PAGE_SIZE: int = 100


settings = Settings()  # type: ignore
