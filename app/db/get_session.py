from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings

# import all models here
from app.db.base import *  # noqa


def _get_engine(db_url: str):
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session() -> Generator[Session, None, None]:
    engine = _get_engine(settings.DATABASE_URL)
    with Session(engine) as session:  # type: ignore
        yield session
    session.close()
