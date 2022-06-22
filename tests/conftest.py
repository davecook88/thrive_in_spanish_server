from typing import Any, AsyncGenerator
from dotenv import load_dotenv
from fastapi import FastAPI
import pytest
import pytest_asyncio
from sqlalchemy.future.engine import Engine
from sqlmodel import SQLModel, Session, create_engine
from app.db.models.user.user import User
from app.main import app
from app.core.config import Settings
from fastapi.testclient import TestClient
from app.db.get_session import get_session


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    load_dotenv()


@pytest.fixture
def app_settings() -> Settings:
    from app.core.config import settings

    return settings


@pytest_asyncio.fixture
async def engine(app_settings: Settings) -> AsyncGenerator[Engine, Any]:
    engine = create_engine(app_settings.TEST_DATABASE_URL)
    yield engine


@pytest_asyncio.fixture
async def session(engine: Engine) -> AsyncGenerator[Session, Any]:
    meta = SQLModel.metadata
    meta.drop_all(engine)
    meta.create_all(engine)
    with Session(engine) as session:  # type: ignore
        session: Session = session
        yield session

    meta.drop_all(engine)


@pytest.fixture
def fast_api_app() -> FastAPI:
    return app


@pytest.fixture
def client(fast_api_app: FastAPI, session: Session) -> TestClient:
    async def override_get_session() -> AsyncGenerator[TestClient, None]:
        yield session  # type: ignore
        return

    fast_api_app.dependency_overrides[get_session] = override_get_session

    return TestClient(fast_api_app)


@pytest.fixture(scope="session")
def google_id() -> str:
    return "abc"


@pytest_asyncio.fixture
async def user(session: Session, google_id: str) -> User:
    u = User.create_user(
        name="test user", email="email@domain.com", google_id=google_id
    )
    await u.save(session)
    user = session.get(User, u.id)
    if not user:
        raise Exception("User fixture didn't save correctly")
    return user
