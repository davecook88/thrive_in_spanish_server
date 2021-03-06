from pydantic import BaseSettings, PostgresDsn
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # DATABASE CONNECTION
    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn
    GOOGLE_CLIENT_ID: str

    DEFAULT_ORGANIZATION_ID: int = 1

    DEFAULT_PAGE_SIZE: int = 100

    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str


settings = Settings()  # type: ignore
